# Codex Reviewer Guidelines

## Role
Read-only code reviewer. You do NOT implement or modify code.

## Project Context
- **HandoverPakageGenerator**: CLI + GUI tool for delivery package validation
- **Tech**: Python (click, PyYAML, pandas, openpyxl, PyQt5, segyio)
- Validates file structures against YAML-defined schemas for project handover
- Supports both CLI (click) and GUI (PyQt5) interfaces
- Handles SEG-Y, Excel, and arbitrary file type validation

## Review Checklist
1. **[BUG]** YAML schema parsing errors — missing required keys, incorrect type coercion, nested structure misread
2. **[BUG]** File path handling using string concatenation instead of pathlib/os.path — breaks on Windows vs Unix
3. **[EDGE]** Symlinks, junction points, or very long paths (>260 chars on Windows) in package directories
4. **[EDGE]** YAML files with duplicate keys silently overwriting — use safe_load and validate uniqueness
5. **[SEC]** YAML deserialization using yaml.load() without SafeLoader — allows arbitrary code execution
6. **[SEC]** User-supplied paths escaping the expected package root directory (path traversal)
7. **[PERF]** Scanning entire directory trees synchronously on the GUI thread causing freezes
8. **[TEST]** Coverage of new logic if test files exist

## Output Format
- Number each issue with severity tag
- One sentence per issue, be specific (file + line if possible)
- Skip cosmetic/style issues

## Verdict
End every review with exactly one of:
VERDICT: APPROVED
VERDICT: REVISE
