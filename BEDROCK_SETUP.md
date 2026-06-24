# Bedrock API Setup Guide

This document provides instructions for setting up the Loan Approval System to use the AWS Bedrock API via the tekstac gateway.

## Configuration Overview

The system is now configured to use:
- **Bedrock API Gateway:** `https://llmgw-wp.tekstac.com/v1`
- **Model:** `global.anthropic.claude-sonnet-4-6`
- **Client Library:** Anthropic Python SDK

## Prerequisites

1. **Python 3.10+**
2. **Bedrock API Key** from tekstac
3. **Environment variables** configured

## Setup Steps

### 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/TSudhakarReddy-tech/CapstoneLoanApproval.git
cd CapstoneLoanApproval/CapstoneLoanApproval

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Bedrock API Configuration
BEDROCK_API_KEY=your_bedrock_api_key_here
BEDROCK_BASE_URL=https://llmgw-wp.tekstac.com/v1

# Model Configuration
BEDROCK_MODEL=global.anthropic.claude-sonnet-4-6

# Database Configuration
DATABASE_URL=sqlite:///./loan_approval.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
```

**Important:** Replace `your_bedrock_api_key_here` with your actual Bedrock API key.

### 3. How Bedrock Integration Works

#### Client Initialization

The `BaseAgent` class initializes the Anthropic client with Bedrock credentials:

```python
from anthropic import Anthropic

bedrock_api_key = os.getenv("BEDROCK_API_KEY")
bedrock_base_url = os.getenv("BEDROCK_BASE_URL", "https://llmgw-wp.tekstac.com/v1")

# Initialize client pointing to Bedrock gateway
client = Anthropic(
    api_key=bedrock_api_key,
    base_url=bedrock_base_url
)
```

#### Model Specification

All agents use the specified model:

```python
model = "global.anthropic.claude-sonnet-4-6"

response = client.messages.create(
    model=model,
    max_tokens=2048,
    temperature=0.7,
    system=system_prompt,
    messages=messages,
)
```

### 4. Running the Application

#### Option A: Run Separately (Development)

**Terminal 1 - Start FastAPI backend:**

```bash
# Ensure .env is loaded
python api_server.py
```

The API will be available at `http://localhost:8000`

- Health check: `http://localhost:8000/health`
- API docs: `http://localhost:8000/docs`

**Terminal 2 - Start Streamlit UI:**

```bash
streamlit run main.py
```

The UI will be available at `http://localhost:8501`

#### Option B: Docker Compose (Optional)

If Docker setup is available:

```bash
docker-compose up
```

### 5. Testing the Integration

#### Quick Test Script

Create `test_bedrock.py`:

```python
#!/usr/bin/env python3
import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("BEDROCK_API_KEY")
base_url = os.getenv("BEDROCK_BASE_URL")

print(f"API Key: {api_key[:10]}...")
print(f"Base URL: {base_url}")

try:
    client = Anthropic(api_key=api_key, base_url=base_url)
    
    response = client.messages.create(
        model="global.anthropic.claude-sonnet-4-6",
        max_tokens=100,
        messages=[
            {
                "role": "user",
                "content": "Say 'Bedrock API is working!' in one sentence."
            }
        ]
    )
    
    print("\n✅ Bedrock API Test Success!")
    print(f"Response: {response.content[0].text}")
    
except Exception as e:
    print(f"\n❌ Bedrock API Test Failed!")
    print(f"Error: {str(e)}")
```

Run the test:

```bash
python test_bedrock.py
```

#### Test Loan Approval Workflow

```bash
# Submit a test application
curl -X POST http://localhost:8000/api/applications \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_name": "John Doe",
    "age": 35,
    "monthly_income": 5000,
    "employment_type": "Salaried",
    "years_employed": 5,
    "credit_score": 750,
    "total_liabilities": 10000,
    "loan_amount": 50000,
    "loan_tenure_months": 60,
    "location": "United States"
  }'
```

### 6. API Endpoints

#### Submit Loan Application

```http
POST /api/applications
Content-Type: application/json

{
  "applicant_name": "John Doe",
  "age": 35,
  "monthly_income": 5000,
  "employment_type": "Salaried",
  "years_employed": 5,
  "credit_score": 750,
  "total_liabilities": 10000,
  "loan_amount": 50000,
  "loan_tenure_months": 60,
  "location": "United States"
}
```

**Response:**

```json
{
  "application_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "decision": {
    "decision": "Approved",
    "confidence_score": 85.5,
    "risk_level": "LOW",
    "case_id": "CASE-APP-20240624-A1B2C3",
    "decision_summary": "...",
    "approval_conditions": {...}
  },
  "created_at": "2024-06-24T10:30:00Z",
  "updated_at": "2024-06-24T10:30:15Z"
}
```

#### Check Application Status

```http
GET /api/applications/{application_id}
```

#### List All Applications

```http
GET /api/applications
```

### 7. Agents Using Bedrock

All four agents now use Bedrock API via the tekstac gateway:

1. **ApplicationProfileAgent** (`app/agents/application_profile_agent.py`)
   - Analyzes income stability and employment suitability
   - Model: `global.anthropic.claude-sonnet-4-6`

2. **FinancialRiskAgent** (`app/agents/financial_risk_agent.py`)
   - Evaluates credit scores and debt ratios
   - Model: `global.anthropic.claude-sonnet-4-6`

3. **LoanDecisionAgent** (`app/agents/loan_decision_agent.py`)
   - Makes final approval/rejection/review decision
   - Model: `global.anthropic.claude-sonnet-4-6`

4. **ComplianceAgent** (`app/agents/compliance_agent.py`)
   - Handles compliance verification and notifications
   - Model: `global.anthropic.claude-sonnet-4-6`

### 8. Troubleshooting

#### Issue: "No BEDROCK_API_KEY found"

**Solution:** Ensure your `.env` file contains the `BEDROCK_API_KEY` variable.

```bash
# Check if .env exists
cat .env

# If not, create it
cp .env.example .env
# Then edit .env with your actual API key
```

#### Issue: Connection Refused to tekstac Gateway

**Solution:** Verify the base URL and network connectivity:

```bash
# Test connectivity
curl -v https://llmgw-wp.tekstac.com/v1/health

# Or use Python
python -c "import requests; print(requests.get('https://llmgw-wp.tekstac.com/v1').status_code)"
```

#### Issue: Authentication Failed

**Solution:** Verify your API key is correct:

```bash
# Test with curl
curl -X POST https://llmgw-wp.tekstac.com/v1/messages \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "global.anthropic.claude-sonnet-4-6", "messages": [{"role": "user", "content": "test"}], "max_tokens": 100}'
```

#### Issue: Application Runs in Mock Mode

**Solution:** This happens when the API key is not found. Check:

1. `.env` file exists and has `BEDROCK_API_KEY` set
2. Environment variables are loaded: `python -c "import os; print(os.getenv('BEDROCK_API_KEY'))"`
3. No whitespace issues in API key

### 9. Production Deployment

#### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set environment variables
ENV BEDROCK_API_KEY=${BEDROCK_API_KEY}
ENV BEDROCK_BASE_URL=https://llmgw-wp.tekstac.com/v1
ENV BEDROCK_MODEL=global.anthropic.claude-sonnet-4-6

EXPOSE 8000 8501

CMD ["python", "api_server.py"]
```

Build and run:

```bash
docker build -t loan-approval-system .

docker run -e BEDROCK_API_KEY=your_key \
  -p 8000:8000 \
  -p 8501:8501 \
  loan-approval-system
```

#### Environment Variables for Production

Use your deployment platform's secret management:

- AWS: Use AWS Secrets Manager
- Azure: Use Azure Key Vault
- Kubernetes: Use Secrets

Example (Kubernetes):

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: bedrock-credentials
type: Opaque
stringData:
  BEDROCK_API_KEY: your_api_key_here
  BEDROCK_BASE_URL: https://llmgw-wp.tekstac.com/v1
```

### 10. Performance Tuning

#### Adjustable Parameters

In `app/agents/base_agent.py`:

```python
response = client.messages.create(
    model=self.model,
    max_tokens=2048,  # Adjust as needed
    temperature=0.7,  # Lower = more deterministic, Higher = more creative
    system=system_prompt,
    messages=messages,
)
```

**Recommendations:**

- **max_tokens:** 1024-2048 for normal decisions
- **temperature:** 0.2-0.3 for compliance (consistent), 0.7-0.8 for reasoning
- **timeout:** Add timeout for long-running requests

#### Connection Pooling

Update `base_agent.py` for production:

```python
self.client = Anthropic(
    api_key=bedrock_api_key,
    base_url=bedrock_base_url,
    timeout=30.0,  # 30 second timeout
    max_retries=3,  # Retry failed requests
)
```

### 11. Monitoring and Logging

#### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Monitor Agent Performance

Track in `app/agents/base_agent.py`:

```python
import time

start_time = time.time()
response = self.client.messages.create(...)
elapsed = time.time() - start_time

print(f"Agent {self.name} took {elapsed:.2f}s")
```

### 12. Support and Issues

For issues related to:

- **Bedrock API:** Contact tekstac support
- **Application Code:** See GitHub issues: https://github.com/TSudhakarReddy-tech/CapstoneLoanApproval/issues
- **Anthropic SDK:** Refer to https://github.com/anthropics/anthropic-sdk-python

---

## Summary

Your Loan Approval System is now configured to use Bedrock API with:

✅ **Base URL:** `https://llmgw-wp.tekstac.com/v1`  
✅ **Model:** `global.anthropic.claude-sonnet-4-6`  
✅ **Client:** Anthropic Python SDK with custom endpoint  
✅ **All Agents:** Using Bedrock for AI reasoning  

To get started, set your `BEDROCK_API_KEY` and run the application!
