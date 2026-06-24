"""Base agent class with Claude integration via Anthropic API."""

import os
import json
from abc import ABC, abstractmethod
from app.models.agent_state import LoanApprovalState


class BaseAgent(ABC):
    """Base class for all loan approval agents."""

    def __init__(self, name: str, model: str = "claude-opus-4-6"):
        self.name = name
        self.model = model

        # Initialize Anthropic client
        api_key = os.getenv("ANTHROPIC_API_KEY")

        # If no API key, use mock mode
        if not api_key:
            print(f"⚠️  No ANTHROPIC_API_KEY found - {name} running in mock mode")
            self.client = None
        else:
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=api_key)
            except Exception as e:
                print(f"⚠️  Failed to initialize Anthropic client: {e} - {name} running in mock mode")
                self.client = None

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
        if self.client is None:
            return json.dumps({"error": "Claude client not available", "mode": "mock"})

        try:
            system_prompt = self._create_system_prompt()

            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                temperature=temperature,
                system=system_prompt,
                messages=messages,
            )

            return response.content[0].text
        except Exception as e:
            print(f"Error querying Claude: {e}")
            return json.dumps({"error": str(e)})

    def _log_action(self, state: LoanApprovalState, action: str, details: dict = None):
        """Log agent action to audit trail."""
        state.add_audit_entry(self.name, action, details)
