# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **Agentic AI Game Builder** — a system that accepts natural-language game ideas and generates playable HTML5 games (index.html, style.css, game.js) through a structured multi-phase pipeline.

## Architecture: Three Mandatory Agent Phases

1. **Requirements Clarification** — Accept a game idea, ask targeted follow-up questions, stop when requirements are clear (no excessive questioning)
2. **Planning** — Define game mechanics, controls, game loop, assets, framework choice (Phaser or vanilla JS), file structure, and core systems (input, rendering, state)
3. **Execution** — Generate `index.html`, `style.css`, and `game.js` that run locally in a browser without manual modification

## Constraints

- No hard-coded game templates — every game must be dynamically generated
- The clarification phase must not be skipped
- Generated output must be playable without manual post-generation edits
- Allowed tools: LLM APIs (OpenAI, Anthropic, etc.), CLI agents, orchestrator scripts, sub-agents, any programming language
- Generated games use HTML/CSS/JavaScript (optionally Phaser framework)

## Docker (Mandatory)

The agent must be containerized. Include a working `Dockerfile` with build/run instructions in the README. The full workflow (clarify → plan → build) must run inside the container.

```bash
# Expected usage pattern
docker build -t game-builder .
docker run -it game-builder
```

## Deliverables Checklist

- Full agent source code
- README.md with: run instructions, architecture explanation, trade-offs, future improvements, Docker instructions
- Working Dockerfile
- Optional: 3-4 minute screen recording demo
