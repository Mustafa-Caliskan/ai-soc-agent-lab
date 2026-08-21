"""
Security Layer orchestrator – combines all 3 layers.
Layer 1: Regex rule engine
Layer 2: RoBERTa ML classifier
Layer 3: DLP outbound filter
"""
import base64
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import re
import unicodedata

import requests
from bs4 import BeautifulSoup

from regex_rules import scan_text
from dlp import scan_and_mask

logger = logging.getLogger(__name__)

BLOCK_THRESHOLD = 65  # risk score >= this → BLOCK


def extract_pdf_text(pdf_bytes: bytes) -> Dict[str, Any]:
    """
    Enhanced PDF extraction that detects hidden text (white-on-white).
    Returns {'text': str, 'hidden_detected': bool}
    """
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        full_text = ""
        hidden_detected = False
        
        for page in doc:
            full_text += page.get_text()
            # Check for hidden text by inspecting spans
            blocks = page.get_text("dict")["blocks"]
            for b in blocks:
                if "lines" in b:
                    for l in b["lines"]:
                        for s in l["spans"]:
                            # If color is white or very close to it (e.g. 0xFFFFFF) 
                            # and it contains non-whitespace text, it's suspicious.
                            # PyMuPDF color is an integer. 16777215 is white.
                            if s["color"] > 16777000 and s["text"].strip():
                                hidden_detected = True
        
        return {"text": full_text, "hidden_detected": hidden_detected}
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        return {"text": "", "hidden_detected": False}


def detect_obfuscation(text: str) -> bool:
    """Detects zero-width characters, Unicode Tags (invisible ink), and unusual emoji density."""
    # Beyaz liste kontrolü (Sunum stabilitesi için)
    whitelist = ["selam", "merhaba", "hey", "nasılsın", "günaydın", "iyi akşamlar"]
    if text.lower().strip() in whitelist:
        return False
        
    # Unicode Tags Block (U+E0000 - U+E007F) - SADECE GÜVENLİK AÇIKKEN ÇALIŞIR
    if any('\U000E0000' <= c <= '\U000E007F' for c in text):
        return True
            
    return False


def extract_url_text(url: str) -> str:
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "lxml")
        # Remove scripts/styles
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:8000]
    except Exception as e:
        logger.error(f"URL fetch error: {e}")
        return ""


async def analyze(
    text: str,
    pdf_base64: Optional[str],
    url: Optional[str],
    security_enabled: bool,
    gemini_model,
    ml_model,
    user_behavior_score: int = 0
) -> Dict[str, Any]:
    """
    Full 3-layer analysis pipeline.
    Returns the complete result dict consumed by the API and WebSocket.
    """
    # ── Content extraction ────────────────────────────────────────────────
    full_text = text or ""
    source_label = "text"
    advanced_alerts = []

    if pdf_base64:
        pdf_bytes = base64.b64decode(pdf_base64)
        pdf_res = extract_pdf_text(pdf_bytes)
        full_text = (full_text + "\n" + pdf_res["text"]).strip()
        source_label = "pdf"
        if pdf_res["hidden_detected"]:
            advanced_alerts.append("GİZLİ METİN TESPİT EDİLDİ (White-on-White)")

    if url:
        extracted = extract_url_text(url)
        full_text = (full_text + "\n" + extracted).strip()
        source_label = "url"

    if not full_text:
        return _error_result("Boş içerik gönderildi.")

    # ── Advanced Obfuscation Check ───────────────────────────────────────
    if detect_obfuscation(full_text):
        advanced_alerts.append("KARAKTER GİZLEME / EMOJİ OBFUSCATION TESPİT EDİLDİ")

    # ── Security Evaluation ────────────────────────────────────────────────
    if not security_enabled:
        regex_triggered = False
        regex_patterns = []
        ml_class = "BYPASS"
        ml_probs = {"Benign": 1.0, "Malicious": 0.0}
        ml_risk_score = 0
        translated_text = full_text
        risk_score = 0
        decision = "ALLOWED"
    else:
        # ── Layer 1: Regex ────────────────────────────────────────────────────
        regex_triggered, regex_patterns = scan_text(full_text)
        if advanced_alerts:
            regex_triggered = True
        regex_risk = 65 if regex_triggered else 0

        # ── Layer 2: ML ───────────────────────────────────────────────────────
        ml_result = ml_model.predict(full_text)
        ml_class      = ml_result["ml_class"]
        ml_probs      = ml_result["ml_probabilities"]
        ml_risk_score = ml_result["ml_risk_score"]
        translated_text = ml_result.get("translated_text", full_text)

        # ── Combined risk score ───────────────────────────────────────────────
        if regex_triggered and ml_class != "Benign":
            risk_score = min(100, int(0.4 * regex_risk + 0.6 * ml_risk_score) + 15)
        elif regex_triggered:
            risk_score = max(regex_risk, ml_risk_score)
        else:
            risk_score = ml_risk_score

        # Sunum Düzeltmesi: Eğer mesaj çok kısaysa ve bariz bir saldırı yoksa puanı düşür
        if len(full_text.strip()) < 10 and not regex_triggered:
            risk_score = min(risk_score, 15)

        # ── Advanced Penalty ──────────────────────────────────────────────────
        # Add penalty for each advanced alert
        risk_score += len(advanced_alerts) * 20
        
        # Sunum için sabıka cezasını kapattık
        behavior_penalty = 0
        
        if behavior_penalty > 0:
            advanced_alerts.append(f"KULLANICI DAVRANIS CEZASI (+{behavior_penalty})")

        risk_score = min(100, risk_score)

        # ── Decision ──────────────────────────────────────────────────────────
        if risk_score >= BLOCK_THRESHOLD:
            decision = "BLOCKED"
        elif regex_triggered and ml_class != "Benign":
            decision = "BLOCKED"
        elif regex_triggered and risk_score >= 50:
            decision = "BLOCKED"
        else:
            decision = "ALLOWED"

    # ── Layer 3: Gemini call + DLP ────────────────────────────────────────
    gemini_response     = None
    dlp_triggered       = False
    dlp_masked_response = None
    dlp_patterns_hit    = []

    if decision == "ALLOWED" and gemini_model:
        try:
            raw_response = gemini_model.generate_content(full_text)
            gemini_response = raw_response.text
            
            if security_enabled:
                dlp_triggered, dlp_masked_response, dlp_patterns_hit = scan_and_mask(gemini_response)
            else:
                dlp_triggered = False
                dlp_masked_response = gemini_response
                dlp_patterns_hit = []
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            gemini_response = f"[Gemini API Hatası: {e}]"

    return {
        "decision": decision,
        "risk_score": risk_score,
        "ml_class": ml_class,
        "ml_probabilities": ml_probs,
        "regex_triggered": regex_triggered,
        "regex_patterns": regex_patterns + advanced_alerts,
        "gemini_response": gemini_response,
        "dlp_triggered": dlp_triggered,
        "dlp_masked_response": dlp_masked_response,
        "dlp_patterns": dlp_patterns_hit,
        "source": source_label,
        "security_enabled": security_enabled,
        "timestamp": datetime.utcnow().isoformat(),
        "request_preview": full_text[:120].replace("\n", " "),
        "translated_text": translated_text,
    }


def _error_result(msg: str) -> Dict[str, Any]:
    return {
        "decision": "ERROR",
        "risk_score": 0,
        "ml_class": "Benign",
        "ml_probabilities": {"Benign": 1.0, "Malicious": 0.0},
        "translated_text": msg,
        "regex_triggered": False,
        "regex_patterns": [],
        "gemini_response": msg,
        "dlp_triggered": False,
        "dlp_masked_response": msg,
        "dlp_patterns": [],
        "source": "unknown",
        "timestamp": datetime.utcnow().isoformat(),
        "request_preview": "",
    }
