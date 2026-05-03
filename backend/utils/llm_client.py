"""
Thin wrapper around the Anthropic Python SDK.
All LLM calls in the pipeline go through here so that
model name, retry logic, and token limits are configured once.
"""

import os
import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

_client: anthropic.Anthropic | None = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "ANTHROPIC_API_KEY is not set. "
                "Copy backend/.env.example to backend/.env and add your key."
            )
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def extract_json(
    system_prompt: str,
    user_prompt: str,
    model: str | None = None,
    max_tokens: int = 4096,
) -> dict:
    """
    Call Claude and return the response parsed as JSON.
    The system prompt must instruct the model to respond ONLY with valid JSON.
    Raises ValueError if the response cannot be parsed.
    """
    client = get_client()
    chosen_model = model or os.getenv("MODEL", "claude-sonnet-4-20250514")

    message = client.messages.create(
        model=chosen_model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw = message.content[0].text.strip()

    # Strip markdown fences if model wraps JSON in ```json ... ```
    if raw.startswith("```"):
        lines = raw.split("\n")
        # Remove opening fence (```json or ```)
        lines = lines[1:] if lines[0].startswith("```") else lines
        # Remove closing fence
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        raw = "\n".join(lines).strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM returned non-JSON response: {e}\n\nRaw output:\n{raw[:500]}")
