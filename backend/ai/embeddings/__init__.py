"""Embedding helpers for AI components.

This module delegates to the configured LLM provider (via `ai.llm.factory`) to
obtain embeddings and provides light normalization utilities used by the
vectorstore.
"""
from __future__ import annotations

import logging
from typing import List, Sequence

import numpy as np

from ai.llm.factory import get_embeddings

logger = logging.getLogger(__name__)


def embed_texts(texts: Sequence[str], model: str | None = None) -> List[List[float]]:
    """Return embeddings for the provided texts.

    This function returns a list of float vectors (one per input text).
    It normalizes vectors to unit length to make cosine similarity queries
    straightforward.
    """
    if not texts:
        return []

    raw = get_embeddings(list(texts), **({} if model is None else {"model": model}))

    # Convert to numpy array for normalization; fall back to raw lists when
    # conversion fails.
    try:
        arr = np.array(raw, dtype=float)
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        # Avoid division by zero
        norms[norms == 0.0] = 1.0
        normalized = (arr / norms).tolist()
        return normalized
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Failed to normalize embeddings: %s", exc)
        return raw


def embed_text(text: str, model: str | None = None) -> List[float]:
    """Convenience wrapper for a single text input."""
    embs = embed_texts([text], model=model)
    return embs[0] if embs else []
