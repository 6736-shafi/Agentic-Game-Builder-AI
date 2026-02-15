"""Phase 3: Code Generation — generate index.html, style.css, and game.js."""

import json
import os
import re

import google.generativeai as genai
from config import MODEL_NAME, EXECUTE_SYSTEM_PROMPT, RETRY_PROMPT, OUTPUT_DIR


def run(plan: dict, history: list[dict]) -> str:
    """Run the execution phase.

    Returns:
        Path to the output directory containing generated files.
    """
    model = genai.GenerativeModel(
        MODEL_NAME,
        system_instruction=EXECUTE_SYSTEM_PROMPT,
        generation_config=genai.GenerationConfig(
            temperature=0.7,
            max_output_tokens=16384,
        ),
    )
    chat = model.start_chat(history=_rebuild_history(history))

    print("\n" + "=" * 60)
    print("PHASE 3: Code Generation")
    print("=" * 60)

    prompt = (
        f"Here is the game plan:\n\n```json\n{json.dumps(plan, indent=2)}\n```\n\n"
        "Generate the complete game now as index.html, style.css, and game.js."
    )
    print("\nGenerating game code (this may take a moment)...")
    response = chat.send_message(prompt)
    code_text = response.text

    # Extract the three files
    files = _extract_files(code_text)

    # Retry if game.js is missing or too short
    if not files.get("game.js") or len(files["game.js"]) < 200:
        print("game.js too short or missing — requesting regeneration...")
        response = chat.send_message(RETRY_PROMPT)
        js_match = re.search(
            r"```(?:js|javascript)\s*\n(.*?)```", response.text, re.DOTALL
        )
        if js_match:
            files["game.js"] = js_match.group(1).strip()

    # Write files to output directory
    output_path = os.path.abspath(OUTPUT_DIR)
    os.makedirs(output_path, exist_ok=True)

    for filename, content in files.items():
        filepath = os.path.join(output_path, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  Written: {filepath} ({len(content)} chars)")

    return output_path


def _extract_files(text: str) -> dict[str, str]:
    """Extract index.html, style.css, and game.js from fenced code blocks."""
    files = {}

    # index.html
    html_match = re.search(r"```html\s*\n(.*?)```", text, re.DOTALL)
    if html_match:
        files["index.html"] = html_match.group(1).strip()

    # style.css
    css_match = re.search(r"```css\s*\n(.*?)```", text, re.DOTALL)
    if css_match:
        files["style.css"] = css_match.group(1).strip()

    # game.js
    js_match = re.search(r"```(?:js|javascript)\s*\n(.*?)```", text, re.DOTALL)
    if js_match:
        files["game.js"] = js_match.group(1).strip()

    return files


def _rebuild_history(history: list[dict]) -> list:
    """Rebuild history into Gemini Content format."""
    from google.generativeai.types import content_types
    contents = []
    for msg in history:
        contents.append(content_types.to_content(
            {"role": msg["role"], "parts": msg["parts"]}
        ))
    return contents
