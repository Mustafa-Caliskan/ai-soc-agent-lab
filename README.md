# CyberTech Neural Shield (v5.0): Multi-Layered Peripheral Defense Gateway for Enterprise LLMs

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-FastAPI-005571.svg)](https://fastapi.tiangolo.com)
[![ONNX Runtime](https://img.shields.io/badge/Engine-ONNX%20INT8-blue.svg)](https://onnxruntime.ai/)
[![Model](https://img.shields.io/badge/Model-XLM--RoBERTa--INT8--v5-orange.svg)](https://huggingface.co/xlm-roberta-base)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Executive Summary

Large Language Model (LLM) agents deployed within corporate backends and critical aviation/airport infrastructures (e.g., flight management systems, passenger self-service portals, administrative databases) cannot inherently separate trusted system instructions from untrusted user inputs. Without a dedicated perimeter defense, even frontier models leak canary secrets, credentials, and execute unauthorized instruction overrides.

**CyberTech Neural Shield (v5.0)** is a production-grade, 4-tier peripheral security gateway operating between untrusted client traffic and enterprise LLMs. It combines deterministic normalization, heuristic rule scoring, native multilingual neural classification (XLM-RoBERTa ONNX INT8 with CyberFocalLoss), and outbound Data Loss Prevention (DLP) under an average latency of **12.27 ms on CPU**.

---

## Architectural Overview

```
                      INGESTION SURFACE (Text / PDF / External URLs)
                                          │
                                          ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│ LAYER 0: NORMALIZATION & STEGANOGRAPHY ENGINE (<0.2 ms)                          │
│ • NFKC Unicode Canonical Normalization & Fullwidth Folding                       │
│ • Zero-Width & Invisible Formatting Character Stripping (ZWJ-Emoji Whitelisted)  │
│ • Soft-Hyphen (U+00AD) & BiDi Directional Mark Neutralization                    │
│ • Cyrillic/Greek Homoglyph Detection and Latin Transliteration                   │
│ • Multi-Codec Recursive Decoders: Base64, Hex, ROT13, Reverse, URL (%XX)        │
│ • Invisible Ink Steganography: Unicode Tag (U+E0000 - U+E007F) Interception      │
└─────────────────────────────────────┬────────────────────────────────────────────┘
                                      │ Clean & Extended Analyzed Text
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│ LAYER 1: DETERMINISTIC HEURISTIC & REGEX ENGINE (<0.3 ms)                        │
│ • Bilingual (TR / EN) Prompt Injection, Jailbreak (DAN) & Roleplay Signatures    │
│ • Cognitive Framing, Authority Simulation (Auditor/Admin Claims) Patterns        │
│ • ROT13, Reversed, and Leetspeak Variant Inspection                              │
│ ──> Output: Triggered Patterns & Severity Score (0 - 100)                        │
└─────────────────────────────────────┬────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│ LAYER 2: MULTILINGUAL NEURAL CLASSIFIER (XLM-RoBERTa ONNX INT8 v5) (12.27 ms)    │
│ • Native Cross-Lingual Semantic Classifier (No external translation bottleneck) │
│ • Quantized INT8 Engine (278 MB) optimized for low-latency CPU deployment        │
│ • Trained on 71,440 Balanced Samples (30 datasets) via CyberFocalLoss (γ=2.0)    │
│ ──> Output: Malicious Probability (0.0 - 1.0) & Neural Risk Score                │
└─────────────────────────────────────┬────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│ 🧠 COMPOSITE RISK & DECISION ENGINE (Config-Driven)                              │
│ Risk = max(ML_Risk, Stego_Floor) + Regex_Contribution                           │
│ Dynamic Ban Policy: Consecutive violations lower effective threshold             │
│                                                                                  │
│ • Risk >= Effective Threshold (Default: 60) ──> 🛑 BLOCKED (Dropped immediately)│
│ • Risk < Effective Threshold                ──> ✅ ALLOWED (Dispatched to LLM)  │
└─────────────────────────────────────┬────────────────────────────────────────────┘
                                      │ (If ALLOWED)
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│ 🤖 PROTECTED LLM BACKEND (SkyPort Operational Core / Gemini / LLaMA / Ollama)    │
│ Executes query within authentic airport operational system context.              │
└─────────────────────────────────────┬────────────────────────────────────────────┘
                                      │ Raw LLM Generation
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│ LAYER 3: OUTBOUND DATA LOSS PREVENTION (DLP) (<0.1 ms)                           │
│ • Canary Token & Secret Credential Masking (Password, API Keys, DB Strings)      │
│ • Algorithmically Verified PII Masking:                                          │
│   - Credit Cards: 16-Digit PAN with LUHN Checksum Validation                     │
│   - Turkish National ID (TC Kimlik No): Official 11-Digit Checksum Algorithm     │
│   - Cloud Credentials (AWS AKIA..., OpenAI sk-..., GitHub ghp_..., Slack xox*)   │
│   - Cryptographic Secrets (PEM Private Keys, JWT Tokens, Turkish IBANs)          │
│   - Configurable Communication PII Masking (Email / Phone - Optional)            │
│ ──> Output: Sanitized Egress Response                                           │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## Key Defense Mechanisms

### 1. Normalization & Obfuscation Stripping (Layer 0)
* **ZWJ-Safe Emoji Handling:** Legitimate Zero-Width Joiner (ZWJ) sequences (`👨‍👩‍👧‍👦`, `🏳️‍🌈`, skin-tone modifiers) are preserved without raising false alarms, while hidden zero-width spaces within alphabetical tokens are isolated and flagged.
* **Invisible Formatting Control:** Neutralizes Soft-Hyphens (`\u00ad`), Arabic letter marks, and BiDi override characters inserted to break word boundaries.
* **Homoglyph Folding:** Transliterates lookalike Cyrillic and Greek characters (e.g., `В`, `Н`, `а`, `е`, `о`, `р`, `с`) into canonical Latin equivalents.
* **Multi-Codec Extraction:** Recursively unpacks Base64, Hex, URL percent-encoding, and HTML entities so concealed payloads cannot bypass downstream layers.

### 2. Weighted Heuristics (Layer 1)
* Operates on canonical text and derived representations (ROT13, reversed string, leetspeak transliteration).
* Assigns risk weights (0 to 100) instead of naive boolean checks, preventing single false alarms while catching composite evasions.

### 3. Native Multilingual ONNX INT8 Model (Layer 2)
* Powered by `xlm-roberta-base` fine-tuned with **CyberFocalLoss ($\gamma=2.0$)** on 71,440 master samples and quantized to INT8 ONNX (278 MB).
* Evaluates semantic intent directly across Turkish and English without translation latency.
* Verified False Positive Rate on technical IT prompts (e.g., Active Directory, firewall configuration, SQL queries) is **0.00%**.

### 4. Verified Outbound DLP (Layer 3)
* Validates credit card candidates against the **Luhn algorithm** and Turkish IDs against official mod-10/11 algorithms to prevent false redaction of order numbers or tracking codes.
* Masks sensitive API keys, JWT headers, and database connection strings before user delivery.

---

## Experimental Benchmark (NeuralShield-v5 SSOT)

Empirical evaluation on held-out test split ($n=10,716$) and latency benchmark ($n=100$ iterations on consumer CPU):

| Evaluation Metric | Measured Result | Performance Benchmark Target |
| :--- | :--- | :--- |
| **Model Accuracy (Held-out Test)** | **94.64%** | > 92.0% |
| **Precision (Macro)** | **94.65%** | > 92.0% |
| **Recall (Macro)** | **94.62%** | > 92.0% |
| **F1-Score (Macro)** | **94.63%** | > 92.0% |
| **Optimal Threshold F1 ($\tau=0.4567$)**| **96.89%** | > 95.0% |
| **AUC-ROC** | **0.9954** | > 0.950 |
| **Technical IT False Alarm Rate** | **0.00%** | < 2.0% |
| **Layer 0 Latency (Normalizer)** | **0.17 ms** | < 0.5 ms |
| **Layer 1 Latency (Regex)** | **0.29 ms** | < 0.5 ms |
| **Layer 2 Latency (ONNX INT8 v5)** | **12.27 ms** | < 15.0 ms |
| **Layer 3 Latency (Outbound DLP)** | **< 0.05 ms** | < 0.5 ms |
| **Total Guardrail CPU Latency** | **12.73 ms** | **< 15.0 ms** |

---

## Repository Structure

```
.
├── backend/
│   ├── main.py                     # FastAPI server, WebSocket log broadcaster & API endpoints
│   ├── security_layer.py           # Core 4-tier pipeline coordinator & composite risk engine
│   ├── normalizer.py               # Layer 0: Unicode NFKC, ZWJ-aware stego & multi-codec engine
│   ├── regex_rules.py              # Layer 1: Bilingual weighted regex attack signatures
│   ├── ml_model.py                 # Layer 2: XLM-RoBERTa ONNX INT8 inference runner
│   ├── dlp.py                      # Layer 3: Luhn/TC-verified outbound data loss prevention
│   ├── shield_config.json          # Config-driven thresholds, weights & ban policies
│   ├── canary.py                   # Synthetic canary secrets for red-team auditing
│   ├── database.py                 # SQLite operational flight & passenger records
│   ├── evren_client.py             # Integration client for EVREN H200 LLM fleet
│   └── models/
│       └── neuralshield_v5/        # Production ONNX INT8 model & tokenizers (278 MB)
├── frontend/
│   ├── index.html                  # SkyPort airport portal & interactive passenger assistant
│   ├── red_team.html               # Red team adversarial simulation workspace
│   ├── blue_team.html              # Blue team live SOC monitoring dashboard
│   ├── admin.html                  # Security threshold & system admin console
│   └── pipeline.html               # Multi-layer architecture interactive diagram
├── scripts/
│   ├── verify_full_pipeline.py     # Automated regression & acceptance test suite (20/20 PASS)
│   ├── probe_pipeline_edge_cases.py# Adversarial bypass & evasion probe suite
│   ├── benchmark_latency_budget.py # CPU latency & performance budget verification
│   ├── run_multi_model_benchmark.py# Multi-LLM Canary leak benchmark runner
│   └── run_evren_tiered_benchmark.py # EVREN H200 Supercomputer 5-tier ASR benchmark runner
├── tests/
│   └── test_security_layer.py      # Pytest-compatible unit test suite
├── docs/                           # Architectural plans, benchmark reports & research papers
│   └── figures/                    # Official publication figures (sekil_1_* to sekil_8_*)
├── requirements.txt                # Python dependencies
└── README.md                       # Master technical documentation
```

---

## Quickstart

### 1. Installation
```bash
git clone https://github.com/Mustafa-Caliskan/ai-soc-agent-lab.git
cd ai-soc-agent-lab
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux / macOS:
# source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Verify Pipeline Integrity
Run the regression suite and unit tests:
```bash
python scripts/verify_full_pipeline.py
pytest tests/test_security_layer.py -v
python scripts/benchmark_latency_budget.py
```

### 3. Launch Gateway Server
```bash
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
Navigate to `http://127.0.0.1:8000/` for the public passenger portal or `http://127.0.0.1:8000/blue` for the SOC console.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
