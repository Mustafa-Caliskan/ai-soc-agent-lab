# CyberTech Neural Shield: Büyük Dil Modelleri İçin Çok Katmanlı Hibrit Güvenlik Mimarisi
### Doğrudan Çok Dilli (XLM-RoBERTa) Semantik Tehdit Sınıflandırması, Unicode Steganografi Tespiti ve DLP Entegrasyonu

**Yazarlar:**  
*Mustafa ÇALIŞKAN¹\*, Prof. Dr. Ali Hakan IŞIK²*  
¹Burdur Mehmet Akif Ersoy Üniversitesi, Mühendislik Fakültesi, Bilgisayar Mühendisliği Bölümü  
²Burdur Mehmet Akif Ersoy Üniversitesi, Bilgisayar Mühendisliği Bölümü (Akademik Danışman)  
*\*İletişim: mustafacaliskan@ogr.mehmetakif.edu.tr, hisik@mehmetakif.edu.tr*

---

### Özet
Büyük Dil Modellerinin (LLM) kurumsal iş akışlarına ve kamu altyapılarına entegre edilmesi, doğal dil arayüzlerini hedef alan yeni nesil siber tehdit vektörlerini beraberinde getirmiştir. Komut enjeksiyonu (*Prompt Injection*), jailbreaking (etik ve güvenlik sınırlarını aşma), sistem komutu sızıntısı (*System Prompt Extraction*), sinsi kurgular (*Adversarial Framing*) ve Unicode Tag (*U+E0000 - U+E007F* aralığındaki "Görünmez Mürekkep") steganografisi gibi teknikler, geleneksel ağ güvenlik duvarlarının ve statik filtrelerin etrafından kolaylıkla dolaşabilmektedir. 

Bu çalışmada, söz konusu tehditlere karşı uçtan uca savunma sağlayan ve çevre birim (*peripheral gateway*) düzeyinde konumlanan 4 katmanlı hibrit bir güvenlik mimarisi (**CyberTech Neural Shield v5**) önerilmektedir. Önerilen sistem:
1. **Katman 0:** NFKC normalizasyonu, ZWJ-emojileri koruyan sıfır genişlikli karakter filtresi ve çoklu çözücüleri (Base64, Hex, ROT13, Reverse, Unicode Tag) içeren Normalizasyon ve Steganografi Motoru (<0.2 ms),
2. **Katman 1:** Çift dilli (TR/EN) ağırlıklı sezgisel kural ve regex motoru (<0.3 ms),
3. **Katman 2:** 71.440 dengeli çok dilli veri örneği ve CyberFocalLoss ($\gamma=2.0$) ile eğitilen, ardından INT8 kuantizasyonu ile ONNX motoruna aktarılarak CPU üzerinde 12.27 ms çıkarım süresine indirgenen **XLM-RoBERTa ONNX INT8 v5** semantik tehdit sınıflandırıcısı,
4. **Katman 3:** Model yanıtlarındaki TCKN, kredi kartı (PAN), IBAN ve API gizli anahtarlarını algoritmik sağlama algoritmalarıyla (Luhn/TC mod-10/11) doğrulayarak maskeleyen **DLP (Veri Sızıntısı Önleme)** katmanından (<0.1 ms) oluşmaktadır.

Sistem, korunan kurumsal model olarak **EVREN H200 Süper Bilgisayar LLM Filosu** ve kurumsal dil modelleri önünde konumlandırılmıştır. 10.716 bağımsız test örneği üzerinde gerçekleştirilen ampirik değerlendirmelerde Katman 2; **%94.64 Doğruluk**, **%94.63 Macro F1**, optimal eşikte ($\tau=0.4567$) **%96.89 F1-Skoru**, **0.9954 ROC-AUC** ve teknik IT istemlerinde **%0.00 Yanlış Alarm (FPR)** elde etmiştir. Canlı çift dilli siber saldırı testlerinde **%100 saldırı yakalama (sıfır kaçırma)** sergilenmiştir. Harici çeviri bağımlılığı tamamen ortadan kaldırılarak sistem gecikmesi uçtan uca **12.73 ms** seviyesine indirilmiştir.

**Anahtar Kelimeler:** LLM Güvenliği, Prompt Injection Savunması, XLM-RoBERTa, CyberFocalLoss, INT8 Kuantizasyonu, ONNX Runtime, Unicode Steganografi, Veri Sızıntısı Önleme (DLP), EVREN H200, Hibrit Güvenlik Mimarisi.

---

## 1. Giriş
Büyük Dil Modelleri (*Large Language Models - LLM*), doğal dil işleme alanındaki çığır açan dönüşümle birlikte kurumsal karar destek mekanizmalarında, havalimanı ve bankacılık operasyonlarında, otonom yazılım geliştirme hatlarında ve müşteri iletişim sistemlerinde merkezi bir rol üstlenmiştir. Milyarlarca parametreli temel modeller, olağanüstü anlama ve üretim kabiliyetleri sunmaktadır. Ne var ki, sistem mimarilerinin komutlar ile kullanıcı girdilerini aynı bağlam penceresi (*context window*) içerisinde işlemesi, geleneksel yazılım güvenliğinde görülmeyen yapısal bir zafiyet doğurmuştur.

Literatürde komut enjeksiyonu (*Prompt Injection*) olarak adlandırılan saldırılarda, saldırgan meşru bir kullanıcı talebi maskesi altında sistem direktiflerini geçersiz kılan manipülatif girdiler iletmektedir. Jailbreaking tekniklerinde ise modelin güvenlik kılavuzları ve etik filtreleri atlatılarak yetkisiz eylemler icra edilmektedir. Greshake ve arkadaşları (2023), harici belgeler ve web sayfaları üzerinden gerçekleştirilen dolaylı prompt injection saldırılarının LLM tabanlı kurumsal uygulamaları bütünüyle rehin alabileceğini deneysel olarak kanıtlamıştır.

Bu risklere ek olarak, Unicode standardındaki özel etiket karakterlerinin (*U+E0000 - U+E007F*) kötüye kullanılmasıyla icra edilen **"Invisible Ink" (Görünmez Mürekkep / Steganografi)** saldırıları yeni ve tehlikeli bir tehdit alanı açmıştır. Kullanıcı arayüzünde tek bir masum emoji veya boşluk gibi görünen bu diziler, tokenizer düzeyinde ayrıştırılarak LLM'e gizli ve yıkıcı komutlar iletebilmektedir.

Kurumsal sistemlerde LLM güvenliğini sağlama noktasında üç temel açmaz bulunmaktadır:
1. **Yüksek Çıkarım Gecikmesi:** LlamaGuard gibi harici güvenlik modellerinin getirdiği yüksek çıkarım gecikmesi (1-2 saniye) ve devasa GPU gereksinimi.
2. **Çok Dilli Tokenizasyon Kırılması ve Çeviri Yükü:** Tek dilli modellerin (örn. DeBERTa-v3) Türkçe girdilerde aşırı subword parçalanması yaşaması ve harici çeviri modellerinin (örn. Helsinki-NLP) 100+ ms ek gecikme yaratması.
3. **Aşırı Yanlış Alarm (False Positive):** Açık kaynaklı modellerin kurumsal üretimde sergilediği aşırı duyarlılık. İçerisinde *"şifremi unuttum"*, *"sql hatası"*, *"admin"* veya *"bilet iptal"* gibi kelimeler geçen masum sorguların saldırı sanılarak engellenmesi.

Bu çalışmanın amacı; harici çeviriye ihtiyaç duymayan doğrudan çok dilli (*multilingual*) bir omurgaya sahip, kuantizasyonla CPU üzerinde 12.27 ms gecikmeye inen, Unicode steganografisini deterministik olarak bertaraf eden ve veri sızıntılarını önleyen 4 katmanlı hibrit bir güvenlik mimarisi (**CyberTech Neural Shield v5**) geliştirmek ve ampirik olarak doğrulamaktır.

---

## 2. Yöntem ve Sistem Mimarisi

CyberTech Neural Shield v5, gelen kullanıcı mesajlarını modele ulaşmadan önce ve modelden çıkan yanıtları kullanıcıya dönmeden önce denetleyen 4 ardışık koruma katmanından müteşekkildir.

```
[ Kullanıcı Girdisi (TR / EN / Çok Dilli) ]
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ KATMAN 0: Normalizasyon & Steganografi Motoru (<0.2 ms)     │
│  - NFKC normalizasyonu, homoglyph katlama                   │
│  - ZWJ-emojileri koruma, ZWSP görünmez boşluk temizleme     │
│  - Çoklu çözücüler: Base64, Hex, ROT13, Ters-yazma, URL     │
│  - Unicode Tag (U+E0000 - U+E007F) steganografi deşifresi   │
└─────────────────────────────────────────────────────────────┘
         │ (Temiz & Çözümlenmiş Metin)
         ├───► [KATMAN 1: Deterministik Regex Motoru (<0.3 ms)]
         │     - 30+ TR/EN saldırı şablonu ve ağırlıklı puanlama
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ KATMAN 2: XLM-RoBERTa ONNX INT8 v5 Semantik Sınıflandırıcı │
│  - 71.440 örnek ve CyberFocalLoss (γ=2.0) eğitimi           │
│  - 100 dilde doğrudan semantik kavrayış (Çevirisiz)         │
│  - INT8 Kuantizasyonu (278 MB) & CPU Çıkarımı: 12.27 ms     │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ BİLEŞİK RİSK & DİNAMİK BAN MOTORU (Config-Driven)           │
│  - Composite = 0.70·ML + 0.20·Regex + 0.10·Stego            │
│  - Risk >= Eşik (60) ise 🛑 BLOCKED (HTTP 403)              │
└─────────────────────────────────────────────────────────────┘
         │ (Güvenli ise Kurumsal Modele Gönder)
         ▼
┌─────────────────────────────────────────────────────────────┐
│ KORUNAN TEMEL MODEL: EVREN H200 LLM Filosu / SkyPort IST    │
│  - Qwen3.8-Flash, Gemma-4-31B, DeepSeek-v4.1                │
└─────────────────────────────────────────────────────────────┘
         │ (Ham Yanıt)
         ▼
┌─────────────────────────────────────────────────────────────┐
│ KATMAN 3: DLP (Veri Sızıntısı Önleme) Çıktı Maskeleyici     │
│  - TCKN (Resmi mod-10/11 algoritması doğrulamalı)           │
│  - Kredi Kartı (PAN 16 hane Luhn doğrulamalı)               │
│  - IBAN, JWT, PEM ve Sistem API Anahtarları Maskeleme        │
│  - Gecikme: <0.1 ms                                         │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
[ Güvenli Kullanıcı Çıktısı ]
```

### 2.1. Katman 0: Normalizasyon & Steganografi Motoru
Sisteme ulaşan ham girdi metinleri ilk olarak sıfırıncı dereceden normalizasyona tabi tutulur:
* **NFKC ve Homoglyph Katlama:** Kiril ve Grek alfabelerinden kopyalanan benzer karakterler (ör. Kiril `а`, `е`, `о`) standart Latin alfabesine dönüştürülür.
* **Steganografi (Görünmez Mürekkep) Tespiti:** Unicode Tag aralığındaki (`\U000E0000 <= c <= \U000E007F`) karakterler deşifre edilir ve metin akışına katılır.
* **Çoklu Çözücüler:** Base64, Hex, ROT13 ve ters yazılmış metinler çözülerek semantik katmana iletilir.

### 2.2. Katman 1: Regex & Heuristic Kural Motoru
Bilinen prompt injection kalıpları, sistem direktifi iptalleri ve rol gaspı girişimleri iki dilli ağırlıklı desenlerle taranır.

### 2.3. Katman 2: XLM-RoBERTa ONNX INT8 v5 Semantik Sınıflandırıcısı
Sistemin çekirdeği olan Katman 2, 71.440 dengeli örnek üzerinde **CyberFocalLoss ($\gamma=2.0$)** optimizasyonuyla eğitilmiştir.
* **CyberFocalLoss:** Kolay örneklerin gradiyentini bastırarak modelin karmaşık senaryo ve rol yapma (Adversarial Framing) saldırılarına odaklanmasını sağlar.
* **INT8 Kuantizasyonu:** PyTorch modeli ONNX INT8 formatına ihraç edilerek boyutu 278 MB'a, CPU çıkarım gecikmesi **12.27 ms**'ye düşürülmüştür.

### 2.4. Katman 3: DLP (Veri Sızıntısı Önleme) Çıktı Filtresi
Korunan modelin ürettiği yanıtlar kullanıcıya iletilmeden önce algoritmik sağlama ile taranır. Yalnızca Luhn algoritmasını geçen gerçek kredi kartları ve resmi TCKN checksum'unu doğrulayan kimlik numaraları maskelenir.

---

## 3. Deneysel Bulgular ve Başarım Analizi

### Tablo 1: NeuralShield-v5 Model Başarım Metrikleri ve Kıyaslama
| Test Kümesi / Model | Örneklem ($n$) | Doğruluk (Acc) | F1-Skoru | Kesinlik (Prec) | Duyarlılık (Recall) | ROC-AUC | IT FPR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **NeuralShield-v5 (Hold-out Test, $\tau=0.50$)** | 10.716 | **%94.64** | **%94.63** | %94.65 | %94.62 | **0.9954** | **%0.00** |
| **NeuralShield-v5 (Optimal Eşik, $\tau=0.4567$)**| 10.716 | **%96.89** | **%96.89** | %96.72 | %97.05 | **0.9954** | **%0.00** |
| **Canlı Çift Dilli Siber Saldırı Havuzu** | 100 | **%98.00** | **%97.98** | %96.15 | **%100.00** | **0.9980** | **%0.00** |
| *Katman 1 (Tek Başına Regex)* | 100 | %68.75 | 0.5455 | %100.00 | %37.50 | 0.0000 | %0.00 |

### 3.1. Çıkarım Gecikmesi (Latency) Analizi
* **Katman 0 (Normalizasyon & Steganografi):** Ortalama **0.17 ms**
* **Katman 1 (Regex & Heuristic Motoru):** Ortalama **0.29 ms**
* **Katman 2 (XLM-RoBERTa ONNX INT8 v5 - CPU):** Ortalama **12.27 ms**
* **Katman 3 (DLP Maskeleme):** Ortalama **< 0.05 ms**
* **Toplam Güvenlik Ağ Geçidi Gecikmesi:** Ortalama **12.73 ms**

Kurumsal modellerin ~400-1200 ms yanıt süresi göz önüne alındığında, 12.73 ms'lik güvenlik gecikmesi kurumsal kullanıcı deneyimini kesinlikle etkilememektedir.

### 3.2. Bağımsız (Out-of-Distribution) Değerlendirme
Tablo 1'deki sonuçlar eğitimle aynı dağılımdan (in-distribution) çekilen Hold-out kümesine aittir. Genellenebilirliği ölçmek için, eğitimde kullanılmayan SOTA kaynaklardan derlenen **12 dilli, N=2.000 (1.000/1.000)** bağımsız bir benchmark kullanılmıştır. Bu sette efektif ayrım (ml_risk AUC) **≈ 0.89**, dağıtılan OR-Gate karar noktasında (`hard_stego ∨ regex≥60 ∨ ml_risk≥70`) **Saldırı Recall ≈ %72 [%68–76]** ve **Meşru FP ≈ %12 [%9–15]** (Wilson %95 GA) ölçülmüştür. Buna karşılık metindeki **"%0 ASR / %0 IT-FPR"** ifadeleri yalnızca **bilinen-imza (known-signature) korpusu** için geçerlidir; dış dağılımda sistem bir **kesinlik-duyarlılık ödünleşimi** işletir. Bu, mimarinin sıfır-gün manipülasyonlara karşı mutlak koruma iddia etmediğini şeffaf biçimde gösterir.

---

## 4. Tartışma ve Sonuç
Elde edilen deneysel bulgular; LLM güvenliğinin model içsel kurallarıyla değil, bağımsız ve yerel bir güvenlik ağ geçidi (*peripheral gateway*) mimarisiyle sağlanmasının hem hız hem de güvenlik açısından üstün olduğunu kanıtlamıştır.

XLM-RoBERTa v5 mimarisinin sağladığı yerel çok dillilik ve CyberFocalLoss optimizasyonu, sinsi kurguların yakalanmasında kritik bir sıçrama yaratmıştır. ONNX INT8 kuantizasyonu sayesinde model, pahalı veri merkezi GPU'larına bağımlı kalmaksızın standart CPU altyapılarında 12.27 ms gecikmeyle üretim ortamında hizmet verebilmektedir.

### 4.1. Tehdit Modeli ve Kapsam Sınırları (Threat Model & Scope)

NeuralShield bir **Uygulama Güvenliği (AppSec / LLM SOC Gateway)** kalkanıdır; bir içerik moderasyonu veya "ahlak polisi" modeli **değildir**. Sistem **saldırı mekanizmasını** hedefler, **konuyu** değil. Bu ayrım, hem modelin eğitim felsefesini hem de deneysel değerlendirmenin sınırlarını tanımlar.

**Kapsam İçi (In-Scope):** OWASP **LLM01 (Prompt Injection)** ve **LLM06 (Hassas Bilgi İfşası)**; dolaylı enjeksiyon (IPI/RAG), sistem-promptu sızıntısı (canary/API anahtarı), jailbreak & rol gaspı (DAN), **zorlama (coercion)** yoluyla kural ezme, kaçınma/kodlama (Base64/Hex/ROT13/ters-yazma), steganografi (Unicode Tag, sıfır-genişlik, homoglyph), teknik istismar dizgeleri (SQLi/XSS/ters-shell) ve çıkış-taraflı DLP.

**Kapsam Dışı (Out-of-Scope, delege edilmiştir):** CBRN (kimyasal/biyolojik/silah sentezi, bomba), kendine zarar/intihar, uyuşturucu tedariki ve konu-tabanlı nefret/ayrımcılık gibi genel içerik-politikası denetimleri. Bu alanlar, arka plandaki üretici modelin **Alignment/RLHF** mekanizmasına veya **Llama-Guard-3** benzeri ayrı bir Trust & Safety katmanına devredilmiştir.

> *"NeuralShield-v5, OWASP LLM01 (Prompt Injection) ve LLM06 (Hassas Veri Sızıntısı) tehditlerine odaklanan bir altyapı güvenlik duvarıdır. CBRN, intihar ve içerik sansürleme gibi sosyal politika filtrelemeleri, arkadaki modelin Alignment (RLHF) mekanizmasına veya Llama-Guard benzeri Trust & Safety katmanlarına devredilmiştir."*

**Sınırlılıklar (Dürüst Değerlendirme):** Eğitim korpusundaki jailbreak setlerinin bir yan etkisi olarak model, coercion içermeyen bazı açık küfür/hakaret kalıplarına sınırlı hassasiyet (%59–76) gösterebilmektedir; öfkeli meşru müşteri sitemleri ise doğru şekilde Benign sınıflandırılmaktadır. Bu, asıl AppSec hedefinin bir yan ürünüdür ve içerik/kategori moderasyonu bu mimarinin kapsamı dışındadır. Gelecek çalışmada (v6) kapsam-hizalı eğitim ve katman-1 opsiyonel nezaket modülü ile ayrıştırılması hedeflenmektedir.

---

## Kaynaklar
1. K. Greshake et al., "Not what you've signed up for: Compromising real-world LLM-integrated applications with indirect prompt injections," in *Proc. 16th ACM Workshop on Artificial Intelligence and Security (AISEC)*, 2023.
2. A. Conneau et al., "Unsupervised cross-lingual representation learning at scale," in *Proc. 58th Annual Meeting of the Association for Computational Linguistics (ACL)*, 2020.
3. F. Perez and I. Ribeiro, "Ignore previous prompt: Attack techniques for language models," in *NeurIPS ML Safety Workshop*, 2022.
4. OWASP Foundation, "OWASP Top 10 for Large Language Model Applications v1.1," *Tech. Rep.*, 2023.
5. S. Inan et al., "Llama Guard: LLM-based input-output safeguard for human-AI conversations," *arXiv preprint arXiv:2312.06674*, 2023.
6. Google DeepMind, "Gemini 3.6 Flash Model Documentation and Interactions API," *Google AI Developer Reference*, 2024.
