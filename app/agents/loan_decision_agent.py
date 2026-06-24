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

        try:
            # Determine decision based on risk scores
            profile_risk = profile.profile_risk_level
            financial_risk = financial.risk_level
            credit_score = app.credit_score
            dti = financial.debt_to_income_ratio

            # Calculate confidence score
            confidence = (profile.income_stability_score + financial.financial_risk_score) / 2

            # Decision logic
            if (profile_risk == "Low" and financial_risk == "Low" and credit_score >= 700 and dti < 0.43):
                decision = "Approved"
                confidence = max(confidence, 85)
                reasoning = f"Excellent profile and financial metrics. Strong approval candidate with {confidence:.0f}% confidence."
                conditions = [
                    "Standard interest rate 4.5%",
                    "Maximum tenure as requested",
                    "Insurance requirement applies"
                ]
            elif (profile_risk == "High" or financial_risk == "High" or credit_score < 600 or dti > 0.50):
                decision = "Rejected"
                confidence = max(confidence, 70)
                reasons = []
                if profile_risk == "High":
                    reasons.append("Employment profile concerns")
                if financial_risk == "High":
                    reasons.append("Financial risk exceeds threshold")
                if credit_score < 600:
                    reasons.append(f"Credit score {credit_score} below minimum")
                if dti > 0.50:
                    reasons.append(f"DTI {dti:.1%} exceeds limits")
                reasoning = f"Application rejected due to: {', '.join(reasons)}"
                conditions = []
            else:
                decision = "Under Review"
                confidence = 50
                reasoning = f"Application requires additional review. Profile risk: {profile_risk}, Financial risk: {financial_risk}, DTI: {dti:.1%}. Further documentation may be requested."
                conditions = ["Additional documentation may be required", "Review expected within 5-7 business days"]

            state.loan_decision = LoanDecision(
                decision=decision,
                confidence_score=confidence,
                reasoning=reasoning,
                recommended_conditions=conditions,
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
                decision="Under Review",
                confidence_score=50,
                reasoning="Error during decision making - manual review required",
                recommended_conditions=["Manual review required"],
            )

        return state
