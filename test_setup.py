#!/usr/bin/env python3
"""
Quick test to verify the agent setup
"""

import sys
import os

# Add source to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'source'))

def test_imports():
    """Test if all modules can be imported"""
    print("Testing imports...")
    try:
        from agent import SimpleAgent, Tool
        from config import AgentConfig
        from tools import read_file, write_file, calculate
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_config():
    """Test configuration"""
    print("\nTesting configuration...")
    try:
        from config import AgentConfig
        config = AgentConfig()
        print(f"✓ Config loaded: max_iterations={config.max_iterations}, timeout={config.timeout}")
        return True
    except Exception as e:
        print(f"✗ Config test failed: {e}")
        return False

def test_tool_registration():
    """Test tool registration"""
    print("\nTesting tool registration...")
    try:
        from agent import SimpleAgent, Tool
        from tools import calculate
        
        agent = SimpleAgent()
        agent.register_tool(Tool(
            name="test_tool",
            description="A test tool",
            func=lambda x: f"Result: {x}"
        ))
        
        if "test_tool" in agent.tools:
            print("✓ Tool registration works")
            return True
        else:
            print("✗ Tool not registered")
            return False
    except Exception as e:
        print(f"✗ Tool registration failed: {e}")
        return False

def test_calculate_tool():
    """Test the calculate tool directly"""
    print("\nTesting calculate tool...")
    try:
        from tools import calculate
        result = calculate("2 + 2")
        if "4" in result:
            print(f"✓ Calculate tool works: {result}")
            return True
        else:
            print(f"✗ Unexpected result: {result}")
            return False
    except Exception as e:
        print(f"✗ Calculate tool failed: {e}")
        return False

def test_file_tools():
    """Test file tools"""
    print("\nTesting file tools...")
    try:
        from tools import write_file, read_file
        
        # Write test
        test_file = "test_verify.txt"
        write_result = write_file(test_file, "Test content")
        
        # Read test
        read_result = read_file(test_file)
        
        # Cleanup
        import os
        if os.path.exists(test_file):
            os.remove(test_file)
        
        if "Test content" in read_result:
            print("✓ File tools work")
            return True
        else:
            print(f"✗ File tools failed: {read_result}")
            return False
    except Exception as e:
        print(f"✗ File tools failed: {e}")
        return False

def test_claude_command():
    """Test if claude-internal is available"""
    print("\nTesting claude-internal command...")
    import subprocess
    try:
        result = subprocess.run(
            ["which", "claude-internal"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✓ claude-internal found at: {result.stdout.strip()}")
            return True
        else:
            print("⚠️  claude-internal not found in PATH")
            print("   The agent will not work without claude-internal")
            return False
    except Exception as e:
        print(f"⚠️  Could not check for claude-internal: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("WorkBot Agent - Verification Tests")
    print("=" * 60)
    print()
    
    tests = [
        test_imports,
        test_config,
        test_tool_registration,
        test_calculate_tool,
        test_file_tools,
        test_claude_command,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"✗ Test crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! Agent is ready to use.")
        print("\nRun: python source/main.py")
    elif passed >= total - 1 and not results[-1]:
        print("⚠️  Almost ready! Install claude-internal to use the agent.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    print("=" * 60)
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
