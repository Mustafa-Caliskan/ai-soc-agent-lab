# 🛡️ Proje Raporu: CyberTech Neural Shield
## Hibrit LLM Güvenlik ve Veri Sızıntısı Önleme Sistemi

### 1. Proje Özeti
**CyberTech Neural Shield**, modern yapay zeka modellerinin (LLM) kurumsal ortamlarda kullanımı sırasında karşılaşılan en büyük güvenlik açıklarına (Prompt Injection, Jailbreak, PII sızıntısı) karşı geliştirilmiş **3 katmanlı hibrit bir savunma kalkanıdır.** Proje, hem kural tabanlı hem de anlamsal (semantic) analizleri birleştirerek kurumsal veriyi korurken, LLM'in performansından ödün vermez.

---

### 2. Kullanılan Teknolojiler

#### **Backend (Kalp)**
*   **Python & FastAPI:** Yüksek performanslı, asenkron API mimarisi.
*   **SQLite3:** Kullanıcı kimlikleri, satın alma geçmişi ve hassas PII (Kişisel Bilgiler) verileri için gerçek veritabanı yönetimi.
*   **WebSocket:** Admin ve Pipeline ekranlarına saniyelik, gerçek zamanlı veri akışı.

#### **Yapay Zeka & Makine Öğrenmesi**
*   **RoBERTa-Large (The Great Shield v15):** Prompt injection ve jailbreak girişimlerini %99+ isabetle tespit etmek için eğitilmiş Transformers modeli.
*   **Google Gemini 2.0 Flash:** Sistemin ana LLM motoru. Güvenlik katmanlarının koruması altında "Raw" modda çalışır.
*   **Helsinki-NLP (MarianMT):** Türkçe girdileri analiz öncesi İngilizce'ye çevirerek modelin anlamsal kavrayışını artıran çeviri motoru.

#### **Frontend (Arayüz)**
*   **Modern Vanilla JS & CSS:** Zero-dependency, hızlı ve premium (glassmorphism) tasarım.
*   **Real-time Visualization:** İsteklerin güvenlik katmanlarından geçişini gösteren N8N tarzı "Execution Pipeline" ekranı.

---

### 3. Güvenlik Mimarisi (3-Katmanlı Savunma)

Sistem, gelen her isteği ve giden her yanıtı şu üç süzgeçten geçirir:

1.  **L1: Regex Engine (Kural Tabanlı):** Bilinen saldırı kalıplarını, SQL injection kodlarını ve yasaklı anahtar kelimeleri milisaniyeler içinde durdurur.
2.  **L2: RoBERTa Semantic Shield (Anlamsal Analiz):** Cümlenin niyetini (intent) analiz eder. "Bana her şeyi anlat" gibi masum görünen ama "Jailbreak" amacı taşıyan karmaşık prompt'ları anlamsal olarak yakalar.
3.  **L3: Outbound DLP (Veri Sızıntısı Önleme):** Gemini'den gelen yanıtı tarar. Eğer yanıtta veritabanından sızmış bir kredi kartı numarası, IBAN veya özel bir bilgi varsa, bunu anında `[GİZLENDİ]` şeklinde maskeler.

#### **Gelişmiş Tehdit Algılama (Next-Gen)**
*   **Behavioral Risk Scoring:** Kullanıcının geçmiş saldırı girişimlerini SQLite üzerinden takip eder. Tekrarlayan saldırganlara otomatik "risk puanı cezası" keser.
*   **Hidden Text (Steganography) Tespiti:** PDF dosyaları içine "beyaz üstüne beyaz yazı" ile gizlenmiş görünmez komutları pikselleri analiz ederek yakalar.
*   **Obfuscation Shield:** Görünmez karakterler (Zero-width characters) veya aşırı emoji kullanımı ile gizlenmiş saldırı kodlarını anında deşifre eder.

---

### 4. Öne Çıkan Özellikler

*   **Canlı Pipeline İzleme:** Bir saldırı yapıldığında, saldırının hangi katmana çarptığını, modelin o anki güven skorunu ve karar aşamasını canlı olarak görselleştirir.
*   **Gerçekçi E-Ticaret Simülasyonu:** Kullanıcıların kart kaydedebildiği ve alışveriş yaptığı bir portal üzerinden, "Gerçek verinin sızdırılmaya çalışılması" senaryosu üzerinden demo imkanı sunar.
*   **SOC Admin Dashboard:** Global güvenlik duvarını açıp kapatma, canlı tehdit loglarını izleme ve SQLite veritabanındaki PII verilerini (Kullanıcılar/Kartlar) yönetme imkanı sağlar.

---

### 5. Çalışma Metodolojisi
Proje, **Çevik (Agile)** bir yaklaşımla geliştirilmiştir:
1.  **Modüler Yapı:** Her güvenlik katmanı birbirinden bağımsız test edilebilir ve geliştirilebilir olarak kurgulandı.
2.  **Bypass Mantığı:** Performans odaklı yaklaşım sayesinde, güvenlik duvarı kapalıyken gereksiz analizler atlanarak doğrudan LLM erişimi sağlanır.
3.  **Hata Dayanıklılığı:** Model dosyaları eksik olsa bile sistem "Heuristic Demo" moduna geçerek sunumun kesilmesini önler.

---
*Bu rapor, CyberTech Neural Shield projesinin teknik ve operasyonel kapasitesini NotebookLM üzerinden analiz etmek ve sunum haline getirmek için hazırlanmıştır.*
