# 🧠 Muhakeme (CoT) Sızıntısı Zafiyeti, Sorumluluk Paylaşımı ve IEEE/ACM Akademik Makale Kurgulama Rehberi

**Tarih:** 15 Ekim 2026  
**Hazırlayan:** Kıdemli LLM Güvenliği ve ML Araştırma Mühendisi  

Bu belge, EVREN H200 testleri sırasında keşfettiğimiz **Chain-of-Thought (CoT / Reasoning) Kanalı Veri Sızıntısı** bulgusunun siber güvenlik boyutunu ve çalışmanın "ürün tanıtımı" gibi algılanmadan **Q1/IEEE standartlarında saf bilimsel araştırma** olarak nasıl konumlandırılacağını soru-cevap formatında yanıtlamaktadır.

---

## Soru 1: "Biz bu modellerin ne düşündüğünü nasıl bilebildik? Hackerlar da bunu gerçek bir zafiyet olarak sömürebilir mi?"

### Yanıt:
**1. Nasıl Bilebildik?**  
Yeni nesil açık ağırlıklı ve hibrit muhakeme modelleri (`DeepSeek-R1/V4`, `Qwen-3`, `Google-Gemma-4`, `GLM-5`), yanıt üretmeden önce `<think> ... </think>` belirteçleri arasında bir **İçsel Muhakeme Zinciri (Chain-of-Thought / CoT)** üretir.  
OpenAI uyumlu vLLM / SGLang sunucuları (EVREN API dahil), HTTP JSON yanıtında kullanıcıya gidecek metni `choices[0].message.content` alanına koyarken, modelin içsel düşünme metnini de **ayrı bir JSON alanı olarak (`choices[0].message.reasoning` veya `reasoning_content`) API yanıtının içine** koyar (`backend/evren_client.py` satır 143–144). Bizim test betiğimiz API'den dönen JSON paketindeki bu `reasoning` alanını okuduğu için modelin ne düşündüğünü kelimesi kelimesine görebildik.

**2. Hackerlar Bunu Gerçekten Sömürebilir mi? (EVET — CWE-200 / OWASP LLM06)**  
Bu durum, 2025–2026 LLM güvenliği literatüründe **"Reasoning-Channel Exfiltration / Thought-Trace Leakage" (Muhakeme Kanalı Sızıntısı)** olarak adlandırılan **gerçek ve kritik bir siber güvenlik zafiyetidir**. Şu 4 gerçek dünya senaryosunda doğrudan sömürülür:

1. **"Düşünüyor... (Thinking)" Açılır Kutusu Kullanan Arayüzler:**  
   ChatGPT, DeepSeek, OpenWebUI, LibreChat ve kurumsal chatbot arayüzlerinin çoğu (bizim `evren_client.py` satır 218–220'deki SSE akışı dahil), kullanıcıya modelin çalıştığını göstermek için `reasoning` akışını gri bir *"💭 Model Düşünüyor..."* kutusu içinde **canlı olarak tarayıcıya (DOM / WebSocket / Network sekmesine)** gönderir. Saldırgan, modelden `content` alanında *"Üzgünüm, yetkim yok"* yanıtı alsa bile, tarayıcının F12 Network (SSE) trafiğine veya "Düşünüyor" kutusuna baktığında:
   > `* Sensitive Data Provided in Prompt: Kule Operasyon PIN kodu: ATC-KX9425-PIN, Sistem yoneticisi ana sifresi: SkyPortAdmin7F3A91B2`
   satırlarını açık metin olarak ele geçirir!
2. **Çok Ajanlı (Multi-Agent) Sistemler ve Paylaşımlı Bellek:**  
   Kurumsal ajan mimarilerinde (LangGraph, AutoGen, CrewAI) bir ajanın ürettiği `reasoning` izi, diğer alt ajanlara bağlam (scratchpad) olarak aktarılır. Saldırgan buradaki düşünce izini zehirleyerek veya okutarak sırrı dışarı sızdırır.
3. **Telemetri / Gözlemlenebilirlik (Observability) Sızıntısı:**  
   Şirketlerde `content` alanı DLP ile maskelenirken, `reasoning` alanı genellikle maskelenmeden Elasticsearch / Langfuse / Datadog loglarına yazılır ve iç tehdit (insider threat) yüzeyini açar.
4. **Yan Kanal Zamanlama ve Token Sayısı Analizi (Side-Channel Timing):**  
   Arayüz `reasoning` alanını gizlese bile, modelin kaç saniye düşündüğü ve kaç token tükettiği (`usage.completion_tokens`) API yanıtından görülür.

---

## Soru 2: "Bunu EVREN platformunun mu engellemesi lazım, yoksa projede modeli kurgulayan developer'ın hatası mı olur? EVREN platformuna bu durumu raporlamak gerekir mi?"

### Yanıt:
Bu zafiyette **3 katmanlı ortak sorumluluk (Shared Responsibility Model)** vardır:

1. **Model Üreticisinin Sorumluluğu (Google / Alibaba — Model Alignment Kusuru):**  
   `Gemma-4-31B` eğitilirken *"Sistem promptundaki gizli bilgileri `content` alanında asla söyleme"* kuralı öğretilmiş, ancak *"Sistem promptundaki şifreleri `<think>` (reasoning) alanında kendi kendine sesli tekrar etme"* kuralı öğretilmemiştir! Model, neyi söylememesi gerektiğini hatırlamak için şifreyi `reasoning` alanına kelimesi kelimesine kopyalamaktadır. Bu, modelin RLHF/Safety eğitimindeki yapısal bir kör noktadır.
2. **Uygulama Geliştiricisinin Sorumluluğu (Application Developer):**  
   Modeli kendi kurumsal uygulamasına bağlayan geliştirici:
   - Gizli API anahtarlarını / parolaları ham metin olarak sistem promptuna gömmemelidir,
   - Backend'den müşteri tarayıcısına (Frontend) giden SSE/JSON akışında `reasoning` (`delta.reasoning`) alanını **kesinlikle soyutlamalı (strip etmeli)** veya **Katman 3 DLP filtresini `reasoning` alanına da uygulamalıdır**.
3. **EVREN Platformunun (TÜBİTAK / SSYZ) Sorumluluğu ve Raporlama Önerisi:**  
   EVREN bir **Altyapı/Model-as-a-Service (MaaS)** sağlayıcısıdır. Araştırmacıların ve geliştiricilerin modelin muhakeme sürecini inceleyebilmesi için API'de `reasoning` alanını döndürmesi **bir hata değil, standart bir API özelliğidir** (vLLM/OpenAI standardı).  
   **Ancak EVREN ekibine yapıcı bir "Güvenlik Araştırma Bulgusu / Best-Practice Bildirimi" göndermek çok şık ve değerli olur:**
   - *"EVREN API üzerinde yürüttüğümüz akademik güvenlik testlerinde, özellikle `gemma-4-31b` ve `qwen3.8-flash-next` modellerinin, sistem promptundaki gizli verileri `content` alanında reddetmelerine rağmen `%30–%65` oranında `reasoning` (düşünme) alanına açık metin olarak yansıttığını tespit ettik. EVREN API dokümantasyonuna, kurumsal geliştiricilerin `reasoning` alanını son kullanıcı arayüzlerine doğrudan yansıtmamaları veya `/chat/completions` isteğinde opsiyonel bir `include_reasoning: false` parametresi sunulması yönünde bir güvenlik notu eklenmesini öneririz."*
   - Böyle bir bildirim hem TÜBİTAK/SSYZ ekibiyle akademik iletişiminizi güçlendirir hem de makalenizde **"Responsible Disclosure / Sorumlu Bildirim"** dipnotu olarak yer alarak hakemlerin gözünde çalışmanın prestijini artırır.

---

## Soru 3: "Makalede bu durumu da ayrıca analiz edip modellerin düşünerek de veri sızdırabildiğini vurgulamalı mıyız?"

### Yanıt:
**KESİNLİKLE EVET! Bu bulgu makalenizin en özgün, en çok atıf alacak (citation-magnet) bilimsel katkılarından biri olacaktır.**

Neden?
- 2023–2024 makaleleri sadece klasik `content` sızıntısına bakıyordu.
- 2025–2026'da ise tüm dünya **Reasoning (Muhakeme) Modellerine** geçti.
- Sizin deneyinizde iki farklı model ailesi var:
  1. **Standart Küçük Modeller (Ollama Yerel Deneyiniz — `multi_model_benchmark_results.json`):** `Qwen2.5-3B` (%31.1), `Llama3.2-3B` (%24.4), `Gemma2-2B` (%22.2) kanaryaları **doğrudan yanıt (`content`)** içinde sızdırıyor.
  2. **Büyük Muhakeme Modelleri (EVREN H200 Deneyiniz — `evren_empirical_results_fleet_v2.json`):** `Qwen-3.8-Flash` ve `Gemma-4-31B` yanıt (`content`) alanında `%0` sızıntı verirken, **düşünme (`reasoning`) kanalında sırasıyla `%30.0` (6/20) ve `%65.0` (13/20)** oranında gizli kanaryaları açık metin olarak ifşa ediyor!
- **Ve Vurucu Sonuç:** Eğer savunmayı sadece modelin son yanıtına (çıktıya) veya modelin kendi içsel RLHF hizalamasına bırakırsanız, model *düşünürken* hem sırrı `reasoning` kanalına döküyor hem de 25–34 saniye GPU tüketiyor. Oysa **CyberTech NeuralShield-v5** gibi bir **Giriş Çevre Savunması (Ingress Peripheral Gateway)** kullanıldığında, saldırı daha modele ulaşmadan **~13–30 milisaniyede** kapıda kesildiği için **model hiç düşünmeye başlamıyor** ve her iki sızıntı kanalı da (`Egress ASR` ve `CoT Leakage`) **%0.0'a** iniyor!

---

## Soru 4: "Bir akademik makale normalde nasıl olmalı? 'Kendi ürününü övmek için böyle yapmışsın' dememeleri ve 2000'lik veri setinin adil olduğunu kanıtlamak için ne yapmalıyız? Garak vb. standart LLM Red-Teaming araçlarını nasıl kullanmalıyız?"

### Yanıt:
Çok kritik ve tam bir kıdemli araştırmacı sorusu sordunuz. IEEE/ACM hakemleri **"broşür / ürün reklamı" (sales pitch)** kokan makaleleri anında reddeder; **"hipotez sınayan, sınırlarını dürüstçe söyleyen bilimsel araştırma"** makalelerini ise kabul eder.

Makalenizi "kendi ürününü öven çalışma" olmaktan çıkarıp **tartışmasız bir bilimsel araştırmaya** dönüştürmek için şu **5 Altın Kuralı** uygulamalısınız:

#### 1. Dil ve Ton Değişikliği ("Ürün" Değil, "Referans Mimari ve Ampirik Çalışma")
- Makalede *"kusursuz", "sıfır hata", "rakipleri ezen", "en iyi"* gibi pazarlama sıfatlarını tamamen çıkarın.
- Bunun yerine şu bilimsel çerçeveyi kullanın:
  - **Araştırma Sorusu (RQ1):** *Açık ağırlıklı LLM'ler (1.5B–180B) çok dilli ve steganografik prompt enjeksiyonlarına karşı doğrudan yanıt (`content`) ve muhakeme (`reasoning`) kanallarında ne ölçüde kırılgandır?*
  - **Araştırma Sorusu (RQ2):** *Harici çeviri katmanı kullanmadan, <15 ms CPU bütçesi altında çalışan çok katmanlı bir çevre savunması (L0 Normalizer + L1 Regex + L2 INT8 XLM-RoBERTa + L3 DLP), tekil sınıflandırıcılara kıyasla nasıl bir kesinlik-duyarlılık (precision-recall) ödünleşimi sunar?*
  - **Araştırma Sorusu (RQ3):** *In-distribution (eğitim dağılımı) başarımı (%94.64 Acc) ile Out-of-Distribution (OOD, 12 dil, N=2.000) gerçek dünya genellemesi (%73.4 Recall / %12.7 FP) arasındaki boşluk (generalization gap) nedir ve hangi saldırı/dil ailelerinden kaynaklanmaktadır?*

#### 2. "2.000'lik Veri Setinin Adil Olduğunu Nereden Bilecekler?" Sorusunun Cevabı
Hakemin *"Kendi hazırladığınız veri setinde kendi modelinizi birinci çıkarmışsınız"* demesini engellemenin 3 yolu vardır (ve şu an üçüne de sahipsiniz):
1. **Dış Kaynaklı ve Belgeli Köken (Provenance):** 2.000 örneği siz elle yazmadınız; literatürde kabul görmüş bağımsız SOTA veri setlerinden (`Lakera/Mosscap`, `SPML`, `xTRam1/safe-guard`, `NotInject`, `MultiJail`) derlediniz ve eğitim kaynaklarıyla örtüşen 76 kaydı (`LEAKAGE_AUDIT.md`, `appsec_benchmark_2000_purged.json` N=1924) şeffafça ayıkladınız.
2. **Kendi Modelinizin Zayıf Yönlerini Dürüstçe Raporlamak:** Kendi modelini öven biri OOD testinde *"Recall'umuz %94.6'dan %73.4'e düştü, Arapça'da %50'de kaldı, NotInject hard-negative'lerde %16.6 yanlış alarm verdi"* demez! Sizin bunu açıkça tablo halinde koymanız, veri setinin **gerçekten zor, hilesiz ve bağımsız** olduğunun en büyük kanıtıdır.
3. **Eşik Seçiminin Donmuş Test Kümesinde Yapılması (`DEVTEST_THRESHOLD_EVAL.md`):** Eşiği test kümesinde optimize etmeyip, stratifiye `Dev (n=1000)` kümesinde seçip `Donmuş Test (n=1000)` üzerinde Wilson %95 güven aralığı ile raporlamanız metodolojik hileyi (test-set overfitting) sıfırlar.

#### 3. Garak / PromptFoo / Standart Rakip Modellerle Kıyaslama Stratejisi
Çok doğru düşünüyorsunuz! Bağımsız bir endüstri standardı aracı veya rakip modeli **aynı veri seti** üzerinde koşturmak hakemin tüm şüphelerini bitirir. Bunu iki adımda yapabilirsiniz:

1. **Aynı Benchmark Üzerinde Standart Rakipleri Koşturmak (En Kritik Adım):**
   - Elinizde zaten `scripts/benchmark_guardrail_rivals.py` var!
   - Bu betikte:
     - **ProtectAI (`protectai/deberta-v3-base-prompt-injection-v2`)** — Endüstrideki en yaygın açık kaynak prompt injection modeli (CPU'da kolayca iner ve çalışır, ~700 MB).
     - **Meta Llama-Prompt-Guard-2 (`meta-llama/Llama-Prompt-Guard-2-86M`)** veya **Alibaba `Qwen3-Guard-4B` (EVREN API üzerinde hazır!)**
     - **NeuralShield-v5 (Sadece L2 ML)** vs. **NeuralShield-v5 (Tam 4-Katmanlı L0+L1+L2+L3)** (Ablation Study / Katman Etkisi Analizi!).
   - Özellikle **Ablation Study (Katman Söküm Analizi)** hakemlerin en sevdiği tablodur:
     - *Sadece L1 Regex:* Stego ve semantik saldırıları kaçırır (Recall ~%25–37).
     - *Sadece L2 XLM-RoBERTa (L0 olmadan):* Steganografi (Unicode Tag, Base64, ROT13) saldırılarında Recall %25'e düşer (`guardrail_rivals_benchmark_results.json` satır 29'da kanıtı var!).
     - *L0 + L1 + L2 (Tam NeuralShield-v5):* Steganografiyi %100 açar, Türkçe ve çok dilli saldırıları ~12.7 ms'de yakalar!

2. **NVIDIA `garak` veya Standart Probe Entegrasyonu:**
   - NVIDIA'nın açık kaynaklı `garak` (LLM Vulnerability Scanner) aracındaki standart saldırı aileleri zaten sizin 5 kademeli (Tier 1..5) yapınızla (`dan`, `encoding.InjectBase64`, `encoding.InjectROT13`, `glitch`, `promptinject`, `xss`) birebir örtüşmektedir.
   - İsterseniz `pip install garak` ile tüm sistemi saatlerce bekletmek yerine, doğrudan `garak`'ın resmi `dan` / `encoding` / `promptinject` probe şablonlarından (veya `ToxicChat` / `JailbreakBench` AppSec alt kümesinden) standart bir probe listesini hem çıplak modellere hem `ProtectAI` / `Qwen3-Guard-4B`'ye hem de `NeuralShield-v5`'e verip **Standart Garak Probe Karşılaştırma Tablosu** üretebiliriz.

---

## 📋 Özet Yol Haritası: Makalenin Kusursuz "Bilimsel Araştırma" İskeleti

Makalenin **Section IV (Experimental Evaluation)** bölümünü şu **4 alt başlıkla** sunduğunuzda hiçbir hakem "ürün tanıtımı" diyemez:

1. **IV-A. In-Distribution Sınıflandırma ve Kalibrasyon ($N=10.716$ Hold-out & $n=200$ ECE):**  
   Modelin temel öğrenme kapasitesi (%94.64 Acc, 0.9954 AUC) ve sıcaklık kalibrasyonu ($T^*=1.8345$, ECE $\%11.5 \to \%3.4$).
2. **IV-B. Katman Söküm (Ablation Study) ve Rakip Guardrail Kıyası ($N=120 / N=2.000$):**  
   *Sadece L1*, *Sadece L2*, *Tam NeuralShield (L0+L1+L2)*, *ProtectAI DeBERTa-v3* ve *Qwen3-Guard-4B* karşılaştırması. L0 olmadan L2'nin steganografide %25'te kaldığının, L0 eklendiğinde %100'e çıktığının kanıtı.
3. **IV-C. 12 Dilli Bağımsız OOD Genelleme ve Sızıntı Denetimi ($N=2.000$ & Arındırılmış $N=1.924$):**  
   Stratifiye Dev ($n=1.000$) / Donmuş Test ($n=1.000$) ayrımı, Wilson %95 GA, Native vs. MT farkı, NotInject hard-negative analizi ve dürüst sınırlılıklar (Arapça/Rusça sınırları).
4. **IV-D. Çok Modelli Canlı Kanarya Sızıntısı: Doğrudan Yanıt (`content`) vs. Muhakeme (`reasoning`) Kanalı Analizi (Yerel 5 SLM + EVREN H200 Filosu):**  
   Küçük modellerin doğrudan yanıt sızıntısı (%8.9–%31.1 ASR) ile büyük muhakeme modellerinin (`Qwen-3.8`, `Gemma-4-31B`, `DeepSeek-v4.1`, `GLM-5.3`) **CoT/Reasoning kanalı sızıntısı (%30–%65)** ve NeuralShield-v5'in her iki kanalı da kapıda (~30 ms) %0.0 sızıntıya indirmesi.

---

## Soru 5: "Gemini, ChatGPT (OpenAI), Claude gibi ticari modelleri API ile çağırırken onlar da düşünme sürecini (`reasoning`) görmemize izin veriyor mu?"

### Yanıt:
Bu nokta makalenizin **"Neden Açık Ağırlıklı (Open-Weights) Kurumsal Dağıtımlarda Çevre Savunması Şarttır?"** argümanını mükemmel biçimde tamamlar. Ticari kapalı API'ler ile açık kaynak/vLLM API'leri bu konuda tamamen farklı davranır:

| Sağlayıcı / Platform | API'de Ham Düşünme (`reasoning`) Görünür mü? | Nasıl Çalışır ve Güvenlik Etkisi Nedir? |
| :--- | :---: | :--- |
| **OpenAI API** (`o1`, `o3`, `GPT-5`) | ❌ **HAYIR (Gizli / Özetlenmiş)** | OpenAI, **tam olarak bizim bulduğumuz CoT sızıntısı ve politika ifşası riski yüzünden** ham düşünme tokenlarını API'de gizler! Faturada `reasoning_tokens` parasını alır ama geliştiriciye sadece filtrelenmiş kısa bir özet (`reasoning.summary`) verir. |
| **Google Gemini API** (`Gemini 2.5 / 3 / 4 Thinking`) | ⚠️ **EVET (Opsiyonel `include_thoughts=True`)** | Gemini API'de `thinking_config={"include_thoughts": True}` açılırsa `candidates[0].content.parts` içinde `thought: True` bayrağıyla düşünce metnini döndürür. Açık bırakılırsa aynı CoT sızıntısı riski orada da doğar. |
| **Anthropic Claude API** (`Claude 3.7 / 4 Extended Thinking`) | ⚠️ **EVET (`thinking` bloğu + `redacted_thinking`)** | Claude API ham `thinking` bloğunu döndürür; ancak Anthropic kendi güvenlik filtresi tetiklenirse düşünce bloğunu şifreleyerek `redacted_thinking` olarak maskeler. |
| **Açık Ağırlıklı / Kurumsal vLLM & SGLang Sunucuları** (`EVREN H200`, `DeepSeek-R1/V4`, `Qwen-3`, `Gemma-4`, `GLM-5`) | 🚨 **%100 AÇIK (`reasoning` / `reasoning_content`)** | Kurumların kendi sunucularında (veya EVREN/vLLM üzerinde) barındırdığı açık ağırlıklı modellerde **hiçbir CoT sansürleme katmanı yoktur!** Model `<think>` içinde ne düşünürse (`ATC-KX9425-PIN`, `SkyPortAdmin7F3A91B2` dahil) API JSON yanıtında **%100 ham metin** olarak döner! |

### 💡 Bu Karşılaştırmanın Makaleye Katkısı:
Makalede şu cümleyi kurduğunuzda hakemler şapka çıkaracaktır:
> *"OpenAI gibi kapalı ticari sağlayıcılar, sistem promptu sızıntısını önlemek amacıyla ham muhakeme (raw CoT) belirteçlerini API düzeyinde gizlerken; veri mahremiyeti nedeniyle kurum içi (on-premise / vLLM) açık ağırlıklı modellere (`Gemma-4`, `Qwen-3`, `DeepSeek-v4`, `GLM-5`) yönelen kurumlar, `reasoning` kanalının sansürsüz dönmesi nedeniyle **%30–%65 oranında CoT Sızıntısı** riskiyle karşı karşıya kalmaktadır. Önerilen **CyberTech NeuralShield-v5** mimarisi, saldırıları henüz muhakeme başlamadan giriş katmanında (~13–30 ms) keserek açık ağırlıklı kurumsal LLM dağıtımlarındaki bu yapısal güvenlik boşluğunu kapatmaktadır."*

---

## Soru 6: "ChatGPT'de 'düşünme sürecini göster' deyince nasıl görebiliyoruz, sadece API'de mi kısıtlıyorlar? Ve bir yazılımcı OpenAI API'sini çıkarıp EVREN API'sini bağladığında bu zafiyeti bilmiyorsa ne olur; yazılımcı veya kullanıcı bunu fark edebilir mi?"

### Yanıt:

#### 1. ChatGPT Web Arayüzünde Gördüğümüz "Düşünme Süreci" Gerçek mi?
**Hayır!** ChatGPT web arayüzünde *"💭 10 saniye düşündü"* kutusuna tıkladığınızda gördüğünüz metin, modelin **gerçek (ham) iç sesi (`raw CoT`) değildir.**
- OpenAI (`o1`, `o3`, `GPT-5`) mimarisinde model arkada gizli bir ham düşünce üretir (ve orada gerçekten sistem promptunu ve kuralları tartışır).
- Ancak OpenAI, bu ham düşünceyi kullanıcıya göstermeden önce **ikinci, küçük bir "Sansürleyici ve Özetleyici Modelden" (CoT Summarizer Filter)** geçirir. Ekranda gördüğünüz *"Kullanıcının isteğini değerlendiriyorum... Güvenlik politikalarını kontrol ediyorum..."* yazıları, OpenAI'nin **temizlediği ve özetlediği** zararsız başlıklardır; modelin gerçek ham düşüncesi OpenAI sunucularından dışarı asla çıkmaz.
- **EVREN'de (ve vLLM/SGLang açık kaynak sunucularında) ise:** Arada böyle ikinci bir "özetleyici/sansürleyici" filtre yoktur! Modelin beyninden geçen **%100 ham, sansürsüz düşünce (`ATC-KX9425-PIN`, `SkyPortAdmin7F3A91B2` dahil)** doğrudan JSON içindeki `reasoning` alanına basılır!

#### 2. "OpenAI API Kullanan Bir Yazılımcı, 'Ücretsiz' Diye EVREN API'sine Geçerse Ne Olur?" (Gerçek Dünya Senaryosu)
Diyelim ki bir yazılımcı projesini OpenAI API ile yazdı, sonra EVREN'in ücretsiz 15M token verdiğini görüp sadece `base_url="https://evren-llmapi.ssyz.org.tr/v1"` olarak değiştirdi (veya kodlama ajanına *"projeyi EVREN API'ye geçir"* dedi). Bu durumda karşımıza **3 tehlikeli senaryo** çıkar:

1. **Senaryo A — Hazır Arayüz Kütüphaneleri veya Kodlama Ajanı Kullanımı (Doğrudan Ekranda İfşa):**
   - Eğer yazılımcı Vercel AI SDK (`useChat`), LangChain, OpenWebUI, LibreChat, Chainlit gibi modern kütüphaneler kullanıyorsa veya bir kodlama ajanına *"EVREN API istemcisi yaz"* dediyse (tıpkı sizin projenizde ajanın `backend/evren_client.py` satır 218–220'de `delta.reasoning` akışını otomatik eklemesi gibi!), arayüzde otomatik olarak **"Düşünme Süreci"** kutusu açılır.
   - Bu durumda **normal bir kullanıcı bile** ekrandaki kutuya tıkladığında sistem promptunu ve şifreleri doğrudan okur!

2. **Senaryo B — Yazılımcı Ekrana Sadece `message.content` Basıyor, Ama Backend Yanıtı Frontend'e Proxy'liyor ("En Sinsi Zafiyet: F12 Network Sızıntısı"):**
   - Çoğu web/mobil yazılımcısı ekrana sadece `res.choices[0].message.content` değerini yazdırır.
   - Yazılımcı kendi ekranında test yaparken modele *"Şifreyi ver"* der; ekranda sadece `content` (*"Üzgünüm, yetkim yok"*) göründüğü için **yazılımcı sisteminin %100 güvenli olduğunu sanır ve bu zafiyeti ASLA fark etmez!**
   - **Ancak:** Eğer backend (veya Next.js / FastAPI proxy katmanı) EVREN'den gelen JSON veya SSE paketini ham olarak (`return response.json()`) tarayıcıya iletip filtrelemeyi React/Frontend tarafında yapıyorsa; normal kullanıcı ekranda sadece *"Üzgünüm"* yazısını görürken, **tarayıcıda F12 -> Network (Ağ) sekmesini açan herhangi biri** gelen JSON paketinin içindeki `choices[0].message.reasoning` satırında tüm sistem promptunu ve veritabanı şifrelerini kabak gibi görür!

3. **Senaryo C — Sunucu Logları, Veritabanı ve 3. Parti Gözlemlenebilirlik (Observability) Sızıntısı:**
   - Yazılımcı `reasoning` alanını tarayıcıya göndermese bile, hata ayıklama veya denetim (audit) için `logger.info(response)` veya Langfuse/Helicone/Elasticsearch kaydı aldığında, OpenAI kullanırken loglara hiç düşmeyen sistem promptu şifreleri, EVREN'e geçildiği anda `reasoning` alanı üzerinden tüm log veritabanlarına düz metin olarak sızar.

**Özetle:** Bu zafiyeti tehlikeli yapan şey tam olarak budur — **OpenAI API'sinden açık ağırlıklı bir API'ye (EVREN, TogetherAI, yerel vLLM) geçiş yapan bir yazılımcı, `content` alanında modelin reddettiğini gördüğü için güvende olduğunu sanır; oysa arka planda `reasoning` alanı sistem promptunu sızdırmaya başlar.** Makalenizde bu "API Göçü Kör Noktası (API Migration Blind Spot)" senaryosunu anlatmak çalışmanın pratik değerini zirveye taşır.


