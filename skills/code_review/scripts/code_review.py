"""
CLI entry point and agent-tool adapter for the code_review skill.

CLI usage:
    python code_review.py --file path/to/code.py
    python code_review.py --code "def foo(): pass"
    python code_review.py --file path/to/code.py --format json
    python code_review.py --file path/to/code.py --min-severity WARNING

Agent tool usage (register in main.py):
    from skills.code_review.scripts.code_review import review_file, review_code
"""
import argparse
import sys
import os

# Allow running as a standalone script from any working directory
_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
_SKILL_DIR = os.path.dirname(_SCRIPTS_DIR)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_SKILL_DIR))
for _p in (_SCRIPTS_DIR, _SKILL_DIR, _PROJECT_ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from .reviewer import CodeReviewer
    from .report import Severity, ReviewReport
except ImportError:
    from reviewer import CodeReviewer          # type: ignore
    from report import Severity, ReviewReport  # type: ignore


# ---------------------------------------------------------------------------
# Agent-tool adapter functions
# ---------------------------------------------------------------------------

def review_file(file_path: str, min_severity: str = "INFO") -> str:
    """
    Perform code review on a Python file.

    Args:
        file_path: Path to the Python file to review.
        min_severity: Minimum severity level to report: ERROR / WARNING / INFO (default INFO).

    Returns:
        A formatted text report string.
    """
    try:
        sev = Severity(min_severity.upper())
    except ValueError:
        return f"Error: invalid severity '{min_severity}'. Choose from ERROR, WARNING, INFO."

    try:
        reviewer = CodeReviewer()
        report = reviewer.review_file(file_path, min_severity=sev)
        return report.summary()
    except FileNotFoundError as exc:
        return f"Error: {exc}"
    except Exception as exc:
        return f"Error during review: {exc}"


def review_code(code: str, min_severity: str = "INFO") -> str:
    """
    Perform code review on a Python code snippet.

    Args:
        code: Python source code string to review.
        min_severity: Minimum severity level to report: ERROR / WARNING / INFO (default INFO).

    Returns:
        A formatted text report string.
    """
    try:
        sev = Severity(min_severity.upper())
    except ValueError:
        return f"Error: invalid severity '{min_severity}'. Choose from ERROR, WARNING, INFO."

    try:
        reviewer = CodeReviewer()
        report = reviewer.review_code(code, min_severity=sev)
        return report.summary()
    except Exception as exc:
        return f"Error during review: {exc}"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="code_review",
        description="Automated Python code review tool",
    )
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--file", metavar="PATH",
        help="Path to the Python file to review",
    )
    source_group.add_argument(
        "--code", metavar="CODE",
        help="Python code snippet to review (inline string)",
    )
    parser.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--min-severity", choices=["ERROR", "WARNING", "INFO"], default="INFO",
        dest="min_severity",
        help="Minimum severity level to report (default: INFO)",
    )
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    min_sev = Severity(args.min_severity)
    reviewer = CodeReviewer()

    try:
        if args.file:
            report: ReviewReport = reviewer.review_file(args.file, min_severity=min_sev)
        else:
            # Unescape \n so users can pass multi-line snippets via shell
            code = args.code.replace("\\n", "\n")
            report = reviewer.review_code(code, min_severity=min_sev)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        print(report.to_json())
    else:
        print(report.summary())

    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
