# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**WorkBot** is an AI agent framework built on top of `claude-internal` (a Claude-like AI assistant). It provides a tool-calling architecture that allows the AI to interact with files, execute code, perform calculations, and fetch web content.

## Architecture

### Core Components

1. **agent.py**: Main agent implementation
   - `SimpleAgent`: Core agent class with tool-calling loop
   - `Tool`: Dataclass for tool definitions
   - Handles Claude API calls via subprocess
   - Implements multi-iteration tool calling

2. **main.py**: Entry point for interactive mode
   - Registers all available tools
   - Runs interactive CLI loop
   - Handles user input/output

3. **config.py**: Configuration management
   - `AgentConfig`: Configuration dataclass
   - Environment variable support
   - Timeout and iteration limits

4. **tools/**: Tool implementations
   - `file_tools.py`: File operations (read, write, list)
   - `web_tools.py`: Web operations (fetch URL)
   - `code_tools.py`: Code execution (Python, shell, calculator)

5. **prompts/**: System prompts
   - `system_prompt.md`: Instructions for the agent on how to use tools

## Key Features

- **Tool Calling**: Agent can call tools using JSON format
- **Multi-iteration**: Supports chaining multiple tool calls
- **Extensible**: Easy to add new tools
- **Configurable**: Environment-based configuration
- **Safe Execution**: Timeouts and error handling

## Development Guidelines

### Adding New Tools

1. Create tool function in appropriate `tools/*.py` file
2. Add clear docstring with parameter descriptions
3. Register in `main.py` with descriptive name and description
4. Update `tools/__init__.py` if needed

### Tool Format

Tools should follow this pattern:
```python
def tool_name(param1: type, param2: type = default) -> str:
    """
    Clear description
    
    Args:
        param1: Description
        param2: Description
        
    Returns:
        Result description
    """
    try:
        # Implementation
        return result
    except Exception as e:
        return f"Error: {e}"
```

### Testing

Run examples:
```bash
python examples.py
```

Run interactive mode:
```bash
python source/main.py
```

## Dependencies

- Python 3.8+
- `requests` library for web operations
- `claude-internal` CLI tool (must be in PATH)

## Common Tasks

### Debugging
Set `DEBUG=true` environment variable or modify `config.py`

### Adjusting Timeouts
Set `TIMEOUT=60` environment variable for longer operations

### Adding More Iterations
Set `MAX_ITERATIONS=10` for complex multi-step tasks

## Notes for Claude Code

- The agent uses subprocess to call `claude-internal` CLI
- Tool calls are parsed from responses using regex
- System prompt guides the agent on tool usage format
- All tools return strings for consistency
- Error handling is built into each tool

