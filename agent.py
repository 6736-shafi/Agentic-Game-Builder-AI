"""GameBuilderAgent — orchestrates the three-phase game generation pipeline."""

from phases import clarify, plan, execute


class GameBuilderAgent:
    """Orchestrates: clarify → plan → execute."""

    def __init__(self):
        self.history: list[dict] = []
        self.requirements: str = ""
        self.plan: dict = {}
        self.output_path: str = ""

    def run(self):
        """Run the full pipeline interactively."""
        print("\n" + "=" * 60)
        print("  Agentic Game-Builder AI")
        print("  Describe a game idea and I'll build it for you!")
        print("=" * 60)

        game_idea = input("\nWhat game would you like me to build?\n> ").strip()
        if not game_idea:
            print("No game idea provided. Exiting.")
            return

        # Phase 1: Clarify requirements
        self.requirements, self.history = clarify.run(game_idea)

        # Phase 2: Generate game plan
        self.plan, self.history = plan.run(self.requirements, self.history)

        # Phase 3: Generate code
        self.output_path = execute.run(self.plan, self.history)

        print("\n" + "=" * 60)
        print("  BUILD COMPLETE!")
        print(f"  Open {self.output_path}/index.html in your browser to play.")
        print("=" * 60 + "\n")
