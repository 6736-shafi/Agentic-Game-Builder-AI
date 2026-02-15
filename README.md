# Agentic Game-Builder AI

An AI agent that generates playable HTML5 games from natural-language descriptions. Describe your game idea and the agent will clarify requirements, design a game plan, and generate ready-to-play code.

## Architecture

The system follows a three-phase agentic pipeline, accessible via both CLI and web UI:

```
User Input (natural language)
        │
        ▼
┌──────────────────┐
│  Phase 1: Clarify │ ← Interactive Q&A (1–3 rounds)
│  (clarify.py)     │   Asks about mechanics, controls, style
└────────┬─────────┘
         │  requirements summary
         ▼
┌──────────────────┐
│  Phase 2: Plan    │ ← Structured JSON game design
│  (plan.py)        │   Mechanics, entities, controls, game loop
└────────┬─────────┘
         │  game plan (JSON)
         ▼
┌──────────────────┐
│  Phase 3: Execute │ ← Code generation
│  (execute.py)     │   index.html + style.css + game.js
└────────┬─────────┘
         │
         ▼
   Playable Game (open in browser)
```

### File Structure

```
├── app.py               # Flask web server (browser-based chat UI)
├── main.py              # CLI entry point
├── agent.py             # CLI orchestrator (clarify → plan → execute)
├── config.py            # Gemini client, system prompts, constants
├── phases/
│   ├── clarify.py       # Phase 1: interactive requirements Q&A
│   ├── plan.py          # Phase 2: structured JSON game plan
│   └── execute.py       # Phase 3: code generation → 3 files
├── templates/
│   └── index.html       # Web UI template
├── static/
│   └── style.css        # Web UI styling
├── Dockerfile           # Docker container setup
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

### Key Design Decisions

- **Conversation history flows through all phases** — each phase has full context of prior decisions
- **Automatic stop** — clarification phase caps at 5 rounds with smart early exit
- **Framework auto-selection** — defaults to vanilla JS; uses Phaser only when physics/tilemaps are needed
- **Auto-retry** — if `game.js` is too short, the agent automatically requests regeneration
- **Model** — Gemini 2.0 Flash for fast, high-quality generation across all phases

## Docker Setup (Mandatory)

### Build the image

```bash
docker build -t game-builder .
```

### Run — Web UI (default)

```bash
docker run -p 5000:5000 -e GOOGLE_API_KEY=your_key_here game-builder
```

Then open **http://localhost:5000** in your browser.

### Run — CLI mode

```bash
docker run -it -e GOOGLE_API_KEY=your_key_here \
  -v $(pwd)/output:/app/output \
  game-builder python main.py
```

The generated game files will appear in `./output/` on your host machine.

### Extract generated files (web mode)

```bash
# Start container
docker run -d --name gb -p 5000:5000 \
  -e GOOGLE_API_KEY=your_key_here game-builder

# After building a game, copy files out
docker cp gb:/app/output ./output
```

## Local Setup (without Docker)

```bash
pip install -r requirements.txt
export GOOGLE_API_KEY=your_key_here   # or add to .env file
```

### Web UI

```bash
python app.py
# Open http://localhost:5000
```

### CLI

```bash
python main.py
# Follow the prompts, then open output/index.html
```

## How It Works

1. You describe a game idea in plain English
2. The agent asks clarifying questions (1–3 rounds)
3. It generates a structured game plan (JSON)
4. It writes complete, playable HTML5/CSS/JS code to `output/`
5. Open `index.html` in any modern browser — no build step needed

## Configuration

| Environment Variable | Default     | Description                           |
|---|---|---|
| `GOOGLE_API_KEY`     | *(required)* | Google Gemini API key                  |
| `OUTPUT_DIR`         | `./output`  | Where generated game files are written |

## Trade-offs

- **Single-model approach:** All three phases use Gemini 2.0 Flash. This keeps the system simple but means code quality depends on one model's capabilities.
- **No iterative debugging:** The agent doesn't test or fix the generated code. If Gemini produces a bug, you'll need to fix it manually or re-run.
- **Vanilla JS default:** Phaser is only used when explicitly needed (physics, tilemaps). This keeps games dependency-free but limits complexity.
- **No asset generation:** Games use programmatic graphics (canvas shapes, text). No sprites or audio are generated.
- **In-memory sessions:** Web UI sessions are stored in-memory. They don't persist across server restarts.

## Improvements with More Time

- Add a self-testing phase that opens the game in a headless browser and checks for JS errors
- Support iterative refinement ("make the player faster", "add a second level")
- Integrate image generation APIs for game sprites and backgrounds
- Add Phaser auto-detection based on game complexity analysis
- Support multiplayer and networked games
- Add WebSocket streaming for real-time build progress
- Persistent session storage (database) for the web UI
- Multi-model pipeline (use a stronger model for code generation)
