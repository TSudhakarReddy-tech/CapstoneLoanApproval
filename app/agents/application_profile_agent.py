"""Application Profile Agent - evaluates income stability and employment."""

import json
from app.agents.base_agent import BaseAgent
from app.models.agent_state import LoanApprovalState
from app.models.schemas import ApplicationProfileAnalysis


class ApplicationProfileAgent(BaseAgent):
    """Analyzes applicant profile for income stability and employment suitability."""

    def __init__(self):
        super().__init__(name="ApplicationProfileAgent")

    def _create_system_prompt(self) -> str:
        return """You are an expert HR and income assessment specialist in a loan approval system.
Your role is to analyze applicant profiles and determine income stability, employment suitability, and demographic appropriateness.

You must respond with valid JSON in this exact format:
{
    "income_stability_score": <float between 0-100>,
    "employment_assessment": "<string describing employment stability>",
    "age_category": "<string: Young Professional/Mid-Career/Experienced/Pre-Retirement>",
    "profile_risk_level": "<string: Low/Medium/High>"
}

Consider:
- Income level relative to typical benchmarks
- Years of employment (stability indicator)
- Employment type (salaried is more stable than self-employed)
- Age appropriateness for loan tenure
- Overall employment history indicators"""

    def run(self, state: LoanApprovalState) -> LoanApprovalState:
        """Analyze applicant profile."""
        app = state.application

        prompt = f"""Analyze this applicant profile:

Applicant Name: {app.applicant_name}
Age: {app.age} years
Monthly Income: ${app.monthly_income:,.2f}
Employment Type: {app.employment_type}
Years Employed: {app.years_employed}
Requested Loan Amount: ${app.loan_amount:,.2f}
Loan Tenure: {app.loan_tenure_months} months

Evaluate income stability and employment suitability. Return only valid JSON."""

        try:
            response = self.query_claude([{"role": "user", "content": prompt}], temperature=0.3)
            result = self._parse_response(response)

            state.profile_analysis = ApplicationProfileAnalysis(
                income_stability_score=result.get("income_stability_score", 50),
                employment_assessment=result.get("employment_assessment", "Assessment pending"),
                age_category=result.get("age_category", "Mid-Career"),
                profile_risk_level=result.get("profile_risk_level", "Medium"),
            )

            self._log_action(
                state,
                "profile_analysis_completed",
                {
                    "income_stability_score": state.profile_analysis.income_stability_score,
                    "risk_level": state.profile_analysis.profile_risk_level,
                },
            )

        except Exception as e:
            state.add_error(f"ApplicationProfileAgent error: {str(e)}")
            state.profile_analysis = ApplicationProfileAnalysis(
                income_stability_score=50,
                employment_assessment="Error during assessment",
                age_category="Unknown",
                profile_risk_level="High",
            )

        return state
