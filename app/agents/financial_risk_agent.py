"""Financial Risk Analysis Agent - evaluates credit and debt ratios."""

import json
from app.agents.base_agent import BaseAgent
from app.models.agent_state import LoanApprovalState
from app.models.schemas import FinancialRiskAnalysis


class FinancialRiskAgent(BaseAgent):
    """Analyzes financial risk through credit scores and debt ratios."""

    def __init__(self):
        super().__init__(name="FinancialRiskAgent")

    def _create_system_prompt(self) -> str:
        return """You are a financial risk assessment specialist in a loan approval system.
Your role is to analyze creditworthiness and debt metrics to determine financial risk.

You must respond with valid JSON in this exact format:
{
    "debt_to_income_ratio": <float>,
    "credit_assessment": "<string describing credit quality>",
    "liability_assessment": "<string describing liability situation>",
    "financial_risk_score": <float between 0-100>,
    "risk_level": "<string: Low/Medium/High>"
}

Consider:
- Credit score (higher is better, 750+ typically excellent)
- Debt-to-income ratio (lower is better, <0.43 is good)
- Total liabilities relative to income
- Payment history indicators
- Overall financial health"""

    def run(self, state: LoanApprovalState) -> LoanApprovalState:
        """Analyze financial risk."""
        app = state.application

        monthly_debt_payments = (app.total_liabilities / 12) if app.total_liabilities > 0 else 0
        debt_to_income_ratio = (
            monthly_debt_payments / app.monthly_income
            if app.monthly_income > 0
            else 0
        )

        try:
            # Assess credit score
            if app.credit_score >= 750:
                credit_assessment = "Excellent credit history - Strong credit profile"
                credit_score_points = 90
            elif app.credit_score >= 700:
                credit_assessment = "Good credit history - Acceptable credit profile"
                credit_score_points = 75
            elif app.credit_score >= 650:
                credit_assessment = "Fair credit history - Some concerns noted"
                credit_score_points = 55
            else:
                credit_assessment = "Poor credit history - Significant concerns"
                credit_score_points = 30

            # Assess liabilities
            if app.total_liabilities == 0:
                liability_assessment = "No existing liabilities - Clean financial slate"
                liability_points = 100
            elif app.total_liabilities < app.monthly_income * 3:
                liability_assessment = "Manageable liabilities - Within acceptable range"
                liability_points = 75
            elif app.total_liabilities < app.monthly_income * 6:
                liability_assessment = "Moderate liabilities - Some concern"
                liability_points = 50
            else:
                liability_assessment = "High liabilities - Significant concern"
                liability_points = 25

            # Assess DTI
            if debt_to_income_ratio < 0.3:
                dti_assessment = "Excellent DTI ratio"
                dti_points = 90
            elif debt_to_income_ratio < 0.43:
                dti_assessment = "Good DTI ratio"
                dti_points = 75
            elif debt_to_income_ratio < 0.50:
                dti_assessment = "Acceptable DTI ratio"
                dti_points = 55
            else:
                dti_assessment = "High DTI ratio - Exceeds threshold"
                dti_points = 20

            # Calculate overall financial risk score
            financial_risk_score = (credit_score_points + liability_points + dti_points) / 3

            # Determine risk level
            if financial_risk_score >= 75:
                risk_level = "Low"
            elif financial_risk_score >= 50:
                risk_level = "Medium"
            else:
                risk_level = "High"

            state.financial_analysis = FinancialRiskAnalysis(
                debt_to_income_ratio=debt_to_income_ratio,
                credit_assessment=credit_assessment,
                liability_assessment=liability_assessment,
                financial_risk_score=financial_risk_score,
                risk_level=risk_level,
            )

            self._log_action(
                state,
                "financial_analysis_completed",
                {
                    "debt_to_income_ratio": state.financial_analysis.debt_to_income_ratio,
                    "financial_risk_score": state.financial_analysis.financial_risk_score,
                },
            )

        except Exception as e:
            state.add_error(f"FinancialRiskAgent error: {str(e)}")
            state.financial_analysis = FinancialRiskAnalysis(
                debt_to_income_ratio=debt_to_income_ratio,
                credit_assessment="Error during assessment",
                liability_assessment="Error during assessment",
                financial_risk_score=50,
                risk_level="High",
            )

        return state
