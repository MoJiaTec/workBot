#!/usr/bin/env python3
"""
Example script demonstrating how to use the WorkBot agent programmatically
"""

from source.agent import SimpleAgent, Tool
from source.tools import read_file, write_file, calculate
from source.config import AgentConfig

def example_basic_usage():
    """Example: Basic agent usage"""
    print("=" * 60)
    print("Example 1: Basic Usage")
    print("=" * 60)
    
    # Create agent
    config = AgentConfig()
    agent = SimpleAgent(config=config)
    
    # Register a simple tool
    agent.register_tool(Tool(
        name="calculate",
        description="Evaluate a mathematical expression. Parameters: expression (str)",
        func=calculate
    ))
    
    # Run agent
    response = agent.run("What is 25 * 4 + 100?")
    print(f"Response: {response}\n")

def example_file_operations():
    """Example: File operations"""
    print("=" * 60)
    print("Example 2: File Operations")
    print("=" * 60)
    
    # Create agent with file tools
    config = AgentConfig()
    agent = SimpleAgent(config=config)
    
    agent.register_tool(Tool(
        name="write_file",
        description="Write content to a file. Parameters: path (str), content (str)",
        func=write_file
    ))
    
    agent.register_tool(Tool(
        name="read_file",
        description="Read file contents. Parameters: path (str)",
        func=read_file
    ))
    
    # Create a test file
    response = agent.run("Create a file called test_example.txt with the content 'Hello from WorkBot!'")
    print(f"Response: {response}\n")

def example_multi_step():
    """Example: Multi-step task"""
    print("=" * 60)
    print("Example 3: Multi-step Task")
    print("=" * 60)
    
    config = AgentConfig()
    config.max_iterations = 10  # Allow more iterations
    agent = SimpleAgent(config=config)
    
    # Register multiple tools
    agent.register_tool(Tool(
        name="calculate",
        description="Evaluate a mathematical expression. Parameters: expression (str)",
        func=calculate
    ))
    
    agent.register_tool(Tool(
        name="write_file",
        description="Write content to a file. Parameters: path (str), content (str)",
        func=write_file
    ))
    
    # Complex task requiring multiple tools
    response = agent.run(
        "Calculate 123 * 456, then write the result to a file called calculation_result.txt"
    )
    print(f"Response: {response}\n")

def example_custom_tool():
    """Example: Creating and using a custom tool"""
    print("=" * 60)
    print("Example 4: Custom Tool")
    print("=" * 60)
    
    # Define a custom tool
    def greet(name: str, language: str = "en") -> str:
        """Greet someone in different languages"""
        greetings = {
            "en": f"Hello, {name}!",
            "es": f"¡Hola, {name}!",
            "fr": f"Bonjour, {name}!",
            "zh": f"你好, {name}!",
        }
        return greetings.get(language, greetings["en"])
    
    # Create agent and register custom tool
    config = AgentConfig()
    agent = SimpleAgent(config=config)
    
    agent.register_tool(Tool(
        name="greet",
        description="Greet someone. Parameters: name (str), language (str, optional: en/es/fr/zh)",
        func=greet
    ))
    
    # Use the custom tool
    response = agent.run("Greet Alice in Spanish")
    print(f"Response: {response}\n")

def main():
    """Run all examples"""
    print("\n🤖 WorkBot Agent Examples\n")
    
    try:
        example_basic_usage()
        example_file_operations()
        example_multi_step()
        example_custom_tool()
        
        print("=" * 60)
        print("✅ All examples completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
