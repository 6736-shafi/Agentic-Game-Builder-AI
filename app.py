"""Flask web server for the Agentic Game-Builder AI."""

import os
import uuid
import zipfile
import io

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory

from phases import clarify, plan, execute

app = Flask(__name__)

# Server-side session store: { session_id: { game_idea, history, requirements, plan, output_path } }
sessions: dict[str, dict] = {}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/start", methods=["POST"])
def api_start():
    """Accept a game idea and run the first clarification round."""
    data = request.get_json()
    game_idea = data.get("game_idea", "").strip()
    if not game_idea:
        return jsonify({"error": "No game idea provided"}), 400

    session_id = str(uuid.uuid4())

    response_text, is_clear, requirements, history = clarify.run_web(game_idea)

    sessions[session_id] = {
        "game_idea": game_idea,
        "history": history,
        "requirements": requirements,
        "plan": None,
        "output_path": None,
    }

    return jsonify({
        "session_id": session_id,
        "response": response_text,
        "is_clear": is_clear,
    })


@app.route("/api/message", methods=["POST"])
def api_message():
    """Accept a user reply during the clarification phase."""
    data = request.get_json()
    session_id = data.get("session_id")
    message = data.get("message", "").strip()

    if not session_id or session_id not in sessions:
        return jsonify({"error": "Invalid session"}), 400
    if not message:
        return jsonify({"error": "Empty message"}), 400

    session = sessions[session_id]

    response_text, is_clear, requirements, history = clarify.run_web(
        game_idea=session["game_idea"],
        history=session["history"],
        user_reply=message,
    )

    session["history"] = history
    if is_clear:
        session["requirements"] = requirements

    return jsonify({
        "response": response_text,
        "is_clear": is_clear,
    })


@app.route("/api/build", methods=["POST"])
def api_build():
    """Run plan + execute phases after requirements are clear."""
    data = request.get_json()
    session_id = data.get("session_id")

    if not session_id or session_id not in sessions:
        return jsonify({"error": "Invalid session"}), 400

    session = sessions[session_id]
    if not session.get("requirements"):
        return jsonify({"error": "Requirements not yet clarified"}), 400

    try:
        # Phase 2: Plan
        game_plan, history = plan.run(session["requirements"], session["history"])
        session["plan"] = game_plan
        session["history"] = history

        # Phase 3: Execute — generate into a session-specific output dir
        output_dir = os.path.join(os.path.abspath("output"), session_id)
        os.makedirs(output_dir, exist_ok=True)

        # Temporarily override OUTPUT_DIR for this build
        import config
        original_output_dir = config.OUTPUT_DIR
        config.OUTPUT_DIR = output_dir

        output_path = execute.run(game_plan, history)

        config.OUTPUT_DIR = original_output_dir
        session["output_path"] = output_path

        return jsonify({
            "success": True,
            "title": game_plan.get("title", "Your Game"),
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/preview/<session_id>/<path:filename>")
def api_preview(session_id, filename):
    """Serve generated game files for iframe preview."""
    if session_id not in sessions:
        return "Session not found", 404

    session = sessions[session_id]
    output_path = session.get("output_path")
    if not output_path:
        return "Game not built yet", 404

    return send_from_directory(output_path, filename)


@app.route("/api/download/<session_id>")
def api_download(session_id):
    """Download all generated game files as a zip."""
    if session_id not in sessions:
        return "Session not found", 404

    session = sessions[session_id]
    output_path = session.get("output_path")
    if not output_path:
        return "Game not built yet", 404

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in ("index.html", "style.css", "game.js"):
            fpath = os.path.join(output_path, fname)
            if os.path.exists(fpath):
                zf.write(fpath, fname)
    buf.seek(0)

    title = "game"
    if session.get("plan"):
        title = session["plan"].get("title", "game").replace(" ", "_").lower()

    return send_file(buf, mimetype="application/zip",
                     as_attachment=True, download_name=f"{title}.zip")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
