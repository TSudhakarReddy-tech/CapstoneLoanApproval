"""Compliance & Action Agent - handles notifications and case management."""

import json
from app.agents.base_agent import BaseAgent
from app.models.agent_state import LoanApprovalState
from app.models.schemas import ComplianceCheckResult


class ComplianceAgent(BaseAgent):
    """Handles compliance checks, notifications, and case management."""

    def __init__(self):
        super().__init__(name="ComplianceAgent")

    def _create_system_prompt(self) -> str:
        return """You are a compliance and case management specialist in a loan approval system.
Your role is to verify compliance requirements and generate appropriate notifications.

You must respond with valid JSON in this exact format:
{
    "compliance_status": "<string: Approved, Flagged, or Rejected>",
    "notification_sent": true/false,
    "case_reference": "<string with case number>",
    "next_steps": ["<step1>", "<step2>"]
}

Compliance checks:
- Verify no red flags in financial history
- Check regulatory requirements
- Ensure decision audit trail is complete
- Generate appropriate notifications based on decision
- Create case reference for record keeping"""

    def run(self, state: LoanApprovalState) -> LoanApprovalState:
        """Perform compliance checks and generate notifications."""
        if not state.loan_decision:
            state.add_error("Loan decision required for compliance check")
            return state

        decision = state.loan_decision
        app = state.application

        prompt = f"""Perform compliance check and generate notification for this loan decision:

Decision: {decision.decision}
Confidence: {decision.confidence_score}%
Applicant: {app.applicant_name}
Credit Score: {app.credit_score}
Loan Amount: ${app.loan_amount:,.2f}

Generate compliance status and next steps. Include audit trail review. Return only valid JSON."""

        try:
            response = self.query_claude([{"role": "user", "content": prompt}], temperature=0.2)
            result = self._parse_response(response)

            case_ref = result.get("case_reference", f"LOAN-{state.application_id[:8].upper()}")

            state.compliance_result = ComplianceCheckResult(
                compliance_status=result.get("compliance_status", "Flagged"),
                notification_sent=result.get("notification_sent", True),
                case_reference=case_ref,
                next_steps=result.get("next_steps", ["Application under review"]),
            )

            self._log_action(
                state,
                "compliance_check_completed",
                {
                    "compliance_status": state.compliance_result.compliance_status,
                    "case_reference": state.compliance_result.case_reference,
                },
            )

            state.workflow_status = "completed"

        except Exception as e:
            state.add_error(f"ComplianceAgent error: {str(e)}")
            state.compliance_result = ComplianceCheckResult(
                compliance_status="Flagged",
                notification_sent=False,
                case_reference=f"LOAN-{state.application_id[:8].upper()}",
                next_steps=["Manual review required due to processing error"],
            )

        return state
