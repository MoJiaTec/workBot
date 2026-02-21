"""
Core review engine: parses source code and runs all rule sets.
"""
import ast
import os
import sys
from typing import Optional

# Support both standalone execution and package import
_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)

try:
    from .report import ReviewReport, Severity
    from .rules import StyleRules, ComplexityRules, SecurityRules, BestPracticeRules
except ImportError:
    from report import ReviewReport, Severity  # type: ignore
    from rules import StyleRules, ComplexityRules, SecurityRules, BestPracticeRules  # type: ignore


class CodeReviewer:
    """
    Orchestrates all rule sets and produces a ReviewReport.

    Usage::

        reviewer = CodeReviewer()
        report = reviewer.review_file("path/to/code.py")
        print(report.summary())
    """

    def __init__(self) -> None:
        self._rules = [
            StyleRules(),
            ComplexityRules(),
            SecurityRules(),
            BestPracticeRules(),
        ]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def review_file(
        self,
        file_path: str,
        min_severity: Optional[Severity] = None,
    ) -> ReviewReport:
        """
        Review a Python source file.

        Args:
            file_path: Path to the .py file.
            min_severity: If provided, only issues >= this severity are included.

        Returns:
            A ReviewReport instance.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as fh:
                source = fh.read()
        except OSError as exc:
            raise FileNotFoundError(f"Cannot read file '{file_path}': {exc}") from exc

        return self._run(source, file_path, min_severity)

    def review_code(
        self,
        code: str,
        label: str = "<snippet>",
        min_severity: Optional[Severity] = None,
    ) -> ReviewReport:
        """
        Review a Python code string.

        Args:
            code: Python source code as a string.
            label: Display name used in the report (default: '<snippet>').
            min_severity: If provided, only issues >= this severity are included.

        Returns:
            A ReviewReport instance.
        """
        return self._run(code, label, min_severity)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _run(
        self,
        source: str,
        label: str,
        min_severity: Optional[Severity],
    ) -> ReviewReport:
        total_lines = len(source.splitlines())

        # Parse AST
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            try:
                from .report import Issue
            except ImportError:
                from report import Issue  # type: ignore
            report = ReviewReport(file_path=label, total_lines=total_lines)
            report.issues.append(Issue(
                rule_id="SYNTAX",
                severity=Severity.ERROR,
                line=exc.lineno or 0,
                message=f"Syntax error: {exc.msg}",
                category="syntax",
            ))
            return report

        report = ReviewReport(file_path=label, total_lines=total_lines)

        for rule_set in self._rules:
            issues = rule_set.check(source, tree)
            report.issues.extend(issues)

        if min_severity is not None:
            report = report.filter_by_severity(min_severity)

        return report
