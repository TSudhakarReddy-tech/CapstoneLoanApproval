"""SQLAlchemy ORM models for persistence."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

Base = declarative_base()


class LoanApplication(Base):
    """Stores submitted loan applications."""

    __tablename__ = "loan_applications"

    id = Column(String, primary_key=True)
    applicant_name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)
    monthly_income = Column(Float, nullable=False)
    employment_type = Column(String(50), nullable=False)
    years_employed = Column(Float, nullable=False)

    credit_score = Column(Integer, nullable=False)
    total_liabilities = Column(Float, nullable=False)

    loan_amount = Column(Float, nullable=False)
    loan_tenure_months = Column(Integer, nullable=False)

    location = Column(String(255), nullable=False)
    submission_timestamp = Column(DateTime, nullable=False)

    status = Column(String(50), default="submitted")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LoanDecisionRecord(Base):
    """Stores loan decisions and analysis results."""

    __tablename__ = "loan_decisions"

    id = Column(String, primary_key=True)
    application_id = Column(String, nullable=False, index=True)

    decision = Column(String(50), nullable=False)
    confidence_score = Column(Float, nullable=False)

    profile_analysis = Column(JSON, nullable=False)
    financial_analysis = Column(JSON, nullable=False)
    decision_reasoning = Column(Text, nullable=False)
    recommended_conditions = Column(JSON)
    compliance_status = Column(String(50), nullable=False)
    case_reference = Column(String(100), nullable=False, unique=True)

    # Enhanced decision details
    decision_summary = Column(Text, nullable=True)
    decision_category = Column(String(20), nullable=True)  # APPROVED, REJECTED, UNDER_REVIEW
    rejection_reason = Column(Text, nullable=True)  # Detailed rejection reason if rejected
    approval_conditions = Column(JSON, nullable=True)  # Conditions for approval
    case_id = Column(String(50), nullable=False, unique=True, index=True)  # Formatted case ID
    review_notes = Column(Text, nullable=True)  # Notes for under-review cases
    risk_level = Column(String(20), nullable=True)  # LOW, MEDIUM, HIGH, CRITICAL

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditTrail(Base):
    """Stores audit trail for all decisions."""

    __tablename__ = "audit_trails"

    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    agent_name = Column(String(100), nullable=False)
    action = Column(String(255), nullable=False)
    details = Column(JSON)


class NotificationLog(Base):
    """Logs notifications sent to applicants."""

    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(String, nullable=False, index=True)
    case_reference = Column(String(100), nullable=False)

    notification_type = Column(String(50), nullable=False)
    recipient = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    sent = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)


__all__ = ["Base", "LoanApplication", "LoanDecisionRecord", "AuditTrail", "NotificationLog"]
