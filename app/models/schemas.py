"""Pydantic schemas for loan application and decision."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class LoanApplicationRequest(BaseModel):
    """Input schema for loan application submission."""

    applicant_name: str = Field(..., description="Full name of applicant")
    age: int = Field(..., ge=18, le=80, description="Applicant age")
    monthly_income: float = Field(..., gt=0, description="Monthly income in dollars")
    employment_type: str = Field(..., description="Type of employment (salaried/self-employed/business)")
    years_employed: float = Field(..., ge=0, description="Years at current employment")

    credit_score: int = Field(..., ge=300, le=850, description="Credit score")
    total_liabilities: float = Field(default=0, ge=0, description="Total outstanding debts")

    loan_amount: float = Field(..., gt=0, description="Requested loan amount in dollars")
    loan_tenure_months: int = Field(..., gt=0, description="Requested tenure in months")

    location: str = Field(..., description="Geographic location")
    submission_timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)


class ApplicationProfileAnalysis(BaseModel):
    """Output from Application Profile Agent."""

    income_stability_score: float = Field(..., ge=0, le=100)
    employment_assessment: str
    age_category: str
    profile_risk_level: str  # Low, Medium, High


class FinancialRiskAnalysis(BaseModel):
    """Output from Financial Risk Analysis Agent."""

    debt_to_income_ratio: float
    credit_assessment: str
    liability_assessment: str
    financial_risk_score: float = Field(..., ge=0, le=100)
    risk_level: str  # Low, Medium, High


class LoanDecision(BaseModel):
    """Output from Loan Decision Agent."""

    decision: str = Field(..., description="Approve, Reject, or Review")
    confidence_score: float = Field(..., ge=0, le=100)
    reasoning: str
    recommended_conditions: Optional[list[str]] = None


class ComplianceCheckResult(BaseModel):
    """Output from Compliance & Action Agent."""

    compliance_status: str  # Approved, Flagged, Rejected
    notification_sent: bool
    case_reference: str
    next_steps: list[str]


class LoanDecisionResponse(BaseModel):
    """Complete decision response with audit trail."""

    application_id: str
    decision: str  # Approve, Reject, Review
    confidence_score: float

    profile_analysis: ApplicationProfileAnalysis
    financial_analysis: FinancialRiskAnalysis
    decision_reasoning: str
    recommended_conditions: Optional[list[str]] = None
    compliance_status: str

    created_at: datetime = Field(default_factory=datetime.utcnow)
    case_reference: str


class ApplicationStatus(BaseModel):
    """Application status response."""

    application_id: str
    status: str  # Submitted, Processing, Completed, Rejected
    decision: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
