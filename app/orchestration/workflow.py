"""LangGraph workflow for loan approval orchestration."""

from langgraph.graph import StateGraph
from app.models.agent_state import LoanApprovalState
from app.agents import (
    ApplicationProfileAgent,
    FinancialRiskAgent,
    LoanDecisionAgent,
    ComplianceAgent,
)


def create_loan_approval_workflow():
    """Create and return the loan approval workflow graph."""

    workflow = StateGraph(LoanApprovalState)

    # Initialize agents
    profile_agent = ApplicationProfileAgent()
    financial_agent = FinancialRiskAgent()
    decision_agent = LoanDecisionAgent()
    compliance_agent = ComplianceAgent()

    # Define workflow nodes
    def profile_node(state: LoanApprovalState) -> LoanApprovalState:
        """Execute profile analysis."""
        return profile_agent.run(state)

    def financial_node(state: LoanApprovalState) -> LoanApprovalState:
        """Execute financial analysis."""
        return financial_agent.run(state)

    def decision_node(state: LoanApprovalState) -> LoanApprovalState:
        """Make loan decision."""
        return decision_agent.run(state)

    def compliance_node(state: LoanApprovalState) -> LoanApprovalState:
        """Execute compliance check."""
        return compliance_agent.run(state)

    # Add nodes to workflow
    workflow.add_node("profile_analysis", profile_node)
    workflow.add_node("financial_analysis", financial_node)
    workflow.add_node("loan_decision", decision_node)
    workflow.add_node("compliance_check", compliance_node)

    # Define edges - workflow sequence
    workflow.add_edge("profile_analysis", "financial_analysis")
    workflow.add_edge("financial_analysis", "loan_decision")
    workflow.add_edge("loan_decision", "compliance_check")

    # Set entry and exit points
    workflow.set_entry_point("profile_analysis")
    workflow.set_finish_point("compliance_check")

    return workflow.compile()


async def run_loan_approval_workflow(state: LoanApprovalState) -> LoanApprovalState:
    """Execute the loan approval workflow."""
    workflow = create_loan_approval_workflow()

    # Execute workflow synchronously (LangGraph returns sync)
    try:
        result = workflow.invoke(state)
        return result
    except Exception as e:
        print(f"Workflow error: {str(e)}")
        state.add_error(f"Workflow execution failed: {str(e)}")
        return state
