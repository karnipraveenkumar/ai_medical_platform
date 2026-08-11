"""Prompt templates for chatbot-style interactions.

Keep templates concise and safe for medical contexts. These are simple
string-based templates; production systems should use richer message formats
or tooling that enforces role-based messages.
"""
from __future__ import annotations

from typing import List


SYSTEM_PROMPT = (
    "You are a helpful, concise, and cautious medical assistant for clinicians "
    "and patients. Provide accurate information, avoid speculation, and when "
    "in doubt, recommend seeking a qualified healthcare professional."
)


def build_chat_prompt(messages: List[str], context: str | None = None) -> str:
    """Construct a single text prompt from a list of user messages.

    This returns a plain text prompt combining the system prompt, optional
    context, and the user messages in order. Agents may use this prompt with
    `get_completion` to produce a reply.
    """
    parts: List[str] = ["System:\n" + SYSTEM_PROMPT]

    if context:
        parts.append("Context:\n" + context)

    # Add user messages as a numbered list to provide history
    user_block = "\n".join(f"{i+1}. {m}" for i, m in enumerate(messages))
    parts.append("User Messages:\n" + user_block)

    parts.append("Assistant:\n")

    return "\n\n".join(parts)
