"""Phase 2: Game Planning — produce a structured JSON game plan."""

import json
import re

import google.generativeai as genai
from config import MODEL_NAME, PLAN_SYSTEM_PROMPT


def run(requirements: str, history: list[dict]) -> tuple[dict, list[dict]]:
    """Run the planning phase.

    Returns:
        (plan_dict, updated_history)
    """
    model = genai.GenerativeModel(
        MODEL_NAME,
        system_instruction=PLAN_SYSTEM_PROMPT,
        generation_config=genai.GenerationConfig(temperature=0.4),
    )
    chat = model.start_chat(history=_rebuild_history(history))

    print("\n" + "=" * 60)
    print("PHASE 2: Game Planning")
    print("=" * 60)

    prompt = (
        f"Here are the clarified requirements:\n\n{requirements}\n\n"
        "Generate the JSON game plan now."
    )
    response = chat.send_message(prompt)
    plan_text = response.text

    # Extract JSON from markdown fences or raw text
    plan = _extract_json(plan_text)

    print(f"\nGame Plan: {plan.get('title', 'Untitled')}")
    print(f"Framework: {plan.get('framework', 'vanilla')}")
    print(f"Mechanics: {', '.join(plan.get('mechanics', []))}")
    print(f"Controls: {json.dumps(plan.get('controls', {}))}")

    return plan, _history_to_dicts(chat.history)


def _extract_json(text: str) -> dict:
    """Extract JSON from markdown code fences or raw text."""
    # Try ```json ... ``` first
    match = re.search(r"```json\s*\n(.*?)```", text, re.DOTALL)
    if match:
        return json.loads(match.group(1))

    # Try bare ``` ... ```
    match = re.search(r"```\s*\n(.*?)```", text, re.DOTALL)
    if match:
        return json.loads(match.group(1))

    # Try raw JSON
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))

    raise ValueError(f"Could not extract JSON from plan response:\n{text[:500]}")


def _rebuild_history(history: list[dict]) -> list:
    """Rebuild history into Gemini Content format."""
    from google.generativeai.types import content_types
    contents = []
    for msg in history:
        contents.append(content_types.to_content(
            {"role": msg["role"], "parts": msg["parts"]}
        ))
    return contents


def _history_to_dicts(history) -> list[dict]:
    """Convert Gemini chat history to serializable dicts."""
    result = []
    for msg in history:
        result.append({
            "role": msg.role,
            "parts": [p.text for p in msg.parts],
        })
    return result
