"""
Regex-based rule engine for detecting known attack patterns.
Layer 1 of the hybrid security system.

Her kural artık (isim, derlenmiş_desen, önem_derecesi) üçlüsü olarak
tanımlanır. `scan_text`, tetiklenen kuralların İÇİNDEKİ EN YÜKSEK önem
derecesini (0-100) döndürür; bu skor `security_layer.py`'deki Bileşik
Risk Formülüne (Composite Risk Score) girdi olarak kullanılır.

v3.1 güncellemesi: Önceden yalnızca ~1 Türkçe kural vardı (proje "çift
dilli TR/EN" iddiasında olmasına rağmen). Bu sürümde Türkçe'ye özgü
doğrudan talimat iptali, yetki/rol simülasyonu, DAN/jailbreak varyantları,
genişletilmiş gizli bilgi talebi ve sistem promptu ifşa kalıpları eklendi.
"""
import re
from typing import List, Tuple

# Her kayıt: (pattern_name, compiled_pattern, severity_0_100)
ATTACK_PATTERNS: List[Tuple[str, "re.Pattern", int]] = [

    # ── PROMPT INJECTION (EN) ───────────────────────────────────────────────
    ("ignore_previous_instructions", re.compile(
        r"ignore\s+(?:all\s+)?(?:previous|prior|above|the\s+above|all)?\s*(?:of\s+the\s+above\s+)?(instructions?|prompts?|context|rules?|directives?)",
        re.IGNORECASE
    ), 70),
    ("disregard_instructions", re.compile(
        r"disregard\s+(?:all\s+)?(?:previous|all|prior|above|the\s+above)?\s*(instructions?|prompts?|rules?|context|directives?)",
        re.IGNORECASE
    ), 70),
    ("forget_context", re.compile(
        r"forget\s+(everything|all|your\s+(previous|prior|above)|the\s+context|your\s+instructions?)",
        re.IGNORECASE
    ), 65),
    ("system_override", re.compile(
        r"(system\s+override|override\s+(system|instructions?|prompt|context)|new\s+instructions?\s*:)",
        re.IGNORECASE
    ), 80),
    ("your_new_task", re.compile(
        r"(your\s+(new|real|true|actual)\s+task\s+is|your\s+new\s+(role|purpose|goal)\s+is)",
        re.IGNORECASE
    ), 60),
    ("act_as_no_restrictions", re.compile(
        r"(pretend|imagine|assume|act)\s+(you\s+)?(have\s+no|don'?t\s+have|without)\s+(restrictions?|limitations?|filters?|guidelines?)",
        re.IGNORECASE
    ), 65),
    ("html_inject_comment", re.compile(
        r"<!--\s*(inject|override|system|prompt|instruction|cmd|exec)",
        re.IGNORECASE
    ), 75),
    ("xml_inject_tag", re.compile(
        r"<\s*(INST|instruction|system|prompt|override)\s*>",
        re.IGNORECASE
    ), 70),

    # ── JAILBREAK (EN) ──────────────────────────────────────────────────────
    ("jailbreak_mode", re.compile(
        r"(jailbreak(\s+mode)?|developer\s+mode|unrestricted\s+mode|god\s+mode)",
        re.IGNORECASE
    ), 70),
    ("dan_jailbreak", re.compile(
        r"\b(DAN|DUDE|STAN|AIM|KEVIN|UCAR|JAILBREAK)\b",
    ), 65),
    ("evil_alter_ego", re.compile(
        r"(evil\s+(twin|alter\s+ego|version)|dark\s+mode\s+ai|unfiltered\s+(ai|version|mode))",
        re.IGNORECASE
    ), 70),
    ("no_ethical_constraints", re.compile(
        r"(without\s+(ethical|moral|safety)\s+(constraints?|filters?|guidelines?|restrictions?))",
        re.IGNORECASE
    ), 65),
    ("base64_payload", re.compile(
        r"(decode\s+this|base64\s+decode|atob\s*\().*[A-Za-z0-9+/]{20,}={0,2}",
        re.IGNORECASE
    ), 60),
    ("token_smuggling", re.compile(
        r"(</?\s*(system|inst|instruction|prompt)\s*>)",
        re.IGNORECASE
    ), 70),
    ("hypothetically_harmful", re.compile(
        r"hypothetically\s+(speaking|if|assume|say)\s+.{0,60}(hack|attack|exploit|bypass|override|inject)",
        re.IGNORECASE
    ), 55),

    # ── DATA EXFILTRATION / LEAKAGE (EN) ────────────────────────────────────
    ("ask_for_password", re.compile(
        r"(what('?s|\s+is)\s+(the|your|a)?\s*(password|şifre|passwd|pass|credentials?|secret|api[\s_]?key))",
        re.IGNORECASE
    ), 60),
    ("reveal_system_prompt", re.compile(
        r"(show|reveal|tell|give|print|output|display|repeat|leak|share|expose)\s+(me\s+)?(your|the)?\s*(system\s*prompt|instructions?|context|secrets?|credentials?|initial\s+prompt|original\s+prompt)",
        re.IGNORECASE
    ), 80),
    ("what_were_you_told", re.compile(
        r"(what\s+(were|was|are)\s+you\s+(told|instructed|programmed|trained|configured|given))",
        re.IGNORECASE
    ), 55),
    ("exfil_via_url", re.compile(
        r"(fetch|request|get|send|post)\s+https?://[^\s]+\?[^\s]*(password|token|secret|key|cred)",
        re.IGNORECASE
    ), 85),
    ("script_injection", re.compile(
        r"<script\b[^>]*>",
        re.IGNORECASE
    ), 75),

    # ── DOĞRUDAN TALİMAT İPTALİ (TR) ────────────────────────────────────────
    ("tr_ignore_instructions", re.compile(
        r"(önceki|tüm|yukarıdaki|verilen)\s+(talimatlar[ıi]n?[ıi]?|yönergeleri|kurallar[ıi]n?[ıi]?|direktifleri|emirleri)\s*"
        r"(hepsini\s*)?(yok\s*say|unut|iptal\s*et|görmezden\s*gel|geçersiz\s*k[ıi]l|salla)",
        re.IGNORECASE
    ), 75),
    ("tr_forget_role", re.compile(
        r"(sana\s+verilen\s+rolleri?\s+(unut|hafızandan\s+sil)|rolünü\s+unut|hafızandan\s+sil)",
        re.IGNORECASE
    ), 65),

    # ── SİSTEM OVERRIDE / YETKİ SİMÜLASYONU (TR) ────────────────────────────
    ("tr_system_override", re.compile(
        r"(sistem\s*(geçersiz\s*k[ıi]lma|override)|güvenlik\s*(duvar[ıi]n[ıi]|filtrelerini|katmanlar[ıi]n[ıi])\s*(devre\s*d[ıi]ş[ıi]\s*b[ıi]rak|kapat|aş))",
        re.IGNORECASE
    ), 80),
    ("tr_authority_roleplay", re.compile(
        r"(ben\s+(bir\s+)?(sistem\s*yöneticisi|denetçi|güvenlik\s*araşt[ıi]rmac[ıi]s[ıi]|yetkiliy?im)|"
        r"acil\s*durum\s*(protokolü|yetkisi|onay[ıi])\s*(onayland[ıi]|devrede|aktif)|"
        r"yönetici\s*onay[ıi]\s*(al[ıi]nd[ıi]|onayland[ıi])|override\s*(kodu|anahtar[ıi]))",
        re.IGNORECASE
    ), 55),
    ("tr_hard_override_phrase", re.compile(
        r"(bütün|tüm)\s+(güvenlik|etik)\s*(k[ıi]s[ıi]tlama(lar[ıi])?|filtreleri|kurallar[ıi]n[ıi])\s*"
        r"(devre\s*d[ıi]ş[ıi]\s*b[ıi]rak|kald[ıi]r|yok\s*say)",
        re.IGNORECASE
    ), 75),

    # ── DAN / JAILBREAK VARYANTLARI (TR) ────────────────────────────────────
    ("tr_dan_jailbreak", re.compile(
        r"(sen\s+art[ıi]k\s+(k[ıi]s[ıi]tlamas[ıi]z|serbest|kurals[ıi]z|özgür|DAN)|"
        r"kurallar[ıi]n\s+(yok|geçersiz)|k[ıi]s[ıi]tlamalar[ıi]n[ıi]\s+kald[ıi]r)",
        re.IGNORECASE
    ), 70),

    # ── SİSTEM PROMPTU İFŞA TALEBİ (TR) ─────────────────────────────────────
    ("tr_reveal_prompt", re.compile(
        r"(sistem\s*prompt(u|unu)?|ilk\s*talimat[ıi]n[ıi]|gizli\s*(direktifleri|kurallar[ıi]n[ıi]|talimatlar[ıi]n[ıi])|"
        r"baş[ıi]ndaki\s*sistem\s*metni|arka\s*plandaki\s*gizli\s*promptu)\s*(.{0,20})"
        r"(yaz|göster|yazd[ıi]r|ekrana\s*bas|paylaş|aç[ıi]kla|dök|aynen\s*(yaz|kopyala))",
        re.IGNORECASE
    ), 80),

    # ── GİZLİ BİLGİ / ŞİFRE TALEBİ (TR — genişletilmiş) ─────────────────────
    ("turkish_password_request", re.compile(
        r"([şs][ıi]fre(yi|nizi|sini|si|ni)?\s*(ver|söyle|yaz|paylaş|göster|aç[ıi]kla))",
        re.IGNORECASE
    ), 60),
    ("tr_secret_request_expanded", re.compile(
        r"(parola(y[ıi]|n[ıi]z[ıi]|s[ıi]n[ıi]|s[ıi]|n[ıi]|lar[ıi]|lar[ıi]n[ıi])?|pin\s*kodu(nu)?|api\s*anahtar([ıi]|ın[ıi]|lar[ıi]|lar[ıi]n[ıi])?|"
        r"gizli\s*anahtar([ıi]|ın[ıi])?|veritaban[ıi]\s*[şs][ıi]fre(si|sini|leri|lerini)?)\s*.{0,25}"
        r"(ver|söyle|yaz|paylaş|göster|aç[ıi]kla|aktar|dök|teslim\s*et|raporla|listele)",
        re.IGNORECASE
    ), 65),
]


def scan_text(text: str) -> Tuple[bool, List[str], int]:
    """
    Scan text against all known attack patterns.
    Returns (triggered: bool, matched_pattern_names: List[str], max_severity_score: int)
    """
    matched: List[str] = []
    max_score = 0
    for name, pattern, severity in ATTACK_PATTERNS:
        if pattern.search(text):
            matched.append(name)
            if severity > max_score:
                max_score = severity
    return (len(matched) > 0, matched, max_score)
