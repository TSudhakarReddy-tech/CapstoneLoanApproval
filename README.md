# Capstone Loan Approval System

An AI-driven automated loan approval system using Claude agents and LangGraph for intelligent decision-making.

## Overview

This system automates the loan approval process through a multi-agent architecture that evaluates:
- Applicant profiles (income stability, employment history)
- Financial risk (debt ratios, credit scores, liabilities)
- Loan decision classification (Approve/Reject/Review)
- Compliance and case management

## Architecture

```
UI Layer (Streamlit)
        ↓
API Layer (FastAPI)
        ↓
Orchestration (LangGraph)
        ↓
Agent Layer (Claude Sonnet)
        ↓
Database (SQLite)
```

## Quick Start

### Prerequisites
- Python 3.10+
- ANTHROPIC_API_KEY environment variable set

### Installation

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running the Application

**Streamlit UI:**
```bash
streamlit run main.py
```

**FastAPI Backend:**
```bash
uvicorn app.api.app:app --reload
```

## Project Structure

```
CapstoneLoanApproval/
├── app/
│   ├── agents/              # Claude-powered agents
│   ├── api/                 # FastAPI endpoints
│   ├── database/            # Database models and ORM
│   ├── models/              # Data schemas and state definitions
│   ├── orchestration/       # LangGraph workflow
│   └── ui/                  # Streamlit interface
├── tests/                   # Test suite
├── docs/                    # Documentation
├── main.py                  # Streamlit entry point
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## Features

- **Multi-Agent Architecture**: Specialized agents for different aspects of loan evaluation
- **Transparent Decision Making**: Audit trail of all agent reasoning
- **LangGraph Orchestration**: Coordinated workflow across multiple agents
- **FastAPI Backend**: Scalable REST API for application submission
- **Streamlit Interface**: User-friendly chatbot for applicants
- **SQLite Persistence**: Persistent storage of applications and decisions

## Technology Stack

- **Language**: Python 3.10+
- **UI Framework**: Streamlit
- **Web Framework**: FastAPI
- **Orchestration**: LangGraph
- **LLM**: Claude Sonnet (Anthropic)
- **Database**: SQLite + SQLAlchemy
- **Async Runtime**: asyncio

## API Endpoints

- `POST /applications` - Submit a new loan application
- `GET /applications/{id}` - Get application status and decision
- `GET /applications` - List all applications

## Environment Variables

```
ANTHROPIC_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///./loan_approval.db
```

## Testing

```bash
pytest
pytest -v  # Verbose output
pytest --cov  # With coverage
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Format code
black app/ tests/

# Lint
ruff check app/ tests/
```

## License

MIT

## Contributing

1. Create a feature branch (`git checkout -b feature/your-feature`)
2. Commit changes (`git commit -am 'Add feature'`)
3. Push to branch (`git push origin feature/your-feature`)
4. Create a Pull Request

## Support

For issues and questions, please create an issue on GitHub.
