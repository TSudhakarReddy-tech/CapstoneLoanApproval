"""API routes for loan applications."""

from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import LoanApplicationRequest, LoanDecisionResponse, ApplicationStatus
from app.database import LoanApplication, LoanDecisionRecord, get_db
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

        # Save decision to database
        decision_id = str(uuid4())
        db_decision = LoanDecisionRecord(
            id=decision_id,
            application_id=application_id,
            decision=final_state.loan_decision.decision if final_state.loan_decision else "Review",
            confidence_score=final_state.loan_decision.confidence_score if final_state.loan_decision else 0,
            profile_analysis=final_state.profile_analysis.model_dump() if final_state.profile_analysis else {},
            financial_analysis=final_state.financial_analysis.model_dump() if final_state.financial_analysis else {},
            decision_reasoning=final_state.loan_decision.reasoning if final_state.loan_decision else "Pending",
            recommended_conditions=final_state.loan_decision.recommended_conditions if final_state.loan_decision else [],
            compliance_status=final_state.compliance_result.compliance_status if final_state.compliance_result else "Pending",
            case_reference=final_state.compliance_result.case_reference if final_state.compliance_result else f"LOAN-{application_id[:8].upper()}",
        )
        db.add(db_decision)

        # Update application status
        db_app.status = "completed"
        db_app.updated_at = datetime.utcnow()
        db.commit()

        return ApplicationStatus(
            application_id=application_id,
            status="completed",
            created_at=db_app.created_at,
            updated_at=db_app.updated_at,
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

    db_app = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()

    if not db_app:
        raise HTTPException(status_code=404, detail="Application not found")

    decision = None
    db_decision = db.query(LoanDecisionRecord).filter(
        LoanDecisionRecord.application_id == application_id
    ).first()

    if db_decision:
        # This would need full reconstruction; simplified for now
        decision = None

    return ApplicationStatus(
        application_id=application_id,
        status=db_app.status,
        created_at=db_app.created_at,
        updated_at=db_app.updated_at,
        decision=decision,
    )


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
