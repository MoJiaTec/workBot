# WorkBot - Claude-Internal Agent

A powerful AI agent built on top of `claude-internal` (similar to Claude) with tool-calling capabilities.

## 🌟 Features

- **Tool Calling**: Agent can use various tools to accomplish tasks
- **Multi-iteration**: Supports multiple tool calls in sequence
- **Extensible**: Easy to add new tools
- **Configurable**: Environment-based configuration
- **Logging**: Built-in logging for debugging

## 🛠️ Available Tools

### File Operations
- `read_file`: Read file contents
- `write_file`: Write content to files
- `list_directory`: List directory contents

### Web Operations
- `fetch_url`: Fetch web page content

### Code Operations
- `execute_python`: Execute Python code safely
- `calculate`: Evaluate mathematical expressions

### MCP Math Server Tools
- `mcp_calculate`: Calculate mathematical expressions
- `mcp_factorial`: Calculate factorial of numbers
- `mcp_is_prime`: Check if a number is prime

### MCP Utils Server Tools
- `mcp_get_time`: Get current system time
- `mcp_get_date_info`: Get detailed date information
- `mcp_format_text`: Format text in different styles
- `mcp_count_words`: Count words in text
- `mcp_reverse_text`: Reverse text

### MCP Generic Tools
- `mcp_list_servers`: List all MCP servers
- `mcp_list_tools`: List tools for a specific server
- `mcp_call_tool`: Call any MCP tool by server and name

## 📦 Installation

### Prerequisites

1. **Python 3.8+**
2. **claude-internal CLI**: Make sure you have `claude-internal` command available

### Setup

```bash
# Clone or navigate to the project
cd workBot

# Install dependencies
pip install -r requirements.txt

# Run the agent
python source/main.py
```

## 🔌 MCP Integration

This agent now supports **Multiple MCP (Model Context Protocol) servers** for extended functionality!

### What is MCP?

MCP is a protocol that allows AI agents to communicate with external services and tools. The agent includes multiple MCP servers organized by category:

#### 📊 Math Server (`mcp_agent_math.py`)
- **calculate**: Safe mathematical expression evaluation
- **factorial**: Calculate factorial of numbers
- **is_prime**: Check if a number is prime

#### 🛠️ Utils Server (`mcp_agent_utils.py`)
- **get_current_time**: Get current system time
- **get_date_info**: Get detailed date information
- **format_text**: Format text in different styles
- **count_words**: Count words, characters, and lines
- **reverse_text**: Reverse text

### Using Multiple MCP Servers

MCP servers are automatically available when you run the agent:

```bash
python source/main.py
```

Example interactions:

```
💬 You: List all MCP servers
🤖 Agent: Available MCP servers: math, utils

💬 You: Calculate 123 * 456
🤖 Agent: Result: 56088

💬 You: Check if 17 is prime
🤖 Agent: 17 is prime

💬 You: Get the current time
🤖 Agent: 2026-02-18 15:45:01

💬 You: Format "hello world" as title case
🤖 Agent: Hello World
```

### Running MCP Examples

```bash
# Test multiple servers
python examples_multi_mcp.py

# Test single server (legacy)
python examples_mcp.py
```

### Configuration

Edit `mcp_config.json` to manage MCP servers:

```json
{
  "servers": [
    {
      "name": "math",
      "script": "mcp_agent_math.py",
      "enabled": true
    },
    {
      "name": "utils",
      "script": "mcp_agent_utils.py",
      "enabled": true
    }
  ]
}
```

### Adding Custom MCP Servers

1. Create a new MCP server file (e.g., `mcp_agent_myserver.py`)
2. Add configuration to `mcp_config.json`
3. Update `source/tools/mcp_tools.py` with tool implementations
4. Register tools in `source/main.py`

See **[MULTI_MCP_GUIDE.md](MULTI_MCP_GUIDE.md)** for detailed instructions.

## 🚀 Usage

### Basic Usage

```bash
python source/main.py
```

Then interact with the agent:

```
💬 You: What files are in the current directory?
🤔 Agent thinking...
🤖 Agent: [Lists files using list_directory tool]

💬 You: Calculate 15 * 23 + 100
🤔 Agent thinking...
🤖 Agent: 15 * 23 + 100 = 445

💬 You: Create a file called test.txt with "Hello World"
🤔 Agent thinking...
🤖 Agent: [Creates file using write_file tool]
```

### Configuration

You can configure the agent using environment variables:

```bash
# Set maximum iterations
export MAX_ITERATIONS=10

# Set timeout (seconds)
export TIMEOUT=60

# Enable debug mode
export DEBUG=true

# Set custom claude command
export CLAUDE_COMMAND=claude-internal

# Run the agent
python source/main.py
```

## 📁 Project Structure

```
workBot/
├── source/
│   ├── main.py              # Entry point
│   ├── agent.py             # Agent implementation
│   ├── config.py            # Configuration management
│   ├── prompts/
│   │   └── system_prompt.md # System prompt for the agent
│   └── tools/
│       ├── __init__.py      # Tools package
│       ├── file_tools.py    # File operation tools
│       ├── web_tools.py     # Web operation tools
│       ├── code_tools.py    # Code execution tools
│       └── mcp_tools.py     # MCP integration tools (multi-server)
├── mcp_agent.py             # Legacy MCP server
├── mcp_agent_math.py        # Math MCP server
├── mcp_agent_utils.py       # Utils MCP server
├── mcp_config.json          # MCP servers configuration
├── examples.py              # Usage examples
├── examples_mcp.py          # Single MCP server examples
├── examples_multi_mcp.py    # Multiple MCP servers examples
├── test_setup.py            # Setup verification tests
├── CLAUDE.md                # Claude Code guidance
├── MCP_GUIDE.md             # MCP integration guide
├── MULTI_MCP_GUIDE.md       # Multiple MCP servers guide
├── MULTI_MCP_SUMMARY.md     # Multiple MCP servers summary
├── README.md                # This file
└── requirements.txt         # Python dependencies
```

## 🔧 Adding New Tools

To add a new tool:

1. **Create the tool function** in an appropriate file under `tools/`:

```python
# tools/my_tools.py
def my_new_tool(param1: str, param2: int) -> str:
    """
    Description of what the tool does
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Result description
    """
    # Implementation
    return f"Result: {param1} {param2}"
```

2. **Register the tool** in `main.py`:

```python
from tools.my_tools import my_new_tool

agent.register_tool(Tool(
    name="my_new_tool",
    description="Description for the agent. Parameters: param1 (str), param2 (int)",
    func=my_new_tool
))
```

## 🎯 Example Use Cases

### File Management
```
You: Read the contents of README.md
You: Create a backup of config.py
You: List all Python files in the source directory
```

### Code Execution
```
You: Calculate the factorial of 10
You: Execute this Python code: print("Hello from agent!")
You: What is 2^10?
```

### Web Scraping
```
You: Fetch the content of https://example.com
```

### Complex Tasks
```
You: Read data.txt, calculate the sum of numbers, and write the result to result.txt
```

### Multiple MCP Servers
```
You: List all MCP servers
You: Calculate 999 * 888 using math server
You: Get the current time
You: Check if 17 is prime
You: Calculate factorial of 10
You: Format "hello world" as title case
You: Count words in "The quick brown fox"
You: Reverse the text "ABC123"
```

## 🐛 Debugging

Enable debug mode to see detailed logs:

```bash
DEBUG=true python source/main.py
```

Or modify `config.py` to set `debug = True` by default.

## ⚠️ Limitations

- **Security**: Code execution tools (`execute_python`, `execute_shell`) should be used carefully
- **Timeout**: Long-running operations may timeout (configurable)
- **Claude-internal**: Requires `claude-internal` CLI to be installed and accessible

## 🤝 Contributing

To contribute:

1. Add new tools in the `tools/` directory
2. Improve the agent logic in `agent.py`
3. Enhance the system prompt in `prompts/system_prompt.md`
4. Add tests and documentation

## 📝 License

This project is open source and available for educational purposes.

## 🙏 Acknowledgments

Built on top of `claude-internal` - a Claude-like AI assistant.

---

**Happy Agent Building! 🤖**
