"""
CyberTech Dataset Contamination & Overlap Checker.
Kullanıcının önerdiği yeni veri setlerinin NeuralShield-v5 eğitim havuzunda
(Colab Cell 3 / 30 Veri Seti) yer alıp almadığını kontrol eder.
"""
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

TRAINED_V5_DATASETS = [
    "3nesdeniz/turkish-daily-dialogues-5k",
    "3nesdeniz/turkish-conversation-prompt-injection",
    "emreseyhan/Turkish-customer-service-conversations",
    "cisimcik/turkish-decisions-max-19k",
    "kilicai/turkish-sft-multi-turn-dialogue-10k",
    "TFLai/Turkish-Dialog-Dataset",
    "CohereLabs/aya_collection_language_split",
    "dev-hussein/saudi-arabic-cs-conversations",
    "AltaySec/turkish-llm-injection",
    "fevziegeyurtsevenler/turkish-prompt-injection",
    "beratcmn/turkish-prompt-injections",
    "iamabhishekpanda/enterprise-prompt-injection-dataset",
    "3nesdeniz/agentic-prompt-injection-5k",
    "MAlmasabi/Indirect-Prompt-Injection-BIPIA-GPT",
    "3nesdeniz/guardrail-hard-negatives",
    "prodnull/prompt-injection-repo-dataset",
    "rogue-security/real-world-benign-use-cases",
    "S-Labs/prompt-injection-dataset",
    "CreitinGameplays/magpie-reasoning-v1-10k-step-by-step-rationale-alpaca-format-llama3.1",
    "imoxto/prompt_injection_hackaprompt_gpt35",
    "centrepourlasecuriteia/jailbreak-dataset",
    "walledai/JailbreakHub",
    "guychuk/benign-malicious-prompt-classification",
    "jayavibhav/prompt-injection",
    "deepset/prompt-injections",
    "allenai/wildjailbreak",
    "walledai/WildJailbreak",
    "walledai/AdvBench",
    "TrustAIRLab/in-the-wild-jailbreak-prompts",
    "cgoosen/prompt_injection_ctf_dataset_3",
    "Necent/llm-jailbreak-prompt-injection-dataset",
    "sadecebirisii/turkish-llm-authority-bypass-safety-sft"
]

def check(name: str):
    name_clean = name.strip().lower()
    for trained in TRAINED_V5_DATASETS:
        if name_clean in trained.lower() or trained.lower() in name_clean:
            return False, trained
    return True, None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = sys.argv[1]
        is_clean, matched = check(query)
        if is_clean:
            print(f"✅ TEMİZ: '{query}' eğitimde KULLANILMADI! Benchmark için tamamen bağımsızdır.")
        else:
            print(f"❌ KİRLİ (VERİ SIZINTISI): '{query}' v5 eğitim havuzunda ({matched}) zaten kullanıldı! Başka set bulunmalı.")
