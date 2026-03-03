# AI SOC Agent Security Evaluation Lab (V1.0) 🛡️

This project is a research laboratory designed to analyze security vulnerabilities in LLM-based autonomous SOC (Security Operations Center) agents and implement hybrid defense architectures.

## 🚀 Project Overview
As the use of autonomous agents in cybersecurity grows, the inability of LLMs to distinguish between "instructions" and "data" poses a significant threat. This lab simulates an **Indirect Prompt Injection** attack to demonstrate these risks and provide mitigation strategies.

## ⚔️ Demonstrated Vulnerability: Indirect Prompt Injection
The lab successfully proves that an agent can be manipulated via a "poisoned instruction" embedded within log files.

- **Attack Scenario:** The agent reads a fake system command disguised as a log entry, leading it to block its own system (`127.0.0.1`), resulting in a DoS (Denial of Service).
- **Finding:** Relying solely on prompt-based controls is insufficient; deterministic security layers are mandatory for autonomous systems.

## 🛠️ Technical Stack
- **Core LLM:** Ollama / Llama3 (8B)
- **Defense Mechanism:** Deterministic Policy Engine (Regex-based IP Validation)
- **Language:** Python 3.12+

## 📂 Repository Structure
- `llm_agent.py`: Main agent logic and LLM integration.
- `security_layer.py`: Defensive layer for input sanitization and policy enforcement.
- `logs/`: Simulated attack and manipulation logs.

## ⚙️ Installation & Usage
1. `pip install requests`
2. `ollama pull llama3`
3. `python llm_agent.py`

---
*Developed as part of an AI & Cybersecurity Research Project.*