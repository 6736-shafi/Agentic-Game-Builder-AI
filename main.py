"""Entry point for the Agentic Game-Builder AI."""

from agent import GameBuilderAgent


def main():
    try:
        agent = GameBuilderAgent()
        agent.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
    except Exception as e:
        print(f"\nError: {e}")
        raise


if __name__ == "__main__":
    main()
