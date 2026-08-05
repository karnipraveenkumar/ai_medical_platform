"""DiagnosisAgent: create differential diagnoses from symptoms using LLM."""
from __future__ import annotations

import logging
from typing import List, Optional

from ai.llm.factory import get_completion
from ai.prompts.symptom_prompt import build_symptom_prompt

logger = logging.getLogger(__name__)


class DiagnosisAgent:
    """Agent that produces a differential diagnosis and associated recommendations.

    This agent is a thin wrapper around the LLM; it constructs prompts using
    `ai.prompts.symptom_prompt` and returns the LLM output. It does not make
    clinical decisions — it only assists with information synthesis.
    """

    def diagnose(
        self,
        symptoms: List[str],
        age: Optional[int] = None,
        sex: Optional[str] = None,
        context: Optional[str] = None,
        output_format: str = "text",
    ) -> str:
        """Return a diagnostic overview for the given symptoms.

        Parameters mirror `build_symptom_prompt`.
        """
        prompt = build_symptom_prompt(
            symptoms=symptoms,
            age=age,
            sex=sex,
            context=context,
            output_format=output_format,
        )

        try:
            response = get_completion(prompt)
            return response
        except Exception as exc:  # pragma: no cover - surface errors to caller
            logger.exception("DiagnosisAgent failed: %s", exc)
            raise
