"""
Data Loss Prevention (DLP) – Outbound Filter.
Layer 3 of the hybrid security system.
Scans LLM responses for sensitive data and masks them.

v3.1 güncellemesi:
  - Kredi kartı deseni artık gerçek bir LUHN doğrulamasından geçmeden
    maskeleme yapmıyor (README'nin "Luhn-compliant" iddiasıyla kod artık
    tutarlı). Luhn'u geçmeyen rastgele 16 haneli sayılar yanlışlıkla
    sansürlenmez.
  - TC Kimlik No deseni artık resmi checksum algoritmasını uyguluyor;
    "herhangi bir 11 haneli sayı" yerine yalnızca GERÇEKTEN geçerli bir
    TC Kimlik No formatına uyan değerler maskeleniyor (FP kaynağı kapatıldı).
  - Kapsam genişletildi: JWT, bulut sağlayıcı/API anahtar formatları
    (AWS AKIA..., OpenAI sk-..., GitHub ghp_..., Slack xox*-...),
    PEM özel anahtar blokları, Türkiye IBAN formatı.
  - E-posta / telefon maskeleme artık `shield_config.json` üzerinden
    opsiyonel olarak açılabilir (varsayılan: kapalı — meşru iletişim
    bilgilerinin aşırı maskelenmesini önlemek için).
"""
import re
from typing import Callable, List, Optional, Tuple

from shield_config import CONFIG

# ── Doğrulayıcı (Checksum) Fonksiyonları ────────────────────────────────────

def luhn_valid(candidate: str) -> bool:
    """Luhn algoritmasıyla kredi kartı numarası geçerliliğini doğrular."""
    digits = [int(ch) for ch in candidate if ch.isdigit()]
    if len(digits) < 12:
        return False
    checksum = 0
    parity = len(digits) % 2
    for i, d in enumerate(digits):
        if i % 2 == parity:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0


def tc_kimlik_valid(candidate: str) -> bool:
    """Türkiye Cumhuriyeti Kimlik No resmi checksum algoritmasını doğrular."""
    digits = [int(ch) for ch in candidate if ch.isdigit()]
    if len(digits) != 11:
        return False
    if digits[0] == 0:
        return False
    odd_sum = digits[0] + digits[2] + digits[4] + digits[6] + digits[8]
    even_sum = digits[1] + digits[3] + digits[5] + digits[7]
    d10_expected = ((odd_sum * 7) - even_sum) % 10
    if d10_expected != digits[9]:
        return False
    d11_expected = sum(digits[0:10]) % 10
    if d11_expected != digits[10]:
        return False
    return True


def _mask_with_validator(
    text: str, pattern: "re.Pattern", validator: Callable[[str], bool], replacement: str
) -> Tuple[str, int]:
    """Yalnızca `validator` True dönen eşleşmeleri maskeler; diğerlerine dokunmaz."""
    count = 0

    def _repl(m: "re.Match") -> str:
        nonlocal count
        if validator(m.group(0)):
            count += 1
            return replacement
        return m.group(0)

    new_text = pattern.sub(_repl, text)
    return new_text, count


# (name, pattern, replacement, validator_or_None)
# validator=None -> koşulsuz maskeleme (desen zaten yeterince spesifik).
DLP_PATTERNS: List[Tuple[str, "re.Pattern", str, Optional[Callable]]] = [

    ("generic_password", re.compile(
        r"(?i)(?:\b(?:password|[şs][ıi]fre(?:si|sini|leri|lerini)?|parola(?:s[ıi]|s[ıi]n[ıi]|lar[ıi])?|passwd|tan[ıi]mlay[ıi]c[ıi]|pin(?:\s*kodu(?:nu)?)?|pass(?:word)?|"
        r"passwort|kennwort|mot\s+de\s+passe|contrase[nñ]a|clave|senha|пароль|пин[- ]?код)"
        r"|(?:كلمة\s+المرور|الرقم\s+السري|密码|口令|パスワード|暗証番号|비밀번호|암호))"
        r"[*_`'~]*(?:\s*(?:(?:\b(?:is|are|lautet|est|es)\b|هي|是)\s*)?(?::|=|：)[*_`'~\s]*([A-Za-z0-9_\-!@#$%^&*]{6,})[*_`'~]?"
        r"|\s+(?:\b(?:is|are|lautet|est|es)\b|هي|是)[*_`'~\s]*([A-Za-z0-9_\-!@#$%^&*]{6,})[*_`'~]?"
        r"|\s+(?:olarak\s+)?[*_`'~]*(?=[^\s'\"`*_]*\d)([A-Za-z0-9_\-!@#$%^&*]{6,})[*_`'~]?)",
    ), "[SANSÜRLENDİ]", None),

    ("api_key", re.compile(
        r"(?i)(?:\b(?:api[_\s]?(?:key|anahtar[ıi]|anahtarlar[ıi]|schl[üu]ssel|cl[eé]|clave|chave|ключ)|access[_\s]?token|secret[_\s]?(?:key|anahtar[ıi])|auth[_\s]?token)"
        r"|(?:مفتاح\s*api|api\s*密钥|api\s*キー|api\s*키))"
        r"[*_`'~]*(?:\s*(?::|=|：|\bis\b|\bare\b)[*_`'~\s]*([A-Za-z0-9_\-]{12,})[*_`'~]?"
        r"|\s+[*_`'~]*(?=[^\s'\"`*_]*\d)([A-Za-z0-9_\-]{12,})[*_`'~]?)"
    ), "[API_KEY_SANSÜRLENDİ]", None),

    ("connection_string", re.compile(
        r"(?i)(jdbc:|mongodb\+srv://|postgresql://|mysql://|redis://)\S+"
    ), "[CONNECTION_STRING_SANSÜRLENDİ]", None),

    ("jwt_token", re.compile(
        r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"
    ), "[JWT_SANSÜRLENDİ]", None),

    ("cloud_secret_key", re.compile(
        r"\b(AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{36}|xox[baprs]-[A-Za-z0-9-]{10,})\b"
    ), "[CLOUD_ANAHTARI_SANSÜRLENDİ]", None),

    ("pem_private_key", re.compile(
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----"
    ), "[ÖZEL_ANAHTAR_SANSÜRLENDİ]", None),

    ("turkish_iban", re.compile(
        r"\bTR\d{2}(?:\s?\d{4}){5}\s?\d{2}\b"
    ), "[IBAN_SANSÜRLENDİ]", None),

    ("credit_card", re.compile(
        r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b"
    ), "[KART_NO_SANSÜRLENDİ]", luhn_valid),

    ("turkish_tc_no", re.compile(
        r"\b[1-9][0-9]{10}\b"
    ), "[TC_NO_SANSÜRLENDİ]", tc_kimlik_valid),
]


def _build_optional_patterns() -> List[Tuple[str, "re.Pattern", str, Optional[Callable]]]:
    """shield_config.json bayraklarına göre opsiyonel PII desenlerini ekler."""
    extra: List[Tuple[str, "re.Pattern", str, Optional[Callable]]] = []
    if CONFIG.get("mask_generic_emails"):
        extra.append((
            "generic_email",
            re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
            "[E-POSTA_SANSÜRLENDİ]",
            None,
        ))
    if CONFIG.get("mask_generic_phones"):
        extra.append((
            "generic_phone_tr",
            re.compile(r"\b(?:\+90|0)?\s?5\d{2}[\s.-]?\d{3}[\s.-]?\d{2}[\s.-]?\d{2}\b"),
            "[TELEFON_SANSÜRLENDİ]",
            None,
        ))
    return extra


def scan_and_mask(text: str) -> Tuple[bool, str, List[str]]:
    """
    Scan LLM response for sensitive data and mask it.
    Returns (triggered, masked_text, triggered_pattern_names).
    """
    triggered = False
    triggered_names: List[str] = []
    result = text

    all_patterns = DLP_PATTERNS + _build_optional_patterns()

    for name, pattern, replacement, validator in all_patterns:
        if validator is None:
            new_result, count = pattern.subn(replacement, result)
        else:
            new_result, count = _mask_with_validator(result, pattern, validator, replacement)

        if count > 0:
            triggered = True
            triggered_names.append(name)
            result = new_result

    return triggered, result, triggered_names
