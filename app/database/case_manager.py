"""Utilities for case ID generation and decision summary management."""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any


class CaseIDGenerator:
    """Generate formatted case IDs for loan decisions."""

    @staticmethod
    def generate_case_id(decision_type: str, application_id: str) -> str:
        """
        Generate a formatted case ID.

        Format: CASE-{TYPE}-{TIMESTAMP}-{HASH}
        Example: CASE-APP-20240615-A1B2C3 (Approved)
                 CASE-REJ-20240615-D4E5F6 (Rejected)
                 CASE-REV-20240615-G7H8I9 (Under Review)

        Args:
            decision_type: 'APPROVED', 'REJECTED', or 'UNDER_REVIEW'
            application_id: The original application ID

        Returns:
            Formatted case ID
        """
        type_map = {
            "APPROVED": "APP",
            "REJECTED": "REJ",
            "UNDER_REVIEW": "REV"
        }

        type_code = type_map.get(decision_type, "GEN")
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        hash_code = str(uuid.uuid4())[:6].upper()

        return f"CASE-{type_code}-{timestamp}-{hash_code}"


class DecisionSummaryGenerator:
    """Generate detailed decision summaries for loan decisions."""

    @staticmethod
    def generate_approval_summary(
        applicant_name: str,
        loan_amount: float,
        monthly_income: float,
        confidence_score: float,
        conditions: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate approval decision summary."""
        summary = f"""
LOAN APPLICATION DECISION - APPROVED

Applicant: {applicant_name}
Decision: APPROVED
Decision Date: {datetime.utcnow().strftime("%B %d, %Y")}
Confidence Score: {confidence_score:.2%}

Loan Details:
- Requested Amount: ${loan_amount:,.2f}
- Monthly Income: ${monthly_income:,.2f}
- Debt-to-Income Ratio: {(loan_amount / (monthly_income * 12)) * 100:.2f}%

Decision Summary:
The applicant has been approved for the requested loan amount based on:
✓ Strong credit profile
✓ Stable employment history
✓ Acceptable debt-to-income ratio
✓ Compliance with all lending criteria
"""

        if conditions:
            summary += "\nApproval Conditions:\n"
            for i, (condition, value) in enumerate(conditions.items(), 1):
                summary += f"{i}. {condition}: {value}\n"

        summary += f"\nThis approval is valid for 30 days from the decision date."
        return summary

    @staticmethod
    def generate_rejection_summary(
        applicant_name: str,
        rejection_reasons: list,
        confidence_score: float
    ) -> str:
        """Generate rejection decision summary."""
        summary = f"""
LOAN APPLICATION DECISION - REJECTED

Applicant: {applicant_name}
Decision: REJECTED
Decision Date: {datetime.utcnow().strftime("%B %d, %Y")}
Confidence Score: {confidence_score:.2%}

Rejection Reasons:
"""
        for i, reason in enumerate(rejection_reasons, 1):
            summary += f"{i}. {reason}\n"

        summary += """
Appeal Process:
If you believe this decision is incorrect, you may appeal within 30 days by:
1. Submitting additional documentation
2. Contacting our loan review team at support@loanapproval.com
3. Requesting a manual review by our underwriting team

We appreciate your interest in our loan products.
"""
        return summary

    @staticmethod
    def generate_review_summary(
        applicant_name: str,
        review_reason: str,
        required_docs: Optional[list] = None
    ) -> str:
        """Generate under-review decision summary."""
        summary = f"""
LOAN APPLICATION DECISION - UNDER REVIEW

Applicant: {applicant_name}
Status: UNDER REVIEW
Review Started: {datetime.utcnow().strftime("%B %d, %Y")}

Review Reason:
{review_reason}
"""

        if required_docs:
            summary += "\nRequired Documentation:\n"
            for i, doc in enumerate(required_docs, 1):
                summary += f"- {doc}\n"
            summary += "\nPlease submit the above documents within 5 business days to expedite the review process.\n"

        summary += "\nExpected Review Completion: 5-7 business days\n"
        summary += "You will be notified via email once the review is complete.\n"

        return summary


class DecisionRecordBuilder:
    """Builder class for creating detailed decision records."""

    def __init__(self, application_id: str, applicant_name: str):
        self.application_id = application_id
        self.applicant_name = applicant_name
        self.decision_data = {}

    def set_approval(
        self,
        confidence_score: float,
        loan_amount: float,
        monthly_income: float,
        conditions: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> "DecisionRecordBuilder":
        """Set approval decision."""
        self.decision_data = {
            "decision": "APPROVED",
            "decision_category": "APPROVED",
            "confidence_score": confidence_score,
            "case_id": CaseIDGenerator.generate_case_id("APPROVED", self.application_id),
            "decision_summary": DecisionSummaryGenerator.generate_approval_summary(
                self.applicant_name, loan_amount, monthly_income, confidence_score, conditions
            ),
            "approval_conditions": conditions or {},
            "risk_level": self._calculate_risk_level(confidence_score),
        }
        self.decision_data.update(kwargs)
        return self

    def set_rejection(
        self,
        confidence_score: float,
        rejection_reasons: list,
        **kwargs
    ) -> "DecisionRecordBuilder":
        """Set rejection decision."""
        self.decision_data = {
            "decision": "REJECTED",
            "decision_category": "REJECTED",
            "confidence_score": confidence_score,
            "case_id": CaseIDGenerator.generate_case_id("REJECTED", self.application_id),
            "decision_summary": DecisionSummaryGenerator.generate_rejection_summary(
                self.applicant_name, rejection_reasons, confidence_score
            ),
            "rejection_reason": " | ".join(rejection_reasons),
            "risk_level": "HIGH",
        }
        self.decision_data.update(kwargs)
        return self

    def set_under_review(
        self,
        review_reason: str,
        required_docs: Optional[list] = None,
        **kwargs
    ) -> "DecisionRecordBuilder":
        """Set under-review decision."""
        self.decision_data = {
            "decision": "UNDER_REVIEW",
            "decision_category": "UNDER_REVIEW",
            "confidence_score": 0.0,
            "case_id": CaseIDGenerator.generate_case_id("UNDER_REVIEW", self.application_id),
            "decision_summary": DecisionSummaryGenerator.generate_review_summary(
                self.applicant_name, review_reason, required_docs
            ),
            "review_notes": review_reason,
            "risk_level": "MEDIUM",
        }
        self.decision_data.update(kwargs)
        return self

    @staticmethod
    def _calculate_risk_level(confidence_score: float) -> str:
        """Calculate risk level based on confidence score."""
        if confidence_score >= 0.9:
            return "LOW"
        elif confidence_score >= 0.75:
            return "MEDIUM"
        elif confidence_score >= 0.6:
            return "HIGH"
        else:
            return "CRITICAL"

    def build(self) -> Dict[str, Any]:
        """Return the built decision record data."""
        return self.decision_data


__all__ = ["CaseIDGenerator", "DecisionSummaryGenerator", "DecisionRecordBuilder"]
