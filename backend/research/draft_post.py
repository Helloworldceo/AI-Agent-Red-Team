"""
Turns today's generated finding (research/findings/YYYY-MM-DD.md, written by
generate_payload.py) into a ready-to-paste LinkedIn post draft. Human stays in
the loop on purpose — no LinkedIn API is wired up, and a personal account's
voice shouldn't be automated. This just removes the "what do I even write"
step every morning.

Usage:
    python -m research.draft_post

Designed to run right after generate_payload.py, both locally and from the
daily GitHub Actions workflow (.github/workflows/daily-research.yml).
"""

import sys
from datetime import date
from pathlib import Path

from research.parsing import extract_field, extract_verdict

FINDINGS_DIR = Path(__file__).parent / "findings"
DEMO_URL = "https://helloworldceo.github.io/AI-Agent-Red-Team/"
REPO_FINDINGS_URL = "https://github.com/Helloworldceo/AI-Agent-Red-Team/tree/main/backend/research/findings"

_HASHTAGS = "#AIsecurity #LLMsecurity #PromptInjection #AgenticAI #RedTeam"


def render_post(finding_text: str) -> str:
    category = extract_field(finding_text, "Category")
    technique = extract_field(finding_text, "Technique")
    hypothesis = extract_field(finding_text, "Hypothesis")
    succeeded, severity = extract_verdict(finding_text)

    if succeeded:
        hook = (
            f"Today's red-team finding: tried a new attack on my own AI agents — "
            f"\"{technique}\" ({category}) — and it got through. ⚠️"
        )
        body = (
            f"What I was testing: {hypothesis}\n\n"
            f"Result: triggered a \"{severity}\" severity outcome against my test agent. "
            f"This is exactly the kind of agentic-AI failure mode most teams aren't "
            f"testing for before shipping a tool-calling agent to production."
        )
    else:
        hook = (
            f"Today's red-team finding: tried a new attack on my own AI agents — "
            f"\"{technique}\" ({category}) — and this one got resisted across the board. ✅"
        )
        body = (
            f"What I was testing: {hypothesis}\n\n"
            f"Not every idea works, and that's the point of actually testing instead of "
            f"assuming your agent is safe."
        )

    cta = (
        f"\nI run one of these tests every day and publish the raw results, pass or fail "
        f"— full log here: {REPO_FINDINGS_URL}\n\n"
        f"Try it on your own agent (bring your own API key, nothing is ever stored): {DEMO_URL}\n\n"
        f"Want me to red-team your agent and send you the full report? DM me.\n\n"
        f"{_HASHTAGS}"
    )

    return f"{hook}\n\n{body}\n{cta}\n"


def main() -> int:
    today = date.today().isoformat()
    finding_path = FINDINGS_DIR / f"{today}.md"
    out_path = FINDINGS_DIR / f"{today}.post.md"

    if not finding_path.exists():
        print(f"No finding for {today} at {finding_path} — nothing to draft. Run generate_payload.py first.")
        return 0

    if out_path.exists():
        print(f"Post draft for {today} already exists — skipping (one per day).")
        return 0

    post = render_post(finding_path.read_text())
    out_path.write_text(post)
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
