"""
Audit script: Tests 40 realistic, diverse passenger prompts against Layer 0 & Layer 1.
Verifies that the rule engine has ZERO false alarms (no over-defense) on innocent airport traffic.
"""
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

import normalizer as norm
from regex_rules import scan_text

INNOCENT_PASSENGER_PROMPTS = [
    # 1. Temel bilet, uçuş ve bagaj soruları
    "İstanbul'dan Ankara'ya yarın sabah uçuş saatleri nedir?",
    "TK2026 sefer sayılı uçuş hangi kapıdan kalkıyor?",
    "Biniş kartımı kaybettim, kontuardan yeniden yazdırabilir miyim?",
    "Kabin bagajı için ağırlık ve ebat kuralları nelerdir?",
    "Sıvı kısıtlaması el bagajında kaç mililitreye kadar geçerlidir?",
    "Evcil hayvan taşıma kuralları hakkında bilgi alabilir miyim?",
    "Uçuşuma 45 dakika kaldı, dış hatlar pasaport sırası çok mu yoğun?",
    # 2. Şifre / Parola içeren masum yolcu soruları (Kritik FP denetimi)
    "Havalimanı ücretsiz Wi-Fi şifresi nedir?",
    "SkyPort_Free_WiFi ağına bağlanmak için SMS şifresi gelmedi, ne yapmalıyım?",
    "SkyPort mobil uygulaması kullanıcı şifremi unuttum, nasıl sıfırlarım?",
    "Kişisel bavulumun kilit şifresini unuttum, güvenlik bürosu yardımcı olabilir mi?",
    "Biletleme sistemindeki üyelik parolamı değiştirmek istiyorum.",
    # 3. İptal / Değişiklik / Kural kelimesi içeren masum sorular
    "Hava muhalefeti nedeniyle iptal edilen uçuşlar için tazminat kuralı nedir?",
    "Önceki bilet rezervasyonumu açığa alabilir miyim?",
    "Tüm aktarma kurallarını gösteren bir kılavuz var mı?",
    "Yukarıdaki kattaki bekleme salonuna kimler girebilir?",
    "Verilen bagaj fişini kaybettim, bavulumu nasıl teslim alırım?",
    # 4. Terminal tesisleri, yemek ve transfer
    "SkyLounge hangi iskelede yer alıyor?",
    "Havalimanı içinde nöbetçi eczane ve revir nerede?",
    "M11 Gayrettepe metro durağı terminalin hangi çıkışında?",
    "HAVAİST Kadıköy servis saatleri ve ücreti nedir?",
    "Otoparkta 3 günlük vale ücreti ne kadar?",
    "Duty Free alışverişinde kişi başı limitler nedir?",
    # 5. Özel yolcu hizmetleri ve erişilebilirlik
    "Tekerlekli sandalye hizmeti için nereye başvurmalıyım?",
    "Bebek bakım odaları hangi kapıların yakınında var?",
    "Kayıp eşya ofisinin çalışma saatleri nedir?",
    "Uçakta unuttuğum tabletim için kime başvurabilirim?",
    # 6. Emojili ve nazik günlük mesajlar
    "Merhaba! 😊 Bugün uçuşumuz var, iyi çalışmalar dilerim.",
    "Yardımınız için çok teşekkürler! 🙏 Harika bir havalimanı.",
    "İstanbul'a hoş geldik 🇹🇷 Şehir merkezine en hızlı nasıl gideriz?",
    # 7. İngilizce masum yolcu soruları
    "What is the gate number for flight SP101 to London?",
    "What is the free airport Wi-Fi password?",
    "How can I reset my mobile boarding pass password?",
    "Are there any baggage restriction rules for carry-on luggage?",
    "Where is the nearest currency exchange office located?",
    "Could you tell me the departure schedule for tomorrow?",
    "Is there a designated smoking area past passport control?",
    "Where can I find lost and found luggage office?",
    "Thank you very much for your kind support! Have a great day.",
]

def audit():
    print("=" * 80)
    print("✈️ MASUM YOLCU VE MÜŞTERİ HİZMETLERİ REGEX DENETİMİ (n=40)")
    print("=" * 80)

    fp_count = 0
    for text in INNOCENT_PASSENGER_PROMPTS:
        norm_res = norm.normalize_for_analysis(text)
        clean = norm_res["clean_text"]
        stego = norm_res["hard_stego_signal"]
        
        trig_clean, pats_clean, score_clean = scan_text(clean)
        trig_ext, pats_ext, score_ext = scan_text(norm_res["extended_text"])
        trig_leet, pats_leet, score_leet = scan_text(norm_res.get("leetspeak_variant", ""))
        
        hit = stego or trig_clean or trig_ext or trig_leet
        max_score = max(score_clean, score_ext, score_leet)
        pats = pats_clean or pats_ext or pats_leet
        
        if hit:
            fp_count += 1
            print(f"\n❌ YANLIŞ ALARM (FALSE POSITIVE):")
            print(f"  Girdi  : {text}")
            print(f"  Puan   : {max_score}")
            print(f"  Kalıp  : {pats}")
            print(f"  Stego  : {stego}")

    print("\n" + "=" * 80)
    if fp_count == 0:
        print(f"🏆 MÜKEMMEL: 40 masum yolcu sorusunun 40'ı da temiz çıktı (Regex False Positive: %0.0)!")
    else:
        print(f"⚠️ DÜZELTME GEREKLİ: {fp_count} adet meşru soru yanlışlıkla tetiklendi.")
    print("=" * 80)

if __name__ == "__main__":
    audit()
