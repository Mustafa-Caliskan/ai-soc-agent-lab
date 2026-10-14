"""
CyberTech Neural Shield - Security Layer Orchestrator.
Combines 4 Peripheral Defense Layers:
- Layer 0: Normalizasyon & Steganografi Motoru (NFKC, homoglyph fold,
  emoji-farkında zero-width temizliği, unicode-tag/hex/base64/rot13/reverse
  çözücüleri) — bkz. normalizer.py (<1 ms)
- Layer 1: Deterministic Regex/Heuristic Engine (ağırlıklı skor) (<0.5 ms)
- Layer 2: XLM-RoBERTa ONNX INT8 Semantic Classifier (~9.5 ms)
- Layer 3: Outbound DLP Masking & Sanitization (<0.5 ms)

Karar motoru artık `shield_config.json` üzerinden okunan Bileşik Risk
Formülü ile çalışır:
    composite = weight_ml * ML_risk + weight_regex * Regex_skoru + weight_stego * Stego_skoru
Kesin/deterministik steganografi veya regex+ML birlikte "Malicious" derse,
bu formülü ezen bir "hard floor" uygulanır (savunmada "zayıf halka"
oluşmaması için).

`user_behavior_score`, çağıran tarafın (main.py) hesapladığı ve son
`ban_window_seconds` içindeki ardışık BLOCKED kararlarına göre büyüyen bir
"ceza puanı"dır (0 .. ban_max_penalty). Etkin blok eşiğini düşürerek basit
bir "dinamik ban politikası" (geçici, kademeli sıkılaştırma) uygular.
"""
import asyncio
import base64
import time
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

import requests
from bs4 import BeautifulSoup

import normalizer as norm
from regex_rules import scan_text
from dlp import scan_and_mask
from shield_config import CONFIG

logger = logging.getLogger(__name__)

# ── Geriye Dönük Uyumluluk (Backward-Compat Re-exports) ─────────────────────
# scripts/run_multi_model_benchmark.py ve scripts/local_model_leak_benchmark.py
# bu isimleri `from security_layer import detect_obfuscation, extract_and_decode_base64`
# şeklinde import ediyor. Gerçek implementasyon artık normalizer.py'de yaşıyor.
detect_obfuscation = norm.detect_obfuscation
extract_and_decode_base64 = norm.extract_and_decode_base64


def extract_pdf_text(pdf_bytes: bytes) -> Dict[str, Any]:
    """
    Enhanced PDF extraction that detects hidden text (white-on-white / zero font size).
    Returns {'text': str, 'hidden_detected': bool}
    """
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        full_text = ""
        hidden_detected = False

        for page in doc:
            full_text += page.get_text()
            blocks = page.get_text("dict")["blocks"]
            for b in blocks:
                if "lines" in b:
                    for l in b["lines"]:
                        for s in l["spans"]:
                            # Color is white/near-white (0xFFFFFF = 16777215)
                            if s.get("color", 0) > 16777000 and s.get("text", "").strip():
                                hidden_detected = True
                            # Tiny invisible font size
                            if s.get("size", 10) < 1.0 and s.get("text", "").strip():
                                hidden_detected = True

        return {"text": full_text, "hidden_detected": hidden_detected}
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        return {"text": "", "hidden_detected": False}


def extract_url_text(url: str) -> str:
    """Fetches text content from untrusted external URL."""
    try:
        resp = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "lxml")
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
    4-Layer Hybrid Defense Pipeline.
    Evaluates requests in real time and coordinates with Gemini LLM.

    user_behavior_score: main.py tarafından hesaplanan 0..ban_max_penalty
    aralığında bir "ceza puanı". Etkin blok eşiğinden doğrudan çıkarılır.
    """
    full_text = text or ""
    source_label = "text"
    pdf_hidden = False

    # ── Content Ingestion ───────────────────────────────────────────────────
    if pdf_base64:
        pdf_bytes = base64.b64decode(pdf_base64)
        pdf_res = extract_pdf_text(pdf_bytes)
        full_text = (full_text + "\n" + pdf_res["text"]).strip()
        source_label = "pdf"
        pdf_hidden = pdf_res["hidden_detected"]

    if url:
        extracted = extract_url_text(url)
        full_text = (full_text + "\n" + extracted).strip()
        source_label = "url"

    if not full_text:
        return _error_result("Boş içerik gönderildi.")

    # ── Layer 0: Normalizasyon & Steganografi Motoru ─────────────────────────
    t_l0_start = time.perf_counter()
    norm_result = norm.normalize_for_analysis(full_text)
    l0_latency_ms = round((time.perf_counter() - t_l0_start) * 1000.0, 2)

    advanced_alerts: List[str] = list(norm_result["alerts"])
    if pdf_hidden:
        advanced_alerts.append("GİZLİ METİN TESPİT EDİLDİ (White-on-White / Zero Size)")

    analysis_text = norm_result["extended_text"]
    clean_text = norm_result["clean_text"]
    hard_stego_signal = bool(norm_result["hard_stego_signal"] or pdf_hidden)

    # ── Layer 1: Regex / Heuristic Engine (ana metin + ROT13/ters-yazma varyantları) ─
    t_l1_start = time.perf_counter()
    regex_triggered, regex_patterns, regex_score = scan_text(analysis_text)

    rot13_triggered, rot13_patterns, rot13_score = scan_text(norm_result.get("rot13_variant", ""))
    rev_triggered, rev_patterns, rev_score = scan_text(norm_result.get("reversed_variant", ""))
    leet_triggered, leet_patterns, leet_score = scan_text(norm_result.get("leetspeak_variant", ""))
    if rot13_triggered:
        advanced_alerts.append(f"ROT13 ÇÖZÜMÜNDE SALDIRI İMZASI TESPİT EDİLDİ: {', '.join(rot13_patterns)}")
    if rev_triggered:
        advanced_alerts.append(f"TERS-YAZMA ÇÖZÜMÜNDE SALDIRI İMZASI TESPİT EDİLDİ: {', '.join(rev_patterns)}")
    if leet_triggered:
        advanced_alerts.append(f"LEETSPEAK ÇÖZÜMÜNDE SALDIRI İMZASI TESPİT EDİLDİ: {', '.join(leet_patterns)}")

    layer1_patterns_found = list(set(regex_patterns + rot13_patterns + rev_patterns + leet_patterns))
    regex_triggered = regex_triggered or rot13_triggered or rev_triggered or leet_triggered
    regex_patterns = layer1_patterns_found
    regex_score = max(regex_score, rot13_score, rev_score, leet_score)
    l1_latency_ms = round((time.perf_counter() - t_l1_start) * 1000.0, 2)

    # ── Security Evaluation (Composite Risk Score) ───────────────────────────
    effective_threshold = CONFIG["block_threshold"]

    if not security_enabled:
        decision = "ALLOWED"
        risk_score = 0
        ml_class = "BYPASS"
        ml_probs = {"Benign": 1.0, "Malicious": 0.0}
        l2_latency_ms = 0.0
    else:
        # ── Layer 2: XLM-RoBERTa ONNX INT8 Semantic Classifier ───────────────
        if ml_model is not None and hasattr(ml_model, "predict"):
            ml_result = ml_model.predict(analysis_text)
            ml_class = ml_result["ml_class"]
            ml_probs = ml_result["ml_probabilities"]
            ml_risk_score = ml_result["ml_risk_score"]
            l2_latency_ms = ml_result.get("inference_latency_ms", 9.47)
        else:
            ml_class = "Unavailable"
            ml_probs = {"Benign": 1.0, "Malicious": 0.0}
            ml_risk_score = regex_score
            l2_latency_ms = 0.0

        stego_score = 100 if hard_stego_signal else 0

        composite_score = (
            CONFIG["weight_ml"] * ml_risk_score
            + CONFIG["weight_regex"] * regex_score
            + CONFIG["weight_stego"] * stego_score
        )

        # Kesin/deterministik sinyaller, ağırlıklı formülü ezebilen bir "taban" oluşturur
        # (tek bir katmana güvenmeme ilkesi — bkz. proje yol haritası §3.1).
        if hard_stego_signal:
            risk_score = max(composite_score, CONFIG["hard_block_stego_score"])
        elif regex_triggered and ml_class == "Malicious":
            risk_score = max(composite_score, CONFIG["hard_block_regex_and_ml_score"])
        elif regex_triggered:
            risk_score = max(composite_score, CONFIG["regex_only_floor_score"])
        elif ml_class == "Malicious" and ml_risk_score >= effective_threshold:
            risk_score = max(composite_score, ml_risk_score)
        else:
            risk_score = composite_score

        risk_score = min(100, round(risk_score))

        # ── Dinamik Ban Politikası: tekrarlanan ihlaller eşik değerini düşürür ──
        effective_threshold = max(
            CONFIG["ban_min_effective_threshold"],
            CONFIG["block_threshold"] - int(user_behavior_score or 0)
        )

        if risk_score >= effective_threshold or (regex_triggered and ml_class == "Malicious"):
            decision = "BLOCKED"
        else:
            decision = "ALLOWED"

    # ── Layer 3: Gemini Execution & DLP Outbound Filtering ──────────────────
    gemini_response = None
    dlp_triggered = False
    dlp_masked_response = None
    dlp_patterns_hit = []
    l3_latency_ms = 0.0

    if decision == "ALLOWED" and gemini_model:
        try:
            loop = asyncio.get_running_loop()
            raw_response = await loop.run_in_executor(None, gemini_model.generate_content, clean_text)
            gemini_response = raw_response.text

            t_l3_start = time.perf_counter()
            if security_enabled:
                dlp_triggered, dlp_masked_response, dlp_patterns_hit = scan_and_mask(gemini_response)
            else:
                dlp_triggered = False
                dlp_masked_response = gemini_response
                dlp_patterns_hit = []
            l3_latency_ms = round((time.perf_counter() - t_l3_start) * 1000.0, 2)
        except Exception as e:
            logger.error(f"Gemini API invocation error: {e}")
            gemini_response = f"[Gemini API Hatası: {e}]"
            dlp_masked_response = gemini_response
    elif decision == "BLOCKED":
        gemini_response = "🛡️ [CyberTech Neural Shield]: Güvenlik ihlali tespit edildi. İstek filtrelendi ve ana modele iletilmedi."
        dlp_masked_response = gemini_response

    total_guardrail_latency_ms = round(l0_latency_ms + l1_latency_ms + l2_latency_ms + l3_latency_ms, 2)

    return {
        "decision": decision,
        "risk_score": risk_score,
        "regex_score": regex_score,
        "effective_threshold": effective_threshold,
        "hard_stego_signal": hard_stego_signal,
        "ml_class": ml_class,
        "ml_probabilities": ml_probs,
        "regex_triggered": regex_triggered,
        "layer0_alerts": advanced_alerts,
        "layer1_patterns": regex_patterns,
        "regex_patterns": regex_patterns + advanced_alerts,  # Geriye dönük uyumluluk
        "gemini_response": gemini_response,
        "dlp_triggered": dlp_triggered,
        "dlp_masked_response": dlp_masked_response,
        "dlp_patterns": dlp_patterns_hit,
        "source": source_label,
        "security_enabled": security_enabled,
        "timestamp": datetime.utcnow().isoformat(),
        "request_preview": full_text[:120].replace("\n", " "),
        "translated_text": clean_text,
        "layer0_latency_ms": l0_latency_ms,
        "layer1_latency_ms": l1_latency_ms,
        "layer2_latency_ms": l2_latency_ms,
        "layer3_latency_ms": l3_latency_ms,
        "total_latency_ms": total_guardrail_latency_ms,
    }


def _error_result(msg: str) -> Dict[str, Any]:
    return {
        "decision": "ERROR",
        "risk_score": 0,
        "regex_score": 0,
        "effective_threshold": CONFIG["block_threshold"],
        "hard_stego_signal": False,
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
        "layer0_latency_ms": 0.0,
        "layer1_latency_ms": 0.0,
        "layer2_latency_ms": 0.0,
        "layer3_latency_ms": 0.0,
        "total_latency_ms": 0.0,
    }
