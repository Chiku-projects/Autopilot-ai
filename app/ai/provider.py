import json
import logging
from abc import ABC, abstractmethod

from anthropic import Anthropic

from groq import Groq

from app.config import settings
from app.ai.schemas import Plan
from app.ai.prompts import PLANNER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

PLAN_TOOL_SCHEMA = {
    "name": "submit_plan",
    "description": "Submit a structured task plan.",
    "input_schema": {
        "type": "object",
        "properties": {
            "goal": {"type": "string"},
            "steps": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string"},
                        "arguments": {"type": "object"},
                        "reason": {"type": "string"},
                    },
                    "required": ["action", "arguments", "reason"],
                },
            },
        },
        "required": ["goal", "steps"],
    },
}


class AIProvider(ABC):
    @abstractmethod
    def create_plan(self, goal: str, observation: dict) -> Plan:
        ...

class GroqProvider(AIProvider):
    def __init__(self):
        self._client = Groq(api_key=settings.groq_api_key)
        self._model = settings.groq_model

    def create_plan(self, goal: str, observation: dict) -> Plan:
        user_content = (
            f"Goal: {goal}\n\nCurrent computer state:\n{json.dumps(observation, indent=2)}"
        )
        # Groq's API is OpenAI-compatible: tools use a "function" wrapper,
        # not Anthropic's flat schema.
        tool_schema = {
            "type": "function",
            "function": {
                "name": PLAN_TOOL_SCHEMA["name"],
                "description": PLAN_TOOL_SCHEMA["description"],
                "parameters": PLAN_TOOL_SCHEMA["input_schema"],
            },
        }
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            tools=[tool_schema],
            tool_choice={"type": "function", "function": {"name": "submit_plan"}},
        )

        message = response.choices[0].message
        if not message.tool_calls:
            raise ValueError("Model did not return a submit_plan tool call")

        call = message.tool_calls[0]
        arguments = json.loads(call.function.arguments)
        return Plan(**arguments)

class AnthropicProvider(AIProvider):
    def __init__(self):
        self._client = Anthropic(api_key=settings.anthropic_api_key)
        self._model = settings.anthropic_model

    def create_plan(self, goal: str, observation: dict) -> Plan:
        user_content = (
            f"Goal: {goal}\n\nCurrent computer state:\n{json.dumps(observation, indent=2)}"
        )
        response = self._client.messages.create(
            model=self._model,
            max_tokens=1024,
            system=PLANNER_SYSTEM_PROMPT,
            tools=[PLAN_TOOL_SCHEMA],
            tool_choice={"type": "tool", "name": "submit_plan"},
            messages=[{"role": "user", "content": user_content}],
        )

        for block in response.content:
            if block.type == "tool_use" and block.name == "submit_plan":
                return Plan(**block.input)

        raise ValueError("Model did not return a submit_plan tool call")
    

def get_ai_provider() -> AIProvider:
    if settings.ai_provider == "groq":
        return GroqProvider()
    return AnthropicProvider()
