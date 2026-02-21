#!/usr/bin/env python3
"""
Example demonstrating MCP (Model Context Protocol) integration
"""

import sys
import os

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))

from agent import SimpleAgent, Tool
from tools.mcp_tools import mcp_calculate, mcp_get_time
from config import AgentConfig

def example_mcp_calculate():
    """Example: Using MCP calculate tool"""
    print("=" * 60)
    print("Example 1: MCP Calculate")
    print("=" * 60)
    
    # Direct tool call
    result = mcp_calculate("15 * 23 + 100")
    print(f"Direct call result: {result}")
    
    # Through agent
    config = AgentConfig()
    agent = SimpleAgent(config=config)
    
    agent.register_tool(Tool(
        name="mcp_calculate",
        description="Calculate using MCP server. Parameters: expression (str)",
        func=mcp_calculate
    ))
    
    response = agent.run("Use MCP to calculate 456 * 789")
    print(f"Agent response: {response}\n")

def example_mcp_time():
    """Example: Using MCP time tool"""
    print("=" * 60)
    print("Example 2: MCP Get Time")
    print("=" * 60)
    
    # Direct tool call
    result = mcp_get_time()
    print(f"Direct call result: {result}")
    
    # Through agent
    config = AgentConfig()
    agent = SimpleAgent(config=config)
    
    agent.register_tool(Tool(
        name="mcp_get_time",
        description="Get current time from MCP server. No parameters required",
        func=mcp_get_time
    ))
    
    response = agent.run("What time is it now using MCP?")
    print(f"Agent response: {response}\n")

def example_mcp_combined():
    """Example: Using multiple MCP tools"""
    print("=" * 60)
    print("Example 3: Combined MCP Tools")
    print("=" * 60)
    
    config = AgentConfig()
    config.max_iterations = 10
    agent = SimpleAgent(config=config)
    
    # Register both MCP tools
    agent.register_tool(Tool(
        name="mcp_calculate",
        description="Calculate using MCP server. Parameters: expression (str)",
        func=mcp_calculate
    ))
    
    agent.register_tool(Tool(
        name="mcp_get_time",
        description="Get current time from MCP server. No parameters required",
        func=mcp_get_time
    ))
    
    response = agent.run("Get the current time and calculate 100 * 50 using MCP tools")
    print(f"Agent response: {response}\n")

def main():
    """Run all MCP examples"""
    print("\n🔌 MCP Integration Examples\n")
    
    try:
        print("Testing MCP tools...\n")
        
        example_mcp_calculate()
        example_mcp_time()
        example_mcp_combined()
        
        print("=" * 60)
        print("✅ All MCP examples completed!")
        print("=" * 60)
        print("\n💡 Tips:")
        print("  - MCP tools are now integrated into the agent")
        print("  - Run 'python core/main.py' to use them interactively")
        print("  - MCP server runs in the background when tools are called")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
