#!/usr/bin/env python3
"""
Example demonstrating Multiple MCP Servers integration
"""

import sys
import os

# Add source to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'source'))

from agent import SimpleAgent, Tool
from tools.mcp_tools import (
    mcp_calculate, mcp_factorial, mcp_is_prime,
    mcp_get_time, mcp_get_date_info,
    mcp_format_text, mcp_count_words, mcp_reverse_text,
    mcp_list_servers, mcp_list_tools, mcp_call_tool
)
from config import AgentConfig

def example_list_servers():
    """Example: List all MCP servers"""
    print("=" * 60)
    print("Example 1: List MCP Servers")
    print("=" * 60)
    
    result = mcp_list_servers()
    print(f"Result: {result}\n")

def example_list_tools():
    """Example: List tools for each server"""
    print("=" * 60)
    print("Example 2: List Tools for Each Server")
    print("=" * 60)
    
    # List math server tools
    result = mcp_list_tools("math")
    print(f"Math server: {result}")
    
    # List utils server tools
    result = mcp_list_tools("utils")
    print(f"Utils server: {result}\n")

def example_math_server():
    """Example: Using Math MCP server"""
    print("=" * 60)
    print("Example 3: Math Server Tools")
    print("=" * 60)
    
    # Calculate
    result = mcp_calculate("15 * 23 + 100")
    print(f"Calculate: {result}")
    
    # Factorial
    result = mcp_factorial(10)
    print(f"Factorial: {result}")
    
    # Prime check
    result = mcp_is_prime(17)
    print(f"Prime check: {result}\n")

def example_utils_server():
    """Example: Using Utils MCP server"""
    print("=" * 60)
    print("Example 4: Utils Server Tools")
    print("=" * 60)
    
    # Get time
    result = mcp_get_time()
    print(f"Current time: {result}")
    
    # Get date info
    result = mcp_get_date_info()
    print(f"Date info: {result}")
    
    # Format text
    result = mcp_format_text("hello world", "title")
    print(f"Format text: {result}")
    
    # Count words
    result = mcp_count_words("The quick brown fox jumps over the lazy dog")
    print(f"Count words: {result}")
    
    # Reverse text
    result = mcp_reverse_text("Hello MCP!")
    print(f"Reverse text: {result}\n")

def example_generic_caller():
    """Example: Using generic MCP tool caller"""
    print("=" * 60)
    print("Example 5: Generic MCP Tool Caller")
    print("=" * 60)
    
    # Call math server tool
    result = mcp_call_tool("math", "calculate", expression="2^10")
    print(f"Generic call (math): {result}")
    
    # Call utils server tool
    result = mcp_call_tool("utils", "format_text", text="python", style="upper")
    print(f"Generic call (utils): {result}\n")

def example_agent_integration():
    """Example: Using multiple MCP servers through agent"""
    print("=" * 60)
    print("Example 6: Agent with Multiple MCP Servers")
    print("=" * 60)
    
    config = AgentConfig()
    config.max_iterations = 10
    agent = SimpleAgent(config=config)
    
    # Register math tools
    agent.register_tool(Tool(
        name="mcp_calculate",
        description="Calculate using MCP math server. Parameters: expression (str)",
        func=mcp_calculate
    ))
    
    agent.register_tool(Tool(
        name="mcp_factorial",
        description="Calculate factorial using MCP math server. Parameters: n (int)",
        func=mcp_factorial
    ))
    
    # Register utils tools
    agent.register_tool(Tool(
        name="mcp_get_time",
        description="Get current time using MCP utils server. No parameters",
        func=mcp_get_time
    ))
    
    agent.register_tool(Tool(
        name="mcp_format_text",
        description="Format text using MCP utils server. Parameters: text (str), style (str)",
        func=mcp_format_text
    ))
    
    # Test complex query
    response = agent.run("Calculate 5 factorial, get the current time, and format 'hello' as uppercase")
    print(f"Agent response: {response}\n")

def example_all_tools():
    """Example: Showcase all MCP tools"""
    print("=" * 60)
    print("Example 7: All MCP Tools Showcase")
    print("=" * 60)
    
    print("\n📊 Math Server Tools:")
    print(f"  calculate(100 + 200): {mcp_calculate('100 + 200')}")
    print(f"  factorial(5): {mcp_factorial(5)}")
    print(f"  is_prime(13): {mcp_is_prime(13)}")
    
    print("\n🛠️  Utils Server Tools:")
    print(f"  get_time(): {mcp_get_time()}")
    print(f"  get_date_info(): {mcp_get_date_info()}")
    print(f"  format_text('test', 'upper'): {mcp_format_text('test', 'upper')}")
    print(f"  count_words('one two three'): {mcp_count_words('one two three')}")
    print(f"  reverse_text('ABC'): {mcp_reverse_text('ABC')}")
    print()

def main():
    """Run all multiple MCP server examples"""
    print("\n🔌 Multiple MCP Servers Integration Examples\n")
    
    try:
        print("Testing multiple MCP servers...\n")
        
        example_list_servers()
        example_list_tools()
        example_math_server()
        example_utils_server()
        example_generic_caller()
        example_all_tools()
        example_agent_integration()
        
        print("=" * 60)
        print("✅ All multiple MCP server examples completed!")
        print("=" * 60)
        print("\n💡 Tips:")
        print("  - You now have 2 MCP servers: math and utils")
        print("  - Each server provides specialized tools")
        print("  - Use mcp_list_servers() to see all servers")
        print("  - Use mcp_list_tools(server_name) to see server tools")
        print("  - Run 'python source/main.py' for interactive mode")
        print("\n📝 Configuration:")
        print("  - Edit mcp_config.json to add/remove servers")
        print("  - Create new MCP server files (mcp_agent_*.py)")
        print("  - Update mcp_tools.py to add tool implementations")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
