"""
Complexity rules: function length, argument count, nesting depth, return count.
"""
import ast
import os
import sys
from typing import List

_SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

try:
    from ..report import Issue, Severity
except ImportError:
    from report import Issue, Severity  # type: ignore


class ComplexityRules:
    """Checks for code complexity issues."""

    MAX_FUNCTION_LINES = 50
    MAX_ARGUMENTS = 5
    MAX_NESTING_DEPTH = 4
    MAX_RETURN_STATEMENTS = 3

    def check(self, source: str, tree: ast.AST) -> List[Issue]:
        issues: List[Issue] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                issues.extend(self._check_function(node))
        return issues

    def _check_function(self, node: ast.FunctionDef) -> List[Issue]:
        issues = []

        # Function length
        end_lineno = getattr(node, "end_lineno", None)
        if end_lineno is not None:
            func_lines = end_lineno - node.lineno + 1
            if func_lines > self.MAX_FUNCTION_LINES:
                issues.append(Issue(
                    rule_id="C001",
                    severity=Severity.WARNING,
                    line=node.lineno,
                    message=(
                        f"Function '{node.name}' is too long: "
                        f"{func_lines} lines (max {self.MAX_FUNCTION_LINES})"
                    ),
                    category="complexity",
                ))

        # Argument count (exclude self / cls)
        args = node.args
        all_args = args.args + args.posonlyargs + args.kwonlyargs
        # Remove self / cls for methods
        arg_names = [a.arg for a in all_args]
        if arg_names and arg_names[0] in ("self", "cls"):
            arg_names = arg_names[1:]
        if len(arg_names) > self.MAX_ARGUMENTS:
            issues.append(Issue(
                rule_id="C002",
                severity=Severity.WARNING,
                line=node.lineno,
                message=(
                    f"Function '{node.name}' has too many arguments: "
                    f"{len(arg_names)} (max {self.MAX_ARGUMENTS})"
                ),
                category="complexity",
            ))

        # Nesting depth
        max_depth = self._max_nesting_depth(node)
        if max_depth > self.MAX_NESTING_DEPTH:
            issues.append(Issue(
                rule_id="C003",
                severity=Severity.WARNING,
                line=node.lineno,
                message=(
                    f"Function '{node.name}' has deep nesting: "
                    f"depth {max_depth} (max {self.MAX_NESTING_DEPTH})"
                ),
                category="complexity",
            ))

        # Return statement count
        return_count = sum(1 for n in ast.walk(node) if isinstance(n, ast.Return))
        if return_count > self.MAX_RETURN_STATEMENTS:
            issues.append(Issue(
                rule_id="C004",
                severity=Severity.INFO,
                line=node.lineno,
                message=(
                    f"Function '{node.name}' has many return statements: "
                    f"{return_count} (max {self.MAX_RETURN_STATEMENTS})"
                ),
                category="complexity",
            ))

        return issues

    def _max_nesting_depth(self, node: ast.AST, current: int = 0) -> int:
        """Recursively compute the maximum nesting depth inside a node."""
        nesting_nodes = (
            ast.If, ast.For, ast.While, ast.With,
            ast.Try, ast.ExceptHandler,
        )
        max_depth = current
        for child in ast.iter_child_nodes(node):
            if isinstance(child, nesting_nodes):
                depth = self._max_nesting_depth(child, current + 1)
                max_depth = max(max_depth, depth)
            else:
                depth = self._max_nesting_depth(child, current)
                max_depth = max(max_depth, depth)
        return max_depth
