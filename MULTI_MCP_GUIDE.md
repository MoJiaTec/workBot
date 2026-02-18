# Multiple MCP Servers Guide

## 📖 Overview

This guide explains how to use **multiple MCP (Model Context Protocol) servers** in the WorkBot Agent system. With multiple servers, you can organize tools by category and scale your agent's capabilities.

## 🎯 Why Multiple MCP Servers?

### Benefits

1. **Organization**: Group related tools together (math, utils, data, etc.)
2. **Scalability**: Add new servers without modifying existing ones
3. **Modularity**: Each server is independent and can be developed separately
4. **Performance**: Distribute load across multiple servers
5. **Flexibility**: Enable/disable servers as needed

## 🏗️ Architecture

```
┌─────────────────────┐
│   WorkBot Agent     │
│    (main.py)        │
└──────────┬──────────┘
           │
           │ uses
           ▼
┌─────────────────────┐
│   MCP Manager       │
│  (mcp_tools.py)     │
└──────────┬──────────┘
           │
           │ manages
           ▼
┌──────────────────────────────────────┐
│         Multiple MCP Clients         │
├──────────────┬───────────────────────┤
│  Math Client │  Utils Client │  ...  │
└──────┬───────┴───────┬───────────────┘
       │               │
       ▼               ▼
┌─────────────┐ ┌─────────────┐
│ Math Server │ │Utils Server │
│(mcp_agent_  │ │(mcp_agent_  │
│  math.py)   │ │  utils.py)  │
└─────────────┘ └─────────────┘
```

## 📦 Available MCP Servers

### 1. Math Server (`mcp_agent_math.py`)

**Purpose**: Mathematical operations

**Tools**:
- `calculate`: Safe mathematical expression evaluation
- `factorial`: Calculate factorial of a number
- `is_prime`: Check if a number is prime

**Example**:
```python
from tools.mcp_tools import mcp_calculate, mcp_factorial, mcp_is_prime

result = mcp_calculate("15 * 23 + 100")  # Result: 445
result = mcp_factorial(10)                # Factorial of 10 is 3628800
result = mcp_is_prime(17)                 # 17 is prime
```

### 2. Utils Server (`mcp_agent_utils.py`)

**Purpose**: Utility operations

**Tools**:
- `get_current_time`: Get current system time
- `get_date_info`: Get detailed date information
- `format_text`: Format text in different styles
- `count_words`: Count words, characters, and lines
- `reverse_text`: Reverse text

**Example**:
```python
from tools.mcp_tools import mcp_get_time, mcp_format_text, mcp_count_words

result = mcp_get_time()                           # 2026-02-18 15:30:45
result = mcp_format_text("hello", "upper")        # HELLO
result = mcp_count_words("Hello world")           # Words: 2, Characters: 11, Lines: 1
```

## ⚙️ Configuration

### Configuration File: `mcp_config.json`

```json
{
  "servers": [
    {
      "name": "math",
      "script": "mcp_agent_math.py",
      "description": "Math operations server",
      "enabled": true,
      "tools": [
        {"name": "calculate", "description": "Calculate mathematical expression"},
        {"name": "factorial", "description": "Calculate factorial"},
        {"name": "is_prime", "description": "Check if number is prime"}
      ]
    },
    {
      "name": "utils",
      "script": "mcp_agent_utils.py",
      "description": "Utility operations server",
      "enabled": true,
      "tools": [
        {"name": "get_current_time", "description": "Get current time"},
        {"name": "get_date_info", "description": "Get date info"},
        {"name": "format_text", "description": "Format text"},
        {"name": "count_words", "description": "Count words"},
        {"name": "reverse_text", "description": "Reverse text"}
      ]
    }
  ]
}
```

### Configuration Options

- **name**: Unique identifier for the server
- **script**: Python file containing the MCP server
- **description**: Human-readable description
- **enabled**: Whether the server is active (true/false)
- **tools**: List of tools provided by the server

## 🚀 Usage

### 1. List Available Servers

```python
from tools.mcp_tools import mcp_list_servers

result = mcp_list_servers()
# Available MCP servers: math, utils
```

### 2. List Tools for a Server

```python
from tools.mcp_tools import mcp_list_tools

result = mcp_list_tools("math")
# Tools on 'math': calculate, factorial, is_prime

result = mcp_list_tools("utils")
# Tools on 'utils': get_current_time, get_date_info, format_text, count_words, reverse_text
```

### 3. Use Specific Server Tools

```python
# Math server
from tools.mcp_tools import mcp_calculate, mcp_factorial

result = mcp_calculate("2^10")  # Result: 1024
result = mcp_factorial(5)       # Factorial of 5 is 120

# Utils server
from tools.mcp_tools import mcp_get_time, mcp_format_text

result = mcp_get_time()                    # 2026-02-18 15:30:45
result = mcp_format_text("test", "title")  # Test
```

### 4. Generic Tool Caller

```python
from tools.mcp_tools import mcp_call_tool

# Call any tool on any server
result = mcp_call_tool("math", "calculate", expression="100 + 200")
result = mcp_call_tool("utils", "format_text", text="hello", style="upper")
```

### 5. Interactive Mode

```bash
python source/main.py
```

Then try:
```
💬 You: List all MCP servers
💬 You: Calculate 123 * 456 using math server
💬 You: Get the current time
💬 You: Format "hello world" as title case
💬 You: Check if 17 is prime
💬 You: Calculate factorial of 8
```

### 6. Run Examples

```bash
python examples_multi_mcp.py
```

## 🔧 Adding a New MCP Server

### Step 1: Create Server File

Create `mcp_agent_myserver.py`:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MyServer")

@mcp.tool()
def my_tool(param: str) -> str:
    """My custom tool"""
    return f"Result: {param}"

if __name__ == "__main__":
    mcp.run()
```

### Step 2: Update Configuration

Edit `mcp_config.json`:

```json
{
  "servers": [
    {
      "name": "myserver",
      "script": "mcp_agent_myserver.py",
      "description": "My custom server",
      "enabled": true,
      "tools": [
        {"name": "my_tool", "description": "My custom tool"}
      ]
    }
  ]
}
```

### Step 3: Add Tool Implementation

Edit `source/tools/mcp_tools.py`, add to `MCPClient` class:

```python
def _tool_my_tool(self, param: str) -> str:
    """My tool implementation"""
    return f"Result: {param}"
```

### Step 4: Create Wrapper Function

Add to `source/tools/mcp_tools.py`:

```python
def mcp_my_tool(param: str) -> str:
    """
    Call my_tool using MCP myserver
    
    Args:
        param: Parameter description
        
    Returns:
        Tool result
    """
    manager = get_mcp_manager()
    return manager.call_tool("myserver", "my_tool", param=param)
```

### Step 5: Export Function

Edit `source/tools/__init__.py`:

```python
from .mcp_tools import mcp_my_tool

__all__ = [
    # ... existing tools
    'mcp_my_tool'
]
```

### Step 6: Register with Agent

Edit `source/main.py`:

```python
from tools import mcp_my_tool

agent.register_tool(Tool(
    name="mcp_my_tool",
    description="My custom tool. Parameters: param (str)",
    func=mcp_my_tool
))
```

### Step 7: Test

```python
from tools.mcp_tools import mcp_my_tool

result = mcp_my_tool("test")
print(result)  # Result: test
```

## 📊 Server Management

### Enable/Disable Servers

Edit `mcp_config.json`:

```json
{
  "name": "math",
  "enabled": false  // Disable this server
}
```

### Check Active Servers

```python
from tools.mcp_tools import mcp_list_servers

print(mcp_list_servers())
```

### Reload Configuration

Restart the agent to reload configuration:

```bash
python source/main.py
```

## 🎨 Best Practices

### 1. Server Organization

- **Group by domain**: math, text, data, web, etc.
- **Keep servers focused**: Each server should have a clear purpose
- **Avoid duplication**: Don't implement the same tool in multiple servers

### 2. Naming Conventions

- **Server names**: lowercase, descriptive (math, utils, data)
- **Tool names**: verb_noun format (calculate, format_text, get_time)
- **Function names**: mcp_server_tool format (mcp_math_calculate)

### 3. Error Handling

Always include error handling in tools:

```python
@mcp.tool()
def my_tool(param: str) -> str:
    try:
        # Tool logic
        return result
    except Exception as e:
        return f"Error: {e}"
```

### 4. Documentation

- Document each tool with clear descriptions
- Specify parameter types and return types
- Provide usage examples

### 5. Testing

Test each server independently:

```bash
python mcp_agent_math.py
python mcp_agent_utils.py
```

## 🧪 Testing

### Test Individual Tools

```python
from tools.mcp_tools import mcp_calculate, mcp_get_time

assert "Result: 4" in mcp_calculate("2 + 2")
assert len(mcp_get_time()) > 0
```

### Test Server Discovery

```python
from tools.mcp_tools import mcp_list_servers, mcp_list_tools

servers = mcp_list_servers()
assert "math" in servers
assert "utils" in servers

tools = mcp_list_tools("math")
assert "calculate" in tools
```

### Run All Examples

```bash
python examples_multi_mcp.py
```

## 🔍 Troubleshooting

### Server Not Found

**Problem**: `MCP server 'xxx' not found`

**Solution**:
1. Check `mcp_config.json` for server configuration
2. Ensure `enabled: true` in configuration
3. Verify server script file exists
4. Restart the agent

### Tool Not Found

**Problem**: `Unknown tool 'xxx' on server 'yyy'`

**Solution**:
1. Check tool is defined in server file
2. Verify tool implementation in `mcp_tools.py`
3. Ensure tool is listed in configuration
4. Check tool name spelling

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'mcp'`

**Solution**:
```bash
pip install -r requirements.txt
```

### Configuration Not Loading

**Problem**: Configuration changes not taking effect

**Solution**:
1. Verify `mcp_config.json` syntax (valid JSON)
2. Restart the agent
3. Check file path is correct

## 📈 Performance Tips

1. **Lazy Loading**: Servers are loaded only when needed
2. **Caching**: Manager instance is cached globally
3. **Parallel Calls**: Multiple tools can be called in parallel
4. **Resource Management**: Servers can be stopped when not needed

## 🎯 Use Cases

### 1. Domain-Specific Agents

Create specialized servers for different domains:
- **Finance**: stock prices, currency conversion
- **Weather**: forecasts, alerts
- **Database**: queries, updates
- **API**: external service integration

### 2. Microservices Architecture

Each MCP server acts as a microservice:
- Independent deployment
- Separate scaling
- Isolated failures

### 3. Plugin System

Add new capabilities without modifying core:
- Drop in new server file
- Update configuration
- Restart agent

## 📚 Examples

See `examples_multi_mcp.py` for complete examples:

```bash
python examples_multi_mcp.py
```

Examples include:
1. Listing servers and tools
2. Using math server tools
3. Using utils server tools
4. Generic tool calling
5. Agent integration
6. All tools showcase

## 🎊 Summary

Multiple MCP servers provide:
- ✅ **Organization**: Tools grouped by category
- ✅ **Scalability**: Easy to add new servers
- ✅ **Flexibility**: Enable/disable as needed
- ✅ **Modularity**: Independent development
- ✅ **Maintainability**: Clear separation of concerns

---

**Ready to use multiple MCP servers! 🚀**
