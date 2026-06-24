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

        try:
            # Calculate income stability score based on years employed
            if app.years_employed >= 5:
                income_stability = 85
                employment_assessment = "Strong employment stability - 5+ years at current employer"
            elif app.years_employed >= 2:
                income_stability = 70
                employment_assessment = "Moderate employment stability - 2+ years at current employer"
            else:
                income_stability = 45
                employment_assessment = "Limited employment history - Less than 2 years at current employer"

            # Adjust based on employment type
            if app.employment_type == "Salaried":
                income_stability += 10
            elif app.employment_type == "Self-employed":
                income_stability -= 15

            # Categorize age
            if app.age < 30:
                age_category = "Young Professional"
            elif app.age < 50:
                age_category = "Mid-Career"
            elif app.age < 65:
                age_category = "Experienced"
            else:
                age_category = "Pre-Retirement"

            # Determine risk level
            if income_stability >= 75:
                risk_level = "Low"
            elif income_stability >= 50:
                risk_level = "Medium"
            else:
                risk_level = "High"

            state.profile_analysis = ApplicationProfileAnalysis(
                income_stability_score=min(100, max(0, income_stability)),
                employment_assessment=employment_assessment,
                age_category=age_category,
                profile_risk_level=risk_level,
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
