"""Prompt templates for summarizing and extracting information from reports.

Provides prompt builders for radiology/lab report summarization and structured
extraction of key findings and recommendations.
"""
from __future__ import annotations

from typing import Optional


def build_report_summary_prompt(report_text: str, length: int = 150) -> str:
    """Ask the model to summarize a medical report into a concise summary.

    `length` suggests the desired maximum token/word length for the summary.
    """
    prompt = (
        "You are a concise medical summarization assistant. Summarize the following "
        "medical report into a short, clear summary highlighting key findings, abnormalities, "
        "and any recommendations. Use lay-friendly language where possible, but keep clinical terms.\n\n"
    )
    prompt += f"Report:\n{report_text}\n\nSummary (max {length} words):\n"
    return prompt


def build_report_extraction_prompt(report_text: str, fields: Optional[list] = None) -> str:
    """Build a prompt asking the model to extract structured fields from the report.

    `fields` is an optional list of keys to extract (e.g., ['diagnosis','impression','recommendations']).
    The prompt asks for JSON output by default to facilitate parsing.
    """
    if fields is None:
        fields = ["impression", "diagnosis", "recommendations", "critical_findings"]

    prompt = (
        "You are a medical report parser. Extract the following fields from the report and return valid JSON with keys: "
        + ", ".join(fields)
        + ". If a field is not present, use null or an empty list as appropriate. Only output valid JSON.\n\n"
    )
    prompt += f"Report:\n{report_text}\n\nJSON:\n"
    return prompt
