# tools/code_tools.py
import subprocess
import sys
from typing import Optional

def execute_python(code: str) -> str:
    """
    Execute Python code safely and return the output
    
    Args:
        code: Python code to execute
        
    Returns:
        The output of the code execution
    """
    try:
        # Create a temporary file to execute
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        # Execute the code
        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Clean up
        import os
        os.unlink(temp_file)
        
        output = result.stdout
        if result.stderr:
            output += f"\nErrors:\n{result.stderr}"
        
        return output if output else "Code executed successfully (no output)"
        
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out (>10s)"
    except Exception as e:
        return f"Error executing code: {e}"

def execute_shell(command: str) -> str:
    """
    Execute a shell command and return the output
    
    Args:
        command: Shell command to execute
        
    Returns:
        The output of the command
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        output = result.stdout
        if result.stderr:
            output += f"\nErrors:\n{result.stderr}"
        
        return output if output else "Command executed successfully (no output)"
        
    except subprocess.TimeoutExpired:
        return "Error: Command timed out (>10s)"
    except Exception as e:
        return f"Error executing command: {e}"

def calculate(expression: str) -> str:
    """
    Safely evaluate a mathematical expression
    
    Args:
        expression: Mathematical expression to evaluate (e.g., "2 + 2 * 3")
        
    Returns:
        The result of the calculation
    """
    try:
        # Only allow safe mathematical operations
        import ast
        import operator
        
        # Supported operations
        ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.Mod: operator.mod,
            ast.FloorDiv: operator.floordiv,
            ast.USub: operator.neg,
        }
        
        def eval_expr(node):
            if isinstance(node, ast.Num):
                return node.n
            elif isinstance(node, ast.BinOp):
                return ops[type(node.op)](eval_expr(node.left), eval_expr(node.right))
            elif isinstance(node, ast.UnaryOp):
                return ops[type(node.op)](eval_expr(node.operand))
            else:
                raise ValueError(f"Unsupported operation: {type(node)}")
        
        tree = ast.parse(expression, mode='eval')
        result = eval_expr(tree.body)
        return f"{expression} = {result}"
        
    except Exception as e:
        return f"Error calculating: {e}"
