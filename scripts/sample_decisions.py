#!/usr/bin/env python3
"""Sample script demonstrating decision record creation with detailed summaries."""

import uuid
from datetime import datetime
from app.database import (
    init_db,
    get_db_session,
    LoanApplication,
    add_decision_with_summary,
)


def create_sample_decisions():
    """Create sample loan applications and decisions with detailed summaries."""
    db = get_db_session()

    try:
        # Initialize database
        init_db()

        # Sample Application 1 - To be Approved
        app1_id = str(uuid.uuid4())
        app1 = LoanApplication(
            id=app1_id,
            applicant_name="John Smith",
            age=35,
            monthly_income=6500,
            employment_type="Full-time",
            years_employed=8,
            credit_score=750,
            total_liabilities=15000,
            loan_amount=50000,
            loan_tenure_months=60,
            location="New York, NY",
            submission_timestamp=datetime.utcnow(),
            status="submitted"
        )
        db.add(app1)
        db.commit()

        # Create APPROVED decision
        decision1 = add_decision_with_summary(
            db,
            application_id=app1_id,
            decision_type="APPROVED",
            confidence_score=0.92,
            profile_analysis={
                "employment_stability": "HIGH",
                "credit_history": "EXCELLENT",
                "age_range": "35-45"
            },
            financial_analysis={
                "debt_to_income_ratio": 0.18,
                "income_stability": "HIGH",
                "savings_rate": "GOOD"
            },
            decision_reasoning="Applicant meets all approval criteria with excellent credit history and stable employment.",
            case_reference="REF-20240615-001",
            conditions={
                "interest_rate": "4.5%",
                "max_tenure": "60 months",
                "insurance_required": True
            },
            compliance_status="COMPLIANT"
        )
        print(f"✓ Approval Decision Created")
        print(f"  Case ID: {decision1.case_id}")
        print(f"  Decision: {decision1.decision_category}")
        print(f"  Risk Level: {decision1.risk_level}\n")

        # Sample Application 2 - To be Rejected
        app2_id = str(uuid.uuid4())
        app2 = LoanApplication(
            id=app2_id,
            applicant_name="Jane Doe",
            age=28,
            monthly_income=2500,
            employment_type="Contract",
            years_employed=1.5,
            credit_score=580,
            total_liabilities=25000,
            loan_amount=40000,
            loan_tenure_months=48,
            location="Los Angeles, CA",
            submission_timestamp=datetime.utcnow(),
            status="submitted"
        )
        db.add(app2)
        db.commit()

        # Create REJECTED decision
        decision2 = add_decision_with_summary(
            db,
            application_id=app2_id,
            decision_type="REJECTED",
            confidence_score=0.15,
            profile_analysis={
                "employment_stability": "LOW",
                "credit_history": "POOR",
                "age_range": "25-35"
            },
            financial_analysis={
                "debt_to_income_ratio": 0.95,
                "income_stability": "LOW",
                "savings_rate": "INSUFFICIENT"
            },
            decision_reasoning="Application does not meet lending criteria.",
            case_reference="REF-20240615-002",
            rejection_reasons=[
                "Credit score below minimum threshold (580 < 650)",
                "Debt-to-income ratio exceeds 0.50 threshold (0.95)",
                "Employment history too short (1.5 years < 2 years required)",
                "Insufficient savings relative to loan amount"
            ],
            compliance_status="COMPLIANT"
        )
        print(f"✓ Rejection Decision Created")
        print(f"  Case ID: {decision2.case_id}")
        print(f"  Decision: {decision2.decision_category}")
        print(f"  Risk Level: {decision2.risk_level}\n")

        # Sample Application 3 - Under Review
        app3_id = str(uuid.uuid4())
        app3 = LoanApplication(
            id=app3_id,
            applicant_name="Michael Johnson",
            age=45,
            monthly_income=5000,
            employment_type="Self-employed",
            years_employed=5,
            credit_score=680,
            total_liabilities=18000,
            loan_amount=60000,
            loan_tenure_months=72,
            location="Chicago, IL",
            submission_timestamp=datetime.utcnow(),
            status="submitted"
        )
        db.add(app3)
        db.commit()

        # Create UNDER_REVIEW decision
        decision3 = add_decision_with_summary(
            db,
            application_id=app3_id,
            decision_type="UNDER_REVIEW",
            confidence_score=0.0,
            profile_analysis={
                "employment_stability": "MEDIUM",
                "credit_history": "FAIR",
                "business_type": "SELF_EMPLOYED"
            },
            financial_analysis={
                "debt_to_income_ratio": 0.42,
                "income_stability": "VARIABLE",
                "business_revenue": "REQUIRES_VERIFICATION"
            },
            decision_reasoning="Self-employed applicant requires additional documentation for income verification.",
            case_reference="REF-20240615-003",
            required_docs=[
                "Last 2 years of business tax returns",
                "Bank statements for last 6 months",
                "Business license and registration documents",
                "Profit & loss statement for current year"
            ],
            compliance_status="PENDING"
        )
        print(f"✓ Under Review Decision Created")
        print(f"  Case ID: {decision3.case_id}")
        print(f"  Decision: {decision3.decision_category}")
        print(f"  Risk Level: {decision3.risk_level}\n")

        print("=" * 60)
        print("Sample Decision Records Created Successfully!")
        print("=" * 60)

        # Display summaries
        print("\n📋 DECISION SUMMARIES:\n")
        print("1. APPROVAL SUMMARY:")
        print("-" * 60)
        print(decision1.decision_summary)
        print("\n2. REJECTION SUMMARY:")
        print("-" * 60)
        print(decision2.decision_summary)
        print("\n3. UNDER REVIEW SUMMARY:")
        print("-" * 60)
        print(decision3.decision_summary)

    finally:
        db.close()


if __name__ == "__main__":
    create_sample_decisions()
