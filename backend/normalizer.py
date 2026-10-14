"""
CyberTech Neural Shield - Layer 0: Normalizasyon ve Steganografi Motoru.

Önceki sürümde (security_layer.py) steganografi teknikleri yalnızca TESPİT
ediliyordu (bir uyarı üretiliyordu) ama metin hiçbir zaman TEMİZLENMİYORDU.
Bu modül, mimaride vaat edilen "Layer 0: Normalizasyon" katmanını gerçekten
uygular:

  1. NFKC Unicode normalizasyonu (tam genişlik / birleşik karakterler).
  2. Zero-width (görünmez) karakter temizliği — ANCAK bilinen/meşru emoji
     ZWJ dizilerini (aile emojisi, gökkuşağı bayrağı, ten tonu vb.) önce
     ayırt edip dokunmadan bırakır; yalnızca bu dizilerin DIŞINDA kalan
     görünmez karakterleri "şüpheli" sayar. (Bkz. P0 madde A2 — eski kod
     her zero-width karakterini şüpheli sayıp meşru emoji içeren masum
     mesajları (örn. 🏳️‍🌈) yanlışlıkla engelliyordu.)
  3. Homoglyph (Kiril/Yunan - Latin benzer harf) tespiti VE katlama
     (regex/ML taraması için okunabilir Latin karşılığına çevirme).
  4. Unicode Tag (U+E0000-U+E007F) gizli ASCII mürekkebinin deşifre edilmesi.
  5. Variation Selector steganografisinin, yaygın tekli emoji sunum
     seçicisini (U+FE0F) yanlış alarm olarak işaretlemeyecek şekilde
     (yalnızca ardışık VS zincirleri veya E0100-E01EF takviye bloğu)
     tespiti.
  6. Base64 (çift kodlamaya kadar), Hex, ROT13 ve ters-yazma (reverse)
     çözücüleri.

Bu modülün ürettiği "clean_text" / "extended_text", Layer 1 (regex) ve
Layer 2 (ML) taramasına gönderilen GERÇEK metindir.
"""
from __future__ import annotations

import base64
import codecs
import html
import json
import re
import unicodedata
import urllib.parse
from typing import Dict, List, Tuple, Any

# ── Zero-Width / Görünmez ve Format Kontrol Karakterleri ──────────────────
ZERO_WIDTH_CHARS = {
    "\u200b",  # ZERO WIDTH SPACE
    "\u200c",  # ZERO WIDTH NON-JOINER
    "\u200d",  # ZERO WIDTH JOINER
    "\ufeff",  # ZERO WIDTH NO-BREAK SPACE / BOM
    "\u2060",  # WORD JOINER
    "\u00ad",  # SOFT HYPHEN (SHY - gizli kelime bölücü)
    "\u061c",  # ARABIC LETTER MARK
    "\u200e",  # LEFT-TO-RIGHT MARK
    "\u200f",  # RIGHT-TO-LEFT MARK
    "\u202a",  # LEFT-TO-RIGHT EMBEDDING
    "\u202b",  # RIGHT-TO-LEFT EMBEDDING
    "\u202c",  # POP DIRECTIONAL FORMATTING
    "\u202d",  # LEFT-TO-RIGHT OVERRIDE
    "\u202e",  # RIGHT-TO-LEFT OVERRIDE
    "\u2061",  # FUNCTION APPLICATION (görünmez)
    "\u2062",  # INVISIBLE TIMES
    "\u2063",  # INVISIBLE SEPARATOR
    "\u2064",  # INVISIBLE PLUS
    "\u2066",  # LEFT-TO-RIGHT ISOLATE
    "\u2067",  # RIGHT-TO-LEFT ISOLATE
    "\u2068",  # FIRST STRONG ISOLATE
    "\u2069",  # POP DIRECTIONAL ISOLATE
    "\x00",    # NULL BYTE
}

# ── Bilinen/Meşru Emoji ZWJ Dizisi Deseni ───────────────────────────────────
# Kapsadığı örnekler: aile emojileri (👨‍👩‍👧‍👦), gökkuşağı bayrağı (🏳️‍🌈),
# ten tonu modifikatörlü emojiler (👍🏽), meslek+cinsiyet kombinasyonları vb.
_EMOJI_BASE_RANGES = (
    "\U0001F000-\U0001FFFF"  # Çoğu emoji bloğu
    "\u2600-\u27BF"           # Çeşitli semboller / dingbat
    "\u2300-\u23FF"           # Çeşitli teknik semboller (⌚ ⏰ vb.)
    "\u2B00-\u2BFF"           # Oklar / yıldızlar (⭐ ➡ vb.)
)
_SKIN_TONE = "\U0001F3FB-\U0001F3FF"
_VS = "\uFE0E\uFE0F"
EMOJI_SEQUENCE_RE = re.compile(
    rf"[{_EMOJI_BASE_RANGES}](?:[{_VS}]|[{_SKIN_TONE}])*"
    rf"(?:\u200D[{_EMOJI_BASE_RANGES}](?:[{_VS}]|[{_SKIN_TONE}])*)*"
)

# ── Homoglyph (Kiril/Yunan - Latin) Tablosu ─────────────────────────────────
HOMOGLYPH_TO_LATIN: Dict[str, str] = {
    # Kiril küçük harfler
    "\u0430": "a", "\u0435": "e", "\u043e": "o", "\u0440": "p", "\u0441": "c",
    "\u0443": "y", "\u0445": "x", "\u0456": "i", "\u0458": "j", "\u0455": "s",
    "\u0432": "v", "\u043a": "k", "\u043c": "m",
    # Kiril büyük harfler
    "\u0410": "A", "\u0415": "E", "\u041e": "O", "\u0420": "P", "\u0421": "C",
    "\u0423": "Y", "\u0425": "X", "\u0412": "B", "\u041d": "H", "\u0422": "T",
    "\u041a": "K", "\u041c": "M", "\u0406": "I",
    # Yunan benzer karakterler
    "\u03b1": "a", "\u03bf": "o", "\u03c1": "p", "\u03c5": "u", "\u03c7": "x",
    "\u03bd": "v", "\u03ba": "k",
    "\u0391": "A", "\u0392": "B", "\u0395": "E", "\u0397": "H", "\u0399": "I",
    "\u039a": "K", "\u039c": "M", "\u039d": "N", "\u039f": "O", "\u03a1": "P",
    "\u03a4": "T", "\u03a7": "X", "\u03a5": "Y",
}
_CONFUSABLE_SET = set(HOMOGLYPH_TO_LATIN.keys())



def nfkc_normalize(text: str) -> str:
    """Tam genişlik / birleşik Unicode karakterleri kanonik forma indirger."""
    if not text:
        return text
    return unicodedata.normalize("NFKC", text)


def strip_zero_width(text: str) -> Tuple[str, bool, int]:
    """
    Görünmez karakterleri metinden temizler.
    Döndürür: (temiz_metin, şüpheli_mi, şüpheli_karakter_sayısı)

    'şüpheli' yalnızca, bilinen emoji ZWJ dizilerinin DIŞINDA kalan
    zero-width karakterler bulunduğunda True olur. Böylece aile emojisi /
    gökkuşağı bayrağı gibi tamamen meşru mesajlar yanlış alarm vermez.
    """
    if not text:
        return text, False, 0

    text_without_emoji = EMOJI_SEQUENCE_RE.sub("", text)
    suspicious_count = sum(1 for c in text_without_emoji if c in ZERO_WIDTH_CHARS)

    clean = "".join(c for c in text if c not in ZERO_WIDTH_CHARS)
    return clean, suspicious_count > 0, suspicious_count


def detect_unicode_tags(text: str) -> bool:
    """Unicode Tag bloğunda (U+E0000 - U+E007F) gizli ASCII mürekkebi var mı?"""
    return any("\U000E0000" <= c <= "\U000E007F" for c in text)


def decode_unicode_tags(text: str) -> List[str]:
    """Unicode Tag karakterlerini gerçek ASCII metnine deşifre eder."""
    decoded: List[str] = []
    current: List[str] = []
    for c in text:
        cp = ord(c)
        if 0xE0000 <= cp <= 0xE007F:
            current.append(chr(cp - 0xE0000))
        else:
            if current:
                s = "".join(current).strip()
                if s:
                    decoded.append(s)
                current = []
    if current:
        s = "".join(current).strip()
        if s:
            decoded.append(s)
    return decoded


def detect_variation_selectors(text: str) -> bool:
    """
    Emoji / variation-selector steganografisini tespit eder.

    - U+E0100-U+E01EF (Variation Selectors Supplement) bloğu normal yazımda
      pratik olarak hiç kullanılmaz; TEK bir karakter dahi şüphelidir.
    - U+FE00-U+FE0F (temel 16 seçici) ise her emojide YAYGIN ve MEŞRU olarak
      TEK başına kullanılır (emoji sunum seçicisi, ör. ❤️). Steganografi
      tekniği aynı taşıyıcıya ARDIŞIK çok sayıda seçici ekler; bu yüzden
      yalnızca 2+ ardışık temel seçici şüpheli sayılır.
    """
    if any(0xE0100 <= ord(c) <= 0xE01EF for c in text):
        return True
    run = 0
    for c in text:
        if 0xFE00 <= ord(c) <= 0xFE0F:
            run += 1
            if run >= 2:
                return True
        else:
            run = 0
    return False


def detect_homoglyphs(text: str) -> bool:
    """
    Kiril/Yunan ve Latin karakterlerin karıştığını tespit eder.
    Ayrıca tamamı konfüze karakterlerden oluşan yapay kelimeleri de yakalar.
    """
    has_any_latin = any("a" <= c.lower() <= "z" for c in text) or any(c in "çğıöşüÇĞİÖŞÜ" for c in text)
    for word in text.split():
        confusable_count = sum(1 for c in word if c in _CONFUSABLE_SET)
        has_latin_word = any("a" <= c.lower() <= "z" for c in word)
        if confusable_count > 0 and (has_latin_word or has_any_latin):
            return True
        if len(word) >= 2 and confusable_count == len(word):
            return True
    return False


def fold_homoglyphs(text: str) -> str:
    """
    Konfüze (Kiril/Yunan benzeri) karakterleri Latin karşılıklarına katlar.
    """
    has_any_latin = any("a" <= c.lower() <= "z" for c in text) or any(c in "çğıöşüÇĞİÖŞÜ" for c in text)
    words = text.split(" ")
    out_words = []
    for word in words:
        confusable_count = sum(1 for c in word if c in _CONFUSABLE_SET)
        has_latin_word = any("a" <= c.lower() <= "z" for c in word)
        if (confusable_count > 0 and (has_latin_word or has_any_latin)) or (len(word) >= 2 and confusable_count == len(word)):
            word = "".join(HOMOGLYPH_TO_LATIN.get(c, c) for c in word)
        out_words.append(word)
    return " ".join(out_words)


# ── Çoklu Kodlama ve Gizleme Çözücüleri ─────────────────────────────────────
# NOT: Sondaki '\b' KASITLI OLARAK kullanılmıyor — Base64 dolgu karakterleri
# ('=') kelime-dışı (\W) olduğu için, dizge "==" ile bitince \b geri izleme
# (backtracking) yaparak dolguyu REGEX EŞLEŞMESİNDEN DÜŞÜRÜYOR, bu da
# `base64.b64decode()` çağrısında "Incorrect padding" hatasına ve (geniş
# except bloğu yüzünden) payload'ın SESSİZCE kaçırılmasına yol açıyordu.
# `(?!\w)` negatif lookahead ile aynı sınır güvenliği, dolguyu kırpmadan
# sağlanır. Ayrıca decode öncesi eksik dolgu otomatik tamamlanır (çifte güvence).
_B64_RE = re.compile(r"\b[A-Za-z0-9+/]{16,}={0,2}(?!\w)")
_HEX_RE = re.compile(r"\b(?:[0-9A-Fa-f]{2}){6,}\b")
_URL_PCT_RE = re.compile(r"(?:%[0-9A-Fa-f]{2}){3,}")
_INTERLEAVED_RE = re.compile(r"\b(?:[a-zA-ZçğıöşüÇĞİÖŞÜ][.\-_*~]){3,}[a-zA-ZçğıöşüÇĞİÖŞÜ]\b")


def extract_and_decode_base64(text: str, _depth: int = 0) -> List[str]:
    """Base64 dizgelerini bulur ve çözer (çift kodlamayı yakalamak için 1 seviye recursive)."""
    decoded_payloads: List[str] = []
    for match in _B64_RE.findall(text):
        candidate = match
        missing_padding = len(candidate) % 4
        if missing_padding:
            candidate += "=" * (4 - missing_padding)
        try:
            raw = base64.b64decode(candidate, validate=False).decode("utf-8", errors="ignore")
            if len(raw) >= 4 and any(c.isalpha() for c in raw):
                decoded_payloads.append(raw)
                if _depth < 1:
                    decoded_payloads.extend(extract_and_decode_base64(raw, _depth=_depth + 1))
        except Exception:
            pass
    return decoded_payloads


def decode_hex(text: str) -> List[str]:
    """Hex-kodlanmış (>=6 byte) dizgeleri bulur ve yazdırılabilir ise çözer."""
    out: List[str] = []
    for match in _HEX_RE.findall(text):
        try:
            raw = bytes.fromhex(match).decode("utf-8", errors="ignore")
            if not raw:
                continue
            printable_ratio = sum(1 for ch in raw if ch.isprintable()) / len(raw)
            if len(raw) >= 4 and printable_ratio > 0.8:
                out.append(raw)
        except Exception:
            pass
    return out


def decode_url_percent(text: str) -> List[str]:
    """URL %XX (percent-encoding) gizlenmiş yükleri deşifre eder."""
    out: List[str] = []
    if "%" not in text:
        return out
    for match in _URL_PCT_RE.findall(text):
        try:
            raw = urllib.parse.unquote(match)
            if len(raw) >= 4 and any(c.isalpha() for c in raw) and raw != match:
                out.append(raw)
        except Exception:
            pass
    return out


def decode_html_entities(text: str) -> List[str]:
    """HTML numeric (&#105;...) veya named (&lt;...) entity gizlenmiş yükleri çözer."""
    out: List[str] = []
    if "&" not in text:
        return out
    try:
        raw = html.unescape(text)
        if raw != text and any(c.isalpha() for c in raw):
            out.append(raw)
    except Exception:
        pass
    return out


def deinterleave_spaced_words(text: str) -> List[str]:
    """i.g.n.o.r.e veya p-a-s-s-w-o-r-d gibi noktalı/tireli gizlenmiş kelimeleri çözer."""
    out: List[str] = []
    for m in _INTERLEAVED_RE.findall(text):
        collapsed = re.sub(r"[.\-_*~]", "", m)
        if len(collapsed) >= 4:
            out.append(collapsed)
    return out


_JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)
_TOOL_CALL_TAG_RE = re.compile(
    r"<(?:tool_call|function_call|call)>(.*?)</(?:tool_call|function_call|call)>",
    re.DOTALL | re.IGNORECASE
)


def _flatten_json_value(val: Any, prefix: str = "") -> List[str]:
    """İç içe JSON/Sözlük nesnelerini düzleştirir."""
    lines: List[str] = []
    if isinstance(val, dict):
        for k, v in val.items():
            sub = f"{prefix}.{k}" if prefix else str(k)
            lines.extend(_flatten_json_value(v, sub))
    elif isinstance(val, list):
        for i, item in enumerate(val):
            sub = f"{prefix}[{i}]" if prefix else f"[{i}]"
            lines.extend(_flatten_json_value(item, sub))
    elif isinstance(val, str):
        if prefix:
            lines.append(f"{prefix}: {val}")
        else:
            lines.append(val)
    elif val is not None:
        if prefix:
            lines.append(f"{prefix}: {val}")
    return lines


def unpack_structured_payload(text: str) -> List[str]:
    """
    Patronus AI ve Qualifire seviyesinde: JSON, kod blokları (```json ... ```) ve
    yapay zeka ajanlarının araç çağrılarına (tool_calls, function_call) gizlenen
    dolaylı komut enjeksiyonlarını tespit edip düz metin olarak açar.
    """
    out: List[str] = []
    if not text:
        return out

    candidates: List[str] = []

    # 1) XML stili tool/function call etiketleri
    for tag_match in _TOOL_CALL_TAG_RE.findall(text):
        clean_tag = tag_match.strip()
        if clean_tag:
            candidates.append(clean_tag)

    # 2) Markdown kod blokları (```json ... ```)
    for block_match in _JSON_BLOCK_RE.findall(text):
        clean_block = block_match.strip()
        if clean_block:
            candidates.append(clean_block)

    # 3) Doğrudan JSON nesnesi veya parantez bloğu { ... }
    stripped = text.strip()
    if (stripped.startswith("{") and stripped.endswith("}")) or \
       (stripped.startswith("[") and stripped.endswith("]")):
        candidates.append(stripped)
    else:
        # Metin içine gömülmüş nesneler
        brace_matches = re.findall(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text)
        for b in brace_matches:
            if len(b) >= 8 and ":" in b:
                candidates.append(b.strip())

    for cand in candidates:
        try:
            parsed = json.loads(cand)
            flattened = _flatten_json_value(parsed)
            if flattened:
                flat_text = " ".join(flattened)
                if len(flat_text) >= 6 and flat_text != text:
                    out.append(flat_text)
        except Exception:
            pass

    # 4) URL Query String veya URL Parametreleri (?q=...&cmd=... veya tam URL)
    try:
        if "?" in text or ("=" in text and ("&" in text or text.strip().startswith("?"))):
            parsed_url = urllib.parse.urlparse(text)
            query_str = parsed_url.query if parsed_url.query else (text.lstrip("?") if "=" in text else "")
            if query_str and "=" in query_str:
                params = urllib.parse.parse_qs(query_str, keep_blank_values=False)
                url_flattened: List[str] = []
                for k, v_list in params.items():
                    for v in v_list:
                        clean_v = urllib.parse.unquote_plus(v).strip()
                        if len(clean_v) >= 3:
                            url_flattened.append(f"{k}: {clean_v}")
                if url_flattened:
                    flat_url = " ".join(url_flattened)
                    if flat_url != text and len(flat_url) >= 6:
                        out.append(flat_url)
    except Exception:
        pass

    return list(dict.fromkeys(out))


def decode_leetspeak(text: str) -> str:
    """Temel leetspeak ikamelerini Latin harflerine çevirir."""
    leet_map = str.maketrans({
        "0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a", "$": "s"
    })
    return text.translate(leet_map)


def decode_rot13(text: str) -> str:
    return codecs.encode(text, "rot_13")


def decode_reversed(text: str) -> str:
    return text[::-1]


def detect_obfuscation(text: str) -> List[str]:
    """
    Geriye dönük uyumluluk için korunan isim: Layer 1'in eski
    `security_layer.detect_obfuscation` fonksiyonunun yerini alır.
    (scripts/run_multi_model_benchmark.py ve scripts/local_model_leak_benchmark.py
    bu fonksiyonu `security_layer` üzerinden import ediyor; security_layer bu
    modülden re-export eder.)
    """
    result = normalize_for_analysis(text)
    return result["alerts"]


def normalize_for_analysis(text: str) -> Dict[str, object]:
    """
    Layer 0'ın ana orkestrasyon fonksiyonu.

    Döndürür:
      clean_text        : Regex/ML taramasına gönderilecek temizlenmiş ana metin.
      extended_text      : clean_text + deşifre edilmiş gizli payload'lar (base64/hex/unicode-tag/url/html).
      rot13_variant       : Yalnızca Layer 1 (regex) ile taranacak ROT13 çözümü.
      reversed_variant    : Yalnızca Layer 1 (regex) ile taranacak ters-yazma çözümü.
      leetspeak_variant   : Yalnızca Layer 1 (regex) ile taranacak Leetspeak çözümü.
      alerts              : Kullanıcıya/loglara gösterilecek insan-okunur uyarı listesi.
      hard_stego_signal   : Kesin/deterministik obfuscation kanıtı (doğrudan BLOCKED için kullanılır).
    """
    if not text:
        return {
            "clean_text": "", "extended_text": "", "rot13_variant": "",
            "reversed_variant": "", "leetspeak_variant": "", "alerts": [],
            "hard_stego_signal": False,
        }

    alerts: List[str] = []

    # 1) NFKC normalizasyonu
    nfkc_text = nfkc_normalize(text)

    # 2) Zero-width / gizli format karakteri temizliği (emoji-farkında)
    zw_clean, zw_suspicious, zw_count = strip_zero_width(nfkc_text)
    if zw_suspicious:
        alerts.append(
            f"SIFIR GENİŞLİKLİ KARAKTER (ZERO-WIDTH / INVISIBLE) TESPİT EDİLDİ: "
            f"{zw_count} adet görünmez karakter (bilinen emoji dizisi dışında)"
        )

    # 3) Unicode Tag tespiti + deşifre
    unicode_tag_found = detect_unicode_tags(nfkc_text)
    hidden_tag_payloads: List[str] = []
    if unicode_tag_found:
        hidden_tag_payloads = decode_unicode_tags(nfkc_text)
        preview = "; ".join(hidden_tag_payloads)[:80]
        alerts.append(f"GÖRÜNMEZ MÜREKKEP / UNICODE TAG TESPİT EDİLDİ (U+E0000-U+E007F): '{preview}'")

    # 4) Variation selector steganografisi (yaygın tekli VS kullanımını yok sayar)
    vs_suspicious = detect_variation_selectors(nfkc_text)
    if vs_suspicious:
        alerts.append("VARIATION SELECTOR / EMOJI STEGANOGRAFİSİ TESPİT EDİLDİ (ardışık VS zinciri)")

    # 5) Homoglyph tespiti + katlama (regex-güvenli metin için)
    homoglyph_found = detect_homoglyphs(zw_clean)
    folded_text = fold_homoglyphs(zw_clean)
    if homoglyph_found:
        alerts.append("HOMOGLYPH / KİRİL-LATİN KARIŞIK HARF TESPİT EDİLDİ")

    # 6) Çoklu Kodlama / Payload Deşifresi (Base64, Hex, URL-Percent, HTML Entities, Noktalı Ayırma)
    b64_payloads = extract_and_decode_base64(folded_text)
    if b64_payloads:
        preview = "; ".join(b64_payloads)[:60]
        alerts.append(f"ŞİFRELİ (BASE64) GİZLİ PAYLOAD DEŞİFRE EDİLDİ: '{preview}'")

    hex_payloads = decode_hex(folded_text)
    if hex_payloads:
        preview = "; ".join(hex_payloads)[:60]
        alerts.append(f"ONALTILIK (HEX) GİZLİ PAYLOAD DEŞİFRE EDİLDİ: '{preview}'")

    url_payloads = decode_url_percent(folded_text)
    if url_payloads:
        preview = "; ".join(url_payloads)[:60]
        alerts.append(f"URL PERCENT-ENCODING GİZLİ PAYLOAD DEŞİFRE EDİLDİ: '{preview}'")

    html_payloads = decode_html_entities(folded_text)
    if html_payloads:
        preview = "; ".join(html_payloads)[:60]
        alerts.append(f"HTML ENTITY GİZLİ PAYLOAD DEŞİFRE EDİLDİ: '{preview}'")

    interleaved_payloads = deinterleave_spaced_words(folded_text)
    if interleaved_payloads:
        preview = "; ".join(interleaved_payloads)[:60]
        alerts.append(f"NOKTALI/TİRELİ AYRILMIŞ GİZLİ KELİME BİRLEŞTİRİLDİ: '{preview}'")

    structured_payloads = unpack_structured_payload(folded_text)
    if structured_payloads:
        preview = "; ".join(structured_payloads)[:60]
        alerts.append(f"YAPILANDIRILMIŞ (JSON/TOOL-CALL) GİZLİ PAYLOAD AYRIŞTIRILDI: '{preview}'")

    decoded_extra = (
        hidden_tag_payloads + b64_payloads + hex_payloads +
        url_payloads + html_payloads + interleaved_payloads +
        structured_payloads
    )
    extended_text = folded_text
    if decoded_extra:
        extended_text = folded_text + "\n" + "\n".join(decoded_extra)

    # 7) ROT13 / Ters-yazma / Leetspeak varyantları (yalnızca Layer 1 regex taraması için)
    rot13_variant = decode_rot13(folded_text)
    reversed_variant = decode_reversed(folded_text)
    leetspeak_variant = decode_leetspeak(folded_text)

    hard_stego_signal = bool(
        zw_suspicious or unicode_tag_found or vs_suspicious or homoglyph_found or
        bool(url_payloads)
    )

    return {
        "clean_text": folded_text,
        "extended_text": extended_text,
        "rot13_variant": rot13_variant,
        "reversed_variant": reversed_variant,
        "leetspeak_variant": leetspeak_variant,
        "alerts": alerts,
        "hard_stego_signal": hard_stego_signal,
    }

