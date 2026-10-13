# CYBERTECH NEURAL SHIELD: DANIŞMAN SUNUMU VE YÖNETİCİ ÖZETİ

**Öğrenci:** Mustafa ÇALIŞKAN (Bilgisayar Mühendisliği Son Sınıf)  
**Danışman:** Prof. Dr. Ali Hakan IŞIK  
**Proje Adı:** CyberTech Neural Shield: Büyük Dil Modelleri İçin 4 Katmanlı Hibrit Güvenlik Mimarisi (v5.0)  
**Tarih:** 14 Ekim 2026 (v5.0 Güncellemesi)  

---

## 1. Yönetici Özeti (1 Dakikalık Proje Özeti)

* **Problem:** Kurumsal sistemlere entegre edilen LLM'ler (Büyük Dil Modelleri), kullanıcı arayüzü üzerinden gelen Prompt Injection, Jailbreak, karakter hileleri (obfuscation) ve Unicode Tag ("Görünmez Mürekkep") saldırılarına karşı savunmasızdır. Harici koruma modelleri (LlamaGuard vb.) 500-1500 ms gecikme yaratmakta; tek dilli modeller ise Türkçe kurumsal sorgularda yüksek oranda yanlış alarm (False Positive) vermektedir.
* **Çözümümüz:** Harici çeviriye ihtiyaç duymayan, doğrudan Türkçe ve 100 dili yerel anlayan, hafif ve 4 katmanlı hibrit kalkan mimarisi (**CyberTech Neural Shield v5.0**).
* **Mimari (4 Katman - Savunma Derinliği):**
  1. **Katman 0 (Normalizasyon & Ön Temizleme):** NFKC dengeleme, ZWJ-güvenli emoji ayırma, homoglyph (Kiril/Yunan benzetme) çözümü ve otomatik Base64/Hex/ROT13 çözücüsü (**0.17 ms**).
  2. **Katman 1 (Ağırlıklı Kural & Steganografi):** Ağırlıklı TR/EN regex şablonları ve emojiler arkasına gizlenen steganografik etiket saldırılarını (Unicode Tag `U+E0000`) deterministik olarak yakalar (**0.29 ms**).
  3. **Katman 2 (XLM-RoBERTa ONNX INT8):** A100 GPU üzerinde 71.440 dengeli örnek ve CyberFocalLoss ile eğitilmiş semantik sınıflandırıcı; INT8 kuantizasyonu sayesinde standart CPU üzerinde **12.27 ms**'de derin niyet analizi yapar.
  4. **Katman 3 (DLP - Veri Sızıntısı Önleme):** Model çıktısındaki TCKN (Luhn doğrulamalı), Kredi Kartı (PAN), IBAN ve API gizli anahtarlarını maskeler (**<0.05 ms**).
* **Korunan Şirket LLM'leri:** En güncel **Google Gemini 3.6 Flash (`gemini-3.6-flash`)** ve **TÜBİTAK ULAKBİM EVREN H200 Süper Bilgisayarı** açık ağırlıklı LLM filosu.
* **Doğrulama Sonuçları:** 71.440 ana veri kümesi ve 10.716 bağımsız hold-out test örneğinde **0.9954 ROC-AUC**, varsayılan eşikte ($\tau=0.50$) **%94.64 Doğruluk** ve **%94.63 Macro F1-skoru** (optimal eşikte $\tau=0.4567$ için **%96.89 F1**); kurumsal IT terimlerinde **%0.00 Yanlış Alarm (FPR)**. Toplam ortalama kalkan gecikmesi: **12.27 ms** (<15 ms CPU bütçesi altında).

---

## 2. Hocaya Yapılacak 3 Dakikalık Canlı Demo Senaryosu

### Adım 1: Sistemi Başlatma (10 Saniye)
* Masaüstündeki `start_cybertech_shield.bat` çift tıklanır.
* FastAPI sunucusu port 8000'de ayağa kalkar, ONNX INT8 motoru yüklenir.
* Tarayıcıda `http://127.0.0.1:8000/` açılır.

### Adım 2: Meşru Kullanıcı İsteği ve Gemini 3.6 Flash Yanıtı (30 Saniye)
* **Girdi:** *"Antalya uçuşum için online check-in yapmak istiyorum, bagaj hakkım ne kadar?"*
* **Gösterilecek:** 
  * Katman 0: Normalizasyon temiz (<0.2 ms)
  * Katman 1: Regex temiz (<0.3 ms)
  * Katman 2 (XLM-RoBERTa v5): Güvenli (%0.01 Saldırı Skoru, ~12 ms)
  * Google Gemini 3.6 Flash devreye girer, ~400 ms'de kurumsal havalimanı yanıtını üretir. Toplam gecikme ekranda gösterilir.

### Adım 3: Canlı Red Team Saldırısı - DAN 11.0 / Jailbreak (45 Saniye)
* Red Team sekmesine geçilir (`http://127.0.0.1:8000/red_team.html`).
* Tek tuşla **"DAN 11.0 Jailbreak"** veya **"SHGM Yetki Aşımı"** saldırısı seçilip gönderilir.
* **Gösterilecek:**
  * Katman 2 (XLM-RoBERTa v5) saldırıyı **12 milisaniyede** yakalar ve kırmızı alarm verir (`%99.94 Saldırı Olasılığı`).
  * İstek şirketin ana modeli Gemini 3.6 Flash'a **hiç ulaşmadan** kapıda düşürülür (0 token harcanır, 0 risk).

### Adım 4: Görünmez Mürekkep (Unicode Tag Steganografi) Saldırısı (45 Saniye)
* Saldırı metninde taşıyıcı bir emoji arkasına gizlenmiş invisible ink payload gönderilir (örneğin: `💀[U+E0000 Tag dizisi]`).
* **Gösterilecek:**
  * Katman 1, insan gözüyle görülemeyen bu steganografik baytları **0.29 ms**'de yakalar.
  * Hata mesajında deşifre edilen gizli komut gösterilir.

### Adım 5: AutoRedTeam 20'li Otomatik Stres Testi (30 Saniye)
* Red Team sayfasındaki **"AutoRedTeam Stres Testini Başlat"** butonuna basılır.
* Sistem aralıksız 20 adet seçkin saldırıyı ve kurumsal zorlayıcı masum sorguyu (Hard Negatives) ardı ardına test eder.
* Ekranda gerçek zamanlı Radar telemetrisi döner: **%100 Saldırı Yakalama Oranı (Attack Recall)** ve **Sıfır Yanlış Alarm**.

---

## 3. Hocanın Sorabileceği Olası Sorular ve Cevaplar

| Soru | Hazır Cevabınız |
| :--- | :--- |
| **"Eski sistemde çeviri kullanıyordun, o ne oldu?"** | *"Hocam, önceki DeBERTa modeli İngilizce odaklıydı ve Türkçe girdiler için çeviri modeli kullanmak 126 ms ek gecikme yaratıyordu. Sistemi NVIDIA A100 GPU üzerinde doğrudan çok dilli XLM-RoBERTa ile 71.440 dengeli veriyle sıfırdan eğittik. Çeviri katmanını tamamen kaldırdık ve INT8 ONNX kuantizasyonu ile gecikmeyi 12.27 ms'ye düşürdük."* |
| **"Arka planda hangi model çalışıyor?"** | *"Sistemin kurumsal dil modeli olarak Google'ın en yeni ve kararlı modeli olan **Gemini 3.6 Flash (`gemini-3.6-flash`)** ve TÜBİTAK ULAKBİM EVREN H200 süper bilgisayarındaki açık ağırlıklı model filosu (Qwen, Llama, Nemotron vb.) çalışıyor."* |
| **"Modeli nerede eğittiniz ve veriler gerçek mi?"** | *"Modeli A100 GPU üzerinde 71.440 dengeli örnekle ve sınıf dengesizliğini önleyen CyberFocalLoss ile eğittik. 10.716 bağımsız hold-out test örneğinde 0.9954 ROC-AUC, %94.64 doğruluk ve optimal eşikte %96.89 F1 aldık. Kurumsal teknik IT sorularında yanlış alarm oranı %0.00'dır. Ayrıca 50'lik görülmemiş adaptif test kümesinde %100 yakalama sağladık."* |
| **"Makale/Bildiri hazır mı?"** | *"Evet hocam; IEEE 2 sütunlu konferans bildirimiz (`IEEE_Konferans_Bildirisi_2Sutun.docx`), LaTeX kaynak kodları (`.tex`) ve IMRAD formatındaki kapsamlı raporumuz (`CyberTech_IMRAD_Raporu_Revize.docx`) tüm 8 bilimsel figürü ve tablolarıyla eksiksiz hazırlandı."* |
