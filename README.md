# CyberTech Neural Shield: Multi-Layered Defense Architecture for LLM Deployments in Critical Infrastructures

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-FastAPI-005571.svg)](https://fastapi.tiangolo.com)
[![Hugging Face Model](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-cybertech--neural--shield--deberta-yellow.svg)](https://huggingface.co/Mustafa5645344/cybertech-neural-shield-deberta)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Executive Summary

Large Language Model (LLM) agents integrated into enterprise and critical infrastructure environments present significant security risks, primarily arising from their inability to inherently separate control instructions from untrusted data inputs. 

**CyberTech Neural Shield** is a deterministic, semantic, and outbound three-tier security gateway designed to protect LLM-integrated operational backends (e.g., flight management systems, passenger portals, administrative databases) against sophisticated adversarial threats. The framework systematically mitigates:

- **Indirect Prompt Injection** and Context Hijacking
- **Covert Channel Steganography** utilizing Unicode Tag Blocks and Zero-Width characters
- **Multimodal Document Smuggling** (White-on-White text in PDF attachments)
- **Data Exfiltration** targeting high-value transactional and operational records

---

## Architectural Overview

The security gateway operates as a non-bypassable intermediary between external data ingestion channels (HTTP/WebSockets, document uploads, user interfaces) and the core generative language model (e.g., Google Gemini 2.5 Flash / Vertex AI).

```
+-----------------------------------------------------------------------------------+
|                            External Ingestion Surface                             |
|               (Web Portal, Red Team Terminal, Document Attachments)               |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|               LAYER 1: Deterministic Heuristic & Obfuscation Engine               |
|  - Unicode Tag Block Detection (U+E0000 - U+E007F)                                 |
|  - Zero-Width Character and Encoding Anomaly Inspection                           |
|  - PDF Luminance & Color-Space Parser (PyMuPDF Text/Background Contrast Check)   |
|  - Deterministic Pattern & Signature Matcher                                      |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|               LAYER 2: Multilingual Semantic Threat Classifier                    |
|  - MarianMT Translation Subsystem (Helsinki-NLP opus-mt-tr-en)                    |
|  - Fine-Tuned DeBERTa-v3 / RoBERTa Classifier Checkpoint                          |
|  - Intent Risk Scoring (0 - 100 Scale) & State-Based Temporary Ban Management     |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          | (If Risk Score < Threshold)
                                          v
+-----------------------------------------------------------------------------------+
|                         Protected LLM Execution Core                             |
|                       (Google Gemini 2.5 Flash / Llama)                           |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|               LAYER 3: Outbound Data Loss Prevention (DLP) Gateway                |
|  - Regex-Based PII & Financial Pattern Masking (PANs, National IDs, CVVs)        |
|  - Operational Data Scrubbing (Crew Authentication Secrets, Private Keys)         |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                            Sanitized Output Egress                                |
|                        (WebSocket Broadcast & User UI)                            |
+-----------------------------------------------------------------------------------+
```

---

## Defense Mechanisms

### 1. Deterministic Heuristic & Obfuscation Engine (Layer 1)
- **Covert Unicode Analysis:** Inspects strings for characters within the private Unicode Tag plane (`U+E0000` to `U+E007F`) used to encode invisible ASCII instructions alongside standard emojis.
- **Document Luminance Analysis:** Analyzes raw PDF structural streams using `PyMuPDF` to compute RGB contrast between rendered text objects and page backgrounds, identifying invisible/near-invisible injection payloads (e.g., `#FFFFFF` text on `#FFFFFF` backgrounds).
- **Signature Scanners:** Evaluates input buffers against deterministic regex rules to identify well-known exploit wrappers (`[SYSTEM OVERRIDE]`, `[DEVELOPER MODE]`, instruction termination tokens).

### 2. Semantic Intent Classification (Layer 2)
- **Neural Classifier:** Employs a fine-tuned Transformer model based on `microsoft/deberta-v3-base` to evaluate semantic toxicity, jailbreaking semantics, and conversational social engineering.
- **Cross-Lingual Normalization:** Utilizes Helsinki-NLP translation bridges to standardize multilingual attack vectors (Turkish, German, English) into a unified semantic embedding space.
- **Dynamic Ban Policy:** Enforces an exponential penalty curve and temporary session isolation (2-minute lockout) upon detection of consecutive critical violations.

### 3. Outbound Data Loss Prevention (Layer 3)
- Intercepts all egress text streams generated by the model.
- Identifies and masks 16-digit Primary Account Numbers (Luhn-compliant), CVV codes, passport identifiers, and internal system credentials before transmission to client endpoints.

---

## Repository Structure

```
.
├── backend/
│   ├── main.py                     # FastAPI application entry point & WebSocket hub
│   ├── security_layer.py           # Core 3-layer security pipeline orchestrator
│   ├── ml_model.py                 # Transformer inference engine & MarianMT wrapper
│   ├── regex_rules.py              # Layer 1 deterministic pattern signatures
│   ├── dlp.py                      # Layer 3 data loss prevention filter
│   ├── database.py                 # SQLite database schema and seed data
│   └── create_poison_pdf.py        # PDF white-paper attack test generator
├── frontend/
│   ├── index.html                  # Airport portal, interactive UI & AI assistant
│   ├── red_team.html               # Red team attack simulation interface
│   ├── blue_team.html              # Blue team SOC monitoring console
│   ├── admin.html                  # Firewall policy control dashboard
│   ├── buy.html                    # Ticket reservation and payment mock
│   └── pipeline.html               # Multi-layer architecture interactive view
├── tools/
│   ├── zehirleyici.py              # CLI adversarial Unicode payload encoder
│   ├── cozucu.py                   # CLI Unicode payload decoder utility
│   └── decoder.html                # Web-based visual decoder utility
├── samples/
│   └── pdf_attacks/                # Pre-compiled white-paper attack PDF test cases
├── docs/
│   ├── CyberTech_IMRAD_Raporu.docx # Comprehensive academic research paper
│   ├── CyberTech_IMRAD_Raporu.pdf  # Compiled PDF research report
│   └── figures/                    # High-resolution architectural diagrams
├── best_model/                     # Transformer configuration, vocabulary & tokenizers
│   ├── config.json
│   ├── tokenizer.json
│   └── tokenizer_config.json
├── requirements.txt                # Production dependencies
├── .env.example                    # Environment variable configuration template
└── README.md                       # Technical documentation
```

---

## Installation & Setup

### Prerequisites
- Python 3.10, 3.11, or 3.12
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/Mustafa-Caliskan/ai-soc-agent-lab.git
cd ai-soc-agent-lab
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the template configuration file and supply your API credentials:
```bash
cp .env.example .env
```
Edit `.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## Usage & Execution

### Starting the Backend Server
```bash
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### Accessing Dashboards
Once the server is running, access the following endpoints via a web browser:
- **Public Passenger Portal:** `http://127.0.0.1:8000/`
- **Red Team Adversarial Terminal:** `http://127.0.0.1:8000/red`
- **Blue Team SOC Monitoring Console:** `http://127.0.0.1:8000/blue`
- **Security Policy & Admin Control:** `http://127.0.0.1:8000/admin`
- **Pipeline Architecture View:** `http://127.0.0.1:8000/pipeline`

---

## Adversarial Evaluation Tools

The framework includes dedicated testing utilities to validate detection capabilities:

### 1. Steganographic Unicode Encoder (`tools/zehirleyici.py`)
Generates payload strings where arbitrary prompt injections are hidden within Unicode Tag characters appended to carrier emojis:
```bash
python tools/zehirleyici.py
```

### 2. Document Smuggling Test Suite (`backend/create_poison_pdf.py`)
Compiles test documents embedding white-on-white text across multiple operational scenarios into `samples/pdf_attacks/`:
```bash
python backend/create_poison_pdf.py
```

Generated artifacts:
- `pdf_1_tr_otopark.pdf`: Turkish parking rate exfiltration payload.
- `pdf_2_en_flights.pdf`: English flight credential scraping payload.
- `pdf_3_benign_selam.pdf`: Baseline benign greeting document.
- `pdf_4_bypass_confirm.pdf`: Direct instruction override verification file.

---

## Experimental Evaluation

Evaluation benchmarks conducted on synthetic and real-world adversarial prompt injection datasets (100,000+ sample iterations):

| Metric | Heuristic (Layer 1) | Neural Classifier (Layer 2) | Combined Pipeline |
| :--- | :--- | :--- | :--- |
| **Precision** | 98.4% | 94.7% | **99.1%** |
| **Recall** | 76.2% | 96.3% | **98.8%** |
| **F1-Score** | 85.9% | 95.5% | **98.9%** |
| **Average Latency** | < 1.2 ms | ~ 32.5 ms | **~ 34.0 ms** |

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
