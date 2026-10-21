# NeuralShield: Çok Dilli, Katmanlı bir LLM Uygulama Güvenliği Geçidi ve Adil Değerlendirme Üzerine Bir Çalışma

**Taslak sürüm:** v1 (sayılar v6.2 deneylerinden; yer tutucular işaretli)
**Yazarlar:** [Mustafa Çalışkan ve ark.] — **Kurum:** [yer tutucu]

---

## Özet (Abstract)

LLM uygulamalarına giden istemler; prompt injection, jailbreak, talimat iptali ve sistem-prompt sızdırma gibi saldırılara açıktır. Bu çalışmada, **12 dilli** ve **katmanlı** bir uygulama güvenliği geçidi olan **NeuralShield**'i sunuyoruz: (L0) normalizasyon/deobfuskasyon, (L1) regex kuralları, (L2) çok dilli transformer sınıflandırıcı, (L3) DLP ve bunları **OR-Gate** ile birleştiren karar katmanı. v6.2 veri kümesiyle (~100k, 50k/50k dengeli, 12 dil) üç omurga eğittik (XLM-R-base, mmBERT-base, BGE-M3). 

Katkılarımız: (i) **kaynak-ayrık (source-disjoint) adil bir 12-dil değerlendirme protokolü** ve eski kıyaslamalarda **%76.9 kaynak-çakışması** bulgusu; (ii) **F1'de güçlü bir ticari rakiple (Patronus Wolf Defender) istatistiksel denklik** (küme-bootstrap %95 GA); (iii) **Türkçe native held-out kümede recall üstünlüğü** (79.4 vs 45.0); (iv) **iki ön-kayıtlı negatif ablasyon** (veri ve kayıp değişikliklerinin ölçülebilir katkı sağlamadığı); (v) CPU'da çalışan INT8 ONNX dağıtımı. Ayrıca, LLM'lerin **iç muhakeme (reasoning/CoT) alanında hassas veriyi açık metin olarak sızdırabildiği** bulgusunu raporluyoruz (ilgili platform tarafından kabul edilmiştir).

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

### 4.1 Eğitim havuzu
- **~100k**, **12 dil**, **50k saldırı / 50k masum** (deterministik alt-kotalar).
- **Supplement:** 83.611 kayıt — saldırı 34.063; masum 49.548 (25.600 MT + 23.948 native).
- **Native benign:** oasst2/aya; **MT:** EVREN `gemma-4-31b` (eğitim saldırılarıyla aynı motor — motor simetrisi).
- **Türkçe:** native-ağırlıklı (MT ≤ ~%30).
- **Dağılım:** en/tr 15.000; diğer 10 dil ~2.000 (dil başına).
- **Split (70/15/15):** train 69.015 / val 14.793 / test 14.790.

### 4.2 Kalite kontrol (QC)
- Bağımsız jüri (ProtectAI/Deepset/Patronus) + **Qwen2.5-7B-Instruct** yargıç.
- **99 kapsam-dışı** örnek silindi/değiştirildi; **684 etiket-çelişkisi silinmedi** (inceleme için loglandı).

### 4.3 Adil (kaynak-ayrık) benchmark
- `heldout_benchmark_v6_fair.json`: **N=2.849**; saldırı = Simsonsun + rubend18; masum = dolly. **jackhhao hariç** (Patronus'un eğitim kaynağı).
- 12 dil; saldırı/masum ~120/120 dil başına.

---

## 5. Deneysel Kurulum

- **Omurgalar:** XLM-R-base (278M), mmBERT-base (307M), BGE-M3 (568M).
- **Eğitim:** 3 epoch, LR 2e-5, CyberFocalLoss (γ=2.0, α=0.65); mmBERT 16×2, BGE 8×4, XLM-R 16×2.
- **Değerlendirme:** Recall/FP @0.5 ve @0.7; Macro-F1; ROC-AUC; **Recall@FP=1%**; **küme-bootstrap %95 GA** (12 dil kümesi) ve per-dil AUC.
- **Dağıtım:** ONNX INT8, CPU gecikmesi (Colab 2-vCPU, 23 token, 2 thread).

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

### 6.5 CPU Dağıtım Gecikmesi (mmBERT INT8 ONNX)
| Ortam | Median | P95 | Boyut |
|---|---|---|---|
| Colab 2-vCPU, 23 token, 2 thread | **61.92 ms** | 210.65 ms | 294.3 MB |
| (XLM-R referansı) | ~8 ms | — | ~266 MB |

> "8 ms" yalnızca **XLM-R** içindir; **mmBERT ~62 ms** (donanıma bağlı).

### 6.6 Kaynak Tüketimi ve Dağıtım (düzeltilmiş)
| | NeuralShield (mmBERT) | Patronus Wolf Defender |
|---|---|---|
| Omurga | mmBERT-base 307M | **mmBERT-base 307M** |
| Bağlam | 512 | 2048 |
| ONNX boyut | INT8 **294 MB** | FP32 1.23 GB / FP16 615 MB / INT8+INT4 **218 MB** |
| CPU gecikme | ~62 ms (Colab 2-vCPU, 23 token) | bu çalışmada ölçülmedi |

> **Not:** İlk taslaktaki "Patronus = 8B Llama-3 / 16–24 GB VRAM / vLLM" iddiası **yanlıştır**; Patronus da **mmBERT-base (307M)** tabanlıdır (model kartı). Adil karşılaştırmada iki model aynı sınıftadır; temel fark **bağlam (2048 vs 512)** ve **eğitim verisidir**. Bu nedenle "ucuz vs pahalı GPU" anlatısı **kullanılmamalıdır.**

---

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

---

## 8. Sınırlamalar (dürüst)

1. **AUC ve Recall@FP=1%'de Patronus önde** (düşük-FP bölgesi); F1 denkliği eşik-bağımlıdır.
2. **2048-token uzun bağlam** test edilemedi (benchmark 600 karakterde kesildi). Gerçek dünyada 512 ötesinde saldırı gizlenebilir.
3. **Native doğrulama tamamlanamadı:** Türkçe temiz; Rusça karışık/heterojen; Arapça/Almanca gated/veri yok.
4. **Translationese riski:** eğitim (EVREN-MT) ve benchmark (NLLB) çeviri metin içerir.
5. **CPU gecikmesi dağıtım donanımına bağlı** (Colab 2-vCPU); üretim CPU'sunda farklı olabilir.
6. **Patronus adilliği:** 2048 token + kendi eşiği; eğitim verisi kesin bilinmiyor (kaynak-ayrık olduğu garanti değil).

---

## 9. Sonuç

NeuralShield, 12 dilli, katmanlı ve CPU'da çalıştırılabilir bir AppSec geçididir. **Adil, kaynak-ayrık bir benchmark'ta F1'de güçlü bir ticari rakip ile denk** performans gösterir; **native Türkçe'de recall'da üstündür**; ancak **AUC ve düşük-FP bölgesinde geridedir**. Çalışmanın en önemli katkısı, yaygın "OOD" kıyaslamalarındaki **kaynak sızıntısını** ortaya koyması ve **adil bir değerlendirme protokolü** önermesidir. İki ön-kayıtlı ablasyon, veri ve kayıp müdahalelerinin bu veri/omurga ile ölçülebilir kazanç sağlamadığını gösterir. Gelecek çalışma: 2048-token uzun bağlam, native Arapça/Almanca/Rusça veri, ve düşük-FP bölgesinde kalibrasyon.

---

## 10. Tekrarlanabilirlik ve Eserler

- Veri: `data/v6_multilingual_supplement.json`, `data/heldout_benchmark_v6_fair.json`.
- Eğitim: `notebooks/Train_{mmBERT,BGE_M3,XLM_RoBERTa}_v6.ipynb`.
- Doğrulama: `notebooks/Validation_CI_v6.ipynb`, `Validation_Native_v6.ipynb`, `Validation_ONNX_v6.ipynb`.
- Plan/gerekçe: `docs/V6_3_VERISETI_DUZELTME_PLANI.md` (pre-reg: `prereg-v6.3`).
- Rakipler: `notebooks/Guardrail_Rivals_Colab.ipynb`.

---

## Kaynakça (yer tutucu)
[1] Patronus Wolf Defender v2 model kartı. [2] ProtectAI deberta-v3 prompt-injection. [3] Deepset deberta-v3 injection. [4] Meta Llama Guard / Prompt Guard. [5] Lakera mosscap. [6] jackhhao jailbreak-classification. [7] xTRam1/safe-guard. [8] leolee99/NotInject. [9] Simsonsun/JailbreakPrompts. [10] CyberFocalLoss, SupCon, FreeLB literatürü.

---

> **NOT (yazıma geçmeden):** Tüm sayılar v6.2/v6.3 deney çıktılarından alınmıştır. Yayın öncesi: (a) native Arapça/Almanca için kaynak doğrulaması, (b) 2048-token uzun-doküman deneyi (opsiyonel), (c) küme-bootstrap CI'ların tabloya eklenmesi.
