"""
Data Loss Prevention (DLP) – Outbound Filter.
Layer 3 of the hybrid security system.
Scans LLM responses for sensitive data and masks them.
"""
import re
from typing import Tuple, List

# (name, pattern, replacement)
DLP_PATTERNS: List[Tuple[str, re.Pattern, str]] = [
    ("db_password_exact", re.compile(
        r"SuperSecret_DB_2026", re.IGNORECASE
    ), "[SANSÜRLENDİ]"),

    ("generic_password", re.compile(
        r"(?i)(?:password|şifre|passwd|pass(?:word)?)\s*(?:is|:|\s+)?\s*['\"]?([A-Za-z0-9_\-!@#$%^&*]{6,})['\"]?",
    ), "[SANSÜRLENDİ]"),

    ("api_key", re.compile(
        r"(?i)(api[_\s]?key|access[_\s]?token|secret[_\s]?key|auth[_\s]?token)\s*[:=]\s*['\"]?([A-Za-z0-9_\-]{16,})['\"]?"
    ), "[API_KEY_SANSÜRLENDİ]"),

    ("connection_string", re.compile(
        r"(?i)(jdbc:|mongodb\+srv://|postgresql://|mysql://|redis://)\S+"
    ), "[CONNECTION_STRING_SANSÜRLENDİ]"),

    ("credit_card", re.compile(
        r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b"
    ), "[KART_NO_SANSÜRLENDİ]"),

    ("turkish_tc_no", re.compile(
        r"\b[1-9][0-9]{10}\b"
    ), "[TC_NO_SANSÜRLENDİ]"),
]


def scan_and_mask(text: str) -> Tuple[bool, str, List[str]]:
    """
    Scan LLM response for sensitive data and mask it.
    Returns (triggered, masked_text, triggered_pattern_names).
    """
    triggered = False
    triggered_names: List[str] = []
    result = text

    for name, pattern, replacement in DLP_PATTERNS:
        new_result, count = pattern.subn(replacement, result)
        if count > 0:
            triggered = True
            triggered_names.append(name)
            result = new_result

    return triggered, result, triggered_names
