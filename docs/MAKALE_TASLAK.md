# NeuralShield: Çok Dilli, Katmanlı bir LLM Uygulama Güvenliği Geçidi ve Adil Değerlendirme Üzerine Bir Çalışma

**Taslak sürüm:** v1 (sayılar v6.2 deneylerinden; yer tutucular işaretli)
**Yazarlar:** [Mustafa Çalışkan ve ark.] — **Kurum:** [yer tutucu]

---

## Özet (Abstract)

LLM uygulamalarına giden istemler; prompt injection, jailbreak, talimat iptali ve sistem-prompt sızdırma gibi saldırılara açıktır. Bu çalışmada, **12 dilli** ve **katmanlı** bir uygulama güvenliği geçidi olan **NeuralShield**'i sunuyoruz: (L0) normalizasyon/deobfuskasyon, (L1) regex kuralları, (L2) çok dilli transformer sınıflandırıcı, (L3) DLP ve bunları **OR-Gate** ile birleştiren karar katmanı. v6.2 veri kümesiyle (~100k, 50k/50k dengeli, 12 dil) üç omurga eğittik (XLM-R-base, mmBERT-base, BGE-M3). 

Katkılarımız: (i) **kaynak-ayrık (source-disjoint) adil bir 12-dil değerlendirme protokolü** ve eski kıyaslamalarda **%76.9 kaynak-düzeyi çakışması** (birebir metin: %3.8) bulgusu; (ii) **F1'de güçlü bir ticari rakiple (Patronus Wolf Defender) istatistiksel denklik** (küme-bootstrap %95 GA); (iii) **Türkçe native held-out kümede recall üstünlüğü** (79.4 vs 45.0); (iv) **iki ön-kayıtlı negatif ablasyon** (veri ve kayıp değişikliklerinin ölçülebilir katkı sağlamadığı); (v) CPU'da çalışan **FP32 ONNX dağıtımı** ve çok dilli OOD'de **INT8 nicemleme duyarlılığı** bulgusu. Ayrıca, LLM'lerin **iç muhakeme (reasoning/CoT) alanında hassas veriyi açık metin olarak sızdırabildiği** bulgusunu raporluyoruz (ilgili platform tarafından kabul edilmiştir).

**Sınırlamalar:** AUC ve düşük-FP bölgesinde rakip öndedir; 2048-token uzun bağlam bu benchmark'ta test edilememiştir; Arapça/Almanca/Rusça için native doğrulama tamamlanamamıştır.

---

## 1. Giriş

LLM tabanlı uygulamalar (sohbet, RAG, ajanlar) güvenilmeyen metni (kullanıcı istemi, doküman, e-posta, araç çıktısı) modele ulaştırır. Bu yüzey, **istem enjeksiyonu (prompt injection)** ve **jailbreak** saldırılarına karşı savunmasızdır. Ticari ve açık guardrail'ler çoğunlukla İngilizce odaklıdır; çok dilli dayanıklılık ve **adil değerlendirme** eksiktir.

Bu çalışma üç soruya odaklanır:
1. Katmanlı bir geçit, 12 dilde yüksek recall ve düşük FP'yi birlikte sağlayabilir mi?
2. Mevcut "OOD" kıyaslamaları ne kadar güvenilir? (Kaynak sızıntısı?)
3. Ticari bir SOTA rakiple **adil** koşulda nerede duruyoruz?

---

## 2. İlgili Çalışmalar

- **Ticari/açık guardrail'ler:** Patronus Wolf Defender (mmBERT-base, 2048 token), ProtectAI DeBERTa-v3, Deepset DeBERTa-v3, Meta Llama Guard / Prompt Guard.
- **Veri setleri:** SPML, deepset, Lakera mosscap, rikka-snow multilingual, jackhhao, xTRam1/safe-guard, NotInject, Simsonsun/JailbreakPrompts.
- **Değerlendirme sorunları:** kaynak-ayrık olmayan ("in-distribution OOD") benchmark'lar, çeviri (translationese) artefaktı, eşik-bağımlı iddialar.
- **CoT sızıntısı:** reasoning/CoT alanının filtrelenmeden iletilmesi.

---

## 3. Sistem Mimarisi

| Katman | İşlev |
|---|---|
| **L0 Normalizasyon** | NFKC, sıfır-genişlik/Unicode-Tag temizliği, homoglyph katlama, Base64/Base32/Hex/ROT13/ters çevirme/leetspeak çözümü |
| **L1 Regex** | Dil-özel enjeksiyon/jailbreak/persona/şifre kalıpları (TR/EN + çok dilli) |
| **L2 ML** | Çok dilli transformer sınıflandırıcı (mmBERT önerilen) |
| **L3 DLP** | Parola/API anahtarı/kişisel veri maskesi (12 dil) |
| **Karar** | **OR-Gate:** `hard_stego ∨ regex≥60 ∨ ml_risk≥70 ∨ (regex_triggered ∧ ml=Malicious)` |

**L0 (normalizasyon/deobfuskasyon):** NFKC; **Unicode-Tag (U+E0000–U+E007F)** steganografi ayıklama; sıfır-genişlik karakter temizliği; homoglyph (Kiril/Yunan benzeri) katlama; **özyinelemeli** Base64/Base32/Hex/ROT13/ters çevirme/leetspeak çözümü; çözülen katman `extended_text` ile L1/L2'ye iletilir. URL yüzdesel kodlamalar tek başına "hard stego" sayılmaz (FP önleme) ama deşifre içerik yine taranır.
**L1 (regex):** Dil-özel enjeksiyon, talimat iptali, persona/DAN, sistem-prompt sızdırma ve şifre/anahtar isteme kalıpları (TR/EN + çok dilli); skor 0–100, ≥60 blok.
**L2 (ML):** Çok dilli transformer; kalibre olasılık; eşik 0.70.
**L3 (DLP):** Parola/API anahtarı/kredi kartı (Luhn)/TCKN (checksum) maskesi ve canary/secret desenleri.
**OR-Gate:** tek katmanın aşırı-tetiklemesini diğerleriyle dengeler; hiçbir katman tek başına yeterli değildir.

---

## 4. Veri Kümesi (v6.2)

### 4.1 Eğitim havuzu (parquet denetimli değerler)
- **98.606** kayıt, **12 dil**, 48.627 saldırı / 49.979 masum (~%49/%51).
- **Supplement:** 83.611 kayıt — saldırı 34.063; masum 49.548 (25.600 MT + 23.948 native).
- **Native benign:** oasst2/aya; **MT:** EVREN `gemma-4-31b` (eğitim saldırılarıyla aynı motor — motor simetrisi).
- **Dil dağılımı:** en 29.983 (%30.4) · tr 29.011 (%29.4) · diğer 10 dil ~4.000.
- **MT payı:** genel %56.7; **tr %82.4** (23.913 MT / 5.098 native — halilneed, TFLai, 3nesdeniz, AltaySec, merve); ru %53.2; en %0.
- **Split (70/15/15):** train 69.021 / val 14.794 / test 14.791.

> **Dürüst not:** Türkçe "native-ağırlıklı" tasarımı yalnızca **v6.3 Aşama A** deneyinde denenmiş ve
> kazanç sağlamadığı için şampiyon v6.2'ye girmemiştir; v6.2'de tr ağırlıkla MT'dir. Native-tr
> held-out üstünlüğü (§6.4) bu koşulda elde edilmiştir.

### 4.2 Kalite kontrol (QC)
- Bağımsız jüri (ProtectAI/Deepset/Patronus) + **Qwen2.5-7B-Instruct** yargıç.
- **98** kapsam-dışı/yanlış etiketli örnek silindi/değiştirildi; **687 etiket-çelişkisi** loglandı (silinmedi).

### 4.3 Adil (kaynak-ayrık) benchmark
- `heldout_benchmark_v6_fair.json`: **N=2.849**; saldırı = Simsonsun + rubend18; masum = dolly-15k. **jackhhao hariç** (Patronus'un eğitim kaynağı; bizim eğitimimizde yoktur).
- 12 dil; saldırı/masum ~120/120 dil başına.

> **Çeşitlilik kısıtı (dürüst beyan):** Set, **240 benzersiz İngilizce promptun** (119 saldırı + 1 rubend18 + 120 masum) NLLB ile 12 dile çevrilmesinden oluşur. Dolayısıyla (i) etkin benzersiz içerik 240 prompttur, (ii) aynı promptun dil kopyaları koreledir — bu nedenle güven aralıkları **dil-kümesi bazında** bootstrap edilmiştir, (iii) saldırı tarafı tek kaynağa (Simsonsun) dayanır. Bu kısıt, kaynak-ayrıklık iddiasını geçersiz kılmaz (eğitimle kesişim yok) ancak genelleme gücünü sınırlar; genişletme gelecek çalışmadır.

---

## 5. Deneysel Kurulum

- **Omurgalar:** XLM-R-base (278M), mmBERT-base (307M), BGE-M3 (568M).
- **Eğitim:** 3 epoch, LR 2e-5, CyberFocalLoss (γ=2.0, α=0.65); mmBERT 16×2, BGE 8×4, XLM-R 16×2.
- **Değerlendirme:** Recall/FP @0.5 ve @0.7; Macro-F1; ROC-AUC; **Recall@FP=1%**; **küme-bootstrap %95 GA** (12 dil kümesi) ve per-dil AUC.
- **Dağıtım:** ONNX **FP32** (şampiyon), CPU gecikmesi (Colab 2-vCPU, 12 token); INT8 nicemleme duyarlılığı ayrıca raporlanır (§6.5).

---

## 6. Sonuçlar

### 6.1 Hold-out (in-distribution, 14.790)
| Model | Acc | Macro-F1 | ROC-AUC |
|---|---|---|---|
| XLM-R v6.2 | 96.15 | 96.15 | 0.9936 |
| **mmBERT v6.2** | **96.82** | **96.82** | 0.9963 |
| BGE-M3 v6.2 | 97.01 | 97.01 | 0.9955 |

### 6.2 Adil kaynak-ayrık benchmark (N=2.849, @0.70)
| Model | Recall | FP | Macro-F1 | AUC |
|---|---|---|---|---|
| **mmBERT v6.2 (önerilen)** | **74.0** | 3.8 | **84.8** | 0.9494 |
| Patronus Wolf Defender | 70.1 | **0.8** | 84.2 | **0.9767** |
| BGE-M3 v6.2 | 61.5 | 2.2 | 78.8 | 0.9347 |
| XLM-R v6.2 | 47.5 | 2.2 | 70.6 | 0.8916 |

### 6.3 Bootstrap güven aralıkları (dil-küme, %95)
| Model | F1@0.7 (GA) | AUC (GA) | Recall@FP=1% (GA) |
|---|---|---|---|
| mmBERT v6.2 | 0.8482 (0.809–0.880) | 0.9494 (0.919–0.972) | 0.5854 (0.454–0.690) |
| Patronus | 0.8423 (0.804–0.881) | 0.9767 (0.967–0.986) | 0.7222 (0.652–0.801) |

> **F1 GA'ları örtüşür → istatistiksel denklik.** AUC ve Recall@FP=1%'de Patronus öndedir.

### 6.4 Native alt küme (held-out)
**Türkçe (n=1.077):**
| Model | Recall@0.7 | FP@0.7 | AUC |
|---|---|---|---|
| **v6.2** | **79.4** | 3.3 | 0.952 |
| Patronus | 45.0 | 0.2 | **0.972** |

> MT benchmark'ta (tr) Patronus öndeydi (51.7 vs 46.7); **native Türkçe'de v6.2 açık önde (79.4 vs 45.0)**. AUC'de Patronus önde.

**Rusça (n=16.636; karışık/dengesiz — 16.112 FaustSS attack + 524 darkknight benign):** v6.2 rec 91.4 / FP 69.8 / AUC 0.890; Patronus 57.9 / 26.9 / 0.631. *(Dağılım uyumsuzluğu nedeniyle temkinli; sınırlama.)* Heterojenliğe rağmen, **Kiril alfabeli yerel saldırılarda Patronus'un sıralaması AUC 0.631'e (rastgeleye yakın) düşerken, mmBERT AUC 0.890 ile sıralamayı korumuştur.**

### 6.5 CPU Dağıtım Gecikmesi ve Nicemleme Duyarlılığı

**Gecikme (mmBERT ONNX, CPU):**
| Varyant | Ortam | Token | Median | P95 | Boyut |
|---|---|---|---|---|---|
| INT8 | Colab 2-vCPU, 2 thread | 23 | 61.92 ms | 210.65 ms | 294 MB |
| FP32 | Colab 2-vCPU | 12 | **50.57 ms** | 67.72 ms | 1.23 GB |
| FP32 | yerel CPU, 2 thread | 12 | 32.1 ms | 39.2 ms | 1.23 GB |
| INT8 | yerel CPU, 2 thread | 12 | 17.3 ms | 22.1 ms | 309 MB |

> **"8 ms" iddiası geri çekilmiştir:** bu değer XLM-R'a (v5, ~266 MB) aittir; **mmBERT için değildir**.

**Nicemleme duyarlılığı (adil benchmark, N=2.849):** INT8 dinamik nicemleme, çok dilli OOD dağılımında belirgin kayıp yaratmaktadır:

| Varyant | Recall@0.7 | FP@0.7 | Macro-F1 | ROC-AUC |
|---|---|---|---|---|
| **FP32 (makale/dağıtım)** | **74.10** | 3.83 | **84.86** | **0.9494** |
| INT8 (dinamik), **ham metin** | 49.03 | 3.05 | 64.50 | — |
| INT8 (dinamik) + L0 | 53.3 | 3.4 | 73.6 | 0.8908 |

> **Etiket düzeltmesi:** Önceki taslakta "INT8 53.3" **L0+INT8**'e aitti; saf INT8 (ham metin) **49.03**'tür. Ayrıntı: `data/quantization_table_fair.json`, `data/int8_fair_raw_vs_l0.json`.

> **Dağıtım kararı:** Makaledeki tüm sonuçlar **FP32** ile üretilmiştir; sistem yapılandırması da FP32'ye (`ml_onnx_file="model.onnx"`) hizalanmıştır. INT8, bellek/gecikme kazancı (~4× küçük, ~2× hızlı) karşılığında OOD recall'unda ~21 puan kayıp verdiğinden **şampiyon konfigürasyon olarak kullanılmamıştır**.

**Mekanizma:** Dinamik nicemleme (PTQ), aktivasyon aralıklarını kalibrasyon verisinden tahmin eder ve ağırlıkları 8-bit tam sayıya indirger. Eğitim dağılımı içinde (in-distribution hold-out F1 ~96.8) kayıp ihmal edilebilir; ancak **dağılım dışı** girdilerde (homoglyph, steganografi, farklı dil) aktivasyonlar kalibrasyon aralığının dışına taşar, aşırı kırpma (clipping) oluşur ve logitler bozulur. Bu etki sınıf bazında asimetriktir: `direct` sınıfında yakalama **%75.0**'e düşerken (katmanlar bu semantik kaçışları kurtaramaz), `indirect`/`encoding`/`stego` sınıflarında deterministik L0/L1 katmanları kaybı telafi eder (bkz. §7.6). Bu nedenle **güvenlik sınıflandırıcılarında INT8, OOD doğrulaması yapılmadan dağıtılmamalıdır**; nicemleme-farkında eğitim (QAT) gelecek çalışmadır.

### 6.6 Kaynak Tüketimi ve Dağıtım (düzeltilmiş)
| | NeuralShield (mmBERT) | Patronus Wolf Defender |
|---|---|---|
| Omurga | mmBERT-base 307M | **mmBERT-base 307M** |
| Bağlam | 512 | 2048 |
| ONNX boyut | FP32 **1.23 GB** (INT8 294 MB) | FP32 1.23 GB / FP16 615 MB / INT8+INT4 **218 MB** |
| CPU gecikme | ~51 ms FP32 (Colab 2-vCPU, 12 token) | bu çalışmada ölçülmedi |

> **Not:** İlk taslaktaki "Patronus = 8B Llama-3 / 16–24 GB VRAM / vLLM" iddiası **yanlıştır**; Patronus da **mmBERT-base (307M)** tabanlıdır (model kartı). Adil karşılaştırmada iki model aynı sınıftadır; temel fark **bağlam (2048 vs 512)** ve **eğitim verisidir**. Bu nedenle "ucuz vs pahalı GPU" anlatısı **kullanılmamalıdır.**

### 6.7 Uçtan Uca (L0–L3) Katman Doğrulaması

Eğitilmiş v6.2 mmBERT FP32 modeli, **tam pipeline** içinde (L0 deobfuskasyon → L1 regex → L2 transformer → L3 DLP → OR-Gate) adil benchmark (N=2.849; 1.440 saldırı / 1.409 masum) üzerinde koşturulmuştur:

| Yapılandırma | Recall | FP | Macro-F1 | AUC |
|---|---|---|---|---|
| **Shield OR-Gate (L0–L3)** | **75.14** | 3.83 | **85.40** | 0.9413 |
| L2 ham metin (katmansız) | 74.10 | 3.83 | 84.86 | 0.9494 |
| L0+L2 (normalize) | 75.14 | 3.83 | 85.40 | 0.9511 |

**L0 katkısı (adil OOD, N=2.849):** ham → normalize geçişi **+1.04 puan recall** (17 saldırı kurtarıldı, 2 bozuldu → net 15), Macro-F1 +0.68, AUC +0.0017 (`data/l0_contribution_fair.json`). Yani **L0 deobfuskasyon OOD'de ölçülebilir katkı sağlar**; L1'in katkısı bu sette görünmez.

**Katman atfı (blok sayıları):** L2 = 1.136, L1 = 44, L1+L2 = 44, L0 = 4, L3 = 0; toplam blok = 1.136.

> **Yorum:** Bloklamanın **tamamına yakını L2 (semantik transformer)** tarafından yapılmaktadır. Ancak L0, L2'nin girdisini normalize ederek **+1.04 puan recall** kazandırır (yukarıdaki tablo); L1'in katkısı bu sette görünmez (obfuskasyonlu saldırı az). L3 DLP masum metinlerde tetiklenmemek üzere tasarlanmıştır. OR-Gate'in FP'yi artırmaması, katmanların **örtüşen ama tutarlı** çalıştığını gösterir. Per-dil E2E recall/FP: en 76.7/0.0, tr 48.3/4.2, de 83.3/0.8, fr 79.2/0.0, es 81.7/0.8, it 82.5/0.0, pt 74.2/0.0, ru 95.0/12.5, ar 64.2/7.5, ja 77.5/8.9, ko 60.8/5.9, zh 78.3/6.1.

> **Not:** Bu sonuçlar `data/e2e_layer_test_v6_2.json` dosyasında saklanmıştır (Colab FP32, 2-vCPU).

### 6.8 Küratörlü Red-Team Seti ve Katman Ablasyonu

Genel benchmark, saldırı **mekanizmasını** ayırt etmez. Bu nedenle 4 katmanın rolünü ölçmek için küratörlü bir red-team seti kuruldu (`data/redteam/curated_redteam_v6_2.json`): **101 saldırı + 60 benign**, 4 analitik sınıf — `direct` 16, `indirect` 26, `encoding` 26, `stego` 33 (dil: TR/EN; kanal: kullanıcı mesajı / gizli belge metni). Ham korusdaki kalite sorunları (birebir kopyalar, bozuk homoglyph, Türkçe-İngilizce karışık şablon, EN benign eksikliği) düzeltildi; ayrıntı `curated_redteam_v6_2_manifest.json`.

| Yapılandırma | Yakalama | FP | F1 | Wilson %95 GA (yakalama) |
|---|---|---|---|---|
| **L2-FP32 tek başına (katmansız)** | **100.0** | 6.7 | **98.1** | [96.3, 100.0] |
| L2-INT8 tek başına | 89.1 | 6.7 | 92.3 | [81.5, 93.8] |
| L2-INT8 + L0 normalize | 95.0 | 6.7 | 95.5 | — |
| L0+L1 (model yok) | 76.2 | **0.0** | 86.5 | [67.1, 83.5] |
| **Tam 4 katman (FP32)** | **100.0** | 6.7 | **98.1** | [96.3, 100.0] |
| Tam (INT8 + L0/L1) | 96.0 | 6.7 | 96.0 | — |

**Sınıf bazında yakalama (FP32 / INT8 / INT8+tam):** `direct` 100.0 / 75.0 / 75.0; `indirect` 100.0 / 88.5 / 100.0; `encoding` 100.0 / 96.2 / 100.0; `stego` 100.0 / 90.9 / 100.0.

> **Dürüst yorum:** FP32'de **L2 tek başına bu sette tüm saldırıları yakalar**; katmanlar ek recall sağlamaz. Katmanların ölçülebilir değeri üç yerdedir: **(i) nicemleme kurtarması** (INT8'de %89→%96; `indirect`/`encoding`/`stego` sınıflarında %100'e tamamlar), **(ii) deterministik hızlı yol** (L0+L1 model çağrısı olmadan %76.2 yakalama, **%0 FP**, <1 ms), **(iii) çıktı tarafı DLP** (§7.6). `direct` sınıfı INT8'de %75'te kalır — katmanlar semantik kaçışı kurtaramaz; bu sınıf n=16 olduğu için **yalnızca keşifsel (exploratory)** raporlanır.

> **Kalibrasyon açığı:** FP %6.7 (4/60) tamamen L2 kaynaklıdır ve kısa/alan-dışı benign sorgularda yoğunlaşır ("SkyLounge nerede?" p=0.91; "Uçuş bilgisi ekranları nerede?" p=0.99; "Check-in kontuarı nerede?" p=0.85; "What is the Wi-Fi password?" p=0.99). L1 bu örneklerde tetiklenmez. Test seti bu bulgudan sonra **ayarlanmamıştır**.

### 6.9 Yerel LLM Zafiyeti ve NeuralShield Kalkan Savunması (Ampirik Red-Team)

Projenin temel tezi şudur: Açık kaynak ve yerel LLM'ler sistem promptuna gömülü sırları (parola, PIN, API anahtarı) prompt injection ile doğrudan sızdırır; NeuralShield 4 katmanlı geçidi bu sızıntıyı keser. 5 farklı açık ağırlıklı model üzerinde 101 küratörlü saldırı ve 60 benign sorgu ile (greedy decoding, deterministik) ampirik olarak test edilmiştir (`data/redteam/redteam_v6_2_summary.json`):

| Model | Parametre | Kalkan OFF (ASR %) | Wilson %95 GA | L3-only (%) | Kalkan ON (ASR %) | Wilson %95 GA | Blok Oranı | FP (%) |
|---|---|---|---|---|---|---|---|---|
| **Qwen2.5-3B** | 3.09B | **25.7%** (26/101) | [18.2, 35.0] | **0.0%** | **0.0%** (0/101) | [0.0, 3.7] | 100.0% | 6.7% |
| **Llama-3.2-3B** | 3.21B | **13.9%** (14/101) | [8.4, 21.9] | **0.0%** | **0.0%** (0/101) | [0.0, 3.7] | 100.0% | 6.7% |
| **Gemma-2-2B** | 2.61B | **8.9%** (9/101) | [4.8, 16.1] | **0.0%** | **0.0%** (0/101) | [0.0, 3.7] | 100.0% | 6.7% |
| **Phi-3-mini** | 3.82B | **7.9%** (8/101) | [4.1, 14.9] | **0.0%** | **0.0%** (0/101) | [0.0, 3.7] | 100.0% | 6.7% |
| **Qwen2.5-1.5B** | 1.54B | **5.0%** (5/101) | [2.1, 11.1] | **0.0%** | **0.0%** (0/101) | [0.0, 3.7] | 100.0% | 6.7% |

- **L3-only sütunu:** Modelin kalkan kapalıyken ürettiği *gerçek sızıntı metinleri* doğrudan L3 çıktı DLP'sinden geçirildiğinde sızıntı istisnasız **%0.0'a** inmiştir (tüm 26/14/9/8/5 sızıntı başarıyla sansürlenmiştir). Bu, "DLP yalnızca sentetik şablonlarda çalışıyor" eleştirisini tamamen ortadan kaldırır.
- **Sıcaklık kontrolü ($n=20$):** Greedy (%35.0) vs $T=0.7$ (%35.0) sızıntı oranı farkı **0.0 puan** bulunmuştur; açgözlü aramanın deterministik temsiliyeti doğrulanmıştır.
- **Etkili Alt Küme ($n=35$):** 101 saldırının 35'i (%34.7) en az bir modelde sızıntı yaratmıştır. Bu etkili kümede `Qwen2.5-3B` zafiyeti **%74.3**, `Llama-3.2-3B` zafiyeti **%40.0** seviyesindedir; kalkan bunu **%0.0'a** indirmiştir (-74.3 / -40.0 puan risk düşüşü).
- **Saldırı sınıfı zafiyet profili:** En savunmasız alan doğrudan enjeksiyon (`direct`: Qwen %50.0, Llama %25.0) ve gizli belge enjeksiyonudur (`indirect`: Qwen %42.3, Llama %26.9).
- **Canlı Savunma Derinliği Kanıtı (Spontaneous Leak — `BEN_TR_016`):** `Llama-3.2-3B`, tamamen masum bir yolcu sorusunda (*"Uçuş rötar yaptı, haklarım neler?"*, `mlp=0.0431`) hiçbir saldırı olmadığı halde bağlam karışması yaşayarak sistem promptundaki **4 sırrın tamamını kendiliğinden yanıtına dökmüştür**. İstem masum olduğu için L0–L2'den geçmiş (`PASSED+DLP`), ancak **L3 çıktı DLP katmanı devreye girerek 4 sırrın tamamını gerçek zamanlı maskelemiştir (`on_leak=[]`)**. Bu vaka, L3'ün gerçek üretim akışındaki bağımsız koruma değerini doğrudan kanıtlar.

### 6.10 Düşünme (CoT) kanalında sızıntı — açık ağırlıklı modeller

Muhakeme modelleri nihai yanıtı sansürleyip sırrı **düşünme metninde** dökebilir. 24 saldırı + 12 benign
üzerinde `reasoning` ve `final` **ayrı ayrı** tarandı (1280 token; iki aşamalı canary eşleşmesi).

| Model | Parametre | CoT sızıntı % | final sızıntı % | SADECE CoT (ham) | **SADECE CoT (doğrulanmış)** | Tamamlanan final |
|---|---|---|---|---|---|---|
| **Qwen3-4B-Thinking** | 4.02B | **50.0** (12/24) | 8.3 (2/24) | 45.8 (11/24) | **12.5 (3/24)** | 8/24 |
| R1-Distill-Qwen-7B | 7.62B | 16.7 (4/24) | **20.8 (5/24)** | 4.2 (1/24) | **4.2 (1/24)** | 19/24 |
| R1-Distill-Qwen-1.5B | 1.78B | 16.7 (4/24) | 12.5 (3/24) | 4.2 (1/24) | **4.2 (1/24)** | 17/24 |

> **Bulgu 1 (sağlam):** Qwen3-4B-Thinking saldırıların **%50.0'sinde** düşünme metninde sırrı açık metin
> olarak yazmıştır; R1 türevlerinde %16.7. **`reasoning` alanı bağımsız bir sızıntı kanalıdır.**
>
> **Bulgu 2 (doğrulanmış cot-only):** Yalnızca **nihai yanıtı tamamlayıp** o yanıtta sır bulunmayan
> vakalar sayıldığında Qwen3'te **3/24 = %12.5**, R1 türevlerinde **1/24 = %4.2**. Ham %45.8'lik oran
> 768-token bütçesinde yanıtın kesilmesinden kaynaklanan yapay bir üst sınırdır; 1280 token ile
> tamamlanan yanıt sayısı 5→8'e çıkmış, doğrulanmış cot-only 2→3'e yükselmiştir.
>
> **Bulgu 3 (dürüst nüans):** Sızıntının CoT'ye özgü olduğu **evrensel değildir** —
> **R1-Distill-Qwen-7B nihai yanıtta (%20.8) düşünme metninden (%16.7) daha fazla sızdırmaktadır.**
> Yani "muhakeme modeli sırrı yalnız düşüncede tutar" genellemesi yanlıştır; model bazında ölçülmelidir.
>
> **Sınırlama:** ON modda 24 saldırının hiçbiri geçide takılmadan geçemedi (0 örnek) → "kalkan açıkken
> CoT sızıntısı" ölçülemedi; bu, savunmanın tam blokajının sonucudur, ayrı başarı olarak sayılmaz.

### 6.11 Tier-3 Amiral Gemisi Modellerde Zafiyet ve Sessiz CoT Sızıntısı (EVREN H200, N=161)

Hakemlerin *"Yalnızca 1.5B–3.8B küçük modeller test edilmiş"* eleştirisini önceden karşılamak üzere, **aynı küratörlü veri seti** (`curated_redteam_v6_2.json`: 101 saldırı + 60 benign = 161 örnek) ve **aynı sistem promptu** ile TÜBİTAK/SSYZ EVREN H200 kümesindeki amiral gemisi/büyük modeller yerel bilgisayardan REST API üzerinden test edilmiştir (1536 token bütçesi, $T=0.0$ deterministik üretim).

| Model | Mimari / Parametre | OFF Final ASR % | Wilson %95 GA | **OFF CoT ASR %** | Wilson %95 GA | **Sadece-CoT %** | L3-only % | **Kalkan ON %** |
|---|---|---|---|---|---|---|---|---|
| **Gemma-4-31B** | Google (31B Dense) | **0.0%** (0/101) | [0.0, 3.7] | **66.3%** (67/101) | [56.7, 74.8] | **66.3%** (67/101) | **0.0%** | **0.0%** (0/101) |
| **Qwen3.8-Flash-Next** | Alibaba (MoE Flagship) | **0.0%** (0/101) | [0.0, 3.7] | **14.9%** (15/101) | [9.2, 23.1] | **14.9%** (15/101) | **0.0%** | **0.0%** (0/101) |
| **GLM-5.3** | Zhipu AI (Flagship) | **0.0%** (0/101) | [0.0, 3.7] | **2.0%** (2/101) | [0.5, 6.9] | **2.0%** (2/101) | **0.0%** | **0.0%** (0/101) |
| **DeepSeek-v4.1-Flash** | DeepSeek (MoE Flagship) | **0.0%** (0/101) | [0.0, 3.7] | **0.0%** (0/101) | [0.0, 3.7] | **0.0%** (0/101) | **0.0%** | **0.0%** (0/101) |

#### Saldırı Sınıfı x Model: CoT Sızıntı Oranı Dağılımı
| Model | direct ($n=16$) | indirect ($n=26$) | encoding ($n=26$) | stego ($n=33$) | Toplam ($n=101$) |
|---|---|---|---|---|---|
| **Gemma-4-31B** | **81.2%** (13/16) | **76.9%** (20/26) | **76.9%** (20/26) | **42.4%** (14/33) | **66.3%** (67/101) |
| **Qwen3.8-Flash-Next** | **25.0%** (4/16) | **34.6%** (9/26) | **3.8%** (1/26) | **3.0%** (1/33) | **14.9%** (15/101) |
| **GLM-5.3** | **6.2%** (1/16) | **0.0%** (0/26) | **0.0%** (0/26) | **3.0%** (1/33) | **2.0%** (2/101) |
| **DeepSeek-v4.1-Flash** | **0.0%** (0/16) | **0.0%** (0/26) | **0.0%** (0/26) | **0.0%** (0/33) | **0.0%** (0/101) |

> **Kritik Bilimsel Çıkarım (Sessiz CoT Sızıntısı):**
> 1. Büyük ölçekli ve kurumsal modeller (`Gemma-4-31B`, `Qwen3.8-Flash-Next`), son kullanıcıya sunulan nihai yanıtta (`content`) saldırıların tamamını reddetmiş (**%0.0 Final ASR**), dışarıdan bakıldığında "kusursuz güvenli" izlenimi vermiştir.
> 2. Ancak modelin iç düşünme akışında (`reasoning` / CoT), `Gemma-4-31B` 101 saldırının 67'sinde (**%66.3**), `Qwen3.8-Flash-Next` ise 15'inde (**%14.9**) sistem promptuna gömülü gizli canary'leri açık metin olarak sayıklamıştır.
> 3. SSE streaming ile düşünme adımlarını son kullanıcıya ileten ya da muhakeme zincirini loglayan sistemlerde bu durum doğrudan veri sızıntısına yol açmaktadır (*Silent CoT Exfiltration*).
> 4. **NeuralShield Koruma Garantisi:** NeuralShield v6.2 devredeyken (`ON`), 101 saldırının tamamı L0–L2 seviyesinde önceden engellendiği için model hiç çağrılmamış (**ON ASR = %0.0**); girdi filtresi devre dışı bırakılsa dahi L3 Çıktı DLP hem nihai yanıtı hem düşünme akışını tarayarak tüm sızıntıları anında maskelemiştir (**L3-Only ASR = %0.0**). Normal yolcu sorgularında ($n=60$) hiçbir sızıntı yaşanmamıştır.

### 6.12 Ölçek ve Hizalama: Zafiyet Model Büyüklüğüne Değil Hizalamaya Bağlıdır

Aynı 161 örneklik küratörlü set ve aynı v6.2 geçidi ile **10 açık ağırlıklı model** (1.5B–14.7B,
4-bit NF4, greedy) ve **4 amiral gemisi API modeli** test edilmiştir.

| Sınıf | Model | Parametre | OFF Final ASR % | Blok % |
|---|---|---|---|---|
| Tier-1 (uç) | Qwen2.5-1.5B | 1.54B | 4.95 [2.1, 11.1] | 100.0 |
| Tier-1 | Phi-3-mini | 3.82B | 7.92 [4.1, 14.9] | 100.0 |
| Tier-1 | Gemma-2-2B | 2.61B | 8.91 [4.8, 16.1] | 100.0 |
| Tier-1 | Llama-3.2-3B | 3.21B | 13.86 [8.4, 21.9] | 100.0 |
| Tier-1 | Qwen2.5-3B | 3.09B | 25.74 [18.2, 35.0] | 100.0 |
| **Tier-2 (kurumsal)** | Gemma-2-9B | 9.24B | 8.91 [4.8, 16.1] | 100.0 |
| **Tier-2** | Qwen2.5-14B | 14.7B | 10.89 [6.2, 18.5] | 100.0 |
| **Tier-2** | Llama-3.1-8B | 8.03B | 14.85 [9.2, 23.1] | 100.0 |
| **Tier-2** | Qwen2.5-7B | 7.62B | 18.81 [12.4, 27.5] | 100.0 |
| **Tier-2** | **Mistral-7B-v0.3** | **7.25B** | **40.59 [31.5, 50.3]** | **100.0** |
| Tier-3 (API) | DeepSeek-v4.1-Flash | MoE | 0.0 (CoT 0.0) | 100.0 |
| Tier-3 | GLM-5.3 | Flagship | 0.0 (CoT 1.98) | 100.0 |
| Tier-3 | Qwen3.8-Flash-Next | MoE | 0.0 (CoT 14.85) | 100.0 |
| Tier-3 | Gemma-4-31B | 31B | 0.0 (**CoT 66.34**) | 100.0 |

> **Etkili alt küme (10 model):** 101 saldırının **62'si (%61.4)** en az bir modelde sızdırmıştır; bu alt kümede **Mistral-7B %66.1**, Qwen2.5-3B %41.9, Qwen2.5-7B %30.6, Llama-3.1-8B %24.2, Qwen2.5-14B %17.7, Qwen2.5-1.5B %8.1'dir (ON modda hepsi %0.0).

> **Sınıf bazında (10 model havuzu, n=1010):** indirect %28.5, direct %27.5, stego %7.3, encoding %5.8 — Mistral-7B stego'da tek başına **%45.5** ile aykırıdır (zayıf hizalamanın doğrudan sonucu).

> **Bulgu 1 — "küçük model" itirazı çürütülmüştür:** Kurumsal ölçekte yaygın kullanılan
> **Mistral-7B-v0.3, tüm 14 model içinde en yüksek final-sızıntı oranına (%40.59) sahiptir**.
> Yani zafiyet "oyuncak model" sorunu değildir; gerçek üretim dağıtımlarını doğrudan ilgilendirir.

> **Bulgu 2 — ölçek monoton değildir:** Qwen ailesinde 1.5B→3B→7B→14B için ASR
> %4.95→%25.74→%18.81→%10.89; Llama'da 3.2B %13.86 → 8B %14.85; Gemma'da 2B %8.91 → 9B %8.91.
> **Büyüklük zafiyeti tek başına açıklamıyor; belirleyici etken hizalama/safety-tuning kalitesidir.**
> Bu, "daha büyük = daha güvenli" varsayımını da "daha büyük = daha zafiyetli" varsayımını da reddeder.

> **Bulgu 3 — iki farklı zafiyet rejimi:** Açık ağırlıklı 7–14B modeller sırrı **doğrudan nihai
> yanıtta** sızdırırken, API ile sunulan amiral gemisi modeller nihai yanıtta reddedip sırrı
> **yalnızca düşünme kanalında** (CoT) sızdırmaktadır (§6.11). İkisi de aynı geçitle %0.0'a indirilmiştir.

> **Sınırlama:** Tüm açık ağırlıklı modeller 4-bit NF4 ile yüklenmiştir; nicemleme güvenlik
> hizalamasını etkileyebilir (FP16 kontrolü gelecek çalışma). Mistral-v0.3'ün görece zayıf güvenlik
> hizalaması bilinen bir özelliktir ve bulguyu açıklar; yine de mutlak ASR değerleri üst sınır sayılmalıdır.

## 7. Analiz

### 7.1 Benchmark kaynak sızıntısı (temel bulgu)
- Eski OOD-2000 setinin **%76.9'u** eğitimle aynı kaynaklardan (rikka-snow, SPML, mosscap, jackhhao).
- Adil benchmark'ta tam+yakın-kopya sızıntısı **%0.1** (2/2.849).
- **Patronus'un 86.9 F1'i**, `jackhhao` eğitimde olduğu için **şişikti**; adilde 84.2.

### 7.2 Hata analizi (adil benchmark)
- Uzunluk hipotezi **elendi** (FN medyan 356 ≈ TP 357.5).
- FP'nin **%98'i <150 karakter** kısa benign.
- MT benzersiz-küme oranı **%88–99** (ciddi duplikasyon yok).

### 7.3 Ön-kayıtlı ablasyonlar (negatif)
- **Aşama A** (tr native-ağırlık + kısa-benign): F1 84.8→83.6, AUC 0.949→0.939.
- **Aşama B** (SupCon 0.05/0.07 + FreeLB 3 adım): F1 84.5, AUC 0.946.
- **Sonuç:** v6.2'den **istatistiksel olarak ayırt edilemez**; **ölçülebilir katkı yok**.

### 7.4 Çok dilli değerlendirme
- MT'de per-dil AUC'de Patronus çoğu dilde önde (tr, ar, ja, zh, ko).
- **Ancak native Türkçe'de v6.2 recall'u belirgin üstün** → MT benchmark'ın recall'u gizlediği gösterildi.
- de/it'te v6.2 AUC hafif önde; diğerlerinde Patronus.

### 7.5 LLM İç Muhakeme (CoT) Sızıntısı ve Sorumlu Bildirim
Ayrı bir deneysel çalışmada (EVREN H200), modellerin **`reasoning`/CoT alanının filtrelenmeden iletilebildiğini** gözlemledik: model `content` alanında reddetse bile **`reasoning` alanında hassas bilgiyi (ör. parola/token) açık metin** olarak dökebilmektedir.

| Model (EVREN H200) | CoT sızıntısı |
|---|---|
| `gemma-4-31b` | **%65.0** |
| `qwen-3.8-flash-next` | **%30.0** |

**Savunma çıkarımı:** İngress'te (NeuralShield L0–L4) istem engellendiğinde model **çağrılmadığı** için CoT sızıntısı **%0'a** iner; yani savunma modelin kendi çıktı filtresine bırakılamaz.
**Sorumlu bildirim:** Bulgu EVREN/SSYZ ekibine iletilmiş; ekip bulguyu **kabul etmiş**, **dokümantasyon güvenlik notu** ve **model geliştiricisine eskalasyon** başlatmış, katkı için **5.000 CR** vermiştir. *(Ham istek/yanıt kanıtı ayrı deney klasöründedir; yayında anonimleştirilecektir.)*

> **Yerel model doğrulaması (ampirik sonuç):** Aynı ölçüm açık ağırlıklı muhakeme modellerinde de doğrulanmıştır (`data/redteam/redteam_v6_2_reasoning_full.json`):

| Model | n (saldırı) | CoT Sızıntısı (%) | Final Yanıt Sızıntısı (%) | SADECE CoT Sızıntısı (%) | Kalkan ON CoT Sızıntısı (%) |
|---|---|---|---|---|---|
| **`Qwen3-4B-Thinking`** | 24 | **%50.0** (12/24) | %8.3 (2/24) | **%45.8** (11/24) | **%0.0** (0/24) |
| **`R1-Distill-Qwen-1.5B`** | 24 | **%16.7** (4/24) | %12.5 (3/24) | **%4.2** (1/24) | **%0.0** (0/24) |

> **Kritik Güvenlik Bulgusu (Görünmez CoT Kanalı ve Token Bütçesi Analizi):** `Qwen3-4B-Thinking`, 24 saldırının **12'sinde (%50.0)** düşünme (`<!->`) aşamasında sırrı açık metin olarak üretmiştir. Ham `SADECE CoT` oranı %45.8 (11/24) olmakla birlikte, adli incelemede bu 11 vakanın **9'unda** model 768 token sınırına takılıp yanıtı tamamlayamamıştır. Yanıtı tamamlayan 8 vakadan yalnız **3'ü** (`RT_PERSONA_0022`, `RT_PERSONA_0032`) doğrulanmış cot-only'dır: model son yanıtta talebi açıkça reddederken düşünme bloğunda sırrı ifşa etmiştir (**doğrulanmış cot-only = 3/24 = %12.5**, 1280-token koşusu). Not: `RT_SEMANTIC_0131` hem CoT **hem nihai yanıtta** sızmıştır (final temiz değildir), bu nedenle cot-only sayılmaz. Benzer şekilde `R1-Distill-Qwen-1.5B` (17/24 tamamlanan yanıt) `RT_SEMANTIC_0031` vakasında 4 sırrın tamamını CoT içinde dökerken nihai yanıtta yalnız 1'ini (`db_root_password`) açığa çıkarmış, 3'ünü gizlemiştir. NeuralShield ingress'te (L0–L2) isteği düşürdüğü için CoT sızıntısı **%0.0** olur.

### 7.6 Savunma Derinliği: L3 Çıktı DLP'nin Tek Başına Gücü

Hakemsel bir itiraz şudur: "Kalkan ON iken saldırı girişte durdurulduğu için model hiç çağrılmıyor; bu bir LLM savunması değil, giriş filtresi başarısıdır." Bu itirazı doğrudan test ettik: **L0–L2 tamamen baypas edildi**, modelin sırrı sızdırdığı varsayıldı ve yalnızca **L3 (çıktı DLP)** uygulandı.

| Tasarım | Sızıntı engelleme | Not |
|---|---|---|
| Yalnızca bağlamsal DLP (ilk sürüm) | %50.0 | anahtar kelime yoksa kaçıyordu |
| **+ `secret_registry` (exact-match denylist)** | **%100.0** (40/40) | bağlamdan bağımsız |

**Bulgu:** Bağlamsal desenler ("password: X", "API key = X") yalnızca **anahtar kelime varsa** maskeler; model sırrı bağlamsız verirse ("Sure, here it is → X") kaçar. Bu nedenle DLP'ye oturuma bağlı **bilinen-sır kayıt defteri** (exact-match denylist, yüksek kesinlik, FP riski yok) eklendi; benign test setinde **0/60 tetiklenme** doğrulandı. Sonuç: iki **bağımsız** savunma hattı — giriş filtresi (L0–L2) ve çıktı DLP (L3) — biri atlatıldığında diğeri devrededir.

**Canary tespitinin sağlamlaştırılması:** Sızıntı ölçümü iki aşamalıdır: (i) katı eşleşme, (ii) **normalleştirilmiş eşleşme** (boşluk/ayraç/Unicode hilesiyle bölünmüş sırlar; ör. `A T C - K X 9 4 2 5`). Bu olmadan, modelin sırrı harf harf yazması **OFF-ASR'yi olduğundan düşük** gösterirdi. Birim testleri: 11/11 (katı, ayraçlı, harf-harf ve benign negatifler).

---

## 8. Sınırlamalar (dürüst)

1. **AUC ve Recall@FP=1%'de Patronus önde** (düşük-FP bölgesi); F1 denkliği eşik-bağımlıdır.
2. **2048-token uzun bağlam** test edilemedi (benchmark 600 karakterde kesildi). Gerçek dünyada 512 ötesinde saldırı gizlenebilir.
3. **Native doğrulama tamamlanamadı:** Türkçe temiz; Rusça karışık/heterojen; Arapça/Almanca gated/veri yok.
4. **Translationese riski:** eğitim (EVREN-MT) ve benchmark (NLLB) çeviri metin içerir.
5. **CPU gecikmesi dağıtım donanımına bağlı** (Colab 2-vCPU); üretim CPU'sunda farklı olabilir.
6. **Patronus adilliği:** 2048 token + kendi eşiği; eğitim verisi kesin bilinmiyor (kaynak-ayrık olduğu garanti değil).
7. **INT8 nicemleme OOD'de kayıp veriyor** (~21 puan recall); bu nedenle FP32 dağıtılır ve bellek/gecikme maliyeti daha yüksektir (§6.5). Nicemleme-farkında eğitim (QAT) gelecek çalışmadır.
8. **L0/L1 katkısı sınırlı örneklemde görünmez:** E2E'de blokların ~%99'u L2'den gelir; obfuskasyon ağırlıklı bir test setiyle ayrıca doğrulanmalıdır (§6.7). Küratörlü red-team setinde ise L0/L1'in değeri nicemlenmiş (INT8) dağıtımda ve model-bağımsız hızlı yolda ölçülür (§6.8).
9. **Alt sınıf örneklemleri küçük:** `direct` n=16 (Wilson GA ~[50.5, 89.8]); bu tür alt-sınıf yüzdeleri **yalnızca keşifsel**dir, genelleme iddiası taşımaz. Ana iddialar N=101 havuzuna ve adil benchmark'ın N=2.849'una dayandırılmıştır.
10. **Red-team seti in-domain'dir:** Küratörlü 161 kayıt, eğitim dağılımına yakın ailelerden gelir; %100 yakalama **OOD başarısı olarak yorumlanmamalıdır** (OOD için §6.2: recall 74.1). İki sayı ayrı raporlanır.
12. **Modeller 4-bit NF4 ile yüklendi:** nicemleme güvenlik hizalamasını zayıflatabilir; FP16 kontrolü yapılmadı (P1). ASR mutlak değerleri üst sınır olarak okunmalıdır.
13. **CoT ON modu boş:** 24 saldırının hiçbiri geçide takılmadan geçemedi (0 örnek) → "kalkan açıkken CoT sızıntısı" ölçülemedi.
14. **Red-team seti TR/EN ve in-domain:** 12 dile yayılmadı (P2).
11. **Kalkan ON karşılaştırmasının asimetrisi kabul edilir:** Bloklanan istem model çağrılmaz (bu tasarım gereğidir); bu nedenle §7.6'da L3 çıktı DLP'si **bağımsız** olarak da ölçülmüştür.

---

## 9. Sonuç

NeuralShield, 12 dilli, katmanlı ve CPU'da çalıştırılabilir bir AppSec geçididir. **Adil, kaynak-ayrık bir benchmark'ta F1'de güçlü bir ticari rakip ile denk** performans gösterir; **native Türkçe'de recall'da üstündür**; ancak **AUC ve düşük-FP bölgesinde geridedir**. Çalışmanın en önemli katkısı, yaygın "OOD" kıyaslamalarındaki **kaynak sızıntısını** ortaya koyması ve **adil bir değerlendirme protokolü** önermesidir. İki ön-kayıtlı ablasyon, veri ve kayıp müdahalelerinin bu veri/omurga ile ölçülebilir kazanç sağlamadığını gösterir. Gelecek çalışma: 2048-token uzun bağlam, native Arapça/Almanca/Rusça veri, ve düşük-FP bölgesinde kalibrasyon.

---

## 10. Tekrarlanabilirlik ve Eserler

- Veri: `data/v6_multilingual_supplement.json`, `data/heldout_benchmark_v6_fair.json`, `data/qc_audit_report_v6.json`.
- Eğitim: `notebooks/Train_{mmBERT,BGE_M3,XLM_RoBERTa}_v6.ipynb`.
- Doğrulama: `notebooks/Validation_CI_v6.ipynb`, `Validation_Native_v6.ipynb`, `Validation_ONNX_v6.ipynb`, `E2E_Shield_v6_2.ipynb`.
- Ölçüm çıktıları: `data/e2e_layer_test_v6_2.json`, `data/validation_ci_v6.json`, `data/native_eval_v6.json`, `data/native_subset_v6.json`.
- Red-team: `data/redteam/curated_redteam_v6_2.json` (+ `_manifest.json`), `data/redteam/layer_ablation_clean.json`, `data/redteam/l3_only_ablation.json`, `data/redteam/l2_only_ablation_v6_2.json`, `notebooks/RedTeam_Local_Models_v6_2.ipynb`; kürasyon betiği `scripts/build_curated_redteam.py`.
- Canary/DLP: `backend/canary.py` (katı + normalleştirilmiş eşleşme), `backend/dlp.py` (bağlamsal desenler + `secret_registry`).
- Model: `backend/models/neuralshield_v6_mmbert/` (FP32 `model.onnx` + tokenizer; INT8 alternatif).
- Plan/gerekçe: `docs/V6_3_VERISETI_DUZELTME_PLANI.md` (pre-reg: `prereg-v6.3`).
- Rakipler: `notebooks/Guardrail_Rivals_Colab.ipynb`.

---

## Kaynakça (yer tutucu)
[1] Patronus Wolf Defender v2 model kartı. [2] ProtectAI deberta-v3 prompt-injection. [3] Deepset deberta-v3 injection. [4] Meta Llama Guard / Prompt Guard. [5] Lakera mosscap. [6] jackhhao jailbreak-classification. [7] xTRam1/safe-guard. [8] leolee99/NotInject. [9] Simsonsun/JailbreakPrompts. [10] CyberFocalLoss, SupCon, FreeLB literatürü.

---

> **NOT (yazıma geçmeden):** Tüm sayılar v6.2/v6.3 deney çıktılarından alınmıştır. Yayın öncesi: (a) native Arapça/Almanca için kaynak doğrulaması, (b) 2048-token uzun-doküman deneyi (opsiyonel), (c) küme-bootstrap CI'ların tabloya eklenmesi.
