"""Database package."""

from app.database.models import (
    Base,
    LoanApplication,
    LoanDecisionRecord,
    AuditTrail,
    NotificationLog,
)
from app.database.db import init_db, get_db_session, close_db_session, get_db, engine
from app.database.case_manager import (
    CaseIDGenerator,
    DecisionSummaryGenerator,
    DecisionRecordBuilder,
)
from app.database.migrations import migrate_existing_decisions, add_decision_with_summary

__all__ = [
    "Base",
    "LoanApplication",
    "LoanDecisionRecord",
    "AuditTrail",
    "NotificationLog",
    "init_db",
    "get_db_session",
    "close_db_session",
    "get_db",
    "engine",
    "CaseIDGenerator",
    "DecisionSummaryGenerator",
    "DecisionRecordBuilder",
    "migrate_existing_decisions",
    "add_decision_with_summary",
]
