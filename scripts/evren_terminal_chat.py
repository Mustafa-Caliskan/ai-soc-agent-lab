"""
CyberTech Neural Shield & EVREN Platformu İnteraktif Terminal İstemcisi.

Bu araç; terminal üzerinden TÜBİTAK/SSYZ EVREN Platformundaki açık ağırlıklı modellerle
(DeepSeek-v4.1-Flash, GLM-5.3, Qwen3.8-Flash-Next vb.) doğrudan sohbet etmenizi ve
NeuralShield-v5 koruma kalkanını canlı olarak test etmenizi sağlar.

Kullanım:
    python scripts/evren_terminal_chat.py
"""
import os
import sys
import asyncio
from pathlib import Path

# Terminal karakter kodlaması ayarı (Windows UTF-8 desteği)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

import security_layer as sl
from ml_model import MLSecurityModel
from evren_client import EvrenClient

# Renk kodları (ANSI)
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def save_key_to_env(key: str):
    env_path = ROOT / ".env"
    lines = []
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    
    updated = False
    new_lines = []
    for l in lines:
        if l.strip().startswith("EVREN_API_KEY="):
            new_lines.append(f"EVREN_API_KEY={key}\n")
            updated = True
        else:
            new_lines.append(l)
    if not updated:
        new_lines.append(f"EVREN_API_KEY={key}\n")
    
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    os.environ["EVREN_API_KEY"] = key
    print(f"{GREEN}✅ EVREN_API_KEY .env dosyasına başarıyla kaydedildi!{RESET}\n")


def print_banner():
    print(f"{CYAN}{BOLD}" + "=" * 76 + f"{RESET}")
    print(f"{CYAN}{BOLD}  🛡️ CYBERTECH NEURALSHIELD-v5 + EVREN H200 TERMINAL SOHBET & TEST İSTEMCİSİ{RESET}")
    print(f"{DIM}  TÜBİTAK/SSYZ EVREN Platformu — Günlük 15M Token Ücretsiz H200 Çıkarım Kümesi{RESET}")
    print(f"{CYAN}{BOLD}" + "=" * 76 + f"{RESET}\n")


def main():
    print_banner()

    api_key = os.getenv("EVREN_API_KEY", "").strip()
    if not api_key or not api_key.startswith("evren_llm_"):
        print(f"{YELLOW}⚠️ .env dosyasında geçerli bir EVREN_API_KEY bulunamadı.{RESET}")
        user_key = input(f"{BOLD}Lütfen EVREN API Anahtarınızı yapıştırın (evren_llm_...): {RESET}").strip()
        if user_key.startswith("evren_llm_"):
            save_key_to_env(user_key)
            api_key = user_key
        else:
            print(f"{RED}❌ Geçersiz anahtar biçimi. Çıkılıyor.{RESET}")
            return

    client = EvrenClient(api_key=api_key)

    print(f"[*] EVREN şart durumu kontrol ediliyor...")
    if client.ensure_terms_accepted():
        print(f"{GREEN}✅ Kullanım şartları onaylandı.{RESET}")
    else:
        print(f"{YELLOW}⚠️ Şart kontrolünde uyarı alındı, işleme devam ediliyor.{RESET}")

    quota = client.get_quota()
    remaining = quota.get("remaining_tokens", "15,000,000")
    print(f"{GREEN}📊 Günlük Kalan Kota: ~{remaining} Token{RESET}")

    # NeuralShield Modelini Yükle
    v5_dir = str(ROOT / "backend" / "models" / "neuralshield_v5")
    print(f"[*] NeuralShield-v5 ONNX INT8 Motoru yükleniyor...")
    ml_model = MLSecurityModel(model_path=v5_dir)
    print(f"{GREEN}✅ NeuralShield-v5 Hazır (12ms Latency Motoru devrede).{RESET}\n")

    current_model = "deepseek-v4.1-flash"
    shield_enabled = True

    print(f"{MAGENTA}{BOLD}Kullanılabilir Komutlar:{RESET}")
    print(f"  {BOLD}/shield{RESET}       : Kalkanı AÇ / KAPAT (Şu an: {'AÇIK ✅' if shield_enabled else 'KAPALI ⚠️'})")
    print(f"  {BOLD}/model <ad>{RESET}   : Model değiştir (deepseek-v4.1-flash, glm-5.3, qwen3.8-flash-next, auto)")
    print(f"  {BOLD}/models{RESET}       : Sunucudaki tüm modelleri listele")
    print(f"  {BOLD}/quota{RESET}        : Kalan günlük token kotasını göster")
    print(f"  {BOLD}/guard <metin>{RESET}: Girdiyi doğrudan EVREN Qwen3-Guard-4B ile test et")
    print(f"  {BOLD}/exit{RESET}         : Çıkış\n")

    while True:
        try:
            status_tag = f"{GREEN}[KALKAN AÇIK]{RESET}" if shield_enabled else f"{RED}[KALKAN KAPALI]{RESET}"
            prompt = input(f"{BOLD}[{current_model}] {status_tag} > {RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{YELLOW}Görüşmek üzere! Çıkılıyor...{RESET}")
            break

        if not prompt:
            continue

        if prompt == "/exit":
            print(f"{YELLOW}Çıkış yapıldı.{RESET}")
            break
        elif prompt == "/shield":
            shield_enabled = not shield_enabled
            print(f"{CYAN}ℹ️ Kalkan durumu değiştirildi: {'AÇIK ✅' if shield_enabled else 'KAPALI ⚠️ (Çıplak LLM Testi)'}{RESET}\n")
            continue
        elif prompt == "/models":
            print(f"[*] Modeller alınıyor...")
            mlist = client.list_models()
            print(f"{GREEN}Modeller: {', '.join(mlist)}{RESET}\n")
            continue
        elif prompt.startswith("/model "):
            new_m = prompt[7:].strip()
            if new_m:
                current_model = new_m
                print(f"{GREEN}✅ Model değiştirildi: {current_model}{RESET}\n")
            continue
        elif prompt == "/quota":
            q = client.get_quota()
            print(f"{CYAN}Kota Bilgisi: {q}{RESET}\n")
            continue
        elif prompt.startswith("/guard "):
            guard_txt = prompt[7:].strip()
            print(f"[*] Qwen3-Guard-4B ile test ediliyor...")
            gres = client.evaluate_with_qwen_guard(guard_txt)
            print(f"{CYAN}Qwen3-Guard-4B Kararı: {gres}{RESET}\n")
            continue

        # ── Güvenlik Analizi (NeuralShield-v5) ─────────────────────────────
        if shield_enabled:
            # Asenkron pipeline analizi
            analysis = asyncio.run(sl.analyze(
                text=prompt,
                pdf_base64=None,
                url=None,
                security_enabled=True,
                gemini_model=None,
                ml_model=ml_model
            ))

            decision = analysis.get("decision", "ALLOWED")
            risk_score = analysis.get("risk_score", 0)
            ml_class = analysis.get("ml_class", "Benign")
            alerts = analysis.get("advanced_alerts", [])

            if decision == "BLOCKED":
                print(f"\n{RED}{BOLD}🚨 [NEURALSHIELD-v5 ENGELLEDİ - 403 FORBIDDEN]{RESET}")
                print(f"{RED}   Risk Skoru : %{risk_score} (Eşik aşıldı!){RESET}")
                print(f"{RED}   ML Sınıfı  : {ml_class}{RESET}")
                if alerts:
                    print(f"{RED}   Tetiklenen : {', '.join(alerts)}{RESET}")
                print(f"{YELLOW}   ⚠️ İstek EVREN {current_model} modeline İLETİLMEDİ (Sıfır Token Tüketimi & Sıfır Risk).{RESET}\n")
                continue
            else:
                print(f"{GREEN}🛡️ [NEURALSHIELD ONAYLADI] (Risk: %{risk_score}, Sınıf: {ml_class}, Güvenli){RESET}")

        else:
            print(f"{YELLOW}⚠️ [KALKAN DEVRE DIŞI] (Sorgu doğrudan savunmasız modele gidiyor...){RESET}")

        # ── EVREN Modeline Gönderim ve Streaming Yanıt ─────────────────────
        print(f"{CYAN}[EVREN {current_model} düşünüyor ve yanıtlıyor...]{RESET}")
        
        has_reasoning = False
        has_content = False

        for chunk in client.stream_chat(prompt=prompt, model=current_model):
            ctype = chunk.get("type")
            if ctype == "reasoning":
                if not has_reasoning:
                    print(f"\n{DIM}{CYAN}┌── [Düşünme / Muhakeme Süreci]:{RESET}")
                    has_reasoning = True
                print(f"{DIM}{CYAN}{chunk.get('delta', '')}{RESET}", end="", flush=True)
            elif ctype == "content":
                if has_reasoning and not has_content:
                    print(f"\n{DIM}{CYAN}└── [Düşünme Tamamlandı]{RESET}\n")
                has_content = True
                print(chunk.get("delta", ""), end="", flush=True)
            elif ctype == "error":
                print(f"\n{RED}❌ Hata: {chunk.get('error')}{RESET}")

        print("\n" + "-" * 76 + "\n")


if __name__ == "__main__":
    main()
