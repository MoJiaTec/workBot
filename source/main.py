# main.py
from agent import SimpleAgent, Tool
from tools import (
    read_file, write_file, list_directory,
    fetch_url, execute_python, calculate,
    mcp_calculate, mcp_factorial, mcp_is_prime,
    mcp_get_time, mcp_get_date_info,
    mcp_format_text, mcp_count_words, mcp_reverse_text,
    mcp_call_tool, mcp_list_servers, mcp_list_tools
)
from config import AgentConfig

def main():
    # Load configuration
    config = AgentConfig.from_env()
    
    # Create Agent with config
    agent = SimpleAgent(config=config)
    
    # Register file tools
    agent.register_tool(Tool(
        name="read_file",
        description="Read the contents of a file. Parameters: path (str) - the file path to read",
        func=read_file
    ))
    
    agent.register_tool(Tool(
        name="write_file",
        description="Write content to a file. Parameters: path (str) - the file path, content (str) - the content to write",
        func=write_file
    ))
    
    agent.register_tool(Tool(
        name="list_directory",
        description="List the contents of a directory. Parameters: path (str, optional) - the directory path, defaults to current directory",
        func=list_directory
    ))
    
    # Register web tools
    agent.register_tool(Tool(
        name="fetch_url",
        description="Fetch the content of a web page. Parameters: url (str) - the URL to fetch",
        func=fetch_url
    ))
    
    # Register code tools
    agent.register_tool(Tool(
        name="execute_python",
        description="Execute Python code and return the output. Parameters: code (str) - the Python code to execute",
        func=execute_python
    ))
    
    agent.register_tool(Tool(
        name="calculate",
        description="Evaluate a mathematical expression. Parameters: expression (str) - the math expression (e.g., '2 + 2 * 3')",
        func=calculate
    ))
    
    # Register MCP Math tools
    agent.register_tool(Tool(
        name="mcp_calculate",
        description="Calculate mathematical expression using MCP math server. Parameters: expression (str) - the math expression",
        func=mcp_calculate
    ))
    
    agent.register_tool(Tool(
        name="mcp_factorial",
        description="Calculate factorial using MCP math server. Parameters: n (int) - the number",
        func=mcp_factorial
    ))
    
    agent.register_tool(Tool(
        name="mcp_is_prime",
        description="Check if number is prime using MCP math server. Parameters: n (int) - the number to check",
        func=mcp_is_prime
    ))
    
    # Register MCP Utils tools
    agent.register_tool(Tool(
        name="mcp_get_time",
        description="Get current time using MCP utils server. No parameters required",
        func=mcp_get_time
    ))
    
    agent.register_tool(Tool(
        name="mcp_get_date_info",
        description="Get detailed date information using MCP utils server. No parameters required",
        func=mcp_get_date_info
    ))
    
    agent.register_tool(Tool(
        name="mcp_format_text",
        description="Format text using MCP utils server. Parameters: text (str), style (str) - upper/lower/title/capitalize",
        func=mcp_format_text
    ))
    
    agent.register_tool(Tool(
        name="mcp_count_words",
        description="Count words in text using MCP utils server. Parameters: text (str) - the text to analyze",
        func=mcp_count_words
    ))
    
    agent.register_tool(Tool(
        name="mcp_reverse_text",
        description="Reverse text using MCP utils server. Parameters: text (str) - the text to reverse",
        func=mcp_reverse_text
    ))
    
    # Register MCP Generic tools
    agent.register_tool(Tool(
        name="mcp_call_tool",
        description="Call any MCP tool by server and tool name. Parameters: server_name (str), tool_name (str), **params",
        func=mcp_call_tool
    ))
    
    agent.register_tool(Tool(
        name="mcp_list_servers",
        description="List all available MCP servers. No parameters required",
        func=mcp_list_servers
    ))
    
    agent.register_tool(Tool(
        name="mcp_list_tools",
        description="List tools for a specific MCP server. Parameters: server_name (str) - the server name",
        func=mcp_list_tools
    ))
    
    # Run interactive loop
    print("🤖 Agent Started (powered by claude-internal)")
    print("=" * 60)
    print(f"Configuration:")
    print(f"  - Max iterations: {config.max_iterations}")
    print(f"  - Timeout: {config.timeout}s")
    print(f"  - Debug mode: {config.debug}")
    print(f"\nRegistered {len(agent.tools)} tools:")
    for tool_name in agent.tools.keys():
        print(f"  ✓ {tool_name}")
    print("=" * 60)
    print("\n💡 MCP Servers Available:")
    print("  📊 Math Server (mcp_agent_math.py):")
    print("     - mcp_calculate: Calculate expressions")
    print("     - mcp_factorial: Calculate factorial")
    print("     - mcp_is_prime: Check if number is prime")
    print("\n  🛠️  Utils Server (mcp_agent_utils.py):")
    print("     - mcp_get_time: Get current time")
    print("     - mcp_get_date_info: Get date information")
    print("     - mcp_format_text: Format text")
    print("     - mcp_count_words: Count words")
    print("     - mcp_reverse_text: Reverse text")
    print("\n  🔧 Generic Tools:")
    print("     - mcp_list_servers: List all MCP servers")
    print("     - mcp_list_tools: List tools for a server")
    print("     - mcp_call_tool: Call any MCP tool")
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