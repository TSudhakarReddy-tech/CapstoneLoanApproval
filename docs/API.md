# Loan Approval API Documentation

## Overview

FastAPI-based REST API for the loan approval system. Handles application submission, status tracking, and decision retrieval.

## Base URL

```
http://localhost:8000/api
```

## Endpoints

### 1. Submit Loan Application

**Endpoint:** `POST /applications`

**Description:** Submit a new loan application for processing.

**Request Body:**
```json
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
  "location": "New York, NY"
}
```

**Response (200 OK):**
```json
{
  "application_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:35:00Z",
  "decision": null
}
```

**Response (500 Error):**
```json
{
  "detail": "Workflow error: connection timeout"
}
```

---

### 2. Get Application Status

**Endpoint:** `GET /applications/{application_id}`

**Description:** Retrieve the status and decision of an application.

**Parameters:**
- `application_id` (path): UUID of the application

**Response (200 OK):**
```json
{
  "application_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:35:00Z",
  "decision": {
    "decision": "Approve",
    "confidence_score": 92.5,
    "case_reference": "LOAN-550E8400"
  }
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Application not found"
}
```

---

### 3. List Applications

**Endpoint:** `GET /applications`

**Description:** List all applications with optional filtering.

**Query Parameters:**
- `skip` (int, default=0): Number of records to skip
- `limit` (int, default=10): Number of records to return
- `status` (string, optional): Filter by status (submitted, processing, completed, error)

**Response (200 OK):**
```json
{
  "count": 5,
  "skip": 0,
  "limit": 10,
  "applications": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "applicant_name": "John Doe",
      "status": "completed",
      "loan_amount": 50000,
      "created_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": "6550e8400-e29b-41d4-a716-446655440001",
      "applicant_name": "Jane Smith",
      "status": "processing",
      "loan_amount": 75000,
      "created_at": "2024-01-15T10:45:00Z"
    }
  ]
}
```

---

### 4. Health Check

**Endpoint:** `GET /health`

**Description:** Check API service health.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "loan-approval-api"
}
```

---

## Field Specifications

### Application Request

| Field | Type | Min | Max | Description |
|-------|------|-----|-----|-------------|
| applicant_name | string | - | 255 | Full name of applicant |
| age | integer | 18 | 80 | Applicant age |
| monthly_income | float | >0 | - | Monthly income in dollars |
| employment_type | string | - | - | Salaried, Self-employed, Business Owner |
| years_employed | float | ≥0 | - | Years at current employment |
| credit_score | integer | 300 | 850 | Credit score |
| total_liabilities | float | ≥0 | - | Total outstanding debts in dollars |
| loan_amount | float | >0 | - | Requested loan amount in dollars |
| loan_tenure_months | integer | >0 | - | Loan tenure in months |
| location | string | - | 255 | Geographic location |

---

## Application Status Values

| Status | Description |
|--------|-------------|
| submitted | Application submitted, awaiting processing |
| processing | Currently being evaluated by agents |
| completed | Decision made |
| error | Processing error occurred |

---

## Decision Values

| Decision | Meaning |
|----------|---------|
| Approve | Loan approved |
| Reject | Loan rejected |
| Review | Requires manual review |

---

## Example Usage

### Using cURL

**Submit application:**
```bash
curl -X POST "http://localhost:8000/api/applications" \
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
    "location": "New York, NY"
  }'
```

**Get status:**
```bash
curl "http://localhost:8000/api/applications/550e8400-e29b-41d4-a716-446655440000"
```

### Using Python Requests

```python
import requests

# Submit application
response = requests.post(
    "http://localhost:8000/api/applications",
    json={
        "applicant_name": "John Doe",
        "age": 35,
        "monthly_income": 5000,
        "employment_type": "Salaried",
        "years_employed": 5,
        "credit_score": 750,
        "total_liabilities": 10000,
        "loan_amount": 50000,
        "loan_tenure_months": 60,
        "location": "New York, NY"
    }
)

application_id = response.json()["application_id"]

# Get status
status_response = requests.get(
    f"http://localhost:8000/api/applications/{application_id}"
)

print(status_response.json())
```

---

## Rate Limiting

Currently no rate limiting. Production deployment should implement:
- Per-IP rate limits
- Per-API-key quotas
- Sliding window limiting

---

## Error Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (validation error) |
| 404 | Not found |
| 422 | Unprocessable entity (invalid data) |
| 500 | Server error |

---

## API Documentation

Interactive API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Running the API

```bash
# Start API server
uvicorn app.api.app:app --reload --host 0.0.0.0 --port 8000
```
