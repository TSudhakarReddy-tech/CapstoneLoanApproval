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
- **Bedrock API Key** from tekstac gateway
- Environment variables configured

### Installation

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Update `.env` with your Bedrock credentials:
```
BEDROCK_API_KEY=your_bedrock_api_key_here
BEDROCK_BASE_URL=https://llmgw-wp.tekstac.com/v1
BEDROCK_MODEL=global.anthropic.claude-sonnet-4-6
```

For detailed setup instructions, see [BEDROCK_SETUP.md](BEDROCK_SETUP.md)

### Running the Application

**FastAPI Backend (Terminal 1):**
```bash
python api_server.py
```

**Streamlit UI (Terminal 2):**
```bash
streamlit run main.py
```

Access the application:
- UI: http://localhost:8501
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

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
# Bedrock API Configuration (Required)
BEDROCK_API_KEY=your_bedrock_api_key_here
BEDROCK_BASE_URL=https://llmgw-wp.tekstac.com/v1
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

**See [BEDROCK_SETUP.md](BEDROCK_SETUP.md) for detailed configuration instructions.**

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
