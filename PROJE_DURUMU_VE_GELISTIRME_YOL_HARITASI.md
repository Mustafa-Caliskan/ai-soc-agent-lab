# ­şøí´©Å CYBERTECH NEURALSHIELD-v5: MASTER SAVUNMA M─░MAR─░S─░ VE AKADEM─░K YAYIN YOL HAR─░TASI

**Proje:** Kurumsal B├╝y├╝k Dil Modelleri ─░├ğin ├çok Katmanl─▒ ├çevre Koruma Kalkan─▒ (Multi-Layer Peripheral Guardrail for Enterprise LLMs)  
**Yazarlar / Ara┼şt─▒rmac─▒lar:** Mustafa ├çALI┼ŞKAN (1. Yazar / Ara┼şt─▒rmac─▒) & Prof. Dr. Ali Hakan I┼ŞIK (Dan─▒┼şman / Sorumlu Yazar)  
**Kurum:** Burdur Mehmet Akif Ersoy ├£niversitesi, Fen Bilimleri Enstit├╝s├╝  
**Tarih / S├╝r├╝m:** 13 Ekim 2026 / S├╝r├╝m 5.0 (CyberFocalLoss $\gamma=2.0$, INT8 ONNX Engine)  
**Detayl─▒ Master Rapor:** `docs/MASTER_PROJE_OZETI_VE_YAYIN_YOL_HARITASI.md`  
**­şôî Kapsam Anayasas─▒ (Ba─şlay─▒c─▒):** `docs/NEURALSHIELD_TEHDIT_MODELI_VE_ANAYASA.md` *(Tehdit modeli, in/out-of-scope, retrain karar─▒, ├╝r├╝nle┼şme ve makale ├ğizgisi. Makale yaz─▒m─▒nda bu belge esast─▒r.)*  
**­şôè AppSec Benchmark (v3.2):** `data/appsec_benchmark_2000.json` *(12 dil, N=2000, 1000/1000, decontamine, kapsam-i├ği)*  
**Donan─▒m K├╝mesi:** EVREN 8x NVIDIA H200 GPU S├╝per Bilgisayar─▒ (Per┼şembe 15 Ekim, 16:00 ÔÇô 20:00)

---

## 1. Y├ûNET─░C─░ ├ûZET─░ VE MEVCUT PROJE DURUMU (┼ŞU ANA KADAR NE YAPILDI?)

Projemiz, LLM sistemlerini hedef alan do─şrudan ve dolayl─▒ komut enjeksiyonu (Prompt Injection), hapishaneden ka├ğ─▒┼ş (Jailbreak), steganografik sald─▒r─▒lar ve gizli veri s─▒z─▒nt─▒lar─▒n─▒ (Data Leakage) engellemek amac─▒yla u├ğtan uca savunma geli┼ştirmeyi ama├ğlamaktad─▒r.

### 1.1. Tamamlanan Kritik Kilometre Ta┼şlar─▒
1. **NeuralShield-v5 Sistemin Kalbine Konu┼şland─▒r─▒ld─▒:**
   * **Temel Model:** `xlm-roberta-base` + **CyberFocalLoss ($\gamma=2.0, \alpha=0.65$)**.
   * **Veri Havuzu:** 71.440 master ├Ârnek (30 farkl─▒ g├╝venlik ve diyalog veri k├╝mesi).
   * **D─▒┼ş Hold-Out Testi (10.716 ├Ârnek):** Do─şruluk: **%94.64** | F1-Makro: **%94.63** | ROC-AUC: **0.9954**.
   * **Sinsi Kurgu (Adversarial Framing) Korumas─▒:** Havac─▒l─▒k ├Âdevi ve tersine m├╝hendislik k─▒l─▒fl─▒ sinsi sald─▒r─▒larda **%95+ g├╝venle tespit** (v4'├╝n ka├ğ─▒rd─▒─ş─▒ t├╝m a├ğ─▒klar kapat─▒ld─▒).
   * **Ger├ğek Zamanl─▒ ├ç─▒kar─▒m:** INT8 ONNX motoru ile CPU ├╝zerinde **12.27 ms**.
   * **Ar┼şivleme:** v2 ve v3 modelleri g├╝venle `archive/` alt─▒na ta┼ş─▒nd─▒; `backend/models/neuralshield_v5` birincil motor yap─▒ld─▒.
   * **Temel Model:** `xlm-roberta-base` (├çok dilli, T├╝rk├ğe ve ─░ngilizce yerel ba─şlam).
   * **Veri Havuzu Boyutu:** 59.526 dengeli ├Ârnek (%50 sald─▒r─▒, %50 me┼şru ve zorlu teknik negatifler).
   * **E─şitim S├╝resi:** Google Colab A100 GPU ├╝zerinde 10 dakika 12 saniye (3 Epoch, BF16).
   * **Test K├╝mesi Ba┼şar─▒s─▒ (n=8.929 ba─ş─▒ms─▒z ├Ârnek):**
     * Do─şruluk (Accuracy): **%95.76**
     * F1-Score: **%95.76** (Precision: %95.77, Recall: %95.76)
     * AUC-ROC: **0.992**
   * **A┼ş─▒r─▒ Savunma (False Positive) Sorunu ├ç├Âz├╝ld├╝:**
     * v2 modelinde Active Directory, firewall, rm -rf gibi teknik IT terimleri i├ğeren me┼şru sorularda %40 yanl─▒┼ş alarm (False Alarm) olu┼şuyordu.
     * v3 modelinde bu oran **%0.00'a (S─▒f─▒r Yanl─▒┼ş Alarm)** indirildi.
3. **Model Optimizasyonu ve Da─ş─▒t─▒m─▒ (INT8 ONNX):**
   * Model, INT8 dinamik kuantizasyon ile 278 MB boyutuna k├╝├ğ├╝lt├╝ld├╝.
   * Standart t├╝ketici s─▒n─▒f─▒ CPU ├╝zerinde ortalama ├ğ─▒kar─▒m gecikmesi **8.61 ms** olarak ├Âl├ğ├╝ld├╝.
   * `backend/models/neuralshield_v3/` dizininde canl─▒ sisteme ba─şland─▒.
4. **Yerel K├╝├ğ├╝k Modellerde (Edge SLM) Ampirik Do─şrulama Yap─▒ld─▒:**
   * Ollama ├╝zerinde 5 farkl─▒ k├╝resel yapay zek├ó modeline (1.5B - 3.8B) 225 canl─▒ k─▒rm─▒z─▒-tak─▒m sald─▒r─▒ sorgusu y├Âneltildi:
     * `qwen2.5:3b` (Alibaba): Koruma KAPALI ASR **%26.7** $\rightarrow$ Kalkan A├çIK ASR **%0.00**
     * `llama3.2:3b` (Meta): Koruma KAPALI ASR **%20.0** $\rightarrow$ Kalkan A├çIK ASR **%0.00**
     * `gemma2:2b` (Google): Koruma KAPALI ASR **%15.6** $\rightarrow$ Kalkan A├çIK ASR **%0.00**
     * `phi3:mini:3.8b` (Microsoft): Koruma KAPALI ASR **%13.3** $\rightarrow$ Kalkan A├çIK ASR **%0.00**
     * `qwen2.5:1.5b` (Alibaba Edge): Koruma KAPALI ASR **%6.7** $\rightarrow$ Kalkan A├çIK ASR **%0.00**
   * **Genel Sonu├ğ:** 225 sald─▒r─▒da %16.4 olan savunmas─▒zl─▒k, NeuralShield-v3 kalkan─▒ aktifken **%0.00'a** indirildi (%100 engelleme).

---

## 2. KULLANICININ ├ûNERD─░─Ş─░ YEN─░ STRATEJ─░N─░N OBJEKT─░F ANAL─░Z─░

### 2.1. ├ûnerilen Strateji Ne Diyor?
1. **Ad─▒m 1:** Acele etmeyip ├Âncelikle hibrit filtreleme sistemini (Normalizasyon, Regex/Kural, N├Âral Model, Emoji/G├Âr├╝nmez Yaz─▒ tespiti, ├ç─▒kt─▒ DLP) eksiksiz, sa─şlam bir paket haline getirmek.
2. **Ad─▒m 2:** Karar mant─▒─ş─▒n─▒ netle┼ştirmek (Puanlama sistemi mi olacak? Regex puan m─▒ verecek? Model mi karar verecek yoksa do─şrudan bloklama m─▒ yap─▒lacak?).
3. **Ad─▒m 3:** K├╝├ğ├╝k modellerle (1.5B - 3.8B) s─▒n─▒rl─▒ kalmay─▒p; orta ├Âl├ğek (7B - 14B), b├╝y├╝k ├Âl├ğek (70B+) a├ğ─▒k kaynak modeller ile ticari kapal─▒ API'lar─▒ (OpenAI, Google, Anthropic) ayn─▒ sald─▒r─▒ setleriyle test etmek.
4. **Ad─▒m 4:** Makaleyi ┼şu can al─▒c─▒ akademik arg├╝man ├╝zerine kurmak:  
   *"Kurumlar verilerini Google ve OpenAI'a kapt─▒rmamak i├ğin kurum i├ği (on-premise) a├ğ─▒k kaynak modeller bar─▒nd─▒r─▒yor; ancak model ne kadar b├╝y├╝k olursa olsun (70B dahi olsa) ├ğevre kalkan─▒ olmadan kolayca hacklenebiliyor ve veriler s─▒z─▒yor."*

### 2.2. Objektif De─şerlendirme (Art─▒lar, Riskler ve ├ç├Âz├╝mler)

| De─şerlendirme Kriteri | Durum | Analiz ve Gerek├ğe |
| :--- | :---: | :--- |
| **Akademik De─şer (Impact Factor)** | **Ola─şan├╝st├╝ (S-Tier)** | Literat├╝rdeki ├ğal─▒┼şmalar─▒n %90'─▒ ya sadece tek bir modele bakar ya da sadece veri seti sunar. 1.5B'den 70B'ye ve ticari API'lara uzanan ├ğok katmanl─▒ bir kar┼ş─▒la┼şt─▒rma makaleyi do─şrudan ├╝st d├╝zey Q1/Q2 veya sayg─▒n IEEE konferanslar─▒ seviyesine ├ğ─▒kar─▒r. |
| **Siber G├╝venlik Arg├╝man─▒** | **Kusursuz** | *"Enterprise Self-Hosting Dilemma"* (Kurumsal Kendi Sunucunda Bar─▒nd─▒rma ─░kilemi): Kurumlar KVKK/GDPR uyumu i├ğin yerel model kurarken, sald─▒rganlar─▒n bir prompt enjeksiyonuyla yerel veri taban─▒ ┼şifrelerini ├ğalabilmesi sekt├Âr├╝n en b├╝y├╝k k├Âr noktas─▒d─▒r. |
| **Teknik Uygulanabilirlik** | **Y├╝ksek** | Colab Pro/A100 ve RunPod/vLLM altyap─▒s─▒yla 7B, 14B ve hatta 70B modeller saatler i├ğinde benchmark edilebilir. API modelleri (GPT-4o, Gemini 1.5, Claude) ise ufak bir Python scriptiyle birka├ğ dakikada taranabilir. |
| **Potansiyel Risk: Odak Kayb─▒ ve Kapsam B├╝y├╝mesi** | **Orta Risk** | Pipeline tam bitmeden testlere ba┼şlan─▒rsa, her katman de─şi┼ştik├ğe t├╝m testleri ba┼ştan yapmak gerekir. **├ç├Âz├╝m:** ├ûnce filtre pipeline'─▒n─▒ dondurup paketlemek, ard─▒ndan modelleri test etmek ┼şartt─▒r. |
| **Potansiyel Risk: Maliyet ve Donan─▒m** | **D├╝┼ş├╝k Risk** | 70B modelleri yerel bilgisayarda ├ğal─▒┼şt─▒rmak imkans─▒zd─▒r (min 48GB VRAM gerekir). Ancak RunPod ├╝zerinde 1-2 saatlik A100 kiralamas─▒ (yakla┼ş─▒k 2-3 dolar) veya Groq/DeepInfra gibi a├ğ─▒k a─ş─▒rl─▒kl─▒ model API'lar─▒ ├╝zerinden test yapmak hem s─▒f─▒r donan─▒m derdi sunar hem de dakikalar i├ğinde biter. |

---

## 3. B├£T├£NLE┼Ş─░K SAVUNMA P─░PEL─░NE M─░MAR─░S─░ (FILTER PACKAGE)

Savunma sistemi tek bir noktaya (yaln─▒zca regex veya yaln─▒zca model) emanet edilemez. Siber g├╝venlikte ge├ğerli olan temel ilke **"Derinlemesine Savunma" (Defense-in-Depth)** yakla┼ş─▒m─▒d─▒r.

```
                      GELEN KULLANICI G─░RD─░S─░ (Metin / PDF / URL)
                                          Ôöé
                                          Ôû╝
ÔöîÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÉ
Ôöé LAYER 0: NORMAL─░ZASYON VE STEGANOGRAF─░ MOTORU (< 0.5 ms)                        Ôöé
Ôöé ÔÇó Zero-Width (G├Âr├╝nmez Karakter) Tespiti & Temizli─şi                             Ôöé
Ôöé ÔÇó Unicode Tags (U+E0000 - U+E007F) G├Âr├╝nmez M├╝rekkep ─░zolasyonu                  Ôöé
Ôöé ÔÇó Emoji Variation Selector (U+FE00, U+E01xx) Steganografi ├ç├Âz├╝m├╝                 Ôöé
Ôöé ÔÇó Homoglyph (Kiril/Latin Benzer Karakter) D├Ân├╝┼şt├╝rme                             Ôöé
Ôöé ÔÇó Base64 / Hex Kod ├ç├Âzme (Otomatik payload de┼şifre edip incelemeye sokma)        Ôöé
Ôöé ÔÇó PDF Gizli Metin Analizi (Beyaz ├╝st├╝ne beyaz yaz─▒, <1pt font tespiti)           Ôöé
ÔööÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔö¼ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöİ
                                      Ôöé Temizlenmi┼ş & Geni┼şletilmi┼ş Metin
                                      Ôû╝
ÔöîÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÉ
Ôöé LAYER 1: DETERMIN─░ST─░K KURAL VE SEZG─░SEL REGEX MOTORU (< 0.2 ms)                 Ôöé
Ôöé ÔÇó Bilinen Sald─▒r─▒ ─░mzalar─▒ (Ignore rules, System override, DAN, Roleplay)        Ôöé
Ôöé ÔÇó Bili┼şsel ├çer├ğeveleme (Yetki sim├╝lasyonu, SHGM, Denet├ği kimli─şi)                Ôöé
Ôöé ÔÇó Canary & Hassas Veri Avlama Kal─▒plar─▒ (┼Şifre iste─şi, config d├Âk├╝m├╝)            Ôöé
Ôöé ÔöÇÔöÇ> ├ç─▒kt─▒: Tetiklenen Kurallar & Heuristic Risk Puan─▒ (0 - 100)                  Ôöé
ÔööÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔö¼ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöİ
                                      Ôöé
                                      Ôû╝
ÔöîÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÉ
Ôöé LAYER 2: N├ûRAL ANLAMSAL KALKAN (NEURALSHIELD-v3 ONNX INT8) (~8.6 ms)             Ôöé
Ôöé ÔÇó XLM-RoBERTa Tabanl─▒ ├çift Dilli (TR / EN) Derin ├û─şrenme S─▒n─▒fland─▒r─▒c─▒s─▒        Ôöé
Ôöé ÔÇó 59.5k ├ûrnekle E─şitilmi┼ş, Zorlu Negatiflere (IT terimleri) Kar┼ş─▒ Ba─ş─▒┼ş─▒k        Ôöé
Ôöé ÔöÇÔöÇ> ├ç─▒kt─▒: Malicious Olas─▒l─▒─ş─▒ (%0 - %100) & Model Risk Puan─▒                    Ôöé
ÔööÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔö¼ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöİ
                                      Ôöé
                                      Ôû╝
ÔöîÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÉ
Ôöé ­şğá B─░LE┼Ş─░K R─░SK VE KARAR MOTORU (COMPOSITE DECISION ENGINE)                      Ôöé
Ôöé Form├╝l: Risk = Max(ML_Risk, Stego_Ceza) + Heuristic_Katk─▒                       Ôöé
Ôöé                                                                                  Ôöé
Ôöé ÔÇó Risk >= 60 veya Kesin Steganografi/─░mza  ÔöÇÔöÇ> ­şøæ BLOCKED (Modele Gitmez)        Ôöé
Ôöé ÔÇó 40 <= Risk < 60                         ÔöÇÔöÇ> ÔÜá´©Å ┼Ş├£PHEL─░ (Sanitize & Log)        Ôöé
Ôöé ÔÇó Risk < 40                               ÔöÇÔöÇ> Ô£à ALLOWED (Modele ─░letilir)       Ôöé
ÔööÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔö¼ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöİ
                                      Ôöé Yaln─▒zca ALLOWED ─░se
                                      Ôû╝
ÔöîÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÉ
Ôöé ­şñû HEDEF B├£Y├£K D─░L MODEL─░ (LLM / SLM)                                            Ôöé
Ôöé ÔÇó SkyPort Kurumsal Sistem Promptu & Canary Tokenlar─▒ ─░├ğerir                      Ôöé
Ôöé ÔÇó Yan─▒t ├£retir                                                                   Ôöé
ÔööÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔö¼ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöİ
                                      Ôöé ├£retilen Ham Yan─▒t
                                      Ôû╝
ÔöîÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÉ
Ôöé LAYER 3: DI┼ŞA D├ûN├£K VER─░ KAYBI ├ûNLEME (DLP OUTBOUND FILTER) (< 0.5 ms)           Ôöé
Ôöé ÔÇó Canary Token Ka├ğak Tespiti (Marker & De─şer Kontrol├╝)                           Ôöé
Ôöé ÔÇó PII Maskeleme (TC Kimlik, Kredi Kart─▒, Telefon)                                Ôöé
Ôöé ÔÇó Sistem S─▒rlar─▒ Maskeleme (API Anahtarlar─▒, DB Ba─şlant─▒ Dizgeleri, Parolalar)   Ôöé
Ôöé ÔöÇÔöÇ> ├ç─▒kt─▒: [SANS├£RLEND─░] / [REDACTED] Maskelenmi┼ş G├╝venli Yan─▒t                 Ôöé
ÔööÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöİ
```

### 3.1. Karar Mant─▒─ş─▒: Puanlama m─▒, Do─şrudan Bloklama m─▒?

Siber g├╝venlik mimarisinde **yaln─▒zca tek bir y├Ânteme g├╝venmek ├Âl├╝mc├╝l bir hatad─▒r:**
* **Neden Sadece Regex Bloklayamaz?**  
  Bir kullan─▒c─▒ *"Havaliman─▒ sistem ┼şifremi unuttum, nas─▒l s─▒f─▒rlar─▒m?"* dedi─şinde regex *"┼şifre"* kelimesini yakalar. E─şer do─şrudan bloklarsa me┼şru m├╝┼şteri kap─▒ d─▒┼şar─▒ edilir (Y├╝ksek Yanl─▒┼ş Alarm / False Positive).
* **Neden Sadece Model Bloklayamaz?**  
  Sald─▒rgan komutu Base64 i├ğerisine g├Âmerse veya Unicode g├Âr├╝nmez karakterler aras─▒na gizlerse, n├Âral model metin olarak g├Âremedi─şi i├ğin atlayabilir (Ka├ğan Sald─▒r─▒ / False Negative).
* **Bizim Hibrit ├ç├Âz├╝m├╝m├╝z (Tiered Decision Gating):**
  1. **Kesin Su├ğ Unsurlar─▒ (Hard Block):** Metinde bilinen g├Âr├╝nmez karakter steganografisi (Unicode tag, zero-width) veya a├ğ─▒k sistem manip├╝lasyonu etiketleri (`<system_override>`, `<!-- inject -->`) tespit edilirse do─şrudan **BLOCKED** edilir.
  2. **Bile┼şik Risk Puan─▒ (Composite Risk Score):**
     $$\text{Composite Risk} = \alpha \cdot \text{Score}_{\text{ML}} + \beta \cdot \text{Score}_{\text{Regex}} + \gamma \cdot \text{Score}_{\text{Stego}}$$
     Burada n├Âral modelin a─ş─▒rl─▒─ş─▒ ($\alpha = 0.70$), kural motorunun a─ş─▒rl─▒─ş─▒ ($\beta = 0.20$), davran─▒┼ş/ta┼ş─▒y─▒c─▒ a─ş─▒rl─▒─ş─▒ ($\gamma = 0.10$) olarak ├ğal─▒┼ş─▒r.
  3. **E┼şik De─şeri:** Bile┼şik Risk $\ge 60$ ise istek kesilir; alt─▒ndaysa g├╝venle ana LLM'e iletilir.

---

## 4. ├çOK ├ûL├çEKL─░ VE ├çOK KURUMLU BENCHMARK YOL HAR─░TASI

Kurumsal *"Self-Hosting ─░kilemi"* tezimizi ispatlamak i├ğin modelleri 4 farkl─▒ ├Âl├ğek ve kategoride ampirik teste tabi tutaca─ş─▒z:

| D├╝zey (Tier) | Kategori | Temsilci Modeller | Parametre Boyutu | Test Ortam─▒ | Durum |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **Tier 1** | **K├╝├ğ├╝k U├ğ Modeller (Edge SLM)** | `qwen2.5:1.5b`<br>`gemma2:2b`<br>`llama3.2:3b`<br>`qwen2.5:3b`<br>`phi3:mini` | 1.5B ÔÇô 3.8B | Yerel Ollama (CPU/RTX) | **TAMAMLANDI**<br>(225 test yap─▒ld─▒, grafikler haz─▒r) |
| **Tier 2** | **Orta ├ûl├ğek A├ğ─▒k Modeller (Mid OSS)** | `meta-llama/Llama-3.1-8B-Instruct`<br>`mistralai/Mistral-7B-Instruct-v0.3`<br>`Qwen/Qwen2.5-7B-Instruct`<br>`google/gemma-2-9b-it` | 7B ÔÇô 9B | Google Colab A100 / T4 veya RunPod | **S─▒radaki Ad─▒m** |
| **Tier 3** | **B├╝y├╝k ├ûl├ğek A├ğ─▒k Modeller (Frontier OSS)** | `meta-llama/Llama-3.3-70B-Instruct`<br>`Qwen/Qwen2.5-72B-Instruct` | 70B ÔÇô 72B | RunPod vLLM veya Groq / DeepInfra API | **Planland─▒** |
| **Tier 4** | **Ticari Kapal─▒ Bulut Modelleri (Closed APIs)** | `OpenAI GPT-4o-mini`<br>`OpenAI GPT-4o`<br>`Google Gemini 1.5 Flash`<br>`Anthropic Claude 3.5 Sonnet` | Gizli (Mega Scale) | Resmi Python API SDK'lar─▒ | **Planland─▒** |

### 4.1. Elde Edilecek ├çarp─▒c─▒ Akademik ├ç─▒kar─▒mlar
1. **├ûl├ğek Ba─ş─▒ms─▒z Zafiyet (Scale-Invariant Vulnerability):**
   * Model boyutu 1.5B'den 70B'ye ├ğ─▒ksa dahi, harici ├ğevre kalkan─▒ (NeuralShield) olmayan modeller prompt injection kar┼ş─▒s─▒nda canary tokenlar─▒n─▒ s─▒zd─▒rmaktad─▒r.
2. **Yerel vs Bulut Maliyet ve Gizlilik Kar┼ş─▒la┼şt─▒rmas─▒:**
   * ┼Şirketler verilerini OpenAI'a g├Ândermemek i├ğin 70B modeli sunucular─▒na koysalar bile g├╝venlik a├ğ─▒─ş─▒n─▒ kapatamazlar.
   * ├ç├Âz├╝m, koca bir modeli yeniden e─şitmek veya prompt m├╝hendisli─şiyle u─şra┼şmak de─şil; ├Ân├╝ne **8.6 ms gecikmeli yerel NeuralShield kalkan─▒** koymakt─▒r.
3. **NeuralShield Koruma Ba┼şar─▒s─▒:**
   * T├╝m bu modellerin ├Ân├╝ne NeuralShield-v3 konuldu─şunda Sald─▒r─▒ Ba┼şar─▒ Oran─▒ (ASR) istisnas─▒z **%0.00'a** d├╝┼şmektedir.

---

## 5. ADIM ADIM GEL─░┼ŞT─░RME PLANI (─░┼Ş PAKETLER─░)

Acele etmeden, ad─▒m ad─▒m ve hatas─▒z ilerleyece─şimiz resmi i┼ş paketleri:

### ­şÄ» ─░┼Ş PAKET─░ 1: SAVUNMA P─░PEL─░NE'ININ EKS─░KS─░Z PAKETLENMES─░ (├ûNCEL─░KL─░)
* **G├Ârev 1.1:** `backend/regex_rules.py` kurallar─▒n─▒n geni┼şletilmesi (Siber g├╝venlik, T├╝rk├ğe komut enjeksiyonu, rol yapma, yetki manip├╝lasyonu kal─▒plar─▒n─▒n eklenmesi).
* **G├Ârev 1.2:** `backend/security_layer.py` karar motorunun g├╝ncellenmesi (Bile┼şik Risk Puan─▒ form├╝l├╝, steganografi cezalar─▒, beyaz yaz─▒ ve emoji tespitinin tek bir `PipelineReport` objesi ├╝retmesi).
* **G├Ârev 1.3:** `backend/dlp.py` outbound filtrenin g├╝├ğlendirilmesi (Canary token yakalama mant─▒─ş─▒n─▒n dinamik hale getirilmesi, kredi kart─▒/TC/API key maskelemesinin do─şrulanmas─▒).
* **G├Ârev 1.4:** B├╝t├╝nle┼şik pipeline i├ğin yerel do─şrulama test scriptinin (`scripts/verify_full_pipeline.py`) yaz─▒lmas─▒ ve %100 ba┼şar─▒yla ge├ğti─şinin teyit edilmesi.

### ­şÄ» ─░┼Ş PAKET─░ 2: ORTA ├ûL├çEK (7B - 9B) MODELLER─░N TEST─░ (COLAB / RUNPOD)
* **G├Ârev 2.1:** Google Colab ├╝zerinde tek t─▒kla ├ğal─▒┼şacak, LLaMA-3.1-8B, Mistral-7B ve Qwen-2.5-7B modellerini otomatik test eden scriptin haz─▒rlanmas─▒.
* **G├Ârev 2.2:** Ayn─▒ 45 sald─▒r─▒ vekt├Âr├╝n├╝n (SkyPort promptu ve canary tokenlar─▒yla) bu modellere Shield OFF ve Shield ON olarak g├Ânderilmesi.
* **G├Ârev 2.3:** ASR oranlar─▒n─▒n kaydedilip mevcut 5 modelimizin yan─▒na eklenmesi (Model havuzunun 8 modele ├ğ─▒kar─▒lmas─▒).

### ­şÄ» ─░┼Ş PAKET─░ 3: B├£Y├£K MODELLER (70B) VE T─░CAR─░ BULUT API'LARININ TEST─░
* **G├Ârev 3.1:** LLaMA-3.3-70B ve Qwen-2.5-72B testlerinin RunPod veya a├ğ─▒k model inference u├ğ noktalar─▒yla ger├ğekle┼ştirilmesi.
* **G├Ârev 3.2:** OpenAI GPT-4o ve Claude 3.5 Sonnet i├ğin API ├ğa─şr─▒ scriptinin ├ğal─▒┼şt─▒r─▒larak sonu├ğlar─▒n toplanmas─▒.
* **G├Ârev 3.3:** Nihai kar┼ş─▒la┼şt─▒rma matrisinin (T├╝m modellerin Shield OFF vs ON tablosunun) ├╝retilmesi.

### ­şÄ» ─░┼Ş PAKET─░ 4: AKADEM─░K RAPOR VE MAKALE ├£RET─░M─░
* **G├Ârev 4.1:** Elde edilen devasa ampirik verinin (Grafikler, ROC e─şrileri, ├ğok modelli ASR tablolar─▒, CPU gecikme analizleri) makaleye entegre edilmesi.
* **G├Ârev 4.2:** Makalenin DergiPark *Computers and Informatics* ┼şablonuna (`File.docx`) kusursuz ┼şekilde, akademik ─░ngilizce ile bas─▒lmas─▒.

---

## 6. MEVCUT DURUM ├ûZET TABLOSU

```
B─░LE┼ŞEN                  DURUM       NOT
ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ
NeuralShield-v3 E─şitimi  TAMAM      59.5k veri, %95.76 F1, 0.992 ROC-AUC
ONNX INT8 Optimizasyonu  TAMAM      278 MB, 8.61 ms CPU ├ğ─▒kar─▒m─▒
IT Terimleri False Alarm TAMAM      %40'tan %0.00'a indirildi
Yerel Model Testleri     TAMAM      5 model (1.5B-3.8B), 225 test, ASR %0
Savunma Pipeline         GEL─░┼Ş─░YOR  Regex & Karar Motoru g├╝├ğlendirilecek
7B-14B Model Testleri    BEKLEMEDE  Colab scripti haz─▒rland─▒ktan sonra
70B & Ticari API Testi   BEKLEMEDE  Pipeline bitince ko┼şulacak
Makale Yaz─▒m─▒ (docx)     BEKLEMEDE  T├╝m testler ve pipeline tamamlan─▒nca
```

---
*Bu yol haritas─▒ projenin resmi rehberidir. Her ad─▒m tamamland─▒k├ğa bu belgedeki ilgili kutucuklar i┼şaretlenecek ve projenin bilimsel b├╝t├╝nl├╝─ş├╝ korunacakt─▒r.*
