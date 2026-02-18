# tools/mcp_tools.py
"""
MCP (Model Context Protocol) integration tools
Support for multiple MCP servers
"""

import subprocess
import json
import time
import os
from typing import Optional, Dict, Any, List

class MCPClient:
    """Client for communicating with a single MCP server"""
    
    def __init__(self, server_name: str, server_script: str):
        self.server_name = server_name
        self.server_script = server_script
        self.server_process = None
        
    def start_server(self) -> bool:
        """Start the MCP server"""
        try:
            import os
            script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), self.server_script)
            
            # Start MCP server as subprocess
            self.server_process = subprocess.Popen(
                ["python3", script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a bit for server to start
            time.sleep(1)
            
            if self.server_process.poll() is None:
                return True
            else:
                return False
        except Exception as e:
            print(f"Failed to start MCP server: {e}")
            return False
    
    def stop_server(self):
        """Stop the MCP server"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            self.server_process = None
    
    def call_tool(self, tool_name: str, **kwargs) -> str:
        """Call a tool on the MCP server"""
        try:
            # Route to appropriate implementation based on server
            method_name = f"_tool_{tool_name}"
            if hasattr(self, method_name):
                return getattr(self, method_name)(**kwargs)
            else:
                return f"Unknown tool '{tool_name}' on server '{self.server_name}'"
        except Exception as e:
            return f"MCP tool error on {self.server_name}: {e}"
    
    # Math server tools
    def _tool_calculate(self, expression: str) -> str:
        """Calculate mathematical expression (safe)"""
        try:
            import ast
            import operator
            
            ops = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.Pow: operator.pow,
                ast.Mod: operator.mod,
                ast.FloorDiv: operator.floordiv,
            }
            
            def eval_expr(node):
                if isinstance(node, ast.Num):
                    return node.n
                elif isinstance(node, ast.Constant):
                    return node.value
                elif isinstance(node, ast.BinOp):
                    return ops[type(node.op)](eval_expr(node.left), eval_expr(node.right))
                elif isinstance(node, ast.UnaryOp):
                    if isinstance(node.op, ast.USub):
                        return -eval_expr(node.operand)
                    elif isinstance(node.op, ast.UAdd):
                        return eval_expr(node.operand)
                    else:
                        raise ValueError(f"Unsupported unary operation")
                else:
                    raise ValueError(f"Unsupported operation")
            
            tree = ast.parse(expression, mode='eval')
            result = eval_expr(tree.body)
            return f"Result: {result}"
        except Exception as e:
            return f"Calculation error: {e}"
    
    def _tool_factorial(self, n: int) -> str:
        """Calculate factorial"""
        try:
            import math
            if n < 0:
                return "Error: Factorial not defined for negative numbers"
            if n > 100:
                return "Error: Number too large (max 100)"
            result = math.factorial(n)
            return f"Factorial of {n} is {result}"
        except Exception as e:
            return f"Factorial error: {e}"
    
    def _tool_is_prime(self, n: int) -> str:
        """Check if number is prime"""
        try:
            if n < 2:
                return f"{n} is not prime"
            if n == 2:
                return f"{n} is prime"
            if n % 2 == 0:
                return f"{n} is not prime"
            
            for i in range(3, int(n**0.5) + 1, 2):
                if n % i == 0:
                    return f"{n} is not prime"
            
            return f"{n} is prime"
        except Exception as e:
            return f"Prime check error: {e}"
    
    # Utils server tools
    def _tool_get_current_time(self) -> str:
        """Get current time"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _tool_get_date_info(self) -> str:
        """Get detailed date information"""
        from datetime import datetime
        now = datetime.now()
        return f"Date: {now.strftime('%Y-%m-%d')}, Day: {now.strftime('%A')}, Week: {now.isocalendar()[1]}"
    
    def _tool_format_text(self, text: str, style: str = "upper") -> str:
        """Format text in different styles"""
        try:
            if style == "upper":
                return text.upper()
            elif style == "lower":
                return text.lower()
            elif style == "title":
                return text.title()
            elif style == "capitalize":
                return text.capitalize()
            else:
                return f"Unknown style: {style}"
        except Exception as e:
            return f"Format error: {e}"
    
    def _tool_count_words(self, text: str) -> str:
        """Count words in text"""
        try:
            words = text.split()
            chars = len(text)
            lines = text.count('\n') + 1
            return f"Words: {len(words)}, Characters: {chars}, Lines: {lines}"
        except Exception as e:
            return f"Count error: {e}"
    
    def _tool_reverse_text(self, text: str) -> str:
        """Reverse text"""
        try:
            return text[::-1]
        except Exception as e:
            return f"Reverse error: {e}"


class MCPManager:
    """Manager for multiple MCP servers"""
    
    def __init__(self, config_path: str = "mcp_config.json"):
        self.config_path = config_path
        self.clients: Dict[str, MCPClient] = {}
        self.config = self._load_config()
        self._initialize_clients()
    
    def _load_config(self) -> Dict:
        """Load MCP configuration"""
        try:
            # Get project root directory
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            config_file = os.path.join(current_dir, self.config_path)
            
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    return json.load(f)
            else:
                # Default configuration
                return {
                    "servers": [
                        {
                            "name": "math",
                            "script": "mcp_agent_math.py",
                            "enabled": True
                        },
                        {
                            "name": "utils",
                            "script": "mcp_agent_utils.py",
                            "enabled": True
                        }
                    ]
                }
        except Exception as e:
            print(f"Error loading MCP config: {e}")
            return {"servers": []}
    
    def _initialize_clients(self):
        """Initialize MCP clients from config"""
        for server in self.config.get("servers", []):
            if server.get("enabled", True):
                name = server["name"]
                script = server["script"]
                self.clients[name] = MCPClient(name, script)
    
    def get_client(self, server_name: str) -> Optional[MCPClient]:
        """Get MCP client by server name"""
        return self.clients.get(server_name)
    
    def call_tool(self, server_name: str, tool_name: str, **kwargs) -> str:
        """Call a tool on a specific server"""
        client = self.get_client(server_name)
        if client:
            return client.call_tool(tool_name, **kwargs)
        else:
            return f"MCP server '{server_name}' not found"
    
    def list_servers(self) -> List[str]:
        """List all available servers"""
        return list(self.clients.keys())
    
    def list_tools(self, server_name: str) -> List[str]:
        """List tools for a specific server"""
        for server in self.config.get("servers", []):
            if server["name"] == server_name:
                return [tool["name"] for tool in server.get("tools", [])]
        return []


# Global MCP manager instance
_mcp_manager = None

def get_mcp_manager() -> MCPManager:
    """Get or create MCP manager instance"""
    global _mcp_manager
    if _mcp_manager is None:
        _mcp_manager = MCPManager()
    return _mcp_manager


# Tool functions for agent

# Math server tools
def mcp_calculate(expression: str) -> str:
    """
    Calculate mathematical expression using MCP math server
    
    Args:
        expression: Mathematical expression to evaluate
        
    Returns:
        Calculation result
    """
    manager = get_mcp_manager()
    return manager.call_tool("math", "calculate", expression=expression)


def mcp_factorial(n: int) -> str:
    """
    Calculate factorial using MCP math server
    
    Args:
        n: Number to calculate factorial for
        
    Returns:
        Factorial result
    """
    manager = get_mcp_manager()
    return manager.call_tool("math", "factorial", n=n)


def mcp_is_prime(n: int) -> str:
    """
    Check if number is prime using MCP math server
    
    Args:
        n: Number to check
        
    Returns:
        Prime check result
    """
    manager = get_mcp_manager()
    return manager.call_tool("math", "is_prime", n=n)


# Utils server tools
def mcp_get_time() -> str:
    """
    Get current time using MCP utils server
    
    Returns:
        Current time string
    """
    manager = get_mcp_manager()
    return manager.call_tool("utils", "get_current_time")


def mcp_get_date_info() -> str:
    """
    Get detailed date information using MCP utils server
    
    Returns:
        Date information
    """
    manager = get_mcp_manager()
    return manager.call_tool("utils", "get_date_info")


def mcp_format_text(text: str, style: str = "upper") -> str:
    """
    Format text using MCP utils server
    
    Args:
        text: Text to format
        style: Format style (upper, lower, title, capitalize)
        
    Returns:
        Formatted text
    """
    manager = get_mcp_manager()
    return manager.call_tool("utils", "format_text", text=text, style=style)


def mcp_count_words(text: str) -> str:
    """
    Count words in text using MCP utils server
    
    Args:
        text: Text to analyze
        
    Returns:
        Word count statistics
    """
    manager = get_mcp_manager()
    return manager.call_tool("utils", "count_words", text=text)


def mcp_reverse_text(text: str) -> str:
    """
    Reverse text using MCP utils server
    
    Args:
        text: Text to reverse
        
    Returns:
        Reversed text
    """
    manager = get_mcp_manager()
    return manager.call_tool("utils", "reverse_text", text=text)


# Generic tool caller
def mcp_call_tool(server_name: str, tool_name: str, **params) -> str:
    """
    Generic MCP tool caller for any server
    
    Args:
        server_name: Name of the MCP server
        tool_name: Name of the tool to call
        **params: Parameters to pass to the tool
        
    Returns:
        Tool execution result
    """
    manager = get_mcp_manager()
    return manager.call_tool(server_name, tool_name, **params)


def mcp_list_servers() -> str:
    """
    List all available MCP servers
    
    Returns:
        List of server names
    """
    manager = get_mcp_manager()
    servers = manager.list_servers()
    return f"Available MCP servers: {', '.join(servers)}"


def mcp_list_tools(server_name: str) -> str:
    """
    List all tools for a specific MCP server
    
    Args:
        server_name: Name of the MCP server
        
    Returns:
        List of tool names
    """
    manager = get_mcp_manager()
    tools = manager.list_tools(server_name)
    if tools:
        return f"Tools on '{server_name}': {', '.join(tools)}"
    else:
        return f"No tools found for server '{server_name}'"
