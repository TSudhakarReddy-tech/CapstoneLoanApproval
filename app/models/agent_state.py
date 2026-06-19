"""LangGraph state definition for loan approval workflow."""

from dataclasses import dataclass, field
from datetime import datetime
from app.models.schemas import (
    LoanApplicationRequest,
    ApplicationProfileAnalysis,
    FinancialRiskAnalysis,
    LoanDecision,
    ComplianceCheckResult,
)


@dataclass
class LoanApprovalState:
    """State object passed through LangGraph workflow."""

    # Original application
    application: LoanApplicationRequest

    # Agent outputs
    profile_analysis: ApplicationProfileAnalysis | None = None
    financial_analysis: FinancialRiskAnalysis | None = None
    loan_decision: LoanDecision | None = None
    compliance_result: ComplianceCheckResult | None = None

    # Metadata
    application_id: str = field(default_factory=lambda: str(datetime.utcnow().timestamp()))
    workflow_status: str = field(default="initiated")
    error_messages: list[str] = field(default_factory=list)
    audit_trail: list[dict] = field(default_factory=list)

    def add_audit_entry(self, agent_name: str, action: str, details: dict = None):
        """Record an audit trail entry."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent": agent_name,
            "action": action,
            "details": details or {},
        }
        self.audit_trail.append(entry)

    def add_error(self, error_message: str):
        """Record an error that occurred during processing."""
        self.error_messages.append(error_message)
        self.workflow_status = "error"
