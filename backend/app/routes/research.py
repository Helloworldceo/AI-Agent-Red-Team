"""Serves the daily research findings (research/findings/YYYY-MM-DD.md) to the
frontend, so visitors can see the automated red-team research without digging
through the repo. Read-only, no LLM calls — not rate-limited like /scans."""

import re

from fastapi import APIRouter, HTTPException

from research import generate_payload
from research.parsing import parse_finding

router = APIRouter()

_DATE_STEM = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _dated_finding_files() -> list:
    findings_dir = generate_payload.FINDINGS_DIR
    if not findings_dir.exists():
        return []
    # Excludes INDEX.md, README.md, and each day's *.post.md draft — only
    # files stemmed exactly "YYYY-MM-DD" are findings.
    return sorted(
        (p for p in findings_dir.glob("*.md") if _DATE_STEM.match(p.stem)),
        key=lambda p: p.stem,
        reverse=True,
    )


@router.get("/research/findings")
def list_findings():
    return {"findings": [parse_finding(p.stem, p.read_text()) for p in _dated_finding_files()]}


@router.get("/research/findings/{finding_date}")
def get_finding(finding_date: str):
    path = generate_payload.FINDINGS_DIR / f"{finding_date}.md"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Finding not found")

    text = path.read_text()
    finding = parse_finding(finding_date, text)
    finding["raw_markdown"] = text

    post_path = generate_payload.FINDINGS_DIR / f"{finding_date}.post.md"
    finding["post_draft"] = post_path.read_text() if post_path.exists() else None

    return finding
