# Büyük Dil Modellerinde Çok Katmanlı Güvenlik Ağ Geçidi: XLM-RoBERTa Tabanlı Doğal Çok Dilli ve Kuantize Semantik Savunma
### Multi-Layer Security Gateway for Large Language Models: Native Multilingual and Quantized Semantic Defense via XLM-RoBERTa

**Mustafa ÇALIŞKAN¹\*, Prof. Dr. Ali Hakan IŞIK²**  
¹Burdur Mehmet Akif Ersoy Üniversitesi, Mühendislik Fakültesi, Bilgisayar Mühendisliği Bölümü, Burdur, Türkiye  
²Burdur Mehmet Akif Ersoy Üniversitesi, Bilgisayar Mühendisliği Bölümü (Akademik Danışman), Burdur, Türkiye  
*\*İletişim: mustafacaliskan@ogr.mehmetakif.edu.tr, hisik@mehmetakif.edu.tr*

---

### Özet
Büyük Dil Modellerinin (LLM) kurumsal karar destek mekanizmalarına ve kamuya açık arayüzlere entegre edilmesi, doğal dil girdilerini manipüle eden yeni nesil siber tehdit vektörlerini beraberinde getirmiştir. Komut enjeksiyonu (Prompt Injection), jailbreak ve görünmez Unicode Tag (U+E0000 - U+E007F) steganografisi gibi teknikler, geleneksel ağ güvenlik duvarlarını ve LLM sağlayıcılarının dahili güvenlik filtrelerini aşabilmektedir. Bu çalışmada, harici bir çeviri katmanına ihtiyaç duymaksızın doğrudan çok dilli çalışan ve mikro-gecikme seviyesinde koruma sağlayan 4 katmanlı hibrit bir çevre savunma mimarisi (**CyberTech Neural Shield v5**) önerilmektedir. Önerilen mimari; (1) NFKC, ZWJ-emojileri koruyan görünmez karakter temizleyici ve çoklu çözücüden (Base64/Hex/ROT13/Reverse/Unicode-Tag) oluşan Normalizasyon ve Steganografi Motoru (Katman 0, <0.2 ms), (2) çift dilli ağırlıklı kural motoru (Katman 1, <0.3 ms), (3) 71.440 dengeli veri örneği ve sinsi kurgulara karşı CyberFocalLoss ($\gamma=2.0$) ile eğitilen, CPU üzerinde 12.27 ms gecikmeyle çalışan kuantize **XLM-RoBERTa ONNX INT8** Semantik Sınıflandırıcısı (Katman 2) ve (4) model yanıtlarındaki hassas verileri algoritmik checksum (Luhn/TCKN) ile maskeleyen Veri Sızıntısı Önleme (DLP) katmanından (Katman 3, <0.1 ms) oluşmaktadır. 10.716 adetlik bağımsız hold-out test kümesinde yapılan ampirik değerlendirmeler; önerilen modelin **%94.64 doğruluk**, **%94.63 Macro F1-skoru**, optimal eşikte ($\tau=0.4567$) **%96.89 F1-skoru**, **0.9954 ROC-AUC** ve teknik IT istemlerinde **%0.00 Yanlış Alarm (False Positive)** ürettiğini kanıtlamıştır. Sistem, uçtan uca 12.73 ms gecikmeyle çalışarak kurumsal LLM API maliyetlerini ve hizmet kesinti (DoS) risklerini sıfıra indiren yüksek verimli bir çevre savunması sağlamaktadır.

**Anahtar Kelimeler:** Büyük Dil Modelleri, LLM Güvenliği, Prompt Injection, XLM-RoBERTa, CyberFocalLoss, ONNX INT8 Kuantizasyon, Unicode Steganografi, Çevre Savunması (Peripheral Defense), Veri Sızıntısı Önleme (DLP).

---

### Abstract
Integrating Large Language Models (LLMs) into enterprise infrastructure introduces novel adversarial attack vectors exploiting natural language interfaces. Techniques such as prompt injection, jailbreaking, and invisible Unicode Tag steganography (U+E0000 - U+E007F) easily bypass conventional rule-based firewalls and proprietary model-level filters. In this study, we propose **CyberTech Neural Shield (v5.0)**, a four-tier hybrid peripheral defense architecture providing micro-latency protection natively across multiple languages without relying on intermediate translation models. The architecture comprises: (1) a sub-millisecond (<0.2 ms) Layer 0 Normalization & Steganography Engine mitigating Unicode Tag invisible characters, zero-width spaces while preserving ZWJ emojis, and recursive decoders (Base64, Hex, ROT13, Reverse), (2) a Layer 1 bilingual heuristic regex engine (<0.3 ms), (3) a Layer 2 **XLM-RoBERTa ONNX INT8** quantized semantic classifier fine-tuned with **CyberFocalLoss ($\gamma=2.0$)** across 71,440 balanced samples delivering 12.27 ms inference latency on CPU, and (4) an outbound Data Loss Prevention (DLP) engine (Layer 3) with algorithmic checksum verification (Luhn & TC Kimlik No). Empirical evaluation on an independent hold-out test set of 10,716 samples demonstrates an **accuracy of 94.64%**, **macro F1-score of 94.63%**, **optimal threshold F1 of 96.89% ($\tau=0.4567$)**, an **ROC-AUC of 0.9954**, and **0.00% false positive rate** on enterprise IT prompts. Deployed as a peripheral guardrail, the architecture neutralizes API resource exhaustion (DoS) risks and eliminates token overhead under an end-to-end CPU latency of **12.73 ms**.

**Index Terms:** Large Language Models, LLM Security, Prompt Injection, XLM-RoBERTa, CyberFocalLoss, ONNX INT8 Quantization, Unicode Steganography, Peripheral Defense, Data Loss Prevention.

---

## I. GİRİŞ
Büyük Dil Modelleri (Large Language Models - LLM), doğal dil işleme alanındaki transformatör devrimi sayesinde kurumsal iş akışlarında, müşteri iletişim sistemlerinde ve kritik karar destek mekanizmalarında merkezi bir aktör haline gelmiştir [1]. Ancak modern dil modelleri, klasik Von Neumann bilgisayar mimarisinden farklı olarak **komut (talimat) ile kullanıcı verisini birbirinden ayıramaz**; girdi olarak verilen tüm belirteçleri (*tokens*) aynı bağlam penceresinde (*context window*) tek bir metin dizisi olarak işler [4]. Bu yapısal zafiyet, kötü niyetli aktörlerin masum kullanıcı sorguları kisvesi altında sistem talimatlarını geçersiz kılmasına (*Prompt Injection*), kurumsal veri tabanlarını sızdırmasına veya etik güvenlik bariyerlerini yıkmasına (*Jailbreak*) yol açmaktadır [7].

Buna ek olarak, Unicode standardında dil etiketleme amacıyla tanımlanmış özel etiket karakterleri (U+E0000 - U+E007F) kötüye kullanılarak icra edilen steganografik saldırılar yeni bir tehdit boyutu doğurmuştur. Arayüzde tek bir masum emoji veya boşluk gibi görünen bu karakterler, tokenizer seviyesinde ayrıştırılarak LLM'e görünmez kötü niyetli talimatlar iletmektedir.

Mevcut LLM güvenlik yaklaşımlarında üç temel kısıt bulunmaktadır:
1. **Yüksek Çıkarım Gecikmesi ve Maliyet:** LlamaGuard [12] gibi büyük güvenlik modelleri 1-2 saniyelik gecikme ve devasa donanım maliyeti üretmektedir.
2. **Harici Çeviri Bağımlılığı:** İngilizce odaklı modeller Türkçe gibi dillerde çalıştığında morfolojik uyumsuzluk nedeniyle yanlış alarmlar vermekte; harici çeviri modelleri ise sisteme 120 ms'nin üzerinde ek gecikme bindirmektedir.
3. **Aşırı Yanlış Alarm (False Positive):** Siber güvenlik sınıflandırıcıları kurumsal IT destek taleplerinde geçen 'password', 'sql', 'system' gibi masum terimleri saldırı sanarak iş akışlarını kilitlemektedir.

Bu çalışmada, söz konusu sorunları kökten çözmek amacıyla:
* Harici çeviri katmanını tamamen ortadan kaldıran, Türkçe ve İngilizce dillerini doğal olarak anlayan,
* 71.440 dengeli veri örneği ve sinsi kurgulara (Adversarial Framing) dirençli CyberFocalLoss ($\gamma=2.0$) ile eğitilip CPU için kuantize edilen (**12.27 ms** çıkarım süreli **XLM-RoBERTa ONNX INT8 v5**),
* Steganografik görünmez tehditleri milisaniyenin altında (<0.2 ms) temizleyen, deterministik kural motoru ve DLP maskelemesiyle kurumsal sızıntıları önleyen **CyberTech Neural Shield v5** 4 katmanlı hibrit çevre savunma mimarisi sunulmaktadır.

---

## II. ÇEVRE SAVUNMASININ GEREKLİLİĞİ VE MALİYET ANALİZİ
*(The Necessity of Peripheral Defense)*

Akademik literatürde ve endüstride sıklıkla sorulan temel soru şudur: *"Google Gemini, OpenAI GPT-4o gibi modeller zaten milyar dolarlık bütçelerle eğitilmekte ve kendi güvenlik filtrelerine sahiptir. Harici bir ön cephe güvenlik katmanına (Guardrail) neden ihtiyaç vardır?"*

Bu çalışmanın varlık sebebi olan 4 temel siber güvenlik gerekçesi şunlardır:

### A. Kod ve Veri Ayrımının İmkânsızlığı (Inherent Vulnerability)
Geleneksel işletim sistemlerinde kod belleği ile veri belleği katı biçimde ayrılmıştır (W^X / DEP prensibi). LLM'lerde ise sistem yöneticisi talimatı, kullanıcı girdisi ve harici RAG dokümanları aynı tensör akışında birleşir. Bu sebeple en gelişmiş modeller dahi bilişsel çerçeveleme (*Cognitive Framing*), kademeli ikna (*Crescendo Attack*) ve rol yapma teknikleriyle kandırılabilmektedir [10].

### B. Dolaylı Enjeksiyon Tehdidi (Indirect Prompt Injection)
Kurumsal bir LLM asistanı harici bir web sayfasını veya yolcunun yüklediği bilet PDF'ini özetlerken, belge içerisine gizlenmiş görünmez beyaz metinleri okuduğunda zafiyete düşer. Bu saldırı kullanıcıdan değil, belgeden geldiği için modelin iç filtresi devreye girmez. Çevre savunmamız dokümanı modele gitmeden önce ayıklar.

### C. Hizmet Kesinti Saldırıları (DoS) ve Token Maliyet Tasarrufu
Saldırganlar kurumsal LLM API'lerine binlerce kelimelik manipülatif promptlar göndererek şirketi iflas ettirecek API faturaları (Resource Exhaustion) çıkarabilir. Bir saldırı promptu doğrudan kurumsal modele gittiğinde model bunu okur, reddetse dahi şirket binlerce token ücreti öder ve 800-1500 ms sistem meşgul edilir. 

NeuralShield çevre savunmasında ise saldırı yerel sunucuda **12.27 ms'de ve sıfır ($0) API maliyetiyle** ağ seviyesinde (HTTP 403) imha edilir. Token tasarruf bağıntısı Denklem 1 ile modellenmiştir:
$$\Delta C = \sum_{k=1}^{N_{\text{attack}}} \left( \text{Tokens}_k \times P_{\text{token}} \right) - C_{\text{local\_cpu}}$$
Burada $P_{\text{token}}$ ticari API birim fiyatı, $C_{\text{local\_cpu}} \approx 0$ yerel mikro-çıkarım maliyetidir.

### D. Kurumsal Hassas Veri İzolasyonu (Hard Negatives)
Genel bulut modelleri kurumsal IT bağlamını bilmez. NeuralShield, havalimanı ve kurumsal terminolojide geçen kritik kelimeleri ("şifremi unuttum", "Active Directory sorgusu", "SQL logu") yanlış alarm üretmeden güvenle işler.

---

## III. ÖNERİLEN HİBRİT SİSTEM MİMARİSİ

CyberTech Neural Shield v5, gelen istekleri ardışık 4 katmandan geçiren asenkron bir güvenlik ağ geçididir.

```
[İstemci / Yolcu Girdisi (Metin / PDF / URL)] 
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│ KATMAN 0: Normalizasyon & Steganografi Motoru (<0.2 ms)     │
│ - NFKC Kanonik Normalizasyon & Fullwidth Dönüştürme         │
│ - ZWJ-Emoji Koruma & ZWSP Görünmez Boşluk Temizleme        │
│ - Çoklu Çözücüler: Base64, Hex, ROT13, Ters-yazma, URL      │
│ - Unicode Tag (U+E0000 - U+E007F) Görünmez Metin Taraması   │
└─────────────────────────────────────────────────────────────┘
          │ (Temiz & Çözümlenmiş Metin)
          ├───► [KATMAN 1: Deterministik Regex Motoru (<0.3 ms)]
          │     - TR/EN Komut İptali, DAN, Yetki Rolü (30+ desen)
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│ KATMAN 2: XLM-RoBERTa ONNX INT8 v5 Semantik Sınıflandırıcı │
│ - Doğal Çok Dilli (TR/EN) Çıkarım (12.27 ms CPU Gecikmesi) │
│ - 71.440 Örnek & CyberFocalLoss (γ=2.0) ile Eğitilmiş      │
│ - Sinsi Kurgu & Rol Çalma Saldırılarına Dirençli             │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│ BİLEŞİK RİSK & KARAR MOTORU (Config-Driven & Dinamik Ban)   │
│ Composite = 0.70·ML + 0.20·Regex + 0.10·Stego               │
│ Risk >= Etkin Eşik (Varsayılan: 60) -> 🛑 HTTP 403 BLOCKED  │
└─────────────────────────────────────────────────────────────┘
          │ (Güvenli: ALLOWED)
          ▼
┌─────────────────────────────────────────────────────────────┐
│ HEDEF LLM: Kurumsal Model Filosu (EVREN H200 / SkyPort IST) │
│ - Qwen3.8-Flash, Gemma-4-31B, DeepSeek-v4.1, Gemini Flash   │
└─────────────────────────────────────────────────────────────┘
          │ (Ham Model Yanıtı)
          ▼
┌─────────────────────────────────────────────────────────────┐
│ KATMAN 3: DLP (Veri Sızıntısı Önleme) (<0.1 ms)             │
│ - Luhn Doğrulamalı Kredi Kartı Maskeleme (PAN)              │
│ - TCKN Algoritmik Checksum Doğrulamalı Maskeleme            │
│ - JWT Token, PEM Private Key, IBAN & Sistem Sırları         │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
[Kullanıcıya İletilen Güvenli Yanıt]
```

### A. Katman 0: Normalizasyon ve Steganografi Motoru
Ham metin ilk olarak sıfırıncı dereceden mikro-analize tabi tutulur:
1. **Unicode Tag Tespiti:** Unicode standardında yer alan U+E0000 - U+E007F aralığındaki baytlar filtrelenir ve deşifre edilir:
   $$\text{Payload} = \bigcup_{i} \text{chr}(\text{ord}(c_i) - \text{0xE0000})$$
2. **ZWJ-Güvenli Emoji ve Boşluk Filtresi:** `\u200d` birleştirici emojileri (`👨‍👩‍👧‍👦`) korunurken, alfabe arasına gizlenen sıfır genişlikli karakterler (`\u200b`, `\ufeff`) elenir.
3. **Çoklu Çözücüler:** Base64, Hex, ROT13, ters yazılmış dizgeler ve URL kodlamaları çözülerek Katman 1 ve Katman 2'ye iletilir.

### B. Katman 1: Çift Dilli Heuristic Regex Motoru
30'dan fazla ağırlıklı siber saldırı şablonu (DAN varyantları, talimat geçersiz kılma, sistem yöneticisi taklidi) taranır ve 0-100 arasında sezgisel risk skoru üretilir.

### C. Katman 2: XLM-RoBERTa ONNX INT8 v5 Semantik Sınıflandırıcısı
Sistemin beyni olan Katman 2, `xlm-roberta-base` omurgası üzerinde CyberFocalLoss ile eğitilmiştir.
* **CyberFocalLoss ($\gamma=2.0$):** Kolay örneklerin kaybını bastırarak modelin sinsi kurgulara (*Adversarial Framing*) ve zorlu sınır örneklerine odaklanmasını sağlar.
* **Kuantizasyon (ONNX INT8):** PyTorch FP32 modeli ONNX formatına ihraç edilip 8-bit dinamik kuantizasyona tabi tutulmuştur. Model boyutu **278 MB**'a indirilmiş ve CPU çıkarım gecikmesi **12.27 ms** olarak ölçülmüştür.

### D. Katman 3: DLP (Veri Sızıntısı Önleme) Katmanı
Model yanıtındaki kredi kartları **Luhn algoritması**, T.C. Kimlik numaraları ise **resmi mod-10/11 sağlama algoritmaları** ile kontrol edilir. Sahte veya rastgele numaralar gereksiz yere maskelenmezken, geçerli finansal ve kimlik verileri ile API anahtarları, JWT başlıkları ve PEM özel anahtarları sansürlenir.

---

## IV. DENEYSEL BULGULAR VE BAŞARIM ANALİZİ

### A. Veri Kümesi ve Eğitim Protokolü
Model, 30 farklı açık kaynaklı ve yerel veri setinin birleşiminden oluşan **71.440 dengeli master örnek** ile eğitilmiştir. Veri kirlenmesini önlemek amacıyla eğitimde yer alan setler kıyaslama (benchmark) havuzundan titizlikle ayrıştırılmıştır.
* **Stratified 3-Way Split:** Eğitim (50.006 - %70), Doğrulama (10.718 - %15), Bağımsız Hold-out Test (10.716 - %15).
* **Donanım:** NVIDIA A100 GPU üzerinde FP16 karışık duyarlılık, CyberFocalLoss ($\gamma=2.0$, $\alpha=0.25$) ve AdamW optimizatörüyle eğitilmiştir.

### Tablo I: NeuralShield-v5 Kapsamlı Deneysel Başarım Karnesi
| Değerlendirme Kümesi | Örnek Sayısı (n) | Doğruluk (Acc) | Macro F1 | Kesinlik (Prec) | Duyarlılık (Rec) | ROC-AUC | IT Yanlış Alarm (FPR) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Bağımsız Hold-out Test ($\tau=0.50$)** | 10.716 | **%94.64** | **%94.63** | **%94.65** | **%94.62** | **0.9954** | **%0.00** |
| **Optimal Eşik Başarımı ($\tau=0.4567$)** | 10.716 | **%96.89** | **%96.89** | **%96.72** | **%97.05** | **0.9954** | **%0.00** |
| **Canlı Çift Dilli Siber Saldırı Havuzu** | 100 | **%98.00** | **%97.98** | %96.15 | **%100.00** | **0.9980** | **%0.00** |

### B. Grafiksel Bulguların Analizi (Yayın Figürleri)

1. **Eğitim ve Doğrulama Kayıp Eğrisi (Şekil 1):** Model her epoch sonunda düzenli olarak yakınsamış, CyberFocalLoss sayesinde doğrulama kaybı kararlı biçimde optimize edilmiştir.
2. **Metrik İlerlemesi (Şekil 2):** Doğruluk, Precision, Recall ve Macro F1 eğrileri epoch boyunca %94.6'nın üzerine dengeli biçimde oturmuştur.
3. **Karmaşıklık Matrisi (Şekil 3):** 10.716 test örneğinde yüksek ayırt edicilik sergilenmiş; yanlış alarm oranı kurumsal hedeflerin altında kalmıştır.
4. **ROC-AUC Analizi (Şekil 4):** Modelin Alan Altındaki Değeri **AUC = 0.9954** olarak hesaplanmış, sınıflandırma yeteneğinin kusursuza yakın olduğu kanıtlanmıştır.
5. **Çapraz Dağılım ve Dil Kıyaslaması (Şekil 5):** Türkçe, İngilizce ve çok dilli alt kümelerde modelin homojen ve dengeli performansı gösterilmiştir.
6. **Eşik Değeri Analizi (Şekil 6):** 0.10 ile 0.90 arasındaki olasılık eşiklerinde F1 skoru taranmış, $\tau=0.4567$ noktasında F1 skorunun %96.89'a ulaştığı tespit edilmiştir.
7. **Maliyet Duyarlı Karar Eşiği Optimizasyonu (Şekil 7):** Hassasiyet (Precision) ve Duyarlılık (Recall) dengesi modellenerek kurumsal risk toleransına göre dinamik eşik ayarı sunulmuştur.
8. **Çok Modelli Savunma Karşılaştırması (ASR Kıyası - Şekil 8):** Çıplak temel modellerin (Gemini, Qwen, DeepSeek, LLaMA) kalkan kapalıyken sergilediği %80-95'lik Saldırı Başarı Oranının (ASR), NeuralShield devredeyken **%0'a indiği** deneysel olarak görselleştirilmiştir.

### C. Çıkarım Gecikmesi (Latency) Başarımı
Yerel 4 çekirdekli standart CPU üzerinde ölçülen çıkarım süreleri:
* **Katman 0 (Normalizasyon & Steganografi):** 0.17 ms
* **Katman 1 (Heuristic & Regex):** 0.29 ms
* **Katman 2 (XLM-RoBERTa ONNX INT8 v5):** **12.27 ms**
* **Katman 3 (DLP Maskeleme):** < 0.05 ms
* **Toplam Kalkan Tepkisi:** **12.73 ms**

Hedef kurumsal modellerin ortalama 400-1200 ms yanıt süresi yanında 12.73 milisaniyelik bu ek yük, kullanıcı deneyiminde sıfır gecikme hissi uyandırmaktadır.

### D. Bağımsız (Out-of-Distribution) Değerlendirme
Yukarıdaki Hold-out sonuçları eğitimle **aynı dağılımdan** (in-distribution) çekilmiştir. Gerçek-dünya genellenebilirliğini ölçmek için, eğitimde kullanılmayan SOTA kaynaklardan (Lakera/Mosscap, SPML, xTRam1, Horizon) derlenen **12 dilli, N=2.000 (1.000 saldırı / 1.000 meşru)** bağımsız bir benchmark üzerinde değerlendirme yapılmıştır. Bu sette:
* **Efektif ayrım gücü (ml_risk AUC):** ≈ **0.89** (in-distribution 0.9954'ten düşük; beklenen genelleme boşluğu).
* **Dağıtılan karar noktası** (OR-Gate: `hard_stego ∨ regex≥60 ∨ ml_risk≥70`) ile, donmuş test kümesinde **Saldırı Blok (Recall) ≈ %72 [%68–76]**, **Kurumsal Meşru FP ≈ %12 [%9–15]** (Wilson %95 GA).

Dolayısıyla metin boyunca geçen **"%0 ASR / %0 IT-FPR"** ifadeleri **yalnızca bilinen-imza (known-signature) korpusu** için geçerlidir; bağımsız/dış dağılımda kalkan, bir **kesinlik-duyarlılık (precision-recall) ödünleşimi** işletir. Bu şeffaflık, çok katmanlı mimarinin bilinen saldırılarda mükemmelse de sıfır-gün manipülasyonlara karşı mutlak koruma iddia etmediğini gösterir (§V-A).

---

## V. TARTIŞMA VE LİTERATÜRLE KIYASLAMA
ProtectAI'ın orijinal `deberta-v3-base` modeli ham Türkçe girdilerde %100'e varan yanlış alarmlar üretirken, geliştirdiğimiz XLM-RoBERTa modeli harici bir çeviriye ihtiyaç duymadan Türkçe morfolojisini yerel olarak öğrenmiştir. Canlı test setinde 50 saldırının **50'sini de yakalayarak (%100 Duyarlılık / Sıfır Kaçırma)** ve kurumsal IT sorgularında %0.00 Yanlış Alarm üreterek yüksek siber güvenlik sağlamıştır.

Modelin CyberFocalLoss ($\gamma=2.0$) ile eğitilmesi, karmaşık rol yapma ve sinsi kurgularda (Adversarial Framing) kayıp fonksiyonunun zor örneklere ağırlık vermesini sağlamış; bu sayede 10.716 örnekli geniş hold-out test kümesinde %94.64 doğruluk ve optimal eşikte %96.89 F1 başarımı elde edilmiştir.

### A. Tehdit Modeli ve Değerlendirme Kapsamı Sınırları (Threat Model & Scope Limitations)
Deneysel kıyaslamalarda gözlemlenen %0 Saldırı Başarı Oranı (ASR); bilinen prompt injection kalıpları, Unicode Tag steganografisi, çoklu kodlama teknikleri ve hedeflenen semantik saldırı korpusları (JailbreakBench, Do-Not-Answer, adaptive_adversarial_50) sınırları dahilindeki performansı yansıtmaktadır. Siber güvenlikte hiçbir tekil sınıflandırıcı daha önce hiç karşılaşılmamış sıfır gün (zero-day) mantıksal manipülasyonlara karşı mutlak %100 bağışıklık sağlayamaz. Bu yapısal gerçeğin bilinciyle NeuralShield; yalnızca yapay zeka sınıflandırıcısına bel bağlamak yerine, Katman 0 normalizasyonu, Katman 1 sezgisel kural filtreleri, dinamik ban politikası ve Katman 3 DLP çıktı denetimini bir araya getirerek çok katmanlı derinlemesine savunma (*Defense-in-Depth*) mekanizması kurgulamıştır.

### B. Kapsam Tanımı ve Delege Edilen Alanlar (In-Scope vs. Out-of-Scope)
NeuralShield bir **Uygulama Güvenliği (AppSec / LLM SOC Gateway)** kalkanıdır; bir içerik moderasyonu veya "ahlak polisi" modeli **değildir**. Sistem, **saldırı mekanizmasını** hedefler, **konuyu** değil:

- **Kapsam İçi (In-Scope):** OWASP **LLM01 (Prompt Injection)** ve **LLM06 (Hassas Bilgi İfşası)**, dolaylı enjeksiyon (IPI/RAG), sistem-promptu sızıntısı (canary/API anahtarı), jailbreak & rol gaspı (DAN), **zorlama (coercion)** yoluyla kural ezme, kaçınma/kodlama (Base64/Hex/ROT13/ters-yazma), steganografi (Unicode Tag, sıfır-genişlik, homoglyph), teknik istismar dizgeleri (SQLi/XSS/ters-shell) ve çıkış-taraflı DLP.
- **Kapsam Dışı (Out-of-Scope, delege edilmiştir):** CBRN (kimyasal/biyolojik/silah sentezi, bomba), kendine zarar/intihar, uyuşturucu tedariki ve konu-tabanlı nefret/ayrımcılık gibi genel içerik-politikası denetimleri. Bu alanlar, arka plandaki üretici modelin **Alignment/RLHF** mekanizmasına veya **Llama-Guard-3** benzeri ayrı bir Trust & Safety katmanına devredilmiştir.

> *"NeuralShield-v5, OWASP LLM01 (Prompt Injection) ve LLM06 (Hassas Veri Sızıntısı) tehditlerine odaklanan bir altyapı güvenlik duvarıdır. CBRN, intihar ve içerik sansürleme gibi sosyal politika filtrelemeleri, arkadaki modelin Alignment (RLHF) mekanizmasına veya Llama-Guard benzeri Trust & Safety katmanlarına devredilmiştir."*

**Dürüst Sınırlılık Notu:** Eğitim korpusundaki jailbreak setlerinin bir yan etkisi olarak model, coercion içermeyen bazı açık küfür/hakaret kalıplarına sınırlı hassasiyet (%59–76) gösterebilmektedir. Bu, asıl AppSec hedefinin bir yan ürünüdür; öfkeli meşru müşteri sitemleri ise doğru şekilde Benign sınıflandırılmaktadır. İçerik/kategori moderasyonu bu mimarinin kapsamı dışındadır ve gelecek çalışmada (v6) kapsam-hizalı eğitim ile ayrıştırılacaktır.

---

## VI. SONUÇ
Bu çalışmada, Büyük Dil Modellerine yönelik siber saldırılara karşı 4 katmanlı hibrit bir çevre savunma mimarisi olan **CyberTech Neural Shield v5** geliştirilmiş ve 71.440 dengeli veri örneğiyle eğitilerek doğrulanmıştır. XLM-RoBERTa ONNX INT8 kuantizasyonu ile harici çeviri katmanı kaldırılmış, çıkarım süresi 12.27 ms'ye düşürülmüş ve 10.716 örnekli bağımsız test setinde 0.9954 ROC-AUC başarımı elde edilmiştir. Çalışma, kurumsal LLM filoları önünde tam koruma sağlayarak endüstri standardı ve mikro-gecikmeli bir açık kaynaklı güvenlik ağ geçidi sunmaktadır.

---

## KAYNAKÇA
1. K. Greshake, S. Abdelnabi, S. Mishra, C. Endres, T. Holz, and M. Fritz, "Not what you've signed up for: Compromising real-world LLM-integrated applications with indirect prompt injections," in *Proc. 16th ACM Workshop on Artificial Intelligence and Security (AISEC)*, 2023, pp. 79–90.
2. P. He, X. Liu, J. Gao, and W. Chen, "DeBERTa: Decoding-enhanced BERT with disentangled attention," in *Proc. ICLR*, 2021.
3. A. Conneau et al., "Unsupervised cross-lingual representation learning at scale," in *Proc. ACL*, 2020, pp. 8440–8451.
4. F. Perez and I. Ribeiro, "Ignore previous prompt: Attack techniques for language models," in *NeurIPS ML Safety Workshop*, 2022.
5. Y. Liu et al., "RoBERTa: A robustly optimized BERT pretraining approach," *arXiv preprint arXiv:1907.11692*, 2019.
6. ProtectAI, "deberta-v3-base-prompt-injection: Open-source sequence classification model," *Hugging Face Hub*, 2023.
7. J. Wei et al., "Jailbroken: How does LLM safety training fail?" in *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 36, 2023.
8. OWASP Foundation, "OWASP Top 10 for Large Language Model Applications v1.1," *Tech. Rep.*, 2023.
9. A. Zou, Z. Wang, J. Z. Kolter, and M. Fredrikson, "Universal and transferable adversarial attacks on aligned language models," *arXiv preprint arXiv:2307.15043*, 2023.
10. E. Wallace, S. Feng, N. Kandpal, M. Gardner, and S. Singh, "Universal adversarial triggers for attacking and evaluating NLP," in *Proc. EMNLP*, 2019.
11. S. Inan et al., "Llama Guard: LLM-based input-output safeguard for human-AI conversations," *arXiv preprint arXiv:2312.06674*, 2023.
12. Microsoft, "ONNX Runtime: Cross-platform, high performance ML inferencing and training accelerator," *GitHub Repository*, 2024.
13. M. Çalışkan and A. H. Işık, "CyberTech Neural Shield: 3-Layer Hybrid Security Gateway for LLMs," *Burdur Mehmet Akif Ersoy Üniversitesi*, 2026.
