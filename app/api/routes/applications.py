"""API routes for loan applications."""

from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import LoanApplicationRequest, LoanDecisionResponse, ApplicationStatus
from app.database import LoanApplication, LoanDecisionRecord, get_db, add_decision_with_summary
from app.orchestration import run_loan_approval_workflow
from app.models.agent_state import LoanApprovalState

router = APIRouter()


@router.post("/applications", response_model=ApplicationStatus)
async def submit_application(
    app_request: LoanApplicationRequest,
    db: Session = Depends(get_db),
):
    """Submit a new loan application and process it."""

    application_id = str(uuid4())

    # Save application to database
    db_app = LoanApplication(
        id=application_id,
        applicant_name=app_request.applicant_name,
        age=app_request.age,
        monthly_income=app_request.monthly_income,
        employment_type=app_request.employment_type,
        years_employed=app_request.years_employed,
        credit_score=app_request.credit_score,
        total_liabilities=app_request.total_liabilities,
        loan_amount=app_request.loan_amount,
        loan_tenure_months=app_request.loan_tenure_months,
        location=app_request.location,
        submission_timestamp=app_request.submission_timestamp or datetime.utcnow(),
        status="processing",
    )
    db.add(db_app)
    db.commit()

    # Create initial state
    state = LoanApprovalState(application=app_request, application_id=application_id)

    # Run workflow
    try:
        final_state = await run_loan_approval_workflow(state)

        # Extract decision details from workflow
        decision_type_raw = final_state.loan_decision.decision if final_state.loan_decision else "UNDER_REVIEW"
        # Normalize decision type (handle both "Approved" and "APPROVED")
        decision_type = decision_type_raw.upper()
        confidence = final_state.loan_decision.confidence_score if final_state.loan_decision else 0.0
        reasoning = final_state.loan_decision.reasoning if final_state.loan_decision else "Application under review"

        # Generate case ID and determine risk level
        decision_type_code = decision_type[:3] if decision_type else "GEN"
        case_id = f"CASE-{decision_type_code}-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid4())[:6].upper()}"

        # Calculate risk level based on decision type AND confidence
        if decision_type == "APPROVED":
            # Approved: Low risk baseline
            if confidence >= 0.9:
                risk_level = "LOW"
            elif confidence >= 0.75:
                risk_level = "LOW"
            else:
                risk_level = "MEDIUM"
        elif decision_type == "REJECTED":
            # Rejected: Always high risk (application has issues)
            risk_level = "HIGH"
        else:  # UNDER_REVIEW
            # Under review: Medium-High risk (pending more info)
            if confidence >= 0.75:
                risk_level = "MEDIUM"
            elif confidence >= 0.6:
                risk_level = "HIGH"
            else:
                risk_level = "CRITICAL"

        # Generate decision summary based on type
        if decision_type == "APPROVED":
            decision_summary = f"""LOAN APPLICATION DECISION - APPROVED

Applicant: {app_request.applicant_name}
Decision: APPROVED
Decision Date: {datetime.utcnow().strftime("%B %d, %Y")}
Confidence Score: {confidence*100:.1f}%

Loan Details:
- Requested Amount: ${app_request.loan_amount:,.2f}
- Monthly Income: ${app_request.monthly_income:,.2f}
- Loan Tenure: {app_request.loan_tenure_months} months

Status: Your application has been APPROVED.

Approval Conditions:
- Standard lending terms apply
- Insurance may be required
- Approval valid for 30 days

Next Steps: Contact us to finalize the loan agreement."""
        elif decision_type == "REJECTED":
            decision_summary = f"""LOAN APPLICATION DECISION - REJECTED

Applicant: {app_request.applicant_name}
Decision: REJECTED
Decision Date: {datetime.utcnow().strftime("%B %d, %Y")}
Confidence Score: {confidence*100:.1f}%

Status: Unfortunately, your application has been REJECTED.

Reason: {reasoning}

Rejection Factors:
- Credit profile assessment
- Financial stability review
- Debt-to-income analysis

Appeal Process:
If you believe this decision is incorrect, you may appeal within 30 days by:
1. Submitting additional documentation
2. Contacting our loan review team
3. Requesting a manual review

For assistance: support@loanapproval.com"""
        else:  # UNDER_REVIEW
            decision_summary = f"""LOAN APPLICATION DECISION - UNDER REVIEW

Applicant: {app_request.applicant_name}
Status: UNDER REVIEW
Review Started: {datetime.utcnow().strftime("%B %d, %Y")}

Your application is currently under review.

Review Reason: {reasoning}

Required Documentation:
- Income verification (pay stubs, tax returns)
- Employment confirmation letter
- Bank statements (last 6 months)

Timeline: Review completion expected within 5-7 business days

Next Steps: Please submit the above documents at your earliest convenience to expedite the review process.

You will be notified via email once the review is complete."""

        # Safely extract analysis data
        profile_data = {}
        if final_state.profile_analysis:
            if hasattr(final_state.profile_analysis, 'model_dump'):
                profile_data = final_state.profile_analysis.model_dump()
            elif hasattr(final_state.profile_analysis, '__dict__'):
                profile_data = {k: v for k, v in final_state.profile_analysis.__dict__.items() if not k.startswith('_')}

        financial_data = {}
        if final_state.financial_analysis:
            if hasattr(final_state.financial_analysis, 'model_dump'):
                financial_data = final_state.financial_analysis.model_dump()
            elif hasattr(final_state.financial_analysis, '__dict__'):
                financial_data = {k: v for k, v in final_state.financial_analysis.__dict__.items() if not k.startswith('_')}

        # Save decision to database
        decision_id = str(uuid4())
        db_decision = LoanDecisionRecord(
            id=decision_id,
            application_id=application_id,
            decision=decision_type,
            confidence_score=confidence,
            profile_analysis=profile_data,
            financial_analysis=financial_data,
            decision_reasoning=reasoning,
            recommended_conditions=final_state.loan_decision.recommended_conditions if final_state.loan_decision else [],
            compliance_status=final_state.compliance_result.compliance_status if final_state.compliance_result else "COMPLIANT",
            case_reference=final_state.compliance_result.case_reference if final_state.compliance_result else f"LOAN-{application_id[:8].upper()}",
            # New enhanced fields
            case_id=case_id,
            decision_category=decision_type,
            decision_summary=decision_summary,
            rejection_reason=reasoning if decision_type == "REJECTED" else None,
            approval_conditions={
                "interest_rate": "4.5%",
                "tenure_months": app_request.loan_tenure_months,
                "loan_amount": app_request.loan_amount
            } if decision_type == "APPROVED" else None,
            review_notes=reasoning if decision_type == "UNDER_REVIEW" else None,
            risk_level=risk_level,
        )
        db.add(db_decision)

        # Update application status
        db_app.status = "completed"
        db_app.updated_at = datetime.utcnow()
        db.commit()

        # Build decision response
        decision_response = {
            "decision": decision_type,
            "case_id": case_id,
            "case_reference": final_state.compliance_result.case_reference if final_state.compliance_result else f"LOAN-{application_id[:8].upper()}",
            "confidence_score": confidence,
            "decision_category": decision_type,
            "decision_summary": decision_summary,
            "rejection_reason": reasoning if decision_type == "REJECTED" else None,
            "approval_conditions": {
                "interest_rate": "4.5%",
                "tenure_months": app_request.loan_tenure_months,
                "loan_amount": app_request.loan_amount
            } if decision_type == "APPROVED" else None,
            "review_notes": reasoning if decision_type == "UNDER_REVIEW" else None,
            "risk_level": risk_level,
            "decision_reasoning": reasoning,
            "profile_analysis": profile_data,
            "financial_analysis": financial_data,
            "compliance_status": final_state.compliance_result.compliance_status if final_state.compliance_result else "COMPLIANT",
        }

        return ApplicationStatus(
            application_id=application_id,
            status="completed",
            created_at=db_app.created_at,
            updated_at=db_app.updated_at,
            decision=decision_response,
        )

    except Exception as e:
        db_app.status = "error"
        db_app.updated_at = datetime.utcnow()
        db.commit()
        raise HTTPException(status_code=500, detail=f"Workflow error: {str(e)}")


@router.get("/applications/{application_id}", response_model=ApplicationStatus)
async def get_application_status(
    application_id: str,
    db: Session = Depends(get_db),
):
    """Get the status and decision of a loan application."""

    try:
        db_app = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()

        if not db_app:
            raise HTTPException(status_code=404, detail="Application not found")

        decision = None
        db_decision = db.query(LoanDecisionRecord).filter(
            LoanDecisionRecord.application_id == application_id
        ).first()

        if db_decision:
            # Return complete decision details
            decision = {
                "decision": db_decision.decision,
                "case_id": getattr(db_decision, 'case_id', None),
                "case_reference": db_decision.case_reference,
                "confidence_score": db_decision.confidence_score,
                "decision_category": getattr(db_decision, 'decision_category', db_decision.decision),
                "decision_summary": getattr(db_decision, 'decision_summary', db_decision.decision_reasoning),
                "rejection_reason": getattr(db_decision, 'rejection_reason', None),
                "approval_conditions": getattr(db_decision, 'approval_conditions', db_decision.recommended_conditions),
                "review_notes": getattr(db_decision, 'review_notes', None),
                "risk_level": getattr(db_decision, 'risk_level', None),
                "decision_reasoning": db_decision.decision_reasoning,
                "profile_analysis": db_decision.profile_analysis or {},
                "financial_analysis": db_decision.financial_analysis or {},
                "compliance_status": db_decision.compliance_status,
            }

        return ApplicationStatus(
            application_id=application_id,
            status=db_app.status,
            created_at=db_app.created_at,
            updated_at=db_app.updated_at,
            decision=decision,
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching application {application_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching application: {str(e)}")


@router.get("/applications")
async def list_applications(
    skip: int = 0,
    limit: int = 10,
    status: str = None,
    db: Session = Depends(get_db),
):
    """List all applications with optional filtering."""

    query = db.query(LoanApplication)

    if status:
        query = query.filter(LoanApplication.status == status)

    applications = query.offset(skip).limit(limit).all()

    return {
        "count": len(applications),
        "skip": skip,
        "limit": limit,
        "applications": [
            {
                "id": app.id,
                "applicant_name": app.applicant_name,
                "status": app.status,
                "loan_amount": app.loan_amount,
                "created_at": app.created_at,
            }
            for app in applications
        ],
    }
