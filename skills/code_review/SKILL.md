---
name: code_review
version: 1.0.0
description: Automated code review for Python files and code snippets, providing structured feedback on style, complexity, security, and best practices.
author: workBot
category: code_quality
tags:
  - python
  - review
  - lint
  - security
  - best-practices
entry_point: scripts/code_review.py
tools:
  - name: review_file
    description: Perform code review on a Python file
    params:
      file_path: str  # path to the Python file
      min_severity: "INFO | WARNING | ERROR"  # default: INFO
  - name: review_code
    description: Perform code review on a Python code snippet
    params:
      code: str  # Python code string
      min_severity: "INFO | WARNING | ERROR"  # default: INFO
dependencies: []
min_python: "3.8"
---

# Code Review Skill

A skill that performs automated code review on Python files or code snippets, providing structured feedback on code quality, style, security, and best practices.

## Overview

| Field       | Value                        |
|-------------|------------------------------|
| Name        | `code_review`                |
| Version     | `1.0.0`                      |
| Language    | Python 3.8+                  |
| Category    | Code Quality                 |

## Features

- **Style Check**: PEP 8 compliance, naming conventions, formatting
- **Complexity Analysis**: Function length, cyclomatic complexity, nesting depth
- **Security Scan**: Detects common security anti-patterns (hardcoded secrets, unsafe calls, etc.)
- **Best Practices**: Docstring coverage, error handling, type hints usage
- **Summary Report**: Structured review report with severity levels (ERROR / WARNING / INFO)

## Directory Structure

```
skills/code_review/
├── SKILL.md                  # This file
├── prompts/
│   └── skill_prompt.md       # Agent trigger & usage instructions
└── scripts/
    ├── code_review.py        # Main entry point (CLI)
    ├── reviewer.py           # Core review engine
    ├── rules/
    │   ├── __init__.py
    │   ├── style_rules.py    # Style & formatting rules
    │   ├── complexity_rules.py  # Complexity rules
    │   ├── security_rules.py    # Security rules
    │   └── best_practice_rules.py  # Best practice rules
    └── report.py             # Report formatter
```

## Usage

### CLI

```bash
# Review a single file
python skills/code_review/scripts/code_review.py --file path/to/your_code.py

# Review a code snippet (inline)
python skills/code_review/scripts/code_review.py --code "def foo():\n    pass"

# Output as JSON
python skills/code_review/scripts/code_review.py --file path/to/your_code.py --format json

# Filter by severity
python skills/code_review/scripts/code_review.py --file path/to/your_code.py --min-severity WARNING
```

### As a Python Module

```python
from skills.code_review.scripts.reviewer import CodeReviewer

reviewer = CodeReviewer()
report = reviewer.review_file("path/to/your_code.py")
print(report.summary())

# Or review a code string directly
report = reviewer.review_code("""
def add(a, b):
    return a + b
""")
for issue in report.issues:
    print(f"[{issue.severity}] Line {issue.line}: {issue.message}")
```

### Register as Agent Tool

```python
from skills.code_review.scripts.code_review import review_file, review_code

agent.register_tool(Tool(
    name="review_file",
    description="Perform code review on a Python file. Parameters: file_path (str) - path to the Python file to review, min_severity (str, optional) - minimum severity level to report: ERROR/WARNING/INFO (default: INFO)",
    func=review_file
))

agent.register_tool(Tool(
    name="review_code",
    description="Perform code review on a Python code snippet. Parameters: code (str) - Python code string to review, min_severity (str, optional) - minimum severity level: ERROR/WARNING/INFO (default: INFO)",
    func=review_code
))
```

## Review Rules

### Style Rules
| Rule ID | Description | Severity |
|---------|-------------|----------|
| S001 | Line too long (> 79 characters) | WARNING |
| S002 | Trailing whitespace | WARNING |
| S003 | Mixed indentation (tabs and spaces) | ERROR |
| S004 | Function/variable name not snake_case | WARNING |
| S005 | Class name not CamelCase | WARNING |

### Complexity Rules
| Rule ID | Description | Severity |
|---------|-------------|----------|
| C001 | Function too long (> 50 lines) | WARNING |
| C002 | Too many arguments (> 5) | WARNING |
| C003 | Nesting depth too deep (> 4 levels) | WARNING |
| C004 | Too many return statements (> 3) | INFO |

### Security Rules
| Rule ID | Description | Severity |
|---------|-------------|----------|
| SEC001 | Hardcoded password or secret detected | ERROR |
| SEC002 | Use of `eval()` or `exec()` | ERROR |
| SEC003 | Use of `shell=True` in subprocess | WARNING |
| SEC004 | Use of `pickle` module | WARNING |
| SEC005 | SQL string concatenation (potential injection) | ERROR |

### Best Practice Rules
| Rule ID | Description | Severity |
|---------|-------------|----------|
| B001 | Missing docstring on public function/class | WARNING |
| B002 | Bare `except:` clause | WARNING |
| B003 | Mutable default argument | ERROR |
| B004 | Missing type hints on function | INFO |
| B005 | `print()` used instead of logging | INFO |

## Output Format

### Text Report (default)

```
============================================================
  Code Review Report
  File: example.py  |  Lines: 42  |  Issues: 5
============================================================

[ERROR]   Line  12 | SEC001 | Hardcoded password detected: password = "secret123"
[WARNING] Line  18 | S001   | Line too long: 95 chars (max 79)
[WARNING] Line  25 | B001   | Missing docstring on public function: process_data
[WARNING] Line  31 | C002   | Too many arguments: 7 (max 5)
[INFO]    Line  40 | B004   | Missing type hints on function: helper

------------------------------------------------------------
Summary: 1 error(s), 3 warning(s), 1 info(s)
Overall: ❌ FAILED (errors found)
============================================================
```

### JSON Report

```json
{
  "file": "example.py",
  "total_lines": 42,
  "issues": [
    {
      "rule_id": "SEC001",
      "severity": "ERROR",
      "line": 12,
      "message": "Hardcoded password detected: password = \"secret123\"",
      "category": "security"
    }
  ],
  "summary": {
    "error": 1,
    "warning": 3,
    "info": 1,
    "passed": false
  }
}
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0    | Review passed (no errors) |
| 1    | Review failed (errors found) |
| 2    | Script/input error |
