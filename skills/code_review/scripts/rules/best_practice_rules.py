"""
Best practice rules: docstrings, bare except, mutable defaults, type hints, print usage.
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


class BestPracticeRules:
    """Checks for Python best practice violations."""

    def check(self, source: str, tree: ast.AST) -> List[Issue]:
        issues: List[Issue] = []
        issues.extend(self._check_docstrings(tree))
        issues.extend(self._check_bare_except(tree))
        issues.extend(self._check_mutable_defaults(tree))
        issues.extend(self._check_type_hints(tree))
        issues.extend(self._check_print_usage(tree))
        return issues

    # ------------------------------------------------------------------

    def _check_docstrings(self, tree: ast.AST) -> List[Issue]:
        """Public functions and classes should have docstrings."""
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                # Skip private / dunder
                if node.name.startswith("_"):
                    continue
                has_docstring = (
                    node.body
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)
                )
                if not has_docstring:
                    kind = "class" if isinstance(node, ast.ClassDef) else "function"
                    issues.append(Issue(
                        rule_id="B001",
                        severity=Severity.WARNING,
                        line=node.lineno,
                        message=f"Missing docstring on public {kind}: '{node.name}'",
                        category="best_practice",
                    ))
        return issues

    def _check_bare_except(self, tree: ast.AST) -> List[Issue]:
        """Bare `except:` catches everything including KeyboardInterrupt."""
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    issues.append(Issue(
                        rule_id="B002",
                        severity=Severity.WARNING,
                        line=node.lineno,
                        message="Bare 'except:' clause catches all exceptions; use 'except Exception:' instead",
                        category="best_practice",
                    ))
        return issues

    def _check_mutable_defaults(self, tree: ast.AST) -> List[Issue]:
        """Mutable default arguments (list, dict, set) are a common bug source."""
        issues = []
        mutable_types = (ast.List, ast.Dict, ast.Set)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for default in node.args.defaults + node.args.kw_defaults:
                    if default is not None and isinstance(default, mutable_types):
                        issues.append(Issue(
                            rule_id="B003",
                            severity=Severity.ERROR,
                            line=node.lineno,
                            message=(
                                f"Mutable default argument in function '{node.name}'; "
                                "use None and initialise inside the function"
                            ),
                            category="best_practice",
                        ))
        return issues

    def _check_type_hints(self, tree: ast.AST) -> List[Issue]:
        """Public functions without type annotations."""
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith("_"):
                    continue
                args = node.args.args + node.args.posonlyargs + node.args.kwonlyargs
                # Exclude self / cls
                typed_args = [
                    a for a in args
                    if a.arg not in ("self", "cls")
                ]
                missing_annotations = any(a.annotation is None for a in typed_args)
                missing_return = node.returns is None
                if missing_annotations or missing_return:
                    issues.append(Issue(
                        rule_id="B004",
                        severity=Severity.INFO,
                        line=node.lineno,
                        message=f"Missing type hints on function '{node.name}'",
                        category="best_practice",
                    ))
        return issues

    def _check_print_usage(self, tree: ast.AST) -> List[Issue]:
        """print() calls should be replaced with logging in production code."""
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == "print":
                    issues.append(Issue(
                        rule_id="B005",
                        severity=Severity.INFO,
                        line=node.lineno,
                        message="Use of print(); consider using the logging module instead",
                        category="best_practice",
                    ))
        return issues
