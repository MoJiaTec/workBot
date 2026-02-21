# tools/__init__.py
"""
Tools package for the agent
"""

from .file_tools import read_file, write_file, list_directory
from .web_tools import fetch_url
from .code_tools import execute_python, execute_shell, calculate
from .mcp_tools import (
    mcp_calculate, mcp_factorial, mcp_is_prime,
    mcp_get_time, mcp_get_date_info,
    mcp_format_text, mcp_count_words, mcp_reverse_text,
    mcp_call_tool, mcp_list_servers, mcp_list_tools
)

__all__ = [
    'read_file',
    'write_file', 
    'list_directory',
    'fetch_url',
    'execute_python',
    'execute_shell',
    'calculate',
    # MCP Math tools
    'mcp_calculate',
    'mcp_factorial',
    'mcp_is_prime',
    # MCP Utils tools
    'mcp_get_time',
    'mcp_get_date_info',
    'mcp_format_text',
    'mcp_count_words',
    'mcp_reverse_text',
    # MCP Generic tools
    'mcp_call_tool',
    'mcp_list_servers',
    'mcp_list_tools'
]
