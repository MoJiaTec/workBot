"""
Report data structures and formatters for code review results.
"""
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import List


class Severity(str, Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"

    @property
    def rank(self) -> int:
        return {"ERROR": 3, "WARNING": 2, "INFO": 1}[self.value]

    def __lt__(self, other: "Severity") -> bool:
        return self.rank < other.rank


@dataclass
class Issue:
    rule_id: str
    severity: Severity
    line: int
    message: str
    category: str


@dataclass
class ReviewReport:
    file_path: str
    total_lines: int
    issues: List[Issue] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def errors(self) -> List[Issue]:
        return [i for i in self.issues if i.severity == Severity.ERROR]

    @property
    def warnings(self) -> List[Issue]:
        return [i for i in self.issues if i.severity == Severity.WARNING]

    @property
    def infos(self) -> List[Issue]:
        return [i for i in self.issues if i.severity == Severity.INFO]

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0

    def filter_by_severity(self, min_severity: Severity) -> "ReviewReport":
        """Return a new report containing only issues >= min_severity."""
        filtered = [i for i in self.issues if i.severity.rank >= min_severity.rank]
        report = ReviewReport(
            file_path=self.file_path,
            total_lines=self.total_lines,
            issues=filtered,
        )
        return report

    # ------------------------------------------------------------------
    # Formatters
    # ------------------------------------------------------------------

    def summary(self) -> str:
        """Return a human-readable text report."""
        width = 60
        lines = []
        lines.append("=" * width)
        lines.append("  Code Review Report")
        lines.append(
            f"  File: {self.file_path}  |  Lines: {self.total_lines}"
            f"  |  Issues: {len(self.issues)}"
        )
        lines.append("=" * width)

        if not self.issues:
            lines.append("\n  ✅ No issues found!")
        else:
            sorted_issues = sorted(self.issues, key=lambda i: i.line)
            for issue in sorted_issues:
                severity_label = f"[{issue.severity.value:<7}]"
                lines.append(
                    f"{severity_label} Line {issue.line:>4} | {issue.rule_id:<6} | {issue.message}"
                )

        lines.append("-" * width)
        lines.append(
            f"Summary: {len(self.errors)} error(s), "
            f"{len(self.warnings)} warning(s), "
            f"{len(self.infos)} info(s)"
        )
        status = "✅ PASSED" if self.passed else "❌ FAILED (errors found)"
        lines.append(f"Overall: {status}")
        lines.append("=" * width)
        return "\n".join(lines)

    def to_json(self, indent: int = 2) -> str:
        """Return a JSON-formatted report string."""
        data = {
            "file": self.file_path,
            "total_lines": self.total_lines,
            "issues": [
                {
                    "rule_id": i.rule_id,
                    "severity": i.severity.value,
                    "line": i.line,
                    "message": i.message,
                    "category": i.category,
                }
                for i in sorted(self.issues, key=lambda x: x.line)
            ],
            "summary": {
                "error": len(self.errors),
                "warning": len(self.warnings),
                "info": len(self.infos),
                "passed": self.passed,
            },
        }
        return json.dumps(data, ensure_ascii=False, indent=indent)
