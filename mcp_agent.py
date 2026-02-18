# mcp_agent.py
# Install: pip install mcp

from mcp.server.fastmcp import FastMCP

# Create MCP server
mcp = FastMCP("MyAgent")

@mcp.tool()
def calculate(expression: str) -> str:
    """Calculate mathematical expression"""
    try:
        # For production, use a safe evaluation method
        import ast
        import operator
        
        ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.Mod: operator.mod,
        }
        
        def eval_expr(node):
            if isinstance(node, ast.Num):
                return node.n
            elif isinstance(node, ast.BinOp):
                return ops[type(node.op)](eval_expr(node.left), eval_expr(node.right))
            else:
                raise ValueError(f"Unsupported operation")
        
        tree = ast.parse(expression, mode='eval')
        result = eval_expr(tree.body)
        return f"Result: {result}"
    except Exception as e:
        return f"Calculation error: {e}"

@mcp.tool()
def get_current_time() -> str:
    """Get current time"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    mcp.run()
