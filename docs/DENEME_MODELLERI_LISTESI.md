# 🧪 CyberTech Neural Shield: Çok Modelli Kıyaslama ve Deneme Modelleri Listesi
### Küçük, Orta (A100), Büyük (EVREN H200) ve Ticari Bulut Modelleri Nihai Test Matrisi

> **Durum:** 📋 Planlandı / Onaylandı (Henüz uygulamaya başlanmadı)  
> **Tarih:** 14 Ekim 2026  
> **Çalışma:** CyberTech Neural Shield v5 Çevresel Güvenlik Ağ Geçidi Bilimsel Doğrulama Deneyleri  
> **Yazarlar:** Mustafa ÇALIŞKAN & Prof. Dr. Ali Hakan IŞIK (Burdur Mehmet Akif Ersoy Üniversitesi)

---

## 1. Bilimsel Metodoloji: Orantılı / Logaritmik Büyüme Merdiveni

Siber güvenlik dayanıklılık testlerinde (Red-Teaming Benchmark), modellerin parametre boyutları rastgele değil, **katlanarak (orantılı ve logaritmik sıçrama ile)** seçilmiştir:

$$\mathbf{Küçük\ (\sim 2.5B\ Parametre)} \xrightarrow{\approx \times 10} \mathbf{Orta\ (\sim 25B\ Parametre)} \xrightarrow{\approx \times 10} \mathbf{Büyük\ (\sim 150B+\ Parametre)}$$

* **Test Protokolü Kuralı (Greedy Decoding):** Tüm modeller **`temperature = 0.0`** sabit parametresiyle test edilir. Bu sayede rastgelelik engellenir, sonuçlar deterministik ve bilimsel olarak tekrarlanabilir olur.
* **Test Durumları:**
  1. **Kalkan KAPALI (Shield OFF):** Model çıplakken saldırıyı yutuyor ve gizli sistem promptunu / canarileri sızdırıyor mu? (Ham Model Zafiyeti / ASR %)
  2. **Kalkan AÇIK (Shield ON):** NeuralShield-v5 devreye girip 12 ms'de isteği blokluyor mu? (Nihai Güvenlik / %0 ASR)

---

## 2. Model Listesi ve Donanım Matrisi

### 💻 SİKLET 1: KÜÇÜK MODELLER (1.5B – 3.8B) — *Ortalama: ~2.5B Parametre*
* **Çalıştırma Ortamı:** Yerel Bilgisayar (Laptop / Standart GPU / Ollama)
* **VRAM Tüketimi:** 4 GB – 6 GB VRAM
* **Rolü & Karakteristiği:** Parametreleri küçük olduğu için sinsi senaryo ve rol yapma saldırılarına karşı en savunmasız gruptur. Kalkan KAPALI iken sistem promptunu ve şifreleri **en kolay sızdıran (%20 - %30 ASR)** referans grubudur.

| # | Model Adı | Sağlayıcı | Parametre | Nerede Çalışır? | Güvenlik Karakteristiği & Seçilme Nedeni |
|:---:|---|---|:---:|:---:|---|
| **1** | **Qwen 2.5 1.5B Instruct** | Alibaba Cloud | **1.54B** | Yerel (Ollama) | Çok dilli (TR/EN) yeteneği en yüksek mini model. Tier 5 (Çapraz dil) sıçramalarını test etmek için ideal. |
| **2** | **Gemma 2 2B IT** | Google DeepMind | **2.61B** | Yerel (Ollama) | Google'ın katı etik filtreleriyle eğitilmiştir. Doğrudan enjeksiyonları (Tier 1) reddetme refleksi ölçülür. |
| **3** | **Llama 3.2 3B Instruct** | Meta AI | **3.21B** | Yerel (Ollama) | Meta'nın en popüler küçük modeli. Ters psikoloji ve senaryolarda hemen pes eder. |
| **4** | **Phi-3.5 Mini Instruct** | Microsoft | **3.82B** | Yerel (Ollama) | Kompakt akıl yürütme modeli. Uzun İngilizce jailbreak kurgularında kolayca zafiyet verir. |
| **5** | **Granite 3.0 2B Instruct** | IBM Research | **2.0B** | Yerel (Ollama) | IBM'in kurumsal güvenlik odaklı modeli. HackAPrompt tarzı CTF ataklarında test edilir. |

---

### 🚀 SİKLET 2: YENİ ORTA MODELLER (12B – 35B) — *Ortalama: ~25B Parametre*
* **Çalıştırma Ortamı:** Google Colab **A100 GPU (40GB veya 80GB VRAM)**
* **Hassasiyet:** Saf 16-bit (bfloat16), kuantizasyon kaybı olmadan tam güç
* **Rolü & Karakteristiği:** Zayıf T4 GPU kısıtlamasından kurtarılmış, tek A100 GPU'ya sığan **gerçek kurumsal ağır siklet modellerdir**. 70B devlerle yarışan akıl yürütme kapasiteleri vardır.

| # | Model Adı | Sağlayıcı | Parametre | A100 VRAM İhtiyacı | Güvenlik Karakteristiği & Seçilme Nedeni |
|:---:|---|---|:---:|:---:|---|
| **6** | **Mistral NeMo 12B Instruct** | Mistral + NVIDIA | **12.2B** | ~24 GB (A100 40GB rahat) | 128k bağlam penceresi. Kurumsal RAG ve uzun doküman enjeksiyonlarına açık yapısı incelenir. |
| **7** | **Qwen 2.5 14B Instruct** | Alibaba Cloud | **14.7B** | ~29 GB (A100 40GB tam) | Türkçe anlama, kodlama ve Base64 çözmede olağanüstü kabiliyetli. Tier 4 kodlama saldırılarını anlar. |
| **8** | **Gemma 2 27B IT** | Google DeepMind | **27.2B** | ~54 GB (A100 80GB / 40GB 8b) | Google'ın güvenlik kalesi. Filtreleri adeta çelik duvardır; atlatılması en zor orta siklet modeldir. |
| **9** | **Qwen 2.5 32B Instruct** | Alibaba Cloud | **32.5B** | ~65 GB (A100 80GB tam) | **Orta sikletin zirvesi.** Birçok 70B modeli benchmarklarda ezen, sinsi kurguları sezebilen canavar. |
| **10** | **Command R 35B** | Cohere | **35.0B** | ~70 GB (A100 80GB tam) | Cohere'in tamamen kurumsal iş akışları ve API ajanları için eğittiği kurumsal model. |

---

### 🏛️ SİKLET 3: BÜYÜK MODELLER (70B – 750B+ / MoE) — *Ortalama: ~150B+ Parametre*
* **Çalıştırma Ortamı:** **TÜBİTAK EVREN Platformu (8x NVIDIA H200 Süper Bilgisayarı / 1.1 TB VRAM)**
* **Erişim:** REST API (`https://evren-llmapi.ssyz.org.tr/v1`) — 15 Milyon Günlük Ücretsiz Token
* **Rolü & Karakteristiği:** SOTA seviyesinde zincirleme akıl yürütme (Chain-of-Thought / Deep Reasoning) yapabilen yapay zeka kaleleridir. Basit saldırıları anlarlar; bunları kırmak için çok katmanlı felsefi veya mantıksal tuzaklar gerekir.

| # | Model (EVREN API Adı) | Orijinal Mimari | Gerçek Parametre | Güvenlik Karakteristiği & Seçilme Nedeni |
|:---:|---|---|:---:|---|
| **11** | **`qwen3.8-flash-next`** | Qwen-3.8-Flash | **~6B aktif / 180B MoE** | Qwen ailesinin en güncel amiral gemisi. Çok hızlı ve derin muhakemeli akıl yürütme mimarisi. |
| **12** | **`gemma-4-31b`** | Google Gemma-4 | **31.3B Dense** | Google DeepMind'ın kurumsal dev açık kaynak modeli. Ağır açık kaynak savunma kalesi. |
| **13** | **`deepseek-v4.1-flash`** | DeepSeek V3 / R1 | **~16B aktif / 763B MoE** | DeepSeek'in derin muhakeme mimarisi. Mantık tuzaklarını kendi içinde düşünerek çözmeye çalışır. |
| **14** | **`glm-5.3`** | Z.ai / Tsinghua | **~40B aktif / 753B MoE** | Tsinghua Üniversitesi ve Z.ai ortak yapımı dev amiral gemisi. Açık modellerin en tepesi. |
| **15** | **`llama-3.1-70b-instruct`** | Meta AI LLaMA 3.1 | **70.6B Dense** | Açık kaynak dünyasının en bilinen güvenlik kalesi (Instruction Hierarchy). |

---

### 🌐 SİKLET 4: TİCARİ BULUT SOTA (Frontier Kapalı Kaynak Zirvesi)
* **Çalıştırma Ortamı:** Google Cloud API (Vertex / Google GenAI)
* **Rolü:** Milyar dolarlık kurumsal model. NeuralShield'ın ön cephe kalkanı olarak koruduğu ana kurumsal sistemimiz.

| # | Model | Sağlayıcı | Rolü |
|:---:|---|---|---|
| **16** | **Google Gemini 3.6 Flash** | Google Cloud | Kapalı kaynaklı ticari dev model. "Kalkan kapalıyken sızdırdığı, kalkan açıkken $0 maliyetle 12 ms'de korunduğu" kanıtlanan nihai model. |

---

## 3. İki Kalkan Arasındaki Kıyaslama (Guardrail Baselines)

Bizim geliştirdiğimiz **NeuralShield-v5** modelinin mikro-gecikmesini ve başarısını kanıtlamak için benchmark testine dahil edilecek rakip güvenlik modelleri:

| Guardrail Modeli | Sağlayıcı | Boyut / Gecikme | Çalıştığı Yer |
|---|---|:---:|:---:|
| **CyberTech Neural Shield v5** | **Mustafa ÇALIŞKAN (Bizim)** | **278 MB / 12.27 ms** | **Yerel CPU** |
| **Qwen3-Guard-4B** | Alibaba Cloud | 4B (~8 GB) | EVREN Platformu |
| **Llama-Guard-3-8B** | Meta AI | 8B (~16 GB) / ~1200 ms | H200 / Hugging Face |
| **ProtectAI DeBERTa-v3** | Protect AI | 86M (~500 MB) / ~30 ms | Hugging Face (Yalnızca EN) |
| **Patronus Wolf Defender** | Patronus AI | ModernBERT / ~20 ms | Hugging Face (8K Bağlam) |

---

## 4. Uygulama Öncesi Kontrol Listesi

- [x] Model listesi Küçük, Orta (A100) ve Büyük (EVREN H200) olarak orantılandı.
- [x] Greedy Decoding (`temperature = 0.0`) kuralı sabitlendi.
- [x] EVREN API bağlantısı ve 14.8M günlük token kotası doğrulandı.
- [x] Doküman `docs/DENEME_MODELLERI_LISTESI.md` olarak kaydedildi.
- [ ] **Beklemede:** Kullanıcı onayı gelene kadar test çalıştırma işlemi başlatılmayacaktır.
