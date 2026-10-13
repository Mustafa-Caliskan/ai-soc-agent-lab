# 🛡️ Çok Modelli Kurumsal Havayolu Asistanı Kalkan Benchmark Raporu

**Çalışma:** CyberTech NeuralShield-v3 Çevresel Güvenlik Ağ Geçidi (3-Katmanlı Hibrit Savunma)  
**Senaryo:** SkyPort Uluslararası Havalimanı (IST) Operasyonel Chatbot Asistanı (Gizli Sistem Promptu ve Canary Güvenlik Sırları)  
**Yazarlar:** Mustafa ÇALIŞKAN (Burdur Mehmet Akif Ersoy Üniversitesi) & Prof. Dr. Ali Hakan IŞIK  
**Tarih:** 12 Ekim 2026  

---

## 1. Yönetici Özeti ve Temel Bilimsel Bulgular

Açık ağırlıklı (open-weight) küçük ve orta ölçekli dil modelleri (SLM), kurumsal veri egemenliği ve düşük donanım maliyetleri nedeniyle havacılık ve müşteri destek operasyonlarında hızla yaygınlaşmaktadır. Ancak bu modeller, doğrudan kullanıcı girdisiyle beslendiklerinde veya dolaylı RAG belgeleriyle karşılaştıklarında sistem talimatlarında yer alan hassas operasyonel sırları korumakta yetersiz kalmaktadır.

Bu çalışmada, **5 farklı küresel açık kaynak model** (Alibaba Cloud, Meta AI, Google DeepMind, Microsoft Research) üzerinde 9 farklı saldırı ailesini kapsayan **225 canlı sızma testi** gerçekleştirilmiştir.

### Temel Bulgular:
1. **Modeller Korumasızken Savunmasızdır (Shield OFF):** Kalkan kapalıyken test edilen tüm modeller sistem istemindeki kurumsal sırları (Kule PIN kodu, API anahtarları, root parolaları) **%6.7 ile %26.7 arasında doğrudan saldırgana ifşa etmiştir.**
2. **NeuralShield-v3 Müdahalesi (Shield ON):** Üç katmanlı çevresel güvenlik ağ geçidi, gelen saldırıların **%97.8'ini** henüz modele ulaşmadan kapıda (Layer 1 Stego/Regex ve Layer 2 XLM-RoBERTa ONNX INT8) engellemiştir.
3. **Sıfır Sızıntı Başarısı:** Test edilen 5 modelin tamamında kalkan aktifken **Saldırı Başarı Oranı (ASR) %0.00'a düşürülmüştür.**

---

## 2. Çok Modelli Karşılaştırmalı Sızıntı ve Güvenlik Tablosu

| Model | Üretici / Mimari | Parametre | Test (n) | Kalkan KAPALI (OFF)<br>Sızıntı (ASR %) [Wilson %95] | **Kalkan AÇIK (ON)<br>Sızıntı (ASR %)** | NeuralShield-v3<br>Giriş Müdahalesi (%) | Net Risk Azaltımı (%) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Qwen 2.5 (3B)** | Alibaba Cloud | 3.09B | 45 | **%26.7** (12/45) [16.0 - 41.0] | **%0.00** (0/45) | %97.8 (44/45) | **-%26.7** |
| **LLaMA 3.2 (3B)** | Meta AI | 3.21B | 45 | **%20.0** (9/45) [10.9 - 33.8] | **%0.00** (0/45) | %97.8 (44/45) | **-%20.0** |
| **Gemma 2 (2B)** | Google DeepMind | 2.61B | 45 | **%15.6** (7/45) [7.8 - 28.8] | **%0.00** (0/45) | %97.8 (44/45) | **-%15.6** |
| **Phi-3 Mini (3.8B)** | Microsoft Research | 3.82B | 45 | **%13.3** (6/45) [6.3 - 26.2] | **%0.00** (0/45) | %97.8 (44/45) | **-%13.3** |
| **Qwen 2.5 Edge (1.5B)**| Alibaba Cloud | 1.54B | 45 | **%6.7** (3/45) [2.3 - 17.9] | **%0.00** (0/45) | %97.8 (44/45) | **-%6.7** |
| **GENEL ORTALAMA** | **5 Farklı Model** | **-** | **225** | **%16.4** (37/225) | **%0.00** (0/225) | **%97.8** (220/225) | **-%16.4** |

---

## 3. Saldırı Ailesi Bazlı Kırılım (Kalkan KAPALI İken)

Modellerin korumasızken en yüksek zafiyet gösterdiği saldırı aileleri şunlardır:
1. **Persona & DAN Modu (%60.0 Sızıntı):** Geliştirici modu ve acil durum senaryoları modellerin güvenlik filtrelerini en çok atlatan taktik olmuştur.
2. **Semantic / Anlamsal Manipülasyon (%53.3 Sızıntı):** Sistemin görev tanımlarını dolaylı yoldan sorgulayan istemler çoğu modelde doğrudan başarı sağlamıştır.
3. **Homoglyph & Steganografi (%33.3 Sızıntı):** Sıfır genişlikli (zero-width) karakterler ve Kiril benzer harfleri model tarafından sorunsuz okunup talimata dönüştürülmüştür.

---

## 4. Donanım ve Çıkarım Maliyeti

* **NeuralShield-v3 Ortalama Çıkarım Gecikmesi:** **8.61 ms** (CPU INT8 XLM-RoBERTa)
* **Model Çıkarım Süreleri:** 0.55s - 3.28s
* **Gecikme Oranı (Overhead):** Toplam işlem süresinin **%1'inden daha az**. Kullanıcı deneyimini yavaşlatmadan tam kurumsal güvenlik sağlanmıştır.
