"""Simple Groq API client wrapper using `httpx`.

This module provides a minimal, robust wrapper around a Groq-compatible
HTTP API. It intentionally keeps payload construction generic so it can be
adjusted to the target Groq endpoint without touching the rest of the codebase.

Functions:
- `get_completion(prompt, ...)` -> returns string completion
- `get_embeddings(texts, ...)` -> returns list[list[float]] embeddings

The client reads `GROQ_API_KEY` and `GROQ_API_BASE_URL` from the environment.
"""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
GROQ_API_BASE_URL: str = os.getenv("GROQ_API_BASE_URL", "https://api.groq.ai/v1")


def _auth_headers() -> Dict[str, str]:
    if not GROQ_API_KEY:
        return {}
    return {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}


def get_completion(
    prompt: str,
    model: str = "groq-1",
    max_tokens: int = 512,
    temperature: float = 0.0,
    timeout: int = 30,
) -> str:
    """Request a text completion from a Groq-compatible completions endpoint.

    This function posts a JSON payload to the configured `GROQ_API_BASE_URL`.
    The exact endpoint and payload keys may be adjusted by changing this
    function to match the target provider.

    Raises RuntimeError if `GROQ_API_KEY` is not set or httpx raises an error.
    """
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not set in the environment")

    url = f"{GROQ_API_BASE_URL}/completions"
    payload: Dict[str, Any] = {
        "model": model,
        "inputs": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(url, json=payload, headers=_auth_headers())
            resp.raise_for_status()
            data = resp.json()

        # Attempt to extract a completion string using common response shapes.
        # Providers differ; prefer `choices[0].text`, then `choices[0].message`,
        # then `outputs[0]`, then `result`.
        if isinstance(data, dict):
            if "choices" in data and data["choices"]:
                first = data["choices"][0]
                if isinstance(first, dict):
                    return first.get("text") or first.get("message", {}).get("content", "")
            if "outputs" in data and data["outputs"]:
                return data["outputs"][0]
            if "result" in data:
                return data["result"]

        # Fallback to returning the JSON string representation
        return str(data)

    except httpx.HTTPError as exc:
        logger.exception("Groq completion request failed: %s", exc)
        raise


def get_embeddings(
    texts: List[str], model: str = "embed-1", timeout: int = 30
) -> List[List[float]]:
    """Request embeddings for a list of texts.

    Returns a list of numeric vectors (one per input text).
    Raises RuntimeError if `GROQ_API_KEY` is not set.
    """
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not set in the environment")

    url = f"{GROQ_API_BASE_URL}/embeddings"
    payload: Dict[str, Any] = {"model": model, "input": texts}

    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(url, json=payload, headers=_auth_headers())
            resp.raise_for_status()
            data = resp.json()

        # Common embedding response shape: {"data": [{"embedding": [...]}, ...]}
        if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
            embeddings: List[List[float]] = []
            for item in data["data"]:
                if isinstance(item, dict) and "embedding" in item:
                    embeddings.append(item["embedding"])
                else:
                    # Unexpected item shape; log and skip
                    logger.warning("Unexpected embedding item shape: %s", item)
            return embeddings

        # Fallback: try to parse `embeddings` key or return empty list
        if isinstance(data, dict) and "embeddings" in data:
            return data["embeddings"]

        logger.warning("Unexpected embeddings response: %s", data)
        return []

    except httpx.HTTPError as exc:
        logger.exception("Groq embeddings request failed: %s", exc)
        raise
