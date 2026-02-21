"""
Security rules: hardcoded secrets, dangerous calls, SQL injection patterns, etc.
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


# Patterns that suggest hardcoded credentials
_SECRET_PATTERNS = re.compile(
    r"(password|passwd|secret|api_key|apikey|token|auth_token|access_token"
    r"|private_key|client_secret)\s*=\s*['\"][^'\"]{4,}['\"]",
    re.IGNORECASE,
)

# SQL concatenation pattern
_SQL_CONCAT_PATTERN = re.compile(
    r"(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE)\b.*\+",
    re.IGNORECASE,
)


class SecurityRules:
    """Checks for common security anti-patterns."""

    def check(self, source: str, tree: ast.AST) -> List[Issue]:
        issues: List[Issue] = []
        issues.extend(self._check_hardcoded_secrets(source))
        issues.extend(self._check_dangerous_calls(tree))
        issues.extend(self._check_subprocess_shell(tree))
        issues.extend(self._check_pickle_usage(tree))
        issues.extend(self._check_sql_injection(source))
        return issues

    # ------------------------------------------------------------------
    # Source-level checks
    # ------------------------------------------------------------------

    def _check_hardcoded_secrets(self, source: str) -> List[Issue]:
        issues = []
        for lineno, line in enumerate(source.splitlines(), start=1):
            if _SECRET_PATTERNS.search(line):
                # Skip obvious placeholders
                if re.search(r"['\"](<.*?>|your_.*|xxx|placeholder|changeme)['\"]",
                             line, re.IGNORECASE):
                    continue
                issues.append(Issue(
                    rule_id="SEC001",
                    severity=Severity.ERROR,
                    line=lineno,
                    message=f"Hardcoded secret/password detected: {line.strip()[:80]}",
                    category="security",
                ))
        return issues

    def _check_sql_injection(self, source: str) -> List[Issue]:
        issues = []
        for lineno, line in enumerate(source.splitlines(), start=1):
            if _SQL_CONCAT_PATTERN.search(line):
                issues.append(Issue(
                    rule_id="SEC005",
                    severity=Severity.ERROR,
                    line=lineno,
                    message="Potential SQL injection: SQL string built with concatenation",
                    category="security",
                ))
        return issues

    # ------------------------------------------------------------------
    # AST-level checks
    # ------------------------------------------------------------------

    def _check_dangerous_calls(self, tree: ast.AST) -> List[Issue]:
        """Detect eval() and exec() calls."""
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                name = None
                if isinstance(func, ast.Name):
                    name = func.id
                elif isinstance(func, ast.Attribute):
                    name = func.attr
                if name in ("eval", "exec"):
                    issues.append(Issue(
                        rule_id="SEC002",
                        severity=Severity.ERROR,
                        line=node.lineno,
                        message=f"Use of dangerous function '{name}()' detected",
                        category="security",
                    ))
        return issues

    def _check_subprocess_shell(self, tree: ast.AST) -> List[Issue]:
        """Detect subprocess calls with shell=True."""
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                is_subprocess = False
                if isinstance(func, ast.Attribute) and func.attr in (
                    "run", "call", "Popen", "check_output", "check_call"
                ):
                    is_subprocess = True
                if is_subprocess:
                    for kw in node.keywords:
                        if kw.arg == "shell" and isinstance(kw.value, ast.Constant):
                            if kw.value.value is True:
                                issues.append(Issue(
                                    rule_id="SEC003",
                                    severity=Severity.WARNING,
                                    line=node.lineno,
                                    message="subprocess called with shell=True, prefer list arguments",
                                    category="security",
                                ))
        return issues

    def _check_pickle_usage(self, tree: ast.AST) -> List[Issue]:
        """Detect import of pickle / cPickle."""
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in ("pickle", "cPickle"):
                        issues.append(Issue(
                            rule_id="SEC004",
                            severity=Severity.WARNING,
                            line=node.lineno,
                            message=f"Use of '{alias.name}' module can be unsafe with untrusted data",
                            category="security",
                        ))
            elif isinstance(node, ast.ImportFrom):
                if node.module in ("pickle", "cPickle"):
                    issues.append(Issue(
                        rule_id="SEC004",
                        severity=Severity.WARNING,
                        line=node.lineno,
                        message=f"Use of '{node.module}' module can be unsafe with untrusted data",
                        category="security",
                    ))
        return issues
