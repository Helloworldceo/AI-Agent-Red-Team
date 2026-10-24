"""
Shared parsing for the daily research findings (research/findings/YYYY-MM-DD.md,
written by generate_payload.py's _write_report()). Used by both draft_post.py
(LinkedIn draft generation) and app/routes/research.py (serving findings to the
frontend) so both read the same markdown shape the same way.
"""

import re


def extract_field(text: str, label: str) -> str:
    match = re.search(rf"\*\*{label}:\*\* (.+?)\s*$", text, re.MULTILINE)
    return match.group(1).strip() if match else ""


def extract_verdict(text: str) -> tuple[bool, str]:
    match = re.search(r"^## Verdict: (.+)$", text, re.MULTILINE)
    if not match:
        return False, "info"
    line = match.group(1)
    succeeded = "⚠️" in line
    severity_match = re.search(r"\(worst severity: (\w+)\)", line)
    severity = severity_match.group(1) if severity_match else "info"
    return succeeded, severity


def extract_template(text: str) -> str:
    match = re.search(r"## The generated payload\n```\n(.*?)\n```", text, re.DOTALL)
    return match.group(1).strip() if match else ""


def parse_finding(date_str: str, text: str) -> dict:
    succeeded, severity = extract_verdict(text)
    return {
        "date": date_str,
        "category": extract_field(text, "Category"),
        "technique": extract_field(text, "Technique"),
        "hypothesis": extract_field(text, "Hypothesis"),
        "template": extract_template(text),
        "succeeded": succeeded,
        "severity": severity,
    }
