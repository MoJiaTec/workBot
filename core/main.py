# main.py
from agent import SimpleAgent, Tool
from tools import (
    read_file, write_file, list_directory,
    fetch_url, execute_python, calculate,
)
from config import AgentConfig

def main():
    # Load configuration
    config = AgentConfig.from_env()

    # Create Agent with config
    agent = SimpleAgent(config=config)

    # Register built-in tools (always available)
    agent.register_tool(Tool(
        name="read_file",
        description="Read the contents of a file. Parameters: path (str) - the file path to read",
        func=read_file,
        tool_type="builtin"
    ))

    agent.register_tool(Tool(
        name="write_file",
        description="Write content to a file. Parameters: path (str) - the file path, content (str) - the content to write",
        func=write_file,
        tool_type="builtin"
    ))

    agent.register_tool(Tool(
        name="list_directory",
        description="List the contents of a directory. Parameters: path (str, optional) - the directory path, defaults to current directory",
        func=list_directory,
        tool_type="builtin"
    ))

    agent.register_tool(Tool(
        name="fetch_url",
        description="Fetch the content of a web page. Parameters: url (str) - the URL to fetch",
        func=fetch_url,
        tool_type="builtin"
    ))

    agent.register_tool(Tool(
        name="execute_python",
        description="Execute Python code and return the output. Parameters: code (str) - the Python code to execute",
        func=execute_python,
        tool_type="builtin"
    ))

    agent.register_tool(Tool(
        name="calculate",
        description="Evaluate a mathematical expression. Parameters: expression (str) - the math expression (e.g., '2 + 2 * 3')",
        func=calculate,
        tool_type="builtin"
    ))

    # Auto-discover skills and MCP tools
    print("🔍 Auto-discovering skills and MCP tools...")
    discovered_count = agent.auto_discover()

    # Print startup banner
    print("🤖 Agent Started (powered by claude-internal)")
    print("=" * 60)
    print(f"Configuration:")
    print(f"  - Max iterations: {config.max_iterations}")
    print(f"  - Timeout: {config.timeout}s")
    print(f"  - Debug mode: {config.debug}")
    print(f"\nRegistered {len(agent.tools)} tools:")
    # Group by type
    by_type = {"builtin": [], "skill": [], "mcp": []}
    for t in agent.tools.values():
        by_type.setdefault(t.tool_type, []).append(t.name)
    icons = {"builtin": "🔧", "skill": "📦", "mcp": "🔌"}
    for t_type, names in by_type.items():
        if names:
            print(f"  {icons.get(t_type, '')} {t_type.upper()} ({len(names)}): {', '.join(names)}")
    print("=" * 60)
    print("\nType 'quit' or 'exit' to stop")
    print("-" * 60)

    while True:
        try:
            user_input = input("\n💬 You: ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break

            if not user_input:
                continue

            print("\n🤔 Agent thinking...")
            response = agent.run(user_input)
            print(f"\n🤖 Agent: {response}")

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            if config.debug:
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    main()