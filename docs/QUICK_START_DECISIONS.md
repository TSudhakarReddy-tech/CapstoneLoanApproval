# Quick Start - Decision Management System

## 🚀 30-Second Overview

Your loan approval system now automatically generates:
- **Case IDs** - Formatted tracking numbers (e.g., `CASE-APP-20240615-A1B2C3`)
- **Decision Summaries** - Professional summaries for applicants
- **Risk Levels** - Automatic risk assessment

---

## 📋 Three Decision Types

### 1️⃣ APPROVED ✓
**When:** Applicant meets all criteria
```
Case ID: CASE-APP-20240615-A1B2C3
Risk: LOW
Includes: Interest rate, tenure, conditions
```

### 2️⃣ REJECTED ✗
**When:** Applicant fails lending criteria
```
Case ID: CASE-REJ-20240615-D4E5F6
Risk: HIGH
Includes: Reasons, appeal process
```

### 3️⃣ UNDER REVIEW 🔄
**When:** Need more information
```
Case ID: CASE-REV-20240615-G7H8I9
Risk: MEDIUM
Includes: Required docs, timeline
```

---

## ⚡ Quickest Way to Create a Decision

```python
from app.database import add_decision_with_summary, get_db_session

db = get_db_session()

# Create APPROVED decision
decision = add_decision_with_summary(
    db=db,
    application_id="app_123",
    decision_type="APPROVED",  # or "REJECTED", "UNDER_REVIEW"
    confidence_score=0.92,
    profile_analysis={"employment": "STABLE"},
    financial_analysis={"dti": 0.18},
    decision_reasoning="Meets all criteria",
    case_reference="REF-001"
)

print(f"✓ Decision: {decision.decision_category}")
print(f"✓ Case ID: {decision.case_id}")
print(f"✓ Risk Level: {decision.risk_level}")

db.close()
```

---

## 📊 Example Outputs

### Approval Decision
```
LOAN APPLICATION DECISION - APPROVED

Applicant: John Smith
Decision: APPROVED
Decision Date: June 15, 2024
Confidence Score: 92.00%

Loan Details:
- Requested Amount: $50,000.00
- Monthly Income: $6,500.00
- Debt-to-Income Ratio: 10.26%

This approval is valid for 30 days from the decision date.
```

### Rejection Decision
```
LOAN APPLICATION DECISION - REJECTED

Applicant: Jane Doe
Decision: REJECTED
Confidence Score: 15.00%

Rejection Reasons:
1. Credit score below minimum threshold (580 < 650)
2. Debt-to-income ratio exceeds 0.50 threshold (0.95)
3. Employment history too short (1.5 years < 2 years)
```

### Under Review Decision
```
LOAN APPLICATION DECISION - UNDER REVIEW

Applicant: Michael Johnson
Status: UNDER REVIEW
Review Started: June 15, 2024

Required Documentation:
- Last 2 years of business tax returns
- Bank statements for last 6 months

Expected Review Completion: 5-7 business days
```

---

## 🎯 Step-by-Step: Creating Each Decision Type

### APPROVED

```python
decision = add_decision_with_summary(
    db=db,
    application_id="app_123",
    decision_type="APPROVED",
    confidence_score=0.92,
    profile_analysis={
        "employment_stability": "HIGH",
        "credit_history": "EXCELLENT"
    },
    financial_analysis={
        "debt_to_income_ratio": 0.18,
        "income_stability": "HIGH"
    },
    decision_reasoning="Applicant meets all approval criteria",
    case_reference="REF-20240615-001",
    conditions={
        "interest_rate": "4.5%",
        "max_tenure": "60 months",
        "insurance_required": True
    }
)
```

### REJECTED

```python
decision = add_decision_with_summary(
    db=db,
    application_id="app_456",
    decision_type="REJECTED",
    confidence_score=0.15,
    profile_analysis={
        "employment_stability": "LOW",
        "credit_history": "POOR"
    },
    financial_analysis={
        "debt_to_income_ratio": 0.95,
        "income_stability": "LOW"
    },
    decision_reasoning="Application does not meet lending criteria",
    case_reference="REF-20240615-002",
    rejection_reasons=[
        "Credit score below minimum (580 < 650)",
        "Debt-to-income ratio exceeds limit (0.95 > 0.50)",
        "Employment history too short (1.5 < 2 years)"
    ]
)
```

### UNDER REVIEW

```python
decision = add_decision_with_summary(
    db=db,
    application_id="app_789",
    decision_type="UNDER_REVIEW",
    confidence_score=0.0,
    profile_analysis={
        "employment_type": "SELF_EMPLOYED"
    },
    financial_analysis={
        "income_verification": "PENDING"
    },
    decision_reasoning="Self-employed applicant requires income verification",
    case_reference="REF-20240615-003",
    required_docs=[
        "Last 2 years of business tax returns",
        "Bank statements for last 6 months",
        "Business license and registration"
    ]
)
```

---

## 🔍 Querying Decisions

```python
from app.database import get_db_session, LoanDecisionRecord

db = get_db_session()

# Get by case ID
decision = db.query(LoanDecisionRecord).filter(
    LoanDecisionRecord.case_id == "CASE-APP-20240615-A1B2C3"
).first()

# Get all approvals
approvals = db.query(LoanDecisionRecord).filter(
    LoanDecisionRecord.decision_category == "APPROVED"
).all()

# Get high-risk decisions
high_risk = db.query(LoanDecisionRecord).filter(
    LoanDecisionRecord.risk_level.in_(["HIGH", "CRITICAL"])
).all()

# Get recent decisions
from datetime import datetime, timedelta
recent = db.query(LoanDecisionRecord).filter(
    LoanDecisionRecord.created_at >= datetime.utcnow() - timedelta(days=7)
).all()

db.close()
```

---

## 📈 Risk Level Guide

```
Confidence ≥ 90%  → Risk: LOW       (Safe approval)
Confidence 75-89% → Risk: MEDIUM    (Moderate approval)
Confidence 60-74% → Risk: HIGH      (Risky approval/rejection)
Confidence < 60%  → Risk: CRITICAL  (Very risky)
```

---

## 🧪 Test Your Setup

```bash
# Run sample script
python scripts/sample_decisions.py

# Run tests
pytest tests/test_case_manager.py -v
```

---

## 📚 Full Documentation

For comprehensive details, see:
- [Full Decision Management Guide](DECISION_MANAGEMENT.md)
- [Database Models](../app/database/models.py)
- [Case Manager Code](../app/database/case_manager.py)
- [Migration Utilities](../app/database/migrations.py)

---

## 🚨 Common Patterns

### Pattern 1: Create Decision and Send Notification
```python
decision = add_decision_with_summary(...)

notification = {
    "recipient": app.applicant_name,
    "case_id": decision.case_id,
    "subject": f"Loan Application Decision - {decision.case_id}",
    "body": decision.decision_summary
}
# Send notification...
```

### Pattern 2: Track Decision in Audit Trail
```python
decision = add_decision_with_summary(...)

audit_entry = {
    "application_id": decision.application_id,
    "case_id": decision.case_id,
    "action": f"Decision recorded: {decision.decision_category}",
    "risk_level": decision.risk_level,
    "timestamp": decision.created_at
}
# Log audit entry...
```

### Pattern 3: Export Decision for Reporting
```python
decision = add_decision_with_summary(...)

report_data = {
    "case_id": decision.case_id,
    "application_id": decision.application_id,
    "decision": decision.decision_category,
    "confidence": f"{decision.confidence_score * 100:.1f}%",
    "risk": decision.risk_level,
    "created": decision.created_at.isoformat()
}
# Export to report...
```

---

## ✅ Checklist for Integration

- [ ] Read through this quick start
- [ ] Review [Full Documentation](DECISION_MANAGEMENT.md)
- [ ] Run sample script: `python scripts/sample_decisions.py`
- [ ] Run tests: `pytest tests/test_case_manager.py -v`
- [ ] Update your API endpoints to use new fields
- [ ] Update notification templates with decision summaries
- [ ] Test end-to-end with a sample application
- [ ] Migrate existing decisions (if applicable)
- [ ] Monitor CRITICAL risk decisions

---

## 💡 Pro Tips

1. **Always use case IDs in communication** - They're unique and trackable
2. **Monitor CRITICAL risk decisions** - They need extra attention
3. **Include decision summaries in notifications** - They're professional and clear
4. **Track appeal requests** - They should reference case IDs
5. **Archive old decisions** - Maintain compliance with retention policies

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Case ID already exists | Case IDs are unique per creation; error is expected if duplicate |
| Application not found | Verify application_id exists in LoanApplication table |
| Summary not generating | Check required parameters are provided |
| Risk level seems wrong | Verify confidence_score; it drives the risk calculation |

---

**Questions?** Check the [Full Documentation](DECISION_MANAGEMENT.md) or review the test cases.

