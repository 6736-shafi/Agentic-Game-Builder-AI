Assignment: Agentic Game-Builder AI

Overview:
You are required to build an agentic AI system capable of designing and generating a small playable HTML/CSS/JavaScript game (using Phaser or vanilla JS) based on an ambiguous natural-language input.

This is not a prompt-engineering exercise. We are evaluating your ability to design a reliable AI agent with proper control flow, decision-making, and engineering structure.

Objective:

Your AI agent must:

Accept a natural-language game idea
Ask clarifying questions before implementation
Produce a structured internal plan
Generate a playable game using index.html, style.css, and game.js
Output runnable files that work locally in a browser
Mandatory Agent Phases:

Requirements Clarification

Ask follow-up questions before coding
Stop only when requirements are sufficiently clear
Avoid unnecessary or excessive questioning
Planning

Define game mechanics, controls, game loop, and assets
Decide the framework (Phaser or vanilla JS)
Decide file structure
Define core systems such as input handling, rendering, and state management
Execution

Generate index.html, style.css (minimal is fine), and game.js
Ensure the game is playable and runs locally
Technical Guidelines:

You may use LLM APIs (OpenAI, Anthropic, etc.), CLI-based coding agents, controller/orchestrator scripts, sub-agents, and any programming language for building the agent.

You may not hard-code a fixed game template, skip the clarification phase, or manually modify the generated game output.

Docker Requirement (Mandatory):

The agent must be packaged inside a Docker container.
Please include a working Dockerfile and clear build and run instructions in the README.
We should be able to build the Docker image and run the agent to generate the game output.

Deliverables:

Please submit:

Code repository
README.md including:
How to run the agent
Explanation of the agent architecture
Trade Offs made
Improvements you would make with more time
Docker build and run instructions
Optional (Recommended):

A short screen recording (3–4 minutes maximum) demonstrating:

Running the Docker container
The agent workflow (clarify → plan → build)
The final playable game
