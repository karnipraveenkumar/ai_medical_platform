from __future__ import annotations

import logging
import os
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

try:
    import openai
except ImportError:  # pragma: no cover
    openai = None

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE_URL = os.getenv("OPENAI_API_BASE_URL", "https://api.openai.com/v1")


def _ensure_openai_configured() -> None:
    if openai is None:
        raise RuntimeError(
            "The OpenAI Python package is not installed. Install it or use GROQ as the provider."
        )

    if OPENAI_API_KEY:
        openai.api_key = OPENAI_API_KEY
    if OPENAI_API_BASE_URL:
        openai.api_base = OPENAI_API_BASE_URL


def get_completion(
    prompt: str,
    model: str = "gpt-3.5-turbo",
    max_tokens: int = 512,
    temperature: float = 0.7,
    timeout: int = 30,
) -> str:
    _ensure_openai_configured()
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
        request_timeout=timeout,
    )
    choices = response.get("choices", [])
    if choices:
        return choices[0].get("message", {}).get("content", "").strip()
    return ""


def get_embeddings(
    texts: List[str],
    model: str = "text-embedding-3-small",
    timeout: int = 30,
) -> List[List[float]]:
    _ensure_openai_configured()
    response = openai.Embedding.create(
        model=model,
        input=texts,
        request_timeout=timeout,
    )
    data = response.get("data", [])
    return [item.get("embedding", []) for item in data if isinstance(item, dict)]
