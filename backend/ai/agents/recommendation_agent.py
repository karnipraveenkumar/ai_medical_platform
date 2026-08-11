"""RecommendationAgent: suggest tests, treatments, and next steps."""
from __future__ import annotations

import logging
from typing import List, Optional

from ai.llm.factory import get_completion

logger = logging.getLogger(__name__)


class RecommendationAgent:
    """Agent that provides recommendations based on symptoms or a diagnosis.

    Produces conservative, evidence-minded suggestions. Not a replacement for
    clinical judgment.
    """

    def recommend(
        self,
        symptoms: Optional[List[str]] = None,
        diagnosis: Optional[str] = None,
        context: Optional[str] = None,
    ) -> str:
        """Produce recommended tests, treatments, and follow-up actions."""
        parts: List[str] = []
        if diagnosis:
            parts.append(f"Diagnosis: {diagnosis}")
        if symptoms:
            parts.append("Symptoms:\n" + "\n".join(f"- {s}" for s in symptoms))
        if context:
            parts.append("Context:\n" + context)

        prompt = (
            "You are a clinical recommendations assistant. Based on the information below, "
            "list recommended diagnostic tests (initial), possible empirical treatments (if applicable), the urgency of care, and suggested follow-up. Be concise and include rationale.\n\n"
            + "\n\n".join(parts)
        )

        try:
            return get_completion(prompt)
        except Exception as exc:  # pragma: no cover - propagate
            logger.exception("RecommendationAgent failed: %s", exc)
            raise
