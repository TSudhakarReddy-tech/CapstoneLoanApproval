# Quick Start Guide

Get the Loan Approval System up and running in minutes.

## Prerequisites

- Python 3.10+
- Anthropic API Key (get one at https://console.anthropic.com)

## Installation

### 1. Clone the Repository

```bash
cd CapstoneLoanApproval
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

```bash
# Copy example .env
cp .env.example .env

# Edit .env and add your API key
export ANTHROPIC_API_KEY="your-api-key-here"
```

## Running the System

### Option 1: Full System (Recommended)

**Terminal 1 - Start the API:**
```bash
uvicorn app.api.app:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Start the Streamlit UI:**
```bash
streamlit run main.py
```

Then open http://localhost:8501 in your browser.

### Option 2: API Only

```bash
uvicorn app.api.app:app --reload
```

API docs available at http://localhost:8000/docs

### Option 3: Command Line Testing

```python
from app.models import LoanApplicationRequest
from app.models.agent_state import LoanApprovalState
from app.orchestration import run_loan_approval_workflow

# Create application
app = LoanApplicationRequest(
    applicant_name="John Doe",
    age=35,
    monthly_income=5000,
    employment_type="Salaried",
    years_employed=5,
    credit_score=750,
    total_liabilities=10000,
    loan_amount=50000,
    loan_tenure_months=60,
    location="New York, NY",
)

# Create state
state = LoanApprovalState(application=app)

# Run workflow
result = run_loan_approval_workflow(state)

# Check decision
print(f"Decision: {result.loan_decision.decision}")
print(f"Confidence: {result.loan_decision.confidence_score}%")
```

## Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_agents.py::test_application_profile_agent -v

# Run with coverage
pytest --cov=app tests/
```

## File Structure

```
CapstoneLoanApproval/
├── app/
│   ├── agents/              # 4 Claude agents
│   ├── api/                 # FastAPI backend
│   ├── database/            # SQLAlchemy models
│   ├── models/              # Pydantic schemas
│   ├── orchestration/       # LangGraph workflow
│   └── ui/                  # Streamlit interface
├── tests/                   # Unit tests
├── docs/                    # Documentation
├── main.py                  # Streamlit entry
└── requirements.txt         # Dependencies
```

## API Examples

### Submit Application

```bash
curl -X POST "http://localhost:8000/api/applications" \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_name": "Jane Smith",
    "age": 30,
    "monthly_income": 6000,
    "employment_type": "Salaried",
    "years_employed": 3,
    "credit_score": 780,
    "total_liabilities": 5000,
    "loan_amount": 100000,
    "loan_tenure_months": 84,
    "location": "San Francisco, CA"
  }'
```

### Check Status

```bash
curl "http://localhost:8000/api/applications/{application_id}"
```

### List Applications

```bash
curl "http://localhost:8000/api/applications?skip=0&limit=10"
```

## Workflow Overview

```
User Submits Application
        ↓
Profile Analysis Agent
(income stability, employment)
        ↓
Financial Risk Agent
(credit score, debt ratios)
        ↓
Loan Decision Agent
(Approve/Reject/Review)
        ↓
Compliance Agent
(regulatory checks, notifications)
        ↓
Result Stored in Database
```

## Troubleshooting

### "Cannot connect to API"
- Make sure API is running on port 8000
- Check: `curl http://localhost:8000/health`

### "ANTHROPIC_API_KEY not set"
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

### Database already exists
```bash
rm loan_approval.db  # Delete old database
```

### Port already in use
- Streamlit: `streamlit run main.py --server.port 8502`
- API: `uvicorn app.api.app:app --port 8001`

## Next Steps

1. **Customize Agents:** Edit agent prompts in `app/agents/`
2. **Add Features:** Create new endpoints in `app/api/routes/`
3. **Improve UI:** Enhance Streamlit app in `app/ui/app.py`
4. **Production:** Set up PostgreSQL, add authentication, deploy to cloud

## Documentation

- [API Documentation](docs/API.md) - Full REST API specs
- [Agent Specifications](docs/AGENTS.md) - How each agent works
- [README](README.md) - Project overview

## Support

For issues, check the logs or create an issue on GitHub.

Happy lending! 🏦💰
