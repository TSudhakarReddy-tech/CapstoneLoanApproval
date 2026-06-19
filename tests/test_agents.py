"""Unit tests for agents."""

import pytest
from app.models import LoanApplicationRequest, LoanApprovalState
from app.agents import ApplicationProfileAgent, FinancialRiskAgent


@pytest.fixture
def sample_application():
    """Create a sample loan application."""
    return LoanApplicationRequest(
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


@pytest.fixture
def loan_state(sample_application):
    """Create a loan approval state."""
    return LoanApprovalState(application=sample_application)


def test_application_profile_agent(loan_state):
    """Test ApplicationProfileAgent execution."""
    agent = ApplicationProfileAgent()
    result = agent.run(loan_state)

    assert result.profile_analysis is not None
    assert 0 <= result.profile_analysis.income_stability_score <= 100
    assert result.profile_analysis.profile_risk_level in ["Low", "Medium", "High"]


def test_financial_risk_agent(loan_state):
    """Test FinancialRiskAgent execution."""
    agent = FinancialRiskAgent()
    result = agent.run(loan_state)

    assert result.financial_analysis is not None
    assert 0 <= result.financial_analysis.financial_risk_score <= 100
    assert result.financial_analysis.risk_level in ["Low", "Medium", "High"]
    assert 0 <= result.financial_analysis.debt_to_income_ratio


def test_audit_trail(loan_state):
    """Test audit trail functionality."""
    agent = ApplicationProfileAgent()
    result = agent.run(loan_state)

    assert len(result.audit_trail) > 0
    assert result.audit_trail[0]["agent"] == "ApplicationProfileAgent"
