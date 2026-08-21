"""
Regex-based rule engine for detecting known attack patterns.
Layer 1 of the hybrid security system.
"""
import re
from typing import List, Tuple

# Each entry: (pattern_name, compiled_pattern)
ATTACK_PATTERNS: List[Tuple[str, re.Pattern]] = [

    # ── PROMPT INJECTION ────────────────────────────────────────────────────
    ("ignore_previous_instructions", re.compile(
        r"ignore\s+(previous|all|prior|above|the\s+above)\s+(instructions?|prompts?|context|rules?|directives?)",
        re.IGNORECASE
    )),
    ("disregard_instructions", re.compile(
        r"disregard\s+(previous|all|prior|above)?\s*(instructions?|prompts?|rules?|context|directives?)",
        re.IGNORECASE
    )),
    ("forget_context", re.compile(
        r"forget\s+(everything|all|your\s+(previous|prior|above)|the\s+context|your\s+instructions?)",
        re.IGNORECASE
    )),
    ("system_override", re.compile(
        r"(system\s+override|override\s+(system|instructions?|prompt|context)|new\s+instructions?\s*:)",
        re.IGNORECASE
    )),
    ("your_new_task", re.compile(
        r"(your\s+(new|real|true|actual)\s+task\s+is|your\s+new\s+(role|purpose|goal)\s+is)",
        re.IGNORECASE
    )),
    ("act_as_no_restrictions", re.compile(
        r"(pretend|imagine|assume|act)\s+(you\s+)?(have\s+no|don'?t\s+have|without)\s+(restrictions?|limitations?|filters?|guidelines?)",
        re.IGNORECASE
    )),
    ("html_inject_comment", re.compile(
        r"<!--\s*(inject|override|system|prompt|instruction|cmd|exec)",
        re.IGNORECASE
    )),
    ("xml_inject_tag", re.compile(
        r"<\s*(INST|instruction|system|prompt|override)\s*>",
        re.IGNORECASE
    )),

    # ── JAILBREAK ───────────────────────────────────────────────────────────
    ("jailbreak_mode", re.compile(
        r"(jailbreak(\s+mode)?|developer\s+mode|unrestricted\s+mode|god\s+mode)",
        re.IGNORECASE
    )),
    ("dan_jailbreak", re.compile(
        r"\b(DAN|DUDE|STAN|AIM|KEVIN|UCAR|JAILBREAK)\b",
    )),
    ("evil_alter_ego", re.compile(
        r"(evil\s+(twin|alter\s+ego|version)|dark\s+mode\s+ai|unfiltered\s+(ai|version|mode))",
        re.IGNORECASE
    )),
    ("no_ethical_constraints", re.compile(
        r"(without\s+(ethical|moral|safety)\s+(constraints?|filters?|guidelines?|restrictions?))",
        re.IGNORECASE
    )),
    ("base64_payload", re.compile(
        r"(decode\s+this|base64\s+decode|atob\s*\().*[A-Za-z0-9+/]{20,}={0,2}",
        re.IGNORECASE
    )),
    ("token_smuggling", re.compile(
        r"(</?\s*(system|inst|instruction|prompt)\s*>)",
        re.IGNORECASE
    )),
    ("hypothetically_harmful", re.compile(
        r"hypothetically\s+(speaking|if|assume|say)\s+.{0,60}(hack|attack|exploit|bypass|override|inject)",
        re.IGNORECASE
    )),

    # ── DATA EXFILTRATION / LEAKAGE ─────────────────────────────────────────
    ("ask_for_password", re.compile(
        r"(what('?s|\s+is)\s+(the|your|a)?\s*(password|şifre|passwd|pass|credentials?|secret|api[\s_]?key))",
        re.IGNORECASE
    )),
    ("reveal_system_prompt", re.compile(
        r"(show|reveal|tell|give|print|output|display|repeat|leak|share|expose)\s+(me\s+)?(your|the)?\s*(system\s*prompt|instructions?|context|secrets?|credentials?|initial\s+prompt|original\s+prompt)",
        re.IGNORECASE
    )),
    ("what_were_you_told", re.compile(
        r"(what\s+(were|was|are)\s+you\s+(told|instructed|programmed|trained|configured|given))",
        re.IGNORECASE
    )),
    ("turkish_password_request", re.compile(
        r"(şifre(yi|nizi|sini|si|ni)?\s*(ver|söyle|yaz|paylaş|göster|açıkla))",
        re.IGNORECASE
    )),
    ("exfil_via_url", re.compile(
        r"(fetch|request|get|send|post)\s+https?://[^\s]+\?[^\s]*(password|token|secret|key|cred)",
        re.IGNORECASE
    )),
    ("script_injection", re.compile(
        r"<script\b[^>]*>",
        re.IGNORECASE
    )),
]


def scan_text(text: str) -> Tuple[bool, List[str]]:
    """
    Scan text against all known attack patterns.
    Returns (triggered: bool, matched_pattern_names: List[str])
    """
    matched: List[str] = []
    for name, pattern in ATTACK_PATTERNS:
        if pattern.search(text):
            matched.append(name)
    return (len(matched) > 0, matched)
