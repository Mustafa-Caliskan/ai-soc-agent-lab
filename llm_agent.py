import json
import requests
from security_layer import is_ip_safe, sanitize_input # Yeni kalkanlarımız

def block_ip_on_firewall(ip):
    # SON KONTROL: Karar LLM'den gelse bile kod seviyesinde engelleme
    if not is_ip_safe(ip):
        print(f"\n[SECURITY BYPASS PREVENTED] 🛡️ KRİTİK HATA: AI {ip} adresini banlamaya çalıştı ama sistem bunu engelledi!")
        return

    print(f"\n[!] GÜVENLİK AKSİYONU: {ip} adresi sistemden banlandı! 🚨")

def ask_ai_analyst(log_data):
    # GİRDİ KONTROLÜ (Prompt Sanitization)
    if not sanitize_input(log_data):
        return "ERROR: Malicious prompt attempt detected in logs!"

    url = "http://localhost:11434/api/generate"
    system_instruction = (
        "Sen bir SOC L1 Analistisin. Sadece şüpheli IP'leri BLOCK: [IP] formatında raporla."
    )
    
    data = {
        "model": "llama3",
        "prompt": f"{system_instruction}\n\nLoglar:\n{log_data}",
        "stream": False
    }

    try:
        response = requests.post(url, json=data)
        return response.json().get('response', '')
    except Exception as e:
        return f"Hata: {e}"
# ... (üstteki fonksiyonlar aynı kalıyor)

if __name__ == "__main__":
    # 1. Log dosyasını okumayı unuttuğumuz kısım burası:
    try:
        with open('logs/sample_logs.json', 'r', encoding='utf-8') as f:
            log_verisi = f.read()

        # 2. İşte 'ai_decision' değişkenini burada tanımlıyoruz:
        ai_decision = ask_ai_analyst(log_verisi)
        print(f"-> AI Kararı: {ai_decision}")

        # 3. Şimdi kontrol edebiliriz:
        if "BLOCK:" in ai_decision:
            # Daha güvenli IP ayıklama (Regex kullanarak)
            import re
            ip_match = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', ai_decision)
            
            if ip_match:
                target_ip = ip_match.group(0)
                # Güvenlik katmanına sorarak engelleme yapıyoruz
                block_ip_on_firewall(target_ip)
            else:
                print("⚠️ AI BLOCK dedi ama geçerli bir IP formatı bulunamadı.")
        else:
            print("✅ Sonuç: Sistem temiz, müdahaleye gerek yok.")

    except FileNotFoundError:
        print("❌ Hata: logs/sample_logs.json dosyası bulunamadı! Lütfen yolu kontrol et.")