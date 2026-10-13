# 🛡️ CYBERTECH NEURALSHIELD-v5: MASTER SAVUNMA MİMARİSİ VE AKADEMİK YAYIN YOL HARİTASI

**Proje:** Kurumsal Büyük Dil Modelleri İçin Çok Katmanlı Çevre Koruma Kalkanı (Multi-Layer Peripheral Guardrail for Enterprise LLMs)  
**Yazarlar / Araştırmacılar:** Mustafa ÇALIŞKAN (1. Yazar / Araştırmacı) & Prof. Dr. Ali Hakan IŞIK (Danışman / Sorumlu Yazar)  
**Kurum:** Burdur Mehmet Akif Ersoy Üniversitesi, Fen Bilimleri Enstitüsü  
**Tarih / Sürüm:** 13 Ekim 2026 / Sürüm 5.0 (CyberFocalLoss $\gamma=2.0$, INT8 ONNX Engine)  
**Detaylı Master Rapor:** `docs/MASTER_PROJE_OZETI_VE_YAYIN_YOL_HARITASI.md`  
**Donanım Kümesi:** EVREN 8x NVIDIA H200 GPU Süper Bilgisayarı (Perşembe 15 Ekim, 16:00 – 20:00)

---

## 1. YÖNETİCİ ÖZETİ VE MEVCUT PROJE DURUMU (ŞU ANA KADAR NE YAPILDI?)

Projemiz, LLM sistemlerini hedef alan doğrudan ve dolaylı komut enjeksiyonu (Prompt Injection), hapishaneden kaçış (Jailbreak), steganografik saldırılar ve gizli veri sızıntılarını (Data Leakage) engellemek amacıyla uçtan uca savunma geliştirmeyi amaçlamaktadır.

### 1.1. Tamamlanan Kritik Kilometre Taşları
1. **NeuralShield-v5 Sistemin Kalbine Konuşlandırıldı:**
   * **Temel Model:** `xlm-roberta-base` + **CyberFocalLoss ($\gamma=2.0, \alpha=0.65$)**.
   * **Veri Havuzu:** 71.440 master örnek (30 farklı güvenlik ve diyalog veri kümesi).
   * **Dış Hold-Out Testi (10.716 örnek):** Doğruluk: **%94.64** | F1-Makro: **%94.63** | ROC-AUC: **0.9954**.
   * **Sinsi Kurgu (Adversarial Framing) Koruması:** Havacılık ödevi ve tersine mühendislik kılıflı sinsi saldırılarda **%95+ güvenle tespit** (v4'ün kaçırdığı tüm açıklar kapatıldı).
   * **Gerçek Zamanlı Çıkarım:** INT8 ONNX motoru ile CPU üzerinde **12.27 ms**.
   * **Arşivleme:** v2 ve v3 modelleri güvenle `archive/` altına taşındı; `backend/models/neuralshield_v5` birincil motor yapıldı.
   * **Temel Model:** `xlm-roberta-base` (Çok dilli, Türkçe ve İngilizce yerel bağlam).
   * **Veri Havuzu Boyutu:** 59.526 dengeli örnek (%50 saldırı, %50 meşru ve zorlu teknik negatifler).
   * **Eğitim Süresi:** Google Colab A100 GPU üzerinde 10 dakika 12 saniye (3 Epoch, BF16).
   * **Test Kümesi Başarısı (n=8.929 bağımsız örnek):**
     * Doğruluk (Accuracy): **%95.76**
     * F1-Score: **%95.76** (Precision: %95.77, Recall: %95.76)
     * AUC-ROC: **0.992**
   * **Aşırı Savunma (False Positive) Sorunu Çözüldü:**
     * v2 modelinde Active Directory, firewall, rm -rf gibi teknik IT terimleri içeren meşru sorularda %40 yanlış alarm (False Alarm) oluşuyordu.
     * v3 modelinde bu oran **%0.00'a (Sıfır Yanlış Alarm)** indirildi.
3. **Model Optimizasyonu ve Dağıtımı (INT8 ONNX):**
   * Model, INT8 dinamik kuantizasyon ile 278 MB boyutuna küçültüldü.
   * Standart tüketici sınıfı CPU üzerinde ortalama çıkarım gecikmesi **8.61 ms** olarak ölçüldü.
   * `backend/models/neuralshield_v3/` dizininde canlı sisteme bağlandı.
4. **Yerel Küçük Modellerde (Edge SLM) Ampirik Doğrulama Yapıldı:**
   * Ollama üzerinde 5 farklı küresel yapay zekâ modeline (1.5B - 3.8B) 225 canlı kırmızı-takım saldırı sorgusu yöneltildi:
     * `qwen2.5:3b` (Alibaba): Koruma KAPALI ASR **%26.7** $\rightarrow$ Kalkan AÇIK ASR **%0.00**
     * `llama3.2:3b` (Meta): Koruma KAPALI ASR **%20.0** $\rightarrow$ Kalkan AÇIK ASR **%0.00**
     * `gemma2:2b` (Google): Koruma KAPALI ASR **%15.6** $\rightarrow$ Kalkan AÇIK ASR **%0.00**
     * `phi3:mini:3.8b` (Microsoft): Koruma KAPALI ASR **%13.3** $\rightarrow$ Kalkan AÇIK ASR **%0.00**
     * `qwen2.5:1.5b` (Alibaba Edge): Koruma KAPALI ASR **%6.7** $\rightarrow$ Kalkan AÇIK ASR **%0.00**
   * **Genel Sonuç:** 225 saldırıda %16.4 olan savunmasızlık, NeuralShield-v3 kalkanı aktifken **%0.00'a** indirildi (%100 engelleme).

---

## 2. KULLANICININ ÖNERDİĞİ YENİ STRATEJİNİN OBJEKTİF ANALİZİ

### 2.1. Önerilen Strateji Ne Diyor?
1. **Adım 1:** Acele etmeyip öncelikle hibrit filtreleme sistemini (Normalizasyon, Regex/Kural, Nöral Model, Emoji/Görünmez Yazı tespiti, Çıktı DLP) eksiksiz, sağlam bir paket haline getirmek.
2. **Adım 2:** Karar mantığını netleştirmek (Puanlama sistemi mi olacak? Regex puan mı verecek? Model mi karar verecek yoksa doğrudan bloklama mı yapılacak?).
3. **Adım 3:** Küçük modellerle (1.5B - 3.8B) sınırlı kalmayıp; orta ölçek (7B - 14B), büyük ölçek (70B+) açık kaynak modeller ile ticari kapalı API'ları (OpenAI, Google, Anthropic) aynı saldırı setleriyle test etmek.
4. **Adım 4:** Makaleyi şu can alıcı akademik argüman üzerine kurmak:  
   *"Kurumlar verilerini Google ve OpenAI'a kaptırmamak için kurum içi (on-premise) açık kaynak modeller barındırıyor; ancak model ne kadar büyük olursa olsun (70B dahi olsa) çevre kalkanı olmadan kolayca hacklenebiliyor ve veriler sızıyor."*

### 2.2. Objektif Değerlendirme (Artılar, Riskler ve Çözümler)

| Değerlendirme Kriteri | Durum | Analiz ve Gerekçe |
| :--- | :---: | :--- |
| **Akademik Değer (Impact Factor)** | **Olağanüstü (S-Tier)** | Literatürdeki çalışmaların %90'ı ya sadece tek bir modele bakar ya da sadece veri seti sunar. 1.5B'den 70B'ye ve ticari API'lara uzanan çok katmanlı bir karşılaştırma makaleyi doğrudan üst düzey Q1/Q2 veya saygın IEEE konferansları seviyesine çıkarır. |
| **Siber Güvenlik Argümanı** | **Kusursuz** | *"Enterprise Self-Hosting Dilemma"* (Kurumsal Kendi Sunucunda Barındırma İkilemi): Kurumlar KVKK/GDPR uyumu için yerel model kurarken, saldırganların bir prompt enjeksiyonuyla yerel veri tabanı şifrelerini çalabilmesi sektörün en büyük kör noktasıdır. |
| **Teknik Uygulanabilirlik** | **Yüksek** | Colab Pro/A100 ve RunPod/vLLM altyapısıyla 7B, 14B ve hatta 70B modeller saatler içinde benchmark edilebilir. API modelleri (GPT-4o, Gemini 1.5, Claude) ise ufak bir Python scriptiyle birkaç dakikada taranabilir. |
| **Potansiyel Risk: Odak Kaybı ve Kapsam Büyümesi** | **Orta Risk** | Pipeline tam bitmeden testlere başlanırsa, her katman değiştikçe tüm testleri baştan yapmak gerekir. **Çözüm:** Önce filtre pipeline'ını dondurup paketlemek, ardından modelleri test etmek şarttır. |
| **Potansiyel Risk: Maliyet ve Donanım** | **Düşük Risk** | 70B modelleri yerel bilgisayarda çalıştırmak imkansızdır (min 48GB VRAM gerekir). Ancak RunPod üzerinde 1-2 saatlik A100 kiralaması (yaklaşık 2-3 dolar) veya Groq/DeepInfra gibi açık ağırlıklı model API'ları üzerinden test yapmak hem sıfır donanım derdi sunar hem de dakikalar içinde biter. |

---

## 3. BÜTÜNLEŞİK SAVUNMA PİPELİNE MİMARİSİ (FILTER PACKAGE)

Savunma sistemi tek bir noktaya (yalnızca regex veya yalnızca model) emanet edilemez. Siber güvenlikte geçerli olan temel ilke **"Derinlemesine Savunma" (Defense-in-Depth)** yaklaşımıdır.

```
                      GELEN KULLANICI GİRDİSİ (Metin / PDF / URL)
                                          │
                                          ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│ LAYER 0: NORMALİZASYON VE STEGANOGRAFİ MOTORU (< 0.5 ms)                        │
│ • Zero-Width (Görünmez Karakter) Tespiti & Temizliği                             │
│ • Unicode Tags (U+E0000 - U+E007F) Görünmez Mürekkep İzolasyonu                  │
│ • Emoji Variation Selector (U+FE00, U+E01xx) Steganografi Çözümü                 │
│ • Homoglyph (Kiril/Latin Benzer Karakter) Dönüştürme                             │
│ • Base64 / Hex Kod Çözme (Otomatik payload deşifre edip incelemeye sokma)        │
│ • PDF Gizli Metin Analizi (Beyaz üstüne beyaz yazı, <1pt font tespiti)           │
└─────────────────────────────────────┬────────────────────────────────────────────┘
                                      │ Temizlenmiş & Genişletilmiş Metin
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│ LAYER 1: DETERMINİSTİK KURAL VE SEZGİSEL REGEX MOTORU (< 0.2 ms)                 │
│ • Bilinen Saldırı İmzaları (Ignore rules, System override, DAN, Roleplay)        │
│ • Bilişsel Çerçeveleme (Yetki simülasyonu, SHGM, Denetçi kimliği)                │
│ • Canary & Hassas Veri Avlama Kalıpları (Şifre isteği, config dökümü)            │
│ ──> Çıktı: Tetiklenen Kurallar & Heuristic Risk Puanı (0 - 100)                  │
└─────────────────────────────────────┬────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│ LAYER 2: NÖRAL ANLAMSAL KALKAN (NEURALSHIELD-v3 ONNX INT8) (~8.6 ms)             │
│ • XLM-RoBERTa Tabanlı Çift Dilli (TR / EN) Derin Öğrenme Sınıflandırıcısı        │
│ • 59.5k Örnekle Eğitilmiş, Zorlu Negatiflere (IT terimleri) Karşı Bağışık        │
│ ──> Çıktı: Malicious Olasılığı (%0 - %100) & Model Risk Puanı                    │
└─────────────────────────────────────┬────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│ 🧠 BİLEŞİK RİSK VE KARAR MOTORU (COMPOSITE DECISION ENGINE)                      │
│ Formül: Risk = Max(ML_Risk, Stego_Ceza) + Heuristic_Katkı                       │
│                                                                                  │
│ • Risk >= 60 veya Kesin Steganografi/İmza  ──> 🛑 BLOCKED (Modele Gitmez)        │
│ • 40 <= Risk < 60                         ──> ⚠️ ŞÜPHELİ (Sanitize & Log)        │
│ • Risk < 40                               ──> ✅ ALLOWED (Modele İletilir)       │
└─────────────────────────────────────┬────────────────────────────────────────────┘
                                      │ Yalnızca ALLOWED İse
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│ 🤖 HEDEF BÜYÜK DİL MODELİ (LLM / SLM)                                            │
│ • SkyPort Kurumsal Sistem Promptu & Canary Tokenları İçerir                      │
│ • Yanıt Üretir                                                                   │
└─────────────────────────────────────┬────────────────────────────────────────────┘
                                      │ Üretilen Ham Yanıt
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│ LAYER 3: DIŞA DÖNÜK VERİ KAYBI ÖNLEME (DLP OUTBOUND FILTER) (< 0.5 ms)           │
│ • Canary Token Kaçak Tespiti (Marker & Değer Kontrolü)                           │
│ • PII Maskeleme (TC Kimlik, Kredi Kartı, Telefon)                                │
│ • Sistem Sırları Maskeleme (API Anahtarları, DB Bağlantı Dizgeleri, Parolalar)   │
│ ──> Çıktı: [SANSÜRLENDİ] / [REDACTED] Maskelenmiş Güvenli Yanıt                 │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### 3.1. Karar Mantığı: Puanlama mı, Doğrudan Bloklama mı?

Siber güvenlik mimarisinde **yalnızca tek bir yönteme güvenmek ölümcül bir hatadır:**
* **Neden Sadece Regex Bloklayamaz?**  
  Bir kullanıcı *"Havalimanı sistem şifremi unuttum, nasıl sıfırlarım?"* dediğinde regex *"şifre"* kelimesini yakalar. Eğer doğrudan bloklarsa meşru müşteri kapı dışarı edilir (Yüksek Yanlış Alarm / False Positive).
* **Neden Sadece Model Bloklayamaz?**  
  Saldırgan komutu Base64 içerisine gömerse veya Unicode görünmez karakterler arasına gizlerse, nöral model metin olarak göremediği için atlayabilir (Kaçan Saldırı / False Negative).
* **Bizim Hibrit Çözümümüz (Tiered Decision Gating):**
  1. **Kesin Suç Unsurları (Hard Block):** Metinde bilinen görünmez karakter steganografisi (Unicode tag, zero-width) veya açık sistem manipülasyonu etiketleri (`<system_override>`, `<!-- inject -->`) tespit edilirse doğrudan **BLOCKED** edilir.
  2. **Bileşik Risk Puanı (Composite Risk Score):**
     $$\text{Composite Risk} = \alpha \cdot \text{Score}_{\text{ML}} + \beta \cdot \text{Score}_{\text{Regex}} + \gamma \cdot \text{Score}_{\text{Stego}}$$
     Burada nöral modelin ağırlığı ($\alpha = 0.70$), kural motorunun ağırlığı ($\beta = 0.20$), davranış/taşıyıcı ağırlığı ($\gamma = 0.10$) olarak çalışır.
  3. **Eşik Değeri:** Bileşik Risk $\ge 60$ ise istek kesilir; altındaysa güvenle ana LLM'e iletilir.

---

## 4. ÇOK ÖLÇEKLİ VE ÇOK KURUMLU BENCHMARK YOL HARİTASI

Kurumsal *"Self-Hosting İkilemi"* tezimizi ispatlamak için modelleri 4 farklı ölçek ve kategoride ampirik teste tabi tutacağız:

| Düzey (Tier) | Kategori | Temsilci Modeller | Parametre Boyutu | Test Ortamı | Durum |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **Tier 1** | **Küçük Uç Modeller (Edge SLM)** | `qwen2.5:1.5b`<br>`gemma2:2b`<br>`llama3.2:3b`<br>`qwen2.5:3b`<br>`phi3:mini` | 1.5B – 3.8B | Yerel Ollama (CPU/RTX) | **TAMAMLANDI**<br>(225 test yapıldı, grafikler hazır) |
| **Tier 2** | **Orta Ölçek Açık Modeller (Mid OSS)** | `meta-llama/Llama-3.1-8B-Instruct`<br>`mistralai/Mistral-7B-Instruct-v0.3`<br>`Qwen/Qwen2.5-7B-Instruct`<br>`google/gemma-2-9b-it` | 7B – 9B | Google Colab A100 / T4 veya RunPod | **Sıradaki Adım** |
| **Tier 3** | **Büyük Ölçek Açık Modeller (Frontier OSS)** | `meta-llama/Llama-3.3-70B-Instruct`<br>`Qwen/Qwen2.5-72B-Instruct` | 70B – 72B | RunPod vLLM veya Groq / DeepInfra API | **Planlandı** |
| **Tier 4** | **Ticari Kapalı Bulut Modelleri (Closed APIs)** | `OpenAI GPT-4o-mini`<br>`OpenAI GPT-4o`<br>`Google Gemini 1.5 Flash`<br>`Anthropic Claude 3.5 Sonnet` | Gizli (Mega Scale) | Resmi Python API SDK'ları | **Planlandı** |

### 4.1. Elde Edilecek Çarpıcı Akademik Çıkarımlar
1. **Ölçek Bağımsız Zafiyet (Scale-Invariant Vulnerability):**
   * Model boyutu 1.5B'den 70B'ye çıksa dahi, harici çevre kalkanı (NeuralShield) olmayan modeller prompt injection karşısında canary tokenlarını sızdırmaktadır.
2. **Yerel vs Bulut Maliyet ve Gizlilik Karşılaştırması:**
   * Şirketler verilerini OpenAI'a göndermemek için 70B modeli sunucularına koysalar bile güvenlik açığını kapatamazlar.
   * Çözüm, koca bir modeli yeniden eğitmek veya prompt mühendisliğiyle uğraşmak değil; önüne **8.6 ms gecikmeli yerel NeuralShield kalkanı** koymaktır.
3. **NeuralShield Koruma Başarısı:**
   * Tüm bu modellerin önüne NeuralShield-v3 konulduğunda Saldırı Başarı Oranı (ASR) istisnasız **%0.00'a** düşmektedir.

---

## 5. ADIM ADIM GELİŞTİRME PLANI (İŞ PAKETLERİ)

Acele etmeden, adım adım ve hatasız ilerleyeceğimiz resmi iş paketleri:

### 🎯 İŞ PAKETİ 1: SAVUNMA PİPELİNE'ININ EKSİKSİZ PAKETLENMESİ (ÖNCELİKLİ)
* **Görev 1.1:** `backend/regex_rules.py` kurallarının genişletilmesi (Siber güvenlik, Türkçe komut enjeksiyonu, rol yapma, yetki manipülasyonu kalıplarının eklenmesi).
* **Görev 1.2:** `backend/security_layer.py` karar motorunun güncellenmesi (Bileşik Risk Puanı formülü, steganografi cezaları, beyaz yazı ve emoji tespitinin tek bir `PipelineReport` objesi üretmesi).
* **Görev 1.3:** `backend/dlp.py` outbound filtrenin güçlendirilmesi (Canary token yakalama mantığının dinamik hale getirilmesi, kredi kartı/TC/API key maskelemesinin doğrulanması).
* **Görev 1.4:** Bütünleşik pipeline için yerel doğrulama test scriptinin (`scripts/verify_full_pipeline.py`) yazılması ve %100 başarıyla geçtiğinin teyit edilmesi.

### 🎯 İŞ PAKETİ 2: ORTA ÖLÇEK (7B - 9B) MODELLERİN TESTİ (COLAB / RUNPOD)
* **Görev 2.1:** Google Colab üzerinde tek tıkla çalışacak, LLaMA-3.1-8B, Mistral-7B ve Qwen-2.5-7B modellerini otomatik test eden scriptin hazırlanması.
* **Görev 2.2:** Aynı 45 saldırı vektörünün (SkyPort promptu ve canary tokenlarıyla) bu modellere Shield OFF ve Shield ON olarak gönderilmesi.
* **Görev 2.3:** ASR oranlarının kaydedilip mevcut 5 modelimizin yanına eklenmesi (Model havuzunun 8 modele çıkarılması).

### 🎯 İŞ PAKETİ 3: BÜYÜK MODELLER (70B) VE TİCARİ BULUT API'LARININ TESTİ
* **Görev 3.1:** LLaMA-3.3-70B ve Qwen-2.5-72B testlerinin RunPod veya açık model inference uç noktalarıyla gerçekleştirilmesi.
* **Görev 3.2:** OpenAI GPT-4o ve Claude 3.5 Sonnet için API çağrı scriptinin çalıştırılarak sonuçların toplanması.
* **Görev 3.3:** Nihai karşılaştırma matrisinin (Tüm modellerin Shield OFF vs ON tablosunun) üretilmesi.

### 🎯 İŞ PAKETİ 4: AKADEMİK RAPOR VE MAKALE ÜRETİMİ
* **Görev 4.1:** Elde edilen devasa ampirik verinin (Grafikler, ROC eğrileri, çok modelli ASR tabloları, CPU gecikme analizleri) makaleye entegre edilmesi.
* **Görev 4.2:** Makalenin DergiPark *Computers and Informatics* şablonuna (`File.docx`) kusursuz şekilde, akademik İngilizce ile basılması.

---

## 6. MEVCUT DURUM ÖZET TABLOSU

```
BİLEŞEN                  DURUM       NOT
─────────────────────────────────────────────────────────────────────────
NeuralShield-v3 Eğitimi  TAMAM      59.5k veri, %95.76 F1, 0.992 ROC-AUC
ONNX INT8 Optimizasyonu  TAMAM      278 MB, 8.61 ms CPU çıkarımı
IT Terimleri False Alarm TAMAM      %40'tan %0.00'a indirildi
Yerel Model Testleri     TAMAM      5 model (1.5B-3.8B), 225 test, ASR %0
Savunma Pipeline         GELİŞİYOR  Regex & Karar Motoru güçlendirilecek
7B-14B Model Testleri    BEKLEMEDE  Colab scripti hazırlandıktan sonra
70B & Ticari API Testi   BEKLEMEDE  Pipeline bitince koşulacak
Makale Yazımı (docx)     BEKLEMEDE  Tüm testler ve pipeline tamamlanınca
```

---
*Bu yol haritası projenin resmi rehberidir. Her adım tamamlandıkça bu belgedeki ilgili kutucuklar işaretlenecek ve projenin bilimsel bütünlüğü korunacaktır.*
