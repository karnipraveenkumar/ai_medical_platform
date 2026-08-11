"""Prompt templates for symptom-based diagnosis requests.

These templates are intentionally conservative: they ask the model to provide
possible causes, differential diagnoses, urgent red flags, recommended tests,
and next steps. Outputs are expected as plain text; callers may request JSON
structured output by appending an instruction to the prompt.
"""
from __future__ import annotations

from typing import List, Optional


def build_symptom_prompt(
    symptoms: List[str],
    age: Optional[int] = None,
    sex: Optional[str] = None,
    context: Optional[str] = None,
    output_format: str = "text",
) -> str:
    """Construct a prompt asking for differential diagnosis and recommendations.

    Parameters:
    - symptoms: list of symptom descriptions (short strings)
    - age: patient age when known
    - sex: patient sex when known
    - context: additional clinical context (medications, history)
    - output_format: 'text' or 'json' — if 'json', ask the model to return a
      structured JSON with keys: 'differential', 'red_flags', 'recommended_tests', 'next_steps'
    """
    header = (
        "You are a clinical decision support assistant. Given the patient's "
        "symptoms and basic demographics, provide a concise differential diagnosis, "
        "list urgent 'red flag' conditions that need immediate attention, recommend "
        "initial diagnostic tests, and suggest next steps. Be conservative and include "
        "uncertainty when appropriate. Avoid definitive pronouncements; state probabilities."
    )

    demographic_lines = []
    if age is not None:
        demographic_lines.append(f"Age: {age}")
    if sex:
        demographic_lines.append(f"Sex: {sex}")

    body = "\n".join([
        header,
        "\nPatient information:",
        "\n".join(demographic_lines) if demographic_lines else "(no demographics provided)",
        "\nSymptoms:",
        "\n".join(f"- {s}" for s in symptoms),
    ])

    if context:
        body += "\n\nAdditional context:\n" + context

    if output_format.lower() == "json":
        body += (
            "\n\nReturn the response in JSON with the following keys: 'differential' (list of {condition:probability}),"
            " 'red_flags' (list), 'recommended_tests' (list), and 'next_steps' (list). Only output valid JSON."
        )
    else:
        body += "\n\nProvide: (1) concise differential diagnoses with brief rationale, (2) red flags, (3) recommended initial tests, and (4) next steps."

    return body
