"""LLM factory selecting provider-specific client adapters.

This module exposes `get_client()` which returns a simple adapter implementing
`get_completion(prompt, **kwargs)` and `get_embeddings(texts, **kwargs)`.

Provider selection is controlled by the `LLM_PROVIDER` environment variable
(case-insensitive). Supported values: `groq` (default), `openai` (if available).

The adapters are intentionally thin — they adapt provider-specific functions
into a common shape used by the higher-level agents.
"""
from __future__ import annotations

import logging
import os
from typing import Callable, List

logger = logging.getLogger(__name__)

# Lazy imports: only import provider modules when selected so optional
# dependencies are not enforced at import-time.


class _BaseAdapter:
    def get_completion(self, prompt: str, **kwargs) -> str:
        raise NotImplementedError()

    def get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        raise NotImplementedError()


class _GroqAdapter(_BaseAdapter):
    def __init__(self):
        from ai.llm.groq_client import get_completion as _g_get_completion
        from ai.llm.groq_client import get_embeddings as _g_get_embeddings

        self._get_completion: Callable = _g_get_completion
        self._get_embeddings: Callable = _g_get_embeddings

    def get_completion(self, prompt: str, **kwargs) -> str:
        return self._get_completion(prompt, **kwargs)

    def get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        return self._get_embeddings(texts, **kwargs)


class _OpenAIAdapter(_BaseAdapter):
    def __init__(self):
        # Optional: import if available
        try:
            from ai.llm.openai_client import get_completion as _o_get_completion
            from ai.llm.openai_client import get_embeddings as _o_get_embeddings
        except Exception as exc:  # pragma: no cover - optional import
            logger.exception("OpenAI client not available: %s", exc)
            raise

        self._get_completion = _o_get_completion
        self._get_embeddings = _o_get_embeddings

    def get_completion(self, prompt: str, **kwargs) -> str:
        return self._get_completion(prompt, **kwargs)

    def get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        return self._get_embeddings(texts, **kwargs)


_CLIENT: _BaseAdapter | None = None


def get_client() -> _BaseAdapter:
    """Return a singleton adapter for the configured LLM provider.

    Environment variables:
    - `LLM_PROVIDER`: 'groq' (default) or 'openai'
    """
    global _CLIENT

    if _CLIENT is not None:
        return _CLIENT

    provider = os.getenv("LLM_PROVIDER", "groq").strip().lower()

    if provider == "groq":
        logger.info("Using Groq LLM provider")
        _CLIENT = _GroqAdapter()
        return _CLIENT

    if provider == "openai":
        logger.info("Using OpenAI LLM provider")
        _CLIENT = _OpenAIAdapter()
        return _CLIENT

    # Unknown provider: fall back to Groq but warn
    logger.warning("Unknown LLM_PROVIDER '%s', falling back to 'groq'", provider)
    _CLIENT = _GroqAdapter()
    return _CLIENT


def get_completion(prompt: str, **kwargs) -> str:
    """Convenience wrapper that delegates to the selected client."""
    client = get_client()
    return client.get_completion(prompt, **kwargs)


def get_embeddings(texts: List[str], **kwargs) -> List[List[float]]:
    client = get_client()
    return client.get_embeddings(texts, **kwargs)
