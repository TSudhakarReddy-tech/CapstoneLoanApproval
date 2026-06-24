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

    # Add nodes to workflow (use descriptive names that don't conflict with state keys)
    workflow.add_node("profile_agent_node", profile_node)
    workflow.add_node("financial_agent_node", financial_node)
    workflow.add_node("decision_agent_node", decision_node)
    workflow.add_node("compliance_agent_node", compliance_node)

    # Define edges - workflow sequence
    workflow.add_edge("profile_agent_node", "financial_agent_node")
    workflow.add_edge("financial_agent_node", "decision_agent_node")
    workflow.add_edge("decision_agent_node", "compliance_agent_node")

    # Set entry and exit points
    workflow.set_entry_point("profile_agent_node")
    workflow.set_finish_point("compliance_agent_node")

    return workflow.compile()


async def run_loan_approval_workflow(state: LoanApprovalState) -> LoanApprovalState:
    """Execute the loan approval workflow."""
    workflow = create_loan_approval_workflow()

    # Execute workflow synchronously (LangGraph returns sync)
    try:
        result = workflow.invoke(state)

        # Convert dict result back to LoanApprovalState if needed
        if isinstance(result, dict):
            state.profile_analysis = result.get('profile_analysis')
            state.financial_analysis = result.get('financial_analysis')
            state.loan_decision = result.get('loan_decision')
            state.compliance_result = result.get('compliance_result')
            state.workflow_status = result.get('workflow_status', 'completed')
            state.error_messages = result.get('error_messages', [])
            state.audit_trail = result.get('audit_trail', [])
            return state

        return result
    except Exception as e:
        print(f"Workflow error: {str(e)}")
        state.add_error(f"Workflow execution failed: {str(e)}")
        return state
