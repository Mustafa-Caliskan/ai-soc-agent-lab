# 🚀 NeuralShield SOTA Geliştirme ve Entegrasyon Eylem Planı
### ProtectAI, Patronus AI (Wolf Defender) ve Qualifire (Sentinel) Özelliklerini Sisteme Kazandırma Stratejisi

> **Tarih:** 14 Ekim 2026  
> **Hedef:** CyberTech Neural Shield v5 mimarisini, Hugging Face'in en popüler SOTA modellerinin (ModernBERT tabanlı Wolf Defender ve Qualifire Sentinel) en güçlü kabiliyetleriyle donatarak Q1 dergi seviyesinde rakipsiz kılmak.

---

## 1. Neleri Ödünç Alıyoruz? (SOTA Transfer Özeti)

```mermaid
flowchart TD
    subgraph Rakipler["Rakiplerin Güçlü Yönleri"]
        P1["Patronus AI: 8K Uzun Bağlam"]
        P2["Patronus AI: Tool/Agent Enjeksiyonları"]
        Q1["Qualifire: Yapılandırılmış JSON/Kod Taraması"]
        PR1["ProtectAI: Saf İngilizce Hızı"]
    end

    subgraph NeuralShield["NeuralShield v5'e Eklenenler"]
        NS1["Layer 0: Kayan Pencere (Sliding Window Chunking)<br/>(512 Sınırını Kaldırma)"]
        NS2["Layer 0: JSON & Tool-Call Payload Unpacker<br/>(Ajan Güvenliği)"]
        NS3["Layer 2: Semantik Olasılık Kalibrasyonu<br/>(Sıcaklık/Platt Scaling)"]
        NS4["Kafa Kafaya (Head-to-Head) Kıyaslama Testi<br/>(Makale Tablo II)"]
    end

    P1 --> NS1
    P2 --> NS2
    Q1 --> NS2
    PR1 --> NS4
```

---

## 2. Somut İş Paketleri ve Yol Haritası

### 📦 İş Paketi 1: 512 Token Sınırını Kayan Pencereyle Aşmak (Sliding Window Chunking)
* **Problem:** RoBERTa modelleri varsayılan olarak 512 token ile sınırlıdır. Rakip ModernBERT ise 8.192 token okuyabilmektedir. Eğer saldırgan zararlı komutu 600. kelimeye saklarsa klasik kesme (*truncation*) bunu kaçırabilir.
* **Çözüm:** `backend/ml_model.py` içerisine **Kayan Pencere (Sliding Window)** algoritması eklenir.
  * Pencere Boyutu: 384 token
  * Örtüşme (Overlap / Stride): 128 token
  * Eğer metin 512 tokenı aşıyorsa parçalara bölünür; her parça bağımsız ONNX INT8 çıkarımına sokulur ve en yüksek risk skoru ($\max(\text{Risk}_i)$) alınır.
* **Akademik & Mühendislik Ödünleşimi (Trade-off):** 
  * 10.000 tokenlik bir doküman yaklaşık 26 pencereye bölünür. $26 \times 12.27\text{ ms} \approx 320\text{ ms}$ gecikme yaratır; dolayısıyla "12 ms ultra-düşük gecikme" iddiası uzun dokümanlarda geçerli değildir.
  * İstatistiksel olarak $\max(\text{Risk}_i)$ kuralı, uzun ve masum metinlerde yanlış alarm (False Positive) ihtimalini artırır. Makalede bu ödünleşim dürüstçe belgelenecektir.
* **Kazanç:** Model yeniden eğitilmeden RAG ve doküman enjeksiyonlarına karşı tam kapsama.

---

### 📦 İş Paketi 2: JSON, Kod ve Araç Çağrısı (Tool-Call) Ayrıştırıcı (Layer 0 Genişletmesi)
* **Problem:** Patronus ve Qualifire, AI ajanlarının araç çağrılarına (`tool_calls`, SQL çıktısı, JSON API yanıtları) saklanan dolaylı enjeksiyonları yakalamakta uzmandır.
* **Çözüm:** `backend/normalizer.py` içine `unpack_structured_payload(text)` fonksiyonu eklenir.
  * Eğer girdi bir JSON nesnesi, markdown kod bloğu (` ```json ... `) veya URL query string ise anahtar ve değerler otomatik ayrıştırılır.
  * `{"user_id": 4, "role": "[OVERRIDE] ignore rules"}` gibi sinsi JSON yapıları düzleştirilip Katman 1 ve 2'ye açık metin olarak beslenir.
* **Kazanç:** Modern AI Ajan (Agentic AI) platformlarına tam entegrasyon.

---

### 📦 İş Paketi 3: Semantik Olasılık Kalibrasyonu (Sıfır Sızıntılı Sıcaklık Optimizasyonu)
* **Katı İlke (Kör Nokta ve Sızıntı Önleme):** Statik regex whitelist veya "greeting bypass" KULLANILMAMIŞTIR. Ayrıca kalibrasyon kümesi modelin nihai test kümesinden (`data/test_multilingual.csv`) kesin olarak yalıtılarak **veri sızıntısı (data leakage)** tamamen engellenmiştir.
* **Uygulanan Çözüm (Guo et al., ICML 2017):**
  * `scripts/calibrate_temperature.py` ile `data/train_multilingual.csv` içerisinden rastgele tohumla (seed=42) ayrılan bağımsız doğrulama kümesi (`data/val_multilingual.csv`, $N=200$, 100 saldırı / 100 meşru) üzerindeki ham logit'ler çıkarılmış, Scipy bounded optimization ile Negative Log-Likelihood (NLL) minimize edilmiştir.
  * **Kalibrasyon Öncesi ($T = 1.0$):** $\text{NLL} = 0.62098$, $\text{ECE} = \%11.51$
  * **Fitted Optimal Sıcaklık:** $T^* = 1.8345$
  * **Kalibrasyon Sonrası ($T^* = 1.8345$):** $\text{NLL} = 0.56556$, $\text{ECE} = \%3.45$
  * **ECE İyileşmesi:** Beklenen Kalibrasyon Hatası $\%11.51 \rightarrow \%3.45$ seviyesine çekilerek **8.07 yüzde puanı mutlak düşüş** ve **%70.1 bağıl hata düşüşü** sağlanmıştır. Modelin ham aşırı özgüveni yumuşatılmıştır.
  * $T^* = 1.8345$ parametresi doğrudan `backend/shield_config.json` ve `backend/shield_config.py` içerisine işlenmiştir.

---

### 📦 İş Paketi 4: Kafa Kafaya (Head-to-Head) Kıyaslama ve Karşılaştırmalı Değerlendirme
* **Metodoloji:** `scripts/benchmark_guardrail_rivals.py` motoru tabakalı (stratified) $N=120$ örneklem (20 İngilizce enjeksiyon, 20 Türkçe enjeksiyon, 20 Unicode steganografi, 20 Türkçe selamlama, 20 IT teknik destek, 20 İngilizce kodlama) üzerinde çalıştırılmıştır.
* **Akademik Bütünlük İlkeleri:**
  * **Simülasyon Yasağı:** Yerel ağırlığı indirilmemiş modeller için hiçbir tahmini/simüle veri üretilmemiş; yalnızca canlı çalışan gerçek sistemler (NeuralShield ve EVREN Qwen3-Guard API) Tablo II-A'ya dahil edilmiştir.
  * **İstatistiksel Güvenilirlik:** $N=120$ örneklem için Wilson Score $\%95$ Güven Aralığı ($\text{GA}$) hassasiyetle hesaplanmıştır.
  * **Bileşen Analizi (Ablation Study):** 4 katmanlı mimarinin tekil modellerle adil kıyaslanabilmesi için hem "Tam Savunma Hattı" hem de "Yalnızca Katman 2 XLM-RoBERTa Modeli" bağımsız olarak ölçülmüştür.

#### 📊 TABLO II-A: CANLI AMPİRİK KIYASLAMA VE GÜVEN ARALIKLARI ($N = 120$, Stratified)

| Güvenlik Mimarisi / Model | Mimari Tipi | TR Yakalama [%95 GA] | Stego Yakalama [%95 GA] | Saldırı Başarısı (ASR) [%95 GA] | Yanlış Alarm (FP) [%95 GA] | Ortalama Gecikme (ms) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **NeuralShield-v5 (Tam 4-Katmanlı)** | 4-Katmanlı Savunma Hattı (Defense-in-Depth Pipeline) | **%85.0** [%64.0, %94.8] | **%100.0** [%83.9, %100.0] | **%11.7** [%5.8, %22.2] | **%10.0** [%4.7, %20.1] | **11.0 ± 3.9 ms** |
| **NeuralShield-v5 (Yalnızca Katman 2)** | Tekil Model (Standalone ONNX INT8 Classifier) | %90.0 [%69.9, %97.2] | %25.0 [%11.2, %46.9] | %28.3 [%18.5, %40.8] | %11.7 [%5.8, %22.2] | **10.9 ± 4.6 ms** |
| **Qwen3-Guard-4B (EVREN API H200)** | Tekil LLM Guardrail (4B Parameter LLM via API) | %95.0 [%76.4, %99.1] | %0.0 [%0.0, %16.1] | %35.0 [%24.2, %47.6] | %1.7 [%0.3, %8.9] | **802.5 ± 136.0 ms** |

#### 📚 TABLO II-B: YAYINLANMIŞ LİTERATÜR & RESMİ MODEL KARTI REFERANSLARI

| Model Adı | Temel Mimari | Bildirilen Başarı / Metrik | Bağlam Uzunluğu | Resmi Model Kartı & Kapsam Notları |
| :--- | :--- | :---: | :---: | :--- |
| **Patronus Wolf Defender** | ModernBERT (base) | %98.44 F1 | 8.192 token | Çok dilli sentetik ve Base64 verisiyle eğitilmiş tekil sınıflandırıcı (`patronus-studio/wolf-defender-prompt-injection`). |
| **ProtectAI DeBERTa-v3 v2** | DeBERTa-v3 (base) | >%99.0 Doğruluk | 512 token | İngilizce prompt injection için optimize edilmiş tekil sınıflandırıcı (`protectai/deberta-v3-base-prompt-injection-v2`). |
| **Qualifire Prompt Sentinel** | ModernBERT (large) | SOTA Gatekeeper | 8.192 token | Kurumsal kapı bekçisi olarak eğitilmiş sınıflandırıcı (`qualifire/prompt-injection-sentinel-modernbert-large`). |

> **Akademik Çıkarımlar:**
> 1. **Bileşen Analizi (Katman 0 ve Katman 1'in Önemi):** Yalnızca Katman 2 ML modeli tek başına çalıştırıldığında Steganografi yakalama oranı $\%100.0$'den $\%25.0$'e düşmekte, genel Saldırı Başarı Oranı (ASR) $\%11.7$'den $\%28.3$'e fırlamaktadır. Bu bulgu, tekil sınıflandırıcıların çok modlu/gizlenmiş saldırılarda yetersiz kaldığını ve katmanlı derinlemesine savunmanın (*defense-in-depth*) vazgeçilmez olduğunu ampirik olarak kanıtlar.
> 2. **LLM Tabanlı Korumalar vs Yerel Pipeline:** Qwen3-Guard-4B bulut H200 GPU üzerinde $802.5\text{ ms}$ gecikme ile çalışırken, NeuralShield yerel CPU'da $11.0\text{ ms}$ ile **~73 kat daha hızlı** yanıt vermiştir. Ayrıca Qwen3-Guard-4B, Unicode Tag steganografisini girdi katmanında ayrıştıramadığı için $\%0.0$ yakalama ile atlatılmış ve genel ASR'si $\%35.0$'a çıkmıştır.

---

## 3. Uygulama Durumu

1. ✅ **Adım 1:** `backend/ml_model.py` dosyasına Kayan Pencere (Sliding Window Chunking) ve Sıcaklık Kalibrasyonu başarıyla kodlandı.
2. ✅ **Adım 2:** `backend/normalizer.py` dosyasına JSON / Structured Payload, Tool-Call ve URL Query String açıcı (`unpack_structured_payload`) eklendi.
3. ✅ **Adım 3:** `scripts/calibrate_temperature.py` ile bağımsız doğrulama split'inde (`val_multilingual.csv`, $N=200$, test verisinden yalıtılmış) optimal $T^* = 1.8345$ fit edildi; ECE $\%11.51$'den $\%3.45$'e (8.07 puan mutlak, %70.1 bağıl düşüş) çekildi.
4. ✅ **Adım 4:** `scripts/benchmark_guardrail_rivals.py` refaktör edilerek Wilson $\%95$ güven aralıkları ve tabakalı $N=120$ benchmark ampirik olarak koşturuldu.
5. ✅ **Adım 5:** Testler doğrulandı: `pytest` 18/18 (%100 PASS), `verify_full_pipeline.py` 20/20 (%100 PASS).


