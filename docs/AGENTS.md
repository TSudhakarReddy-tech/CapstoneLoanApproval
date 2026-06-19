# Loan Approval Agents

This document describes the four core agents in the loan approval system.

## Agent Architecture

Each agent is a specialized Claude instance that handles a specific aspect of loan evaluation:

```
┌─────────────────┐
│ Application     │
│ Profile Agent   │ → Evaluates income stability & employment
└────────┬────────┘
         │
┌────────▼────────┐
│ Financial Risk  │
│ Analysis Agent  │ → Analyzes credit & debt ratios
└────────┬────────┘
         │
┌────────▼────────┐
│ Loan Decision   │
│ Agent           │ → Makes final Approve/Reject/Review
└────────┬────────┘
         │
┌────────▼────────┐
│ Compliance &    │
│ Action Agent    │ → Compliance checks & notifications
└─────────────────┘
```

## 1. Application Profile Agent

**Responsibility:** Evaluate income stability and employment suitability.

**Inputs:**
- Age, employment type, years employed
- Monthly income
- Requested loan amount and tenure

**Outputs:**
```json
{
  "income_stability_score": 75.0,
  "employment_assessment": "Stable salaried employment with 5 years tenure",
  "age_category": "Mid-Career",
  "profile_risk_level": "Low"
}
```

**Decision Logic:**
- Higher income relative to loan amount → Higher stability score
- More years employed → More stable
- Salaried > Self-employed (employment stability)
- Age 25-55 → Best loan prospects

**File:** `app/agents/application_profile_agent.py`

---

## 2. Financial Risk Analysis Agent

**Responsibility:** Analyze credit scores and debt ratios.

**Inputs:**
- Credit score (300-850)
- Total liabilities
- Monthly income
- Loan amount

**Outputs:**
```json
{
  "debt_to_income_ratio": 0.15,
  "credit_assessment": "Excellent credit history",
  "liability_assessment": "Manageable debt load",
  "financial_risk_score": 85.0,
  "risk_level": "Low"
}
```

**Decision Logic:**
- Credit score 750+ → Excellent
- DTI < 0.43 → Acceptable risk
- Liabilities < 50% of annual income → Manageable

**File:** `app/agents/financial_risk_agent.py`

---

## 3. Loan Decision Agent

**Responsibility:** Synthesize analyses and make final decision.

**Inputs:**
- Profile analysis results
- Financial risk analysis results
- Original application data

**Outputs:**
```json
{
  "decision": "Approve",
  "confidence_score": 92.5,
  "reasoning": "Strong credit profile with stable income and manageable debt",
  "recommended_conditions": [
    "Maximum interest rate: 5.2%",
    "Require proof of employment"
  ]
}
```

**Decision Rules:**
- **Approve:** Profile risk Low, Financial risk Low, Credit ≥700, DTI <0.43
- **Reject:** Profile risk High, Financial risk High, Credit <600, DTI >0.50
- **Review:** All other combinations

**File:** `app/agents/loan_decision_agent.py`

---

## 4. Compliance & Action Agent

**Responsibility:** Compliance checks and notifications.

**Inputs:**
- Loan decision
- Application data
- Audit trail

**Outputs:**
```json
{
  "compliance_status": "Approved",
  "notification_sent": true,
  "case_reference": "LOAN-ABC12345",
  "next_steps": [
    "Applicant notification sent",
    "Schedule document collection",
    "Initiate underwriting"
  ]
}
```

**Compliance Checks:**
- Regulatory requirements met
- Decision audit trail complete
- No fraud indicators
- Proper documentation

**File:** `app/agents/compliance_agent.py`

---

## Agent Implementation

### Base Class

All agents inherit from `BaseAgent` which provides:
- Claude connection management
- Response parsing
- Audit trail logging
- Error handling

**File:** `app/agents/base_agent.py`

### Example: Creating a New Agent

```python
from app.agents import BaseAgent
from app.models.agent_state import LoanApprovalState

class CustomAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="CustomAgent")
    
    def _create_system_prompt(self) -> str:
        return "Your agent description and instructions"
    
    def run(self, state: LoanApprovalState) -> LoanApprovalState:
        # Implement your logic
        return state
```

---

## Error Handling

Each agent implements error handling:
- Catches API failures gracefully
- Logs errors to audit trail
- Returns safe defaults on failure
- Prevents workflow interruption

---

## Testing Agents

```bash
# Run agent tests
pytest tests/test_agents.py -v

# Test specific agent
pytest tests/test_agents.py::test_application_profile_agent -v
```

---

## Performance Tuning

### Temperature Settings
- **Profile & Financial Analysis:** 0.3 (deterministic, consistent)
- **Loan Decision:** 0.2 (very deterministic)
- **Compliance:** 0.2 (rule-based)

### Token Limits
- Max tokens per agent: 2048
- Total workflow budget: ~8000 tokens

### Latency Targets
- Per agent: 2-5 seconds
- Full workflow: 15-20 seconds

---

## Debugging

### Enable Audit Trail
Audit entries are automatically created for each agent action:
```python
state.audit_trail  # List of all actions
```

### View Agent Logs
```python
# After workflow execution
for entry in state.audit_trail:
    print(f"{entry['timestamp']} - {entry['agent']}: {entry['action']}")
```
