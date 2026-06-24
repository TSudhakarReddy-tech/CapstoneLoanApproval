# Decision Management System - Enhanced Database Schema

## Overview

The Loan Approval System now includes enhanced decision management with automated case ID generation and detailed decision summaries. This system categorizes decisions into three states: **APPROVED**, **REJECTED**, and **UNDER_REVIEW**, each with comprehensive documentation.

---

## Database Schema Updates

### New Fields in `LoanDecisionRecord`

| Field | Type | Description |
|-------|------|-------------|
| `case_id` | String (Unique) | Formatted case ID (e.g., CASE-APP-20240615-A1B2C3) |
| `decision_category` | String | Decision category: APPROVED, REJECTED, or UNDER_REVIEW |
| `decision_summary` | Text | Detailed decision summary for the applicant |
| `rejection_reason` | Text | Detailed reason if decision is REJECTED |
| `approval_conditions` | JSON | Conditions applied if decision is APPROVED |
| `review_notes` | Text | Notes for UNDER_REVIEW decisions |
| `risk_level` | String | Risk assessment: LOW, MEDIUM, HIGH, or CRITICAL |

---

## Case ID Format

### Naming Convention

`CASE-{TYPE}-{YYYYMMDD}-{HASH}`

**Type Codes:**
- `APP` - Approved
- `REJ` - Rejected
- `REV` - Under Review
- `GEN` - Generic/Other

**Example Case IDs:**
- `CASE-APP-20240615-A1B2C3` - Approval decision from June 15, 2024
- `CASE-REJ-20240615-D4E5F6` - Rejection decision from June 15, 2024
- `CASE-REV-20240615-G7H8I9` - Under review decision from June 15, 2024

---

## Decision Summaries

### 1. Approval Summary

Includes:
- Applicant name and approval date
- Decision confidence score
- Loan amount and monthly income analysis
- Debt-to-income ratio calculation
- Approval conditions (if any)
- Validity period

**Example:**
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

Approval Conditions:
1. Interest Rate: 4.5%
2. Max Tenure: 60 months
3. Insurance Required: True

This approval is valid for 30 days from the decision date.
```

### 2. Rejection Summary

Includes:
- Applicant name and rejection date
- Confidence score
- Numbered list of rejection reasons
- Appeal process information
- Contact information for support

**Example:**
```
LOAN APPLICATION DECISION - REJECTED

Applicant: Jane Doe
Decision: REJECTED
Decision Date: June 15, 2024
Confidence Score: 15.00%

Rejection Reasons:
1. Credit score below minimum threshold (580 < 650)
2. Debt-to-income ratio exceeds 0.50 threshold (0.95)
3. Employment history too short (1.5 years < 2 years required)
4. Insufficient savings relative to loan amount

Appeal Process:
If you believe this decision is incorrect, you may appeal within 30 days by:
1. Submitting additional documentation
2. Contacting our loan review team at support@loanapproval.com
3. Requesting a manual review by our underwriting team
```

### 3. Under Review Summary

Includes:
- Applicant name and review start date
- Review reason
- Required documentation list
- Expected completion timeline
- Contact information

**Example:**
```
LOAN APPLICATION DECISION - UNDER REVIEW

Applicant: Michael Johnson
Status: UNDER REVIEW
Review Started: June 15, 2024

Review Reason:
Self-employed applicant requires additional documentation for income verification.

Required Documentation:
- Last 2 years of business tax returns
- Bank statements for last 6 months
- Business license and registration documents
- Profit & loss statement for current year

Please submit the above documents within 5 business days to expedite the review process.

Expected Review Completion: 5-7 business days
You will be notified via email once the review is complete.
```

---

## Using the Decision Management System

### 1. Case ID Generator

```python
from app.database import CaseIDGenerator

# Generate approval case ID
case_id = CaseIDGenerator.generate_case_id("APPROVED", "app_123")
# Output: CASE-APP-20240615-A1B2C3

# Generate rejection case ID
case_id = CaseIDGenerator.generate_case_id("REJECTED", "app_456")
# Output: CASE-REJ-20240615-D4E5F6

# Generate under-review case ID
case_id = CaseIDGenerator.generate_case_id("UNDER_REVIEW", "app_789")
# Output: CASE-REV-20240615-G7H8I9
```

### 2. Decision Summary Generator

```python
from app.database import DecisionSummaryGenerator

# Generate approval summary
summary = DecisionSummaryGenerator.generate_approval_summary(
    applicant_name="John Smith",
    loan_amount=50000,
    monthly_income=6500,
    confidence_score=0.92,
    conditions={
        "interest_rate": "4.5%",
        "max_tenure": "60 months",
        "insurance_required": True
    }
)

# Generate rejection summary
summary = DecisionSummaryGenerator.generate_rejection_summary(
    applicant_name="Jane Doe",
    rejection_reasons=[
        "Credit score below minimum",
        "High debt-to-income ratio"
    ],
    confidence_score=0.15
)

# Generate under-review summary
summary = DecisionSummaryGenerator.generate_review_summary(
    applicant_name="Michael Johnson",
    review_reason="Self-employed applicant requires income verification",
    required_docs=[
        "Tax returns (2 years)",
        "Bank statements (6 months)"
    ]
)
```

### 3. Decision Record Builder

```python
from app.database import DecisionRecordBuilder

builder = DecisionRecordBuilder("app_123", "John Smith")

# For approval
builder.set_approval(
    confidence_score=0.92,
    loan_amount=50000,
    monthly_income=6500,
    conditions={"interest_rate": "4.5%"}
)

# For rejection
builder.set_rejection(
    confidence_score=0.15,
    rejection_reasons=["Credit score below minimum", "High DTI"]
)

# For under-review
builder.set_under_review(
    review_reason="Income verification needed",
    required_docs=["Tax returns", "Bank statements"]
)

decision_data = builder.build()
```

### 4. Creating Decision Records

```python
from app.database import add_decision_with_summary, get_db_session

db = get_db_session()

try:
    decision = add_decision_with_summary(
        db=db,
        application_id="app_123",
        decision_type="APPROVED",  # or "REJECTED", "UNDER_REVIEW"
        confidence_score=0.92,
        profile_analysis={...},
        financial_analysis={...},
        decision_reasoning="Applicant meets all criteria",
        case_reference="REF-20240615-001",
        conditions={...},
        compliance_status="COMPLIANT"
    )
    
    print(f"Decision created with Case ID: {decision.case_id}")
    print(f"Category: {decision.decision_category}")
    print(f"Risk Level: {decision.risk_level}")

finally:
    db.close()
```

---

## Risk Level Calculation

Risk levels are automatically calculated based on confidence score:

| Confidence Score | Risk Level |
|------------------|-----------|
| ≥ 90% | LOW |
| 75% - 89% | MEDIUM |
| 60% - 74% | HIGH |
| < 60% | CRITICAL |

---

## Migration Guide

### For Existing Databases

```python
from app.database import migrate_existing_decisions, get_db_session

db = get_db_session()

try:
    stats = migrate_existing_decisions(db)
    print(f"Total Records: {stats['total_records']}")
    print(f"Updated: {stats['updated_records']}")
    if stats['errors']:
        for error in stats['errors']:
            print(f"Error: {error}")

finally:
    db.close()
```

---

## Sample Usage

Run the sample script to create test decision records:

```bash
python scripts/sample_decisions.py
```

This creates three sample applications with decisions:
1. **Approved** - Full approval with conditions
2. **Rejected** - Rejection with detailed reasons
3. **Under Review** - Pending additional documentation

---

## API Integration

### Endpoint Response Format

```json
{
  "id": "dec_123456",
  "application_id": "app_123",
  "decision": "APPROVED",
  "decision_category": "APPROVED",
  "case_id": "CASE-APP-20240615-A1B2C3",
  "confidence_score": 0.92,
  "decision_summary": "...",
  "approval_conditions": {
    "interest_rate": "4.5%",
    "max_tenure": "60 months"
  },
  "risk_level": "LOW",
  "created_at": "2024-06-15T10:30:00Z"
}
```

---

## Querying Decision Records

```python
from app.database import get_db_session, LoanDecisionRecord

db = get_db_session()

# Get approval decisions
approvals = db.query(LoanDecisionRecord).filter(
    LoanDecisionRecord.decision_category == "APPROVED"
).all()

# Get high-risk rejections
rejections = db.query(LoanDecisionRecord).filter(
    LoanDecisionRecord.decision_category == "REJECTED",
    LoanDecisionRecord.risk_level == "CRITICAL"
).all()

# Get by case ID
decision = db.query(LoanDecisionRecord).filter(
    LoanDecisionRecord.case_id == "CASE-APP-20240615-A1B2C3"
).first()

db.close()
```

---

## Best Practices

1. **Always generate case IDs programmatically** - Use `CaseIDGenerator` for consistency
2. **Use decision summaries in notifications** - Send formatted summaries to applicants
3. **Track risk levels** - Monitor CRITICAL and HIGH-risk decisions
4. **Maintain audit trail** - Record who created/modified decisions
5. **Archive old decisions** - Implement retention policies for compliance
6. **Validate rejection reasons** - Ensure all reasons are clear and actionable

---

## Troubleshooting

### Duplicate Case ID Error

**Problem:** `IntegrityError: UNIQUE constraint failed`

**Solution:** Case IDs are unique. Ensure you're not creating duplicate decisions for the same application.

### Missing Application Error

**Problem:** `ValueError: Application not found`

**Solution:** Verify the application exists before creating a decision record.

### Migration Fails

**Problem:** Migration script encounters errors

**Solution:** Check database connectivity and existing data integrity before running migration.

---

## References

- [Database Models](../app/database/models.py)
- [Case Manager](../app/database/case_manager.py)
- [Migration Utilities](../app/database/migrations.py)
- [Sample Script](../scripts/sample_decisions.py)

