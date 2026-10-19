# 📋 NeuralShield-v6.3 — Verisetini Düzeltme Planı (Gerekçe + Uygulama + Hedefler)

**Tarih:** 17 Ekim 2026
**Durum:** v6.2 eğitimleri bitti; **adil (source-disjoint) benchmark** ile gerçek konum ölçüldü. Bu belge, **verisetinde yapılacak v6.3 düzenlemelerini**, **neden** yapıldığını, **nerelere bakılacağını** ve **başarı koşullarını** tanımlar.

---

## 1. Proje Amacı

**NeuralShield**, LLM uygulamalarına giden istemleri koruyan **4 katmanlı AppSec güvenlik geçididir** (L0 normalizer → L1 regex → L2 ML sınıflandırıcı → L3 DLP), OR-Gate karar mekanizmasıyla.

- **Kapsam:** Prompt injection, jailbreak, talimat iptali, sistem-prompt sızdırma, indirect/agentic injection, steganografi, exfiltration.
- **Kapsam dışı:** İçerik moderasyonu / etik / nefret (delege edilir).
- **Hedef:** 12 dilde (en, tr, de, fr, es, it, pt, ru, ar, ja, ko, zh) dengeli, **kaynak-ayrık (source-disjoint)**, düşük FP, yüksek recall ile **rakipleri adil koşulda geçmek** ve yayınlanabilir bir ablasyon sunmak.
- **Omurgalar (ablasyon):** XLM-RoBERTa-base (278M), mmBERT-base (307M), BGE-M3 (568M). **Şampiyon adayı: mmBERT.**

---

## 2. Mevcut Durum (v6.2 sonrası, adil benchmark)

### 2.1 Adil (source-disjoint) benchmark sonuçları — th=0.70
Kaynak: `heldout_benchmark_v6_fair.json` (Simsonsun + rubend18 saldırı / dolly masum, NLLB 12-dil, **jackhhao YOK**)

| Model | Recall | FP | Macro-F1 | AUC |
|---|---|---|---|---|
| **mmBERT v6.2 (şampiyon)** | **74.0** | 3.8 | **84.8** | 0.9494 |
| Patronus Wolf Defender | 70.1 | 0.8 | 84.2 | 0.9767 |
| BGE-M3 v6.2 | 61.5 | 2.2 | 78.8 | 0.9347 |
| XLM-R v6.2 | 47.5 | 2.2 | 70.6 | 0.8916 |

> @th=0.50: mmBERT **86.2** vs Patronus **86.3** → F1'de **başabaş**.
> **BGE-M3** hold-out'ta en iyi (97.0) ama adilde mmBERT'in gerisinde → aşırı-uydurma; **şampiyon yapılmaz**.

### 2.2 Kritik bulgu: Eski benchmark kontamineydi
- Eski `heldout_benchmark_v6_clean.json` (jackhhao ağırlıklı) **Patronus'un eğitim kaynağı** (`jackhhao/jailbreak-classification`).
- Bu yüzden Patronus'un oradaki 86.9 F1'i **şişik**; adilde 84.2'ye indi.
- **Ders:** kıyas **yalnızca kaynak-ayrık** benchmark ile yapılmalı.

### 2.3 Patronus'a göre kalan açıklar (mmBERT, adil, @0.7)
| Dil/Metrik | mmBERT | Patronus | Açık |
|---|---|---|---|
| **ar (Arapça)** | 65.0 | **91.7** | **-26.7 (en büyük)** |
| en | 75.8 | 86.7 | -10.9 |
| tr | 46.7 | 51.7 | -5.0 |
| ru FP | 12.5 | 0.8 | yüksek FP |
| **AUC** | 0.949 | 0.977 | kalibrasyon |
| de/fr/es/it/pt/ja/zh | ✅ | — | **biz öndeyiz** |

---

## 3. Neden Verisetini Düzenliyoruz? (Kök nedenler)

1. **Arapça zayıf (65 vs 91.7):** Eğitimde Arapça saldırılar neredeyse tamamen MT/çeviri; native çeşitlilik az. → **native Arapça (saldırı + masum) gerekli.**
2. **İngilizce açık (75.8 vs 86.7):** EN saldırı çeşitliliği ve "saldırıya komşu bening" (hard-negative) eksik.
3. **FP ve AUC geride:** Patronus, **simetrik augmentasyon + hedefli hard-negative + contrastive + FreeLB** kullanıyor (model kartı). Bizim benign'imiz genel/roleplay ağırlıklı; sınıf-stil simetrisi zayıf.
4. **Geçmişte yapılan hata (tekrarlanmayacak):** v6.2'de benign'i tek taraflı MT/roleplay ile doldurduk → sınıf-stil kısayolu + recall düşüşü. Bu kez **hedefli ve ölçülü** ekleme yapılacak.
5. **Adil değerlendirme zorunluluğu:** Benchmark kaynakları hiçbir değerlendirilen modelin eğitiminde olmamalı.

**Patronus model kartı (referans):** `https://huggingface.co/patronus-studio/wolf-defender-prompt-injection`
- mmBERT-base, 2048 token, 3 epoch, LR 1e-5, BF16.
- **Supervised contrastive loss (0.05, temp 0.07) + FreeLB (3 adım, 0.01, max norm 0.1).**
- **Augmentasyon her iki sınıfa** (Unicode/homoglyph/Base64/tag/leet/case/boşluk).
- **Counterfactual** çiftler + **hedefli hard-neg** (güvenlik dokümanı, kod, politika, saldırı açıklaması).
- 90% dedup, long-context (2048) + Smooth-Max.

---

## 4. Ne Değiştireceğiz? (v6.3 veri düzenlemeleri)

> **İlke:** Mevcut dengeli (50k/50k) iskeleti KORU. Saldırı sayısını bozmadan, **açığı olan dillere native çeşitlilik** ve **hedefli hard-negative** ekle. Benign'i genel roleplay ile DOLDURMA.

### 4.1 Arapça (ve zayıf diller) native takviye — EN YÜKSEK ÖNCELİK
- **Hedef:** `ar` saldırı + masum için **native** örnek ekle (MT değil).
- Kaynaklar (doğrulanacak, eğitimde OLMAYAN): Arapça prompt-injection/guardrail setleri (ör. NAMAA-Space / Arabic injection), native benign (Arabic instruction/QA).
- **Hedef kota:** `ar` saldırı ve masumda native oranı ≥%50.
- Başarı: `ar` recall **65 → ≥85**, FP ≤%6.

### 4.2 İngilizce saldırı çeşitliliği + hedefli hard-negative
- **Saldırı:** subtle/örtük jailbreak & injection örnekleri (mevcut EN havuzundan çeşitlendir; aynı şablonları çoğaltma).
- **Masum (hard-neg):** **genel roleplay DEĞİL**; şunlar:
  - Güvenlik hakkında dokümanlar ("SQL injection nasıl önlenir?"),
  - Kod/markup/konfig parçaları (talimat benzeri metin içeren),
  - Sistem-prompt / politika dili,
  - Saldırı **açıklamaları** (saldırıyı anlatan ama uygulamayan),
  - Leksik olarak injection'a benzeyen ama yönlendirmeyen masum.
- **Hedef:** EN benign'e **+3.000–5.000** hedefli hard-neg (mevcut 15k'yı bozmadan, kontrollü).

### 4.3 Türkçe: native-ağırlıklı kal (MT ≤ %30)
- v6.2'de tr benign %73 MT yapıldı → tr recall düştü (%46.7). **Geri al:** tr benign **native-ağırlıklı** (MT ≤ %30).
- `halilneed` doğal Türkçe hard-neg korunur.

### 4.4 Eğitim tarafı: Contrastive + FreeLB
- `FocalTrainer`'a **supervised contrastive loss (w=0.05, temp=0.07)** ve **FreeLB (3 adım)** ekle (Patronus tarzı).
- Amaç: **AUC 0.949 → ≥0.96**, FP düşüşü, genelleme.

### 4.5 Değerlendirme: adil benchmark birincil
- **Birincil metrik:** `heldout_benchmark_v6_fair.json` (jackhhao'suz).
- İkincil: hold-out 15k, `OOD-2000`, `STRESS-1070`.
- **Yapılmayacaklar:** sentetik persona şablonları (sızıntı), 687 etiket-çelişkisini otomatik silme (en zor örnekler), benign'i tek taraflı doldurma.

---

## 5. Diğer Ajan Nereye Bakmalı? (Dosya + Anahtar Değerler)

### 5.1 Eğitim verisi
- **`data/v6_multilingual_supplement.json`** (83.611 kayıt)
  - `label`: {1: 34.063, 0: 49.548}
  - `src`: {mt: 34.063 (saldırılar), native: 23.948}; **MT benign 25.600** (tier=2, src=mt)
  - `language` başına: tr 25.253, ru 4.693, diğer ~6.000
- **`scripts/build_v6_multilingual_supplement.py`**
  - `TGT_BEN_MT` (~satır 30): tr 11.000, ru 200, 9 dil×1.600
  - `build_en_benign_3way()` (~satır 136): hard-neg 4.800 + roleplay 3.600 + genel 3.600
  - `ok()` (~satır 180+): `len<=600`, script/TR kontrolü
  - **v6.3'te:** Arapça native kaynak + hedefli hard-neg + tr MT oranı düşürme buraya eklenecek.

### 5.2 Notebook (veri fabrikası + QC)
- **`notebooks/Master_Dataset_QC_and_Builder_v6.ipynb`**
  - Hücre 2: adil/contaminated benchmark üretimi
  - Hücre 4: MT benign (repo fallback; **EVREN zorunlu** — Colab'da DNS çalışmaz, repo'dan okur)
  - Hücre 5: deterministik kota (satır ~244 `take_deterministic`), şablon budama (`dedup_and_prune_templates`, max_per_prefix=5)
  - Hücre 6: jüri (ProtectAI/Deepset/Patronus) + Qwen judge; **OUT_OF_SCOPE silinir, 687 çelişki SİLİNMEZ**
  - Hücre 7: `train/val/test_v6_clean.parquet` + `qc_audit_report_v6.json`
- **`scripts/build_v6_notebook.py`** (3 eğitim defterinin üreticisi)
  - Cell 4: `EVAL_TEXT_FILES` (BLACKLIST) → `heldout_benchmark_v6.json` dahil
  - Cell 5: deterministik `ATK_NAT/ATK_MT/BEN_NAT/BEN_MT` tablosu (Kural 5) ve `_src` fallback
  - Cell 8: `FocalTrainer` (v6.3'te **contrastive + FreeLB** eklenecek)

### 5.3 Eğitim defterleri (parquet çift-mod)
- **`notebooks/Train_mmBERT_v6.ipynb`**, **`Train_BGE_M3_v6.ipynb`**, **`Train_XLM_RoBERTa_v6.ipynb`**
  - Cell 3: `MASTER_READY` → Drive'dan parquet yüklenir (HF indirme atlanır)
  - Cell 5: parquet varsa atlanır
  - Cell 6: `read_parquet` → train/val/test
  - Cell 12: 3 benchmark (OOD-2000, STRESS-1070, **heldout_v6**)
  - mmBERT: 16×2 batch; BGE: 8×4; XLM-R: 16×2

### 5.4 Benchmark'lar
- **`heldout_benchmark_v6_clean.json`** → **KONTAMİNE** (jackhhao; Patronus bununla eğitilmiş). Sadece iç rapor.
- **`heldout_benchmark_v6_fair.json`** → **BİRİNCİL** (Simsonsun+rubend18/dolly, jackhhao yok). 2.849 örnek.
- **`notebooks/Build_Fair_Benchmark_v6.ipynb`** → adil benchmark + 4 model kıyası (XLM-R, mmBERT, BGE, Patronus).

### 5.5 Anahtar ölçümler (özet)
- v6.2 adil @0.7: mmBERT **74.0/3.8/84.8/0.9494**; Patronus **70.1/0.8/84.2/0.9767**.
- mmBERT hold-out F1 96.8; BGE 97.0; XLM-R 96.15.
- CPU ONNX: mmBERT **8.09 ms/266MB**; BGE **24.27 ms/543MB**.

---

## 6. Hedeflenen Başarı Koşulları (v6.3 kabul kriterleri)

**Birincil (adil benchmark, `heldout_benchmark_v6_fair.json`, th=0.70):**
- [ ] **Macro-F1 ≥ 86.0** (Patronus 84.2'yi geç)
- [ ] **Recall ≥ 75.0**
- [ ] **FP ≤ 2.0**
- [ ] **AUC ≥ 0.960**
- [ ] **Arapça recall ≥ 85** (65'ten)
- [ ] **İngilizce recall ≥ 82** (75.8'den)
- [ ] Türkçe recall ≥ 55, ru FP ≤ 6

**İkincil:**
- [ ] Hold-out (15k) Macro-F1 ≥ 97.0
- [ ] STRESS-1070 FP ≤ 10
- [ ] CPU ONNX gecikme ≤ 10 ms (mmBERT)
- [ ] Sızıntı: benchmark kaynakları ile eğitim kaynakları **0 ortak metin** (BLACKLIST) ve **kaynak-düzeyi ayrık**
- [ ] 687 etiket-çelişkisi: **silinmemiş**, audit raporunda listelenmiş

**Model seçimi:** v6.3 sonrası **mmBERT** şampiyon; BGE-M3 ablasyon; XLM-R baseline. En iyi skoru mmBERT almalı.

---

## 7. Uygulama Sırası ve Süre

1. **Arapça native + EN hedefli hard-neg veri üretimi** (script): ~1 saat
2. **tr MT oranını düşür** (native-ağırlıklı): ~20 dk
3. **Contrastive + FreeLB** trainer güncellemesi: ~1 saat
4. **Yeni parquet** (Master Cell 5-7): ~30 dk
5. **mmBERT retrain** (şampiyon): ~30 dk
6. **Adil benchmark eval**: ~10 dk
7. Kriterler tutarsa → BGE/XLM-R ablation; tutmazsa → hedefli iterasyon

**Toplam (ilk tur):** ~3-3.5 saat

---

## 8. Riskler ve Önlemler

| Risk | Önlem |
|---|---|
| Benign'i aşırı doldurma → recall düşüşü | Hedefli, ölçülü ekleme; native oranı korunur |
| MT motoru asimetrisi (EVREN vs NLLB) | Eğitimde **tek motor (EVREN)**; benchmark NLLB (eğitimden bağımsız) |
| Arapça native kaynak bulunamaması | Aday kaynaklar önce doğrulanır; yoksa sınırlama yazılır |
| Benchmark kontaminasyonu | Kaynak-ayrık tutulur (jackhhao çıkarıldı) |
| Jüri (Qwen) gürültüsü | Yalnızca OUT_OF_SCOPE silinir; çelişkiler loglanır |
| Overfitting (BGE örneği) | Adil benchmark birincil; hold-out tek başına yeterli değil |

---

## 9. Tek Cümlelik Özet (diğer ajan için)
> v6.3'te **Arapça/İngilizce native çeşitlilik** ve **hedefli (roleplay-olmayan) hard-negative** eklenecek, Türkçe native-ağırlıklıya dönecek, mmBERT'e **contrastive+FreeLB** uygulanacak; başarı **adil source-disjoint benchmark'ta F1≥86, ar≥85, AUC≥0.96** ile ölçülecek. Mevcut şampiyon mmBERT (adil F1 84.8), Patronus 84.2 (kontamine benchmark'taki 86.9 sızıntıydı).
