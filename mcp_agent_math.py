# mcp_agent_math.py
# Math-focused MCP server
# Install: pip install mcp

from mcp.server.fastmcp import FastMCP

# Create MCP server for math operations
mcp = FastMCP("MathAgent")

@mcp.tool()
def calculate(expression: str) -> str:
    """Calculate mathematical expression safely"""
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

@mcp.tool()
def factorial(n: int) -> str:
    """Calculate factorial of a number"""
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

@mcp.tool()
def is_prime(n: int) -> str:
    """Check if a number is prime"""
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

if __name__ == "__main__":
    mcp.run()
