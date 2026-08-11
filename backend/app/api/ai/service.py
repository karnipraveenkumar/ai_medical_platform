from ai.llm.factory import get_completion


def generate_text(prompt: str) -> str:
    return get_completion(prompt)
