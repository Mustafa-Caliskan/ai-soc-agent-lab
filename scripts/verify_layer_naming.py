"""
Terminology gate: one canonical layer scheme across the manuscript.

Canonical scheme (matches Figure 1 and backend/security_layer.py):
  L0 normalisation | L1 regex/canary | L2 classifier | L3 OR-Gate arbiter
  L4 target LLM    | L5 egress DLP

Fails when
  * 'four-layer' / 'five defenses' survive anywhere,
  * L3 is used for anything except the arbiter,
  * DLP is numbered L3,
  * the DLP layer is never called L5.

Exit code 1 on any failure.
"""

import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

TARGETS = ["docs/CI_MANUSCRIPT_EN.md", "docs/CI_COVER_LETTER.md"]

FORBIDDEN = ["four-layer", "four layers", "five defenses", "5 defenses"]

ARBITER_WORDS = ("or-gate", "arbiter", "decision gate", "gate")
TARGET_LLM_WORDS = ("target llm", "target model", "llm orchestration", "execution barrier")


def context(text, start, end, pad=160):
    return text[max(0, start - pad):min(len(text), end + pad)].lower()


def main():
    failures = []

    for path in TARGETS:
        try:
            text = io.open(path, encoding="utf-8").read()
        except FileNotFoundError:
            failures.append(f"{path}: missing")
            continue

        low = text.lower()
        for token in FORBIDDEN:
            count = low.count(token)
            if count:
                failures.append(f"{path}: forbidden phrase '{token}' x{count}")

        for match in re.finditer(r"\bL3\b", text):
            window = context(text, match.start(), match.end())
            if not any(word in window for word in ARBITER_WORDS):
                snippet = text[max(0, match.start() - 60):match.end() + 60].replace("\n", " ")
                failures.append(f"{path}: L3 used outside arbiter context -> ...{snippet}...")

        for match in re.finditer(r"\bL4\b", text):
            window = context(text, match.start(), match.end())
            if not any(word in window for word in TARGET_LLM_WORDS):
                snippet = text[max(0, match.start() - 60):match.end() + 60].replace("\n", " ")
                failures.append(f"{path}: L4 used outside target-LLM context -> ...{snippet}...")

        dlg = re.compile(r"L3[^.\n]{0,60}DLP|DLP[^.\n]{0,60}L3", re.IGNORECASE)
        for match in dlg.finditer(text):
            failures.append(f"{path}: DLP still numbered L3 -> ...{match.group(0)[:80]}...")

        if path.endswith("CI_MANUSCRIPT_EN.md"):
            if not re.search(r"\bL5\b", text):
                failures.append(f"{path}: egress DLP is never labelled L5")
            if not re.search(r"\bL0\b", text):
                failures.append(f"{path}: normalisation is never labelled L0")

    if failures:
        print(f"=== {len(failures)} LAYER-NAMING FAILURE(S) ===")
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("PASS: single canonical layer scheme (L0-L5), no retired phrasing.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
