"""Phase 1: Requirements Clarification — interactive Q&A with the user."""

import google.generativeai as genai
from config import MODEL_NAME, CLARIFY_SYSTEM_PROMPT

MAX_ROUNDS = 5
CLEAR_TOKEN = "REQUIREMENTS_CLEAR"


def run(game_idea: str) -> tuple[str, list[dict]]:
    """Run the clarification phase.

    Returns:
        (requirements_summary, conversation_history)
    """
    model = genai.GenerativeModel(
        MODEL_NAME,
        system_instruction=CLARIFY_SYSTEM_PROMPT,
    )
    chat = model.start_chat()

    print("\n" + "=" * 60)
    print("PHASE 1: Requirements Clarification")
    print("=" * 60)

    # Send the initial game idea
    response = chat.send_message(f"Game idea: {game_idea}")
    assistant_text = response.text

    for round_num in range(1, MAX_ROUNDS + 1):
        # Check if the agent is satisfied
        if CLEAR_TOKEN in assistant_text:
            summary = _extract_summary(assistant_text)
            print(f"\n[Requirements clarified after {round_num} round(s)]\n")
            print(summary)
            return summary, _history_to_dicts(chat.history)

        # Show the agent's questions and get user input
        print(f"\n--- Round {round_num} ---")
        print(f"Agent: {assistant_text}\n")
        user_input = input("You: ").strip()
        if not user_input:
            user_input = "Looks good, proceed with your best judgment."

        response = chat.send_message(user_input)
        assistant_text = response.text

    # Hard cap reached — force extraction
    print(f"\n[Max rounds ({MAX_ROUNDS}) reached, proceeding with current info]\n")
    # Ask for a final summary
    response = chat.send_message(
        "Please summarize the final requirements now. Output REQUIREMENTS_CLEAR "
        "followed by the summary."
    )
    summary = _extract_summary(response.text)
    print(summary)
    return summary, _history_to_dicts(chat.history)


def run_web(game_idea: str, history=None, user_reply=None):
    """Run clarification for the web UI (non-interactive).

    Args:
        game_idea: The original game idea text.
        history: Existing Gemini chat history dicts, or None for first call.
        user_reply: The user's reply to continue the conversation, or None.

    Returns:
        (response_text, is_clear, requirements_summary, history_dicts)
        - response_text: The agent's message to display
        - is_clear: True if requirements are finalized
        - requirements_summary: The extracted summary (only when is_clear)
        - history_dicts: Serializable conversation history for next call
    """
    model = genai.GenerativeModel(
        MODEL_NAME,
        system_instruction=CLARIFY_SYSTEM_PROMPT,
    )

    if history:
        chat = model.start_chat(history=_rebuild_history(history))
    else:
        chat = model.start_chat()

    if user_reply:
        response = chat.send_message(user_reply)
    else:
        response = chat.send_message(f"Game idea: {game_idea}")

    assistant_text = response.text
    history_dicts = _history_to_dicts(chat.history)

    if CLEAR_TOKEN in assistant_text:
        summary = _extract_summary(assistant_text)
        return summary, True, summary, history_dicts

    # Check if we've hit the max rounds
    round_count = sum(1 for m in history_dicts if m["role"] == "model")
    if round_count >= MAX_ROUNDS:
        response = chat.send_message(
            "Please summarize the final requirements now. Output REQUIREMENTS_CLEAR "
            "followed by the summary."
        )
        summary = _extract_summary(response.text)
        history_dicts = _history_to_dicts(chat.history)
        return summary, True, summary, history_dicts

    return assistant_text, False, None, history_dicts


def _rebuild_history(history: list[dict]) -> list:
    """Rebuild history dicts into Gemini Content format."""
    from google.generativeai.types import content_types
    contents = []
    for msg in history:
        contents.append(content_types.to_content(
            {"role": msg["role"], "parts": msg["parts"]}
        ))
    return contents


def _extract_summary(text: str) -> str:
    """Extract the summary after the REQUIREMENTS_CLEAR token."""
    if CLEAR_TOKEN in text:
        parts = text.split(CLEAR_TOKEN, 1)
        return parts[1].strip() if len(parts) > 1 else text
    return text


def _history_to_dicts(history) -> list[dict]:
    """Convert Gemini chat history to serializable dicts."""
    result = []
    for msg in history:
        result.append({
            "role": msg.role,
            "parts": [p.text for p in msg.parts],
        })
    return result
