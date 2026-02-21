# Code Review Skill — Agent Instructions

## When to Use This Skill

Activate this skill when the user requests any of the following:
- Review, check, or analyze Python code quality
- Find bugs, issues, or problems in Python code
- Check code for security vulnerabilities
- Verify PEP 8 / style compliance
- Audit code before committing or merging

**Trigger keywords**: `review`, `check code`, `code quality`, `lint`, `audit`, `security scan`, `find issues`

---

## Available Tools

### `review_file`
Review a Python source file on disk.

```
TOOL_CALL: {"tool": "review_file", "params": {"file_path": "<path>", "min_severity": "INFO"}}
```

| Parameter    | Type   | Required | Description                              |
|--------------|--------|----------|------------------------------------------|
| file_path    | str    | ✅       | Absolute or relative path to `.py` file  |
| min_severity | str    | ❌       | Filter level: `INFO` / `WARNING` / `ERROR` (default: `INFO`) |

---

### `review_code`
Review a Python code snippet provided as a string.

```
TOOL_CALL: {"tool": "review_code", "params": {"code": "<python code>", "min_severity": "INFO"}}
```

| Parameter    | Type   | Required | Description                              |
|--------------|--------|----------|------------------------------------------|
| code         | str    | ✅       | Python source code string to review      |
| min_severity | str    | ❌       | Filter level: `INFO` / `WARNING` / `ERROR` (default: `INFO`) |

---

## Decision Logic

```
User wants to review code?
├── Has a file path → use review_file
├── Has inline code → use review_code
└── Has both → prefer review_file, use review_code as fallback
```

---

## Interpreting Results

After calling a review tool, interpret the output as follows:

| Result        | Meaning                                      | Response to User                        |
|---------------|----------------------------------------------|-----------------------------------------|
| `passed: true`  | No errors found                            | Confirm code passes review, list warnings/info if any |
| `passed: false` | One or more ERRORs found                   | Highlight errors first, then warnings   |
| Empty issues  | Code is clean                                | Tell user the code looks good           |

**Severity priority when summarizing**: `ERROR` > `WARNING` > `INFO`

---

## Example Interactions

**Example 1: Review a file**
```
User: "Please review my code in src/utils.py"
→ TOOL_CALL: {"tool": "review_file", "params": {"file_path": "src/utils.py"}}
```

**Example 2: Review inline code**
```
User: "Check this code: def foo(x=[]):  pass"
→ TOOL_CALL: {"tool": "review_code", "params": {"code": "def foo(x=[]):\n    pass"}}
```

**Example 3: Security-only review**
```
User: "Scan auth.py for security issues only"
→ TOOL_CALL: {"tool": "review_file", "params": {"file_path": "auth.py", "min_severity": "ERROR"}}
```

---

## Output Format Reference

The tool returns a structured report. Key fields:

```json
{
  "file": "example.py",
  "total_lines": 42,
  "issues": [
    {
      "rule_id": "SEC001",
      "severity": "ERROR",
      "line": 12,
      "message": "Hardcoded password detected",
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
