"""
Style rules: PEP 8 compliance, naming conventions, formatting checks.
"""
import ast
import os
import re
import sys
from typing import List

_SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

try:
    from ..report import Issue, Severity
except ImportError:
    from report import Issue, Severity  # type: ignore


class StyleRules:
    """Checks for code style and formatting issues."""

    MAX_LINE_LENGTH = 79

    def check(self, source: str, tree: ast.AST) -> List[Issue]:
        issues: List[Issue] = []
        issues.extend(self._check_line_length(source))
        issues.extend(self._check_trailing_whitespace(source))
        issues.extend(self._check_mixed_indentation(source))
        issues.extend(self._check_naming_conventions(tree))
        return issues

    # ------------------------------------------------------------------
    # Line-level checks
    # ------------------------------------------------------------------

    def _check_line_length(self, source: str) -> List[Issue]:
        issues = []
        for lineno, line in enumerate(source.splitlines(), start=1):
            if len(line) > self.MAX_LINE_LENGTH:
                issues.append(Issue(
                    rule_id="S001",
                    severity=Severity.WARNING,
                    line=lineno,
                    message=f"Line too long: {len(line)} chars (max {self.MAX_LINE_LENGTH})",
                    category="style",
                ))
        return issues

    def _check_trailing_whitespace(self, source: str) -> List[Issue]:
        issues = []
        for lineno, line in enumerate(source.splitlines(), start=1):
            if line != line.rstrip():
                issues.append(Issue(
                    rule_id="S002",
                    severity=Severity.WARNING,
                    line=lineno,
                    message="Trailing whitespace detected",
                    category="style",
                ))
        return issues

    def _check_mixed_indentation(self, source: str) -> List[Issue]:
        issues = []
        for lineno, line in enumerate(source.splitlines(), start=1):
            stripped = line.lstrip()
            indent = line[: len(line) - len(stripped)]
            if " " in indent and "\t" in indent:
                issues.append(Issue(
                    rule_id="S003",
                    severity=Severity.ERROR,
                    line=lineno,
                    message="Mixed tabs and spaces in indentation",
                    category="style",
                ))
        return issues

    # ------------------------------------------------------------------
    # AST-level naming checks
    # ------------------------------------------------------------------

    def _check_naming_conventions(self, tree: ast.AST) -> List[Issue]:
        issues = []
        for node in ast.walk(tree):
            # Class names should be CamelCase
            if isinstance(node, ast.ClassDef):
                if not re.match(r"^[A-Z][a-zA-Z0-9]*$", node.name):
                    issues.append(Issue(
                        rule_id="S005",
                        severity=Severity.WARNING,
                        line=node.lineno,
                        message=f"Class name not CamelCase: '{node.name}'",
                        category="style",
                    ))
            # Function / method names should be snake_case
            elif isinstance(node, ast.FunctionDef):
                if not re.match(r"^[a-z_][a-z0-9_]*$", node.name):
                    # Allow dunder methods
                    if not (node.name.startswith("__") and node.name.endswith("__")):
                        issues.append(Issue(
                            rule_id="S004",
                            severity=Severity.WARNING,
                            line=node.lineno,
                            message=f"Function name not snake_case: '{node.name}'",
                            category="style",
                        ))
        return issues
