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

        prompt = f"""Analyze this applicant's financial risk:

Credit Score: {app.credit_score}
Total Liabilities: ${app.total_liabilities:,.2f}
Monthly Income: ${app.monthly_income:,.2f}
Debt-to-Income Ratio: {debt_to_income_ratio:.2%}
Loan Amount Requested: ${app.loan_amount:,.2f}

Evaluate credit quality, debt burden, and overall financial risk. Return only valid JSON."""

        try:
            response = self.query_claude([{"role": "user", "content": prompt}], temperature=0.3)
            result = self._parse_response(response)

            state.financial_analysis = FinancialRiskAnalysis(
                debt_to_income_ratio=result.get("debt_to_income_ratio", debt_to_income_ratio),
                credit_assessment=result.get("credit_assessment", "Assessment pending"),
                liability_assessment=result.get("liability_assessment", "Assessment pending"),
                financial_risk_score=result.get("financial_risk_score", 50),
                risk_level=result.get("risk_level", "Medium"),
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
