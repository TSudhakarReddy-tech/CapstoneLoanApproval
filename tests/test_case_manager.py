"""Tests for case management system."""

import pytest
from datetime import datetime
from app.database.case_manager import (
    CaseIDGenerator,
    DecisionSummaryGenerator,
    DecisionRecordBuilder,
)


class TestCaseIDGenerator:
    """Test case ID generation."""

    def test_generate_approval_case_id(self):
        """Test generating approval case ID."""
        case_id = CaseIDGenerator.generate_case_id("APPROVED", "app_123")
        assert case_id.startswith("CASE-APP-")
        assert len(case_id) == 28  # CASE-APP-YYYYMMDD-XXXXXX

    def test_generate_rejection_case_id(self):
        """Test generating rejection case ID."""
        case_id = CaseIDGenerator.generate_case_id("REJECTED", "app_456")
        assert case_id.startswith("CASE-REJ-")

    def test_generate_review_case_id(self):
        """Test generating under-review case ID."""
        case_id = CaseIDGenerator.generate_case_id("UNDER_REVIEW", "app_789")
        assert case_id.startswith("CASE-REV-")

    def test_case_ids_are_unique(self):
        """Test that case IDs are unique."""
        id1 = CaseIDGenerator.generate_case_id("APPROVED", "app_123")
        id2 = CaseIDGenerator.generate_case_id("APPROVED", "app_123")
        assert id1 != id2  # Different hash codes


class TestDecisionSummaryGenerator:
    """Test decision summary generation."""

    def test_generate_approval_summary(self):
        """Test generating approval summary."""
        summary = DecisionSummaryGenerator.generate_approval_summary(
            applicant_name="John Smith",
            loan_amount=50000,
            monthly_income=6500,
            confidence_score=0.92,
            conditions={"interest_rate": "4.5%"}
        )
        assert "APPROVED" in summary
        assert "John Smith" in summary
        assert "$50,000.00" in summary
        assert "92.00%" in summary
        assert "4.5%" in summary

    def test_generate_rejection_summary(self):
        """Test generating rejection summary."""
        summary = DecisionSummaryGenerator.generate_rejection_summary(
            applicant_name="Jane Doe",
            rejection_reasons=["Low credit score", "High debt-to-income ratio"],
            confidence_score=0.15
        )
        assert "REJECTED" in summary
        assert "Jane Doe" in summary
        assert "Low credit score" in summary
        assert "High debt-to-income ratio" in summary
        assert "Appeal Process" in summary

    def test_generate_review_summary(self):
        """Test generating under-review summary."""
        summary = DecisionSummaryGenerator.generate_review_summary(
            applicant_name="Michael Johnson",
            review_reason="Income verification needed",
            required_docs=["Tax returns", "Bank statements"]
        )
        assert "UNDER REVIEW" in summary
        assert "Michael Johnson" in summary
        assert "Income verification needed" in summary
        assert "Tax returns" in summary
        assert "Bank statements" in summary
        assert "5-7 business days" in summary


class TestDecisionRecordBuilder:
    """Test decision record builder."""

    def test_build_approval(self):
        """Test building approval record."""
        builder = DecisionRecordBuilder("app_123", "John Smith")
        builder.set_approval(
            confidence_score=0.92,
            loan_amount=50000,
            monthly_income=6500,
            conditions={"rate": "4.5%"}
        )
        data = builder.build()

        assert data["decision"] == "APPROVED"
        assert data["decision_category"] == "APPROVED"
        assert data["confidence_score"] == 0.92
        assert data["case_id"].startswith("CASE-APP-")
        assert data["risk_level"] == "LOW"
        assert "approval conditions" in data.get("decision_summary", "").lower()

    def test_build_rejection(self):
        """Test building rejection record."""
        builder = DecisionRecordBuilder("app_456", "Jane Doe")
        builder.set_rejection(
            confidence_score=0.15,
            rejection_reasons=["Low credit score"]
        )
        data = builder.build()

        assert data["decision"] == "REJECTED"
        assert data["decision_category"] == "REJECTED"
        assert data["confidence_score"] == 0.15
        assert data["case_id"].startswith("CASE-REJ-")
        assert data["risk_level"] == "HIGH"
        assert data["rejection_reason"] == "Low credit score"

    def test_build_under_review(self):
        """Test building under-review record."""
        builder = DecisionRecordBuilder("app_789", "Michael Johnson")
        builder.set_under_review(
            review_reason="Income verification",
            required_docs=["Tax returns"]
        )
        data = builder.build()

        assert data["decision"] == "UNDER_REVIEW"
        assert data["decision_category"] == "UNDER_REVIEW"
        assert data["case_id"].startswith("CASE-REV-")
        assert data["risk_level"] == "MEDIUM"
        assert data["review_notes"] == "Income verification"

    def test_risk_level_calculation(self):
        """Test risk level calculation."""
        assert DecisionRecordBuilder._calculate_risk_level(0.95) == "LOW"
        assert DecisionRecordBuilder._calculate_risk_level(0.80) == "MEDIUM"
        assert DecisionRecordBuilder._calculate_risk_level(0.65) == "HIGH"
        assert DecisionRecordBuilder._calculate_risk_level(0.50) == "CRITICAL"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
