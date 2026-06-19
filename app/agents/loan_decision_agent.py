"""Loan Decision Agent - makes final Approve/Reject/Review decision."""

import json
from app.agents.base_agent import BaseAgent
from app.models.agent_state import LoanApprovalState
from app.models.schemas import LoanDecision


class LoanDecisionAgent(BaseAgent):
    """Makes the final loan approval decision based on prior analyses."""

    def __init__(self):
        super().__init__(name="LoanDecisionAgent")

    def _create_system_prompt(self) -> str:
        return """You are the final decision-maker in a loan approval system.
Your role is to synthesize prior analyses and make a final decision.

You must respond with valid JSON in this exact format:
{
    "decision": "<string: Approve, Reject, or Review>",
    "confidence_score": <float between 0-100>,
    "reasoning": "<string explaining the decision>",
    "recommended_conditions": ["<condition1>", "<condition2>"]
}

Decision rules:
- Approve: Profile risk Low, Financial risk Low, credit score 700+, DTI < 0.43
- Reject: Profile risk High, Financial risk High, credit score < 600, DTI > 0.50
- Review: All other cases where more analysis is needed

Always provide reasoning that references the prior analyses."""

    def run(self, state: LoanApprovalState) -> LoanApprovalState:
        """Make final loan decision."""
        if not state.profile_analysis or not state.financial_analysis:
            state.add_error("Missing required analyses for loan decision")
            return state

        profile = state.profile_analysis
        financial = state.financial_analysis
        app = state.application

        prompt = f"""Based on prior analyses, make a final loan decision:

Profile Analysis:
- Income Stability Score: {profile.income_stability_score}
- Employment Assessment: {profile.employment_assessment}
- Risk Level: {profile.profile_risk_level}

Financial Analysis:
- Debt-to-Income Ratio: {financial.debt_to_income_ratio:.2%}
- Credit Assessment: {financial.credit_assessment}
- Financial Risk Score: {financial.financial_risk_score}
- Risk Level: {financial.risk_level}

Application Details:
- Credit Score: {app.credit_score}
- Loan Amount: ${app.loan_amount:,.2f}
- Loan Tenure: {app.loan_tenure_months} months
- Monthly Income: ${app.monthly_income:,.2f}

Make a final decision (Approve/Reject/Review) with reasoning and any recommended conditions. Return only valid JSON."""

        try:
            response = self.query_claude([{"role": "user", "content": prompt}], temperature=0.2)
            result = self._parse_response(response)

            state.loan_decision = LoanDecision(
                decision=result.get("decision", "Review"),
                confidence_score=result.get("confidence_score", 50),
                reasoning=result.get("reasoning", "Decision pending"),
                recommended_conditions=result.get("recommended_conditions", []),
            )

            self._log_action(
                state,
                "loan_decision_completed",
                {
                    "decision": state.loan_decision.decision,
                    "confidence_score": state.loan_decision.confidence_score,
                },
            )

        except Exception as e:
            state.add_error(f"LoanDecisionAgent error: {str(e)}")
            state.loan_decision = LoanDecision(
                decision="Review",
                confidence_score=0,
                reasoning="Error during decision making",
                recommended_conditions=[],
            )

        return state
