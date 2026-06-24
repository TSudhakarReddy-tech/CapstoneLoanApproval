"""Database migration utilities for enhanced decision records."""

from datetime import datetime
from sqlalchemy.orm import Session
from app.database.models import LoanDecisionRecord, LoanApplication
from app.database.case_manager import CaseIDGenerator, DecisionRecordBuilder


def migrate_existing_decisions(db: Session) -> dict:
    """
    Migrate existing decision records with new fields.

    Returns:
        Dictionary with migration statistics
    """
    stats = {
        "total_records": 0,
        "updated_records": 0,
        "errors": []
    }

    try:
        decisions = db.query(LoanDecisionRecord).all()
        stats["total_records"] = len(decisions)

        for decision in decisions:
            try:
                # Skip if already migrated
                if decision.case_id and decision.decision_category:
                    stats["updated_records"] += 1
                    continue

                # Get the original application
                app = db.query(LoanApplication).filter(
                    LoanApplication.id == decision.application_id
                ).first()

                if not app:
                    stats["errors"].append(f"Application not found for decision {decision.id}")
                    continue

                # Generate case ID based on existing decision
                decision_type = decision.decision.upper()
                if decision_type == "APPROVED":
                    case_id = CaseIDGenerator.generate_case_id("APPROVED", decision.application_id)
                    category = "APPROVED"
                elif decision_type == "REJECTED":
                    case_id = CaseIDGenerator.generate_case_id("REJECTED", decision.application_id)
                    category = "REJECTED"
                else:
                    case_id = CaseIDGenerator.generate_case_id("UNDER_REVIEW", decision.application_id)
                    category = "UNDER_REVIEW"

                # Update decision record
                decision.case_id = case_id
                decision.decision_category = category
                decision.decision_summary = decision.decision_reasoning or ""
                decision.risk_level = DecisionRecordBuilder._calculate_risk_level(decision.confidence_score)

                if category == "REJECTED":
                    decision.rejection_reason = decision.decision_reasoning

                db.add(decision)
                stats["updated_records"] += 1

            except Exception as e:
                stats["errors"].append(f"Error migrating decision {decision.id}: {str(e)}")

        db.commit()

    except Exception as e:
        db.rollback()
        stats["errors"].append(f"Migration failed: {str(e)}")

    return stats


def add_decision_with_summary(
    db: Session,
    application_id: str,
    decision_type: str,  # 'APPROVED', 'REJECTED', 'UNDER_REVIEW'
    confidence_score: float,
    profile_analysis: dict,
    financial_analysis: dict,
    decision_reasoning: str,
    case_reference: str,
    **kwargs
) -> LoanDecisionRecord:
    """
    Add a new decision record with enhanced fields.

    Args:
        db: Database session
        application_id: Application ID
        decision_type: Type of decision (APPROVED, REJECTED, UNDER_REVIEW)
        confidence_score: Confidence score of the decision
        profile_analysis: Profile analysis data
        financial_analysis: Financial analysis data
        decision_reasoning: Detailed reasoning
        case_reference: Case reference
        **kwargs: Additional fields like rejection_reason, conditions, etc.

    Returns:
        Created LoanDecisionRecord
    """
    app = db.query(LoanApplication).filter(
        LoanApplication.id == application_id
    ).first()

    if not app:
        raise ValueError(f"Application {application_id} not found")

    # Generate case ID
    case_id = CaseIDGenerator.generate_case_id(decision_type, application_id)

    # Build decision data
    builder = DecisionRecordBuilder(application_id, app.applicant_name)

    if decision_type == "APPROVED":
        builder.set_approval(
            confidence_score=confidence_score,
            loan_amount=app.loan_amount,
            monthly_income=app.monthly_income,
            conditions=kwargs.get("conditions"),
            compliance_status=kwargs.get("compliance_status", "COMPLIANT")
        )
    elif decision_type == "REJECTED":
        builder.set_rejection(
            confidence_score=confidence_score,
            rejection_reasons=kwargs.get("rejection_reasons", [decision_reasoning]),
            compliance_status=kwargs.get("compliance_status", "COMPLIANT")
        )
    else:  # UNDER_REVIEW
        builder.set_under_review(
            review_reason=decision_reasoning,
            required_docs=kwargs.get("required_docs"),
            compliance_status=kwargs.get("compliance_status", "PENDING")
        )

    decision_data = builder.build()

    # Create the decision record
    record = LoanDecisionRecord(
        id=str(__import__('uuid').uuid4()),
        application_id=application_id,
        decision=decision_data["decision"],
        confidence_score=confidence_score,
        profile_analysis=profile_analysis,
        financial_analysis=financial_analysis,
        decision_reasoning=decision_reasoning,
        case_reference=case_reference,
        case_id=decision_data["case_id"],
        decision_category=decision_data["decision_category"],
        decision_summary=decision_data["decision_summary"],
        rejection_reason=decision_data.get("rejection_reason"),
        approval_conditions=decision_data.get("approval_conditions"),
        review_notes=decision_data.get("review_notes"),
        risk_level=decision_data.get("risk_level"),
        recommended_conditions=kwargs.get("recommended_conditions"),
        compliance_status=kwargs.get("compliance_status", "COMPLIANT")
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


__all__ = ["migrate_existing_decisions", "add_decision_with_summary"]
