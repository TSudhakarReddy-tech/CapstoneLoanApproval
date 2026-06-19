"""Base agent class with Claude integration."""

import os
import json
from abc import ABC, abstractmethod
from anthropic import Anthropic
from app.models.agent_state import LoanApprovalState


class BaseAgent(ABC):
    """Base class for all loan approval agents."""

    def __init__(self, name: str, model: str = "claude-sonnet-4-20250514"):
        self.name = name
        self.model = model
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def _create_system_prompt(self) -> str:
        """Override this method to define agent-specific system prompt."""
        return f"You are {self.name}, an AI agent in a loan approval system."

    def _parse_response(self, response: str) -> dict:
        """Parse Claude's response. Override for custom parsing."""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"raw_response": response}

    def run(self, state: LoanApprovalState) -> LoanApprovalState:
        """Main entry point for agent execution. Override in subclasses."""
        return state

    def query_claude(self, messages: list[dict], temperature: float = 0.7) -> str:
        """Query Claude with structured messages."""
        system_prompt = self._create_system_prompt()

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            temperature=temperature,
            system=system_prompt,
            messages=messages,
        )

        return response.content[0].text

    def _log_action(self, state: LoanApprovalState, action: str, details: dict = None):
        """Log agent action to audit trail."""
        state.add_audit_entry(self.name, action, details)
