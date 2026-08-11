"""MedicalAgent: high-level coordinator combining diagnosis and recommendations."""
from __future__ import annotations

import logging
from typing import List, Optional

from ai.agents.diagnosis_agent import DiagnosisAgent
from ai.agents.recommendation_agent import RecommendationAgent
from ai.prompts.chatbot_prompt import build_chat_prompt
from ai.llm.factory import get_completion

logger = logging.getLogger(__name__)


class MedicalAgent:
    """High-level agent that coordinates diagnosis and recommendation agents.

    Provides simple orchestration methods useful for API endpoints or workflows.
    """

    def __init__(self) -> None:
        self.diagnosis_agent = DiagnosisAgent()
        self.recommendation_agent = RecommendationAgent()

    def assess(self, symptoms: List[str], age: Optional[int] = None, sex: Optional[str] = None, context: Optional[str] = None) -> dict:
        """Run diagnosis and recommendation pipelines and return combined results.

        Returns a dictionary with keys: 'diagnosis', 'recommendations'.
        """
        try:
            diag = self.diagnosis_agent.diagnose(symptoms=symptoms, age=age, sex=sex, context=context)
            rec = self.recommendation_agent.recommend(symptoms=symptoms, diagnosis=diag, context=context)

            return {"diagnosis": diag, "recommendations": rec}
        except Exception as exc:  # pragma: no cover - let caller handle
            logger.exception("MedicalAgent.assess failed: %s", exc)
            raise

    def chat(self, messages: List[str], context: Optional[str] = None) -> str:
        """Simple chat interface built on top of the chatbot prompt template."""
        prompt = build_chat_prompt(messages=messages, context=context)
        try:
            return get_completion(prompt)
        except Exception as exc:
            logger.exception("MedicalAgent.chat failed: %s", exc)
            raise
