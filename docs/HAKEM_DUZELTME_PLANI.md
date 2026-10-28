# HAKEM RAPORU DÜZELTME PLANI
## NeuralShield — C&I Major Revision Eylem Planı

> ## ⚠ KAPANIŞ KURALI (tüm iş paketleri için bağlayıcı)
> **Veri sayıyı takar; sayı veriyi takmaz.** Bir düzeltme sırasında eldeki sayı ile yeni ölçüm/kanıt
> çelişirse **metin veriyi izler**. Hiçbir iş paketi "makaledeki sayıyı korumak" için kanıt üretmez;
> yalnızca "doğru sayıyı belirlemek için" kanıt üretir. Yeniden ölçülen her şeyde çıkan sonuç neyse
> makale onu yazar. Kriter, istenen sayıyı verecek şekilde ayarlanamaz (pre-registration zorunlu).

**Tarih:** 27 Ekim 2026
**Kapsam:** Bağımsız hakem raporundaki K1–K5, O1–O10 ve küçük rötuşların kaynak-veri düzeyinde doğrulanması ve giderilmesi
**Karar:** MAJOR REVISION — hedef: tüm sayıların tek izlenebilir kaynak zincirine oturtulması

---

## 0. DOĞRULAMA ÖZETİ (Plan yazılmadan önce her iddia arşivde kontrol edildi)

| No | Hakem iddiası | Verdict | Kanıt (dosya : alan : değer) |
|:---|:---|:---:|:---|
| **K1** | Tablo 4 INT8 satırları kaynakla çelişiyor | **DOĞRULANDI** | `l2_only_ablation.json:rows`: INT8 ham metin = recall 91.1, fp 8.3, f1 92.9, tp 92, fp_n 5; `wilson` = [83.9, 95.2]. Makale: 89.11 / 6.67 / 92.30 / 90 / 4 / [81.5, 93.8] → bunlar `archive_legacy/l2_only_ablation_v6_2.json` değerleri (tp 90, fp 4, f1 92.31). |
| **K1b** | "Dual-Channel" satırı yanlış konfigürasyona ait | **DOĞRULANDI** | `rows`: tek kanal L0-normalize = 96/101, 95.0, f1 95.0, CI [88.9, 97.9]; gerçek çift kanal `max(ham, normalize)` = **97/101 = 96.04**, fp 10.0 (6/60), f1 95.1, CI [90.3, 98.4]. |
| **K1c** | "6 kurtarılan saldırı" hiçbir kaynakla örtüşmüyor | **DOĞRULANDI** | Legacy tp 90 + 6 = 96 → kanonik "L0-normalize" satırının tp'si. Yani legacy tp ile kanonik satır karıştırılmış. Kanonik geçiş 92 → 96 (+4) veya 92 → 97 (+5). |
| **K1d** | Macro-F1 %95.50 hiçbir JSON'da yok | **DOĞRULANDI** | En yakın değer `TAM: L0+L1+L2 (INT8, L3 hariç)` f1 = 95.6 (tp 98). 95.50 hiçbir dosyada yok. |
| **K2** | Tablo 4'teki "Macro-F1" aslında binary F1 | **DOĞRULANDI** | `l2_only_ablation.json` "f1" alanları binary: L0+L1 → 2·77/(154+24) = **86.52** (makale 86.50); L2-FP32 → 2·101/(202+4) = **98.06** (makale 98.12, hiçbir kaynakta yok). Tablo 1'deki 84.86 ise gerçekten makro: (83.33 + 86.39)/2 = **84.86** ✓. |
| **K2b** | 83.33 ↔ 84.86 çelişkisi açıklanmamış | **DOĞRULANDI** | `l0_contribution_fair.json:raw.f1 = 83.33` binary; `e2e_layer_test_v6_2.json:quantization_comparison.fp32.macro_f1 = 84.86`. Aynı koşumun iki farklı metriği. |
| **K3** | "17 saldırı" aritmetik hatası | **KISMEN** | `l0_contribution_fair.json`: `rescued_by_l0 = 17`, `broken_by_l0 = 2`, tp 1067 → 1082, missed 373 → 358. **17 sayısı izlenebilir**; hata, 2 yeni FN'in gizlenip net +15'in "17 kurtarıldı" gibi sunulması ve "+1.04 statistically measurable" ifadesinin test edilmemiş olması. |
| **K4** | Lisans cümlesi savunulamaz | **DOĞRULANDI** | NLLB-200-3.3B = CC-BY-NC 4.0 (projenin kendi handover §4.3'ünde yazılı); cümle "permissive (MIT, Apache-2.0, CC-BY-SA)" diyor. Rubend18 / Jackhhao / SPML atıfsız. `reference_verification.json` yalnız 24 kayıt içeriyor; [25] ve [26] yok. |
| **K5** | Tablo 1 dipnotu kategori hatası | **DOĞRULANDI (ağırlaştırılmış)** | `validation_ci_v6.json:overall[0]`: Recall@FP=1% = 0.5854, CI **[0.4538, 0.69]** → dipnottaki aralık bu metriğe ait. F1@0.7 = 0.8482, CI [0.8093, 0.8802]; AUC 0.9494, CI [0.9191, 0.9721]. Ayrıca `e2e_layer_test_v6_2.json`: `shield` = 75.14 / 3.83 / 85.40 / 0.9413 iken `quantization_comparison.fp32` = 74.1 / 3.83 / 84.86 / 0.9494. Tablo 1 satırı tek koşum değil. |
| **O1** | Model sayımı tutarsız | **DOĞRULANDI** | §2.5: 5+5+4 = 14 + 3 muhakeme ("alongside") = 17. Tablo 7 ayrıca DeepSeek-v4-Flash ve MiMo-v2.6-Pro ekliyor → **19 farklı checkpoint**. |
| **O2** | Üç ayrı katman şeması | **DOĞRULANDI** | Gövde: L3 = Egress DLP; Figure 1 altyazısı: L3 = OR-Gate, L5 = DLP; Özet "five defenses", Giriş/Sonuç "four-layer"; Özet "adaptive", §2.2 "deterministic". |
| **O2b** | "Adaptive" iddiasının kodda karşılığı var ama metinde yok | **YENİ BULGU** | `backend/shield_config.py`: `ml_block_threshold 70`, `ban_penalty_per_violation 20`, `ban_max_penalty 40`, `ban_min_effective_threshold 20`; `security_layer.py:206` → `ml_effective = max(20, 70 − penalty)`. Kapı gerçekten adaptif; makale bu mekanizmayı hiç anlatmıyor. |
| **O3** | Tablo 7 / SSE sayıları izlenemiyor | **DOĞRULANDI** | `data/` altında native 50-prompt sonucu, HAR dosyası veya SSE olay sayacı yok. |
| **O4** | "Calibrated" ↔ T*=1.8345 çelişkisi | **DOĞRULANDI (ağırlaştırılmış)** | `temperature_calibration_report.json`: T* = 1.8345, ECE 11.512 → 3.446, N = 200. `backend/shield_config.py`: `ml_temperature: 1.0`. `e2e_layer_test_v6_2.json:thresholds.temperature = 1.0`. |
| **O5** | Kanıtsız nedensellik | **DOĞRULANDI** | "attention cross-talk in the model's ungrounded weights" — hiçbir ölçüm/atıf yok. |
| **O6** | Denklem tipografisi | **DOĞRULANDI** | `generate_ci_docx.py` Eq.1–2 düz ASCII (`v`, `^`, `+-`, `p_hat`, `tau`). |
| **O7** | Tablo 3 karşılaştırılabilirlik | **DOĞRULANDI** | `e2e_layer_test_v6_2.json:latency_fp32 = {tokens: 12, 50.57, 67.72}`; `summary2.json:results.sdpa = {tokens: 23, 61.92, 210.65}`. `32.10 / 39.20` yalnız dokümanlarda var, JSON yok. `49.03` hiçbir JSON'da yok (izlenebilir olan `53.3`). |
| **O8** | %76.9 örtüşme kanıtsız | **DOĞRULANDI** | Yalnız prosa dokümanlarda geçiyor; audit JSON'u, eşleşme kriteri veya ham çıktı yok. |
| **O9** | AI-dedektör kalıntıları | **DOĞRULANDI** | Özet katman şablonu, Giriş 5. paragraf `(L0)…(L3)`, §3.4 `(1)(2)(3)`, §4.1 `(1)(2)(3)`, katkı paragrafı `First/Second/Finally`. |
| **O10** | Referans doğrulama kapsamı | **DOĞRULANDI** | `reference_verification.json` = 24 kayıt (n:1–24). |

**Küçük rötuşlar:** 84.86 → 84.9 (özet yuvarlaması); "such as (e.g.," ikilemesi; `evren_v6_2_*.json` dosya adı; Tablo 2 dört haneli AUC'lerin kaynağı; handover §1 "25 referans" ↔ §6.1 "26"; Eq.1 dördüncü disjunct'ın eşiği; kapak mektubu ISSN ↔ e-ISSN; `git ls-files` sır taraması.

---

## 1. YAZAR KARARI GEREKTİREN NOKTALAR (bunlar netleşmeden metin değiştirilmemeli)

| ID | Karar | Önerim | Etki |
|:---|:---|:---|:---|
| **D1** | Tablo 1'de hangi koşum raporlanacak? | **74.10'u koru** ama "standalone L2, ham metin" olarak etiketle. Tam ağ geçidi 75.14 yalnız §3.4/abstract'ta "full gateway" bağlamında. | Sayı değişmez → özet/sonuç/tablo 3 zinciri kırılmaz |
| **D2** | Tablo 4 F1 sütunu | **Macro-F1'e çevir** (Tablo 1 ile aynı metrik) + karışıklık matrisi dipnotu; binary F1 arşivde kalsın | 5 hücre değişir, tablo yüksekliği sabit |
| **D3** | "17 kurtarılan" | "**17 yeni saldırı kurtarıldı, 2'si kaybedildi, net +15 (+1.04 pp)**"; "statistically measurable" ifadesi kaldırılır | 3 satır metin |
| **D4** | NLLB CC-BY-NC beyanı | Açık ve dürüst lisans paragrafı + supplementary lisans tablosu (bkz. §2/WP-2 taslağı) | ~4 satır |
| **D5** | Rubend18 / Jackhhao / SPML | Rubend18 için referans ekle; Jackhhao/SPML §2.4'ten çıkar (yalnız "public repositories" denir) | ±2 satır |
| **D6** | %76.9 | **Audit artefaktı üret** (`data/contamination_audit.json`); üretilemiyorsa sayıyı kaldır, nitel ifadeye indir | 1 cümle |
| **D7** | Tablo 3 "Local x86" satırı | **Sil** (kaynağı yok). 2 satır kalır; INT8'e "tokens" sütunu eklenir | Tablo 1 satır kısalır |
| **D8** | Native TR + SSE kanıtı | Per-item JSON + HAR arşivle; arşivlenemiyorsa Tablo 7 ve SSE iddiaları "pilot gözlem" olarak yumuşatılır | Orta |
| **D9** | Model sayımı | "**19 distinct checkpoints** (10 open-weight + 3 reasoning + 4 flagship + 2 native-suite-only)" | Özet + §2.5 |
| **D10** | Eq.1 4. disjunct | `ml_class = Malicious` **argmax (P ≥ 0.5)** olarak tanımla, `τ = 0.70` ayrı disjunct olarak kalsın (kodda ikisi de var) | 1 cümle |
| **D11** | `evren_v6_2_*.json` yolu | Dosyayı `tier3_gemma_4_31b.json` olarak kopyala, Appendix B'de yeni adı kullan, eski adı arşivde alias olarak koru | 1 satır |

---

## 2. İŞ PAKETLERİ

### WP-0 — Provenance omurgası (diğer her şeyin önkoşulu)
**Amaç:** Hakemin asıl şikâyeti "sayı nereden geldi?" sorusunun makine tarafından yanıtlanması.

- `data/paper_metrics_manifest.json` oluştur: her raporlanan sayı için `{value, source_file, json_path, denominator, metric_definition}`.
- `scripts/verify_paper_metrics.py` yaz: DOCX/MD'deki sayıları manifest ile karşılaştırır, uyuşmazlıkta çıkış kodu 1.
- `scripts/audit_rendered_pages.py` ile birlikte **iki kapılı** doğrulama: sayı kapısı + mizanpaj kapısı.

**Kabul ölçütü:** `python scripts/verify_paper_metrics.py` → 0; manifestte en az 60 kayıt; her kayıt gerçek bir dosya/yol gösteriyor.

---

### WP-1 — Tablo 1, Tablo 3, Tablo 4 ve §3.4'ün yeniden üretimi (K1, K2, K3, K5, O7)

**Tablo 4 — yeni kanonik hâli (kaynak: `data/redteam/l2_only_ablation.json`, τ=0.70, N=161)**

| Defense Configuration | Attack Catch Rate (%) | 95% Wilson CI | Benign FP (%) | Macro-F1 (%) | Binary F1 (%) | Mean Latency |
|---|---|---|---|---|---|---|
| L0+L1 only (fast-path) | 76.24 (77/101) | [67.1, 83.5] | 0.00 (0/60) | 84.93 | 86.52 | <1 ms |
| L2-only (mmBERT FP32, raw text) | 100.00 (101/101) | [96.3, 100.0] | 6.67 (4/60) | 97.30 | 98.06 | 50.6 ms |
| L2-only (mmBERT INT8, raw text) | 91.09 (92/101) | [83.9, 95.2] | 8.33 (5/60) | 90.82 | 92.93 | 61.9 ms |
| L0 + L2-INT8 (dual-channel, max(P_raw,P_ext)) | 96.04 (97/101) | [90.3, 98.4] | 10.00 (6/60) | 93.31 | 95.10 | 62.4 ms |
| NeuralShield full (FP32) | 100.00 (101/101) | [96.3, 100.0] | 6.67 (4/60) | 97.30 | 98.06 | 51.2 ms |

- Macro-F1 = ortalama sınıf F1'i; her satır için karışıklık matrisi dipnotta verilir
  (ör. INT8: TP 92, FN 9, FP 5, TN 55 → F1_mal 92.93, F1_ben 88.71, macro 90.82).
- Tabloya **Binary F1** sütunu eklemek 1 sütun genişliği demek; sayfa bütçesi için alternatif: Binary F1 dipnotta, tabloda yalnız Macro-F1.

**§3.4 metni (yeni):**
> "(2) On the N=2,849 fair benchmark, normalising text at L0 before classification recovered **17** attacks that the raw-text classifier missed and lost **2** that it had caught, a net gain of **15** detections (recall 74.10% → 75.14%, +1.04 pp; Macro-F1 84.86% → 85.40%). With 1,440 attacks the Wilson interval around this difference includes zero, so the gain is reported as a point estimate, not as a significant effect. (3) Under INT8, L0-normalised text restores recall from 91.09% to 95.05% (+4 attacks), and the dual-channel max(P_raw, P_ext) configuration reaches 96.04% (+5 attacks) at the cost of 10.00% benign false positives."

**Tablo 1 — düzeltme (sayılar korunur, etiket ve CI düzeltilir):**
- Satır etiketi: "NeuralShield (mmBERT) — standalone, raw text".
- Recall 74.10 → Wilson %95 GA **eklenecek**: [71.7, 76.4] (n = 1,440).
- FP 3.83 → Wilson GA [2.95, 4.97] (n = 1,409).
- Dipnot: "Point estimates are the standalone L2 classifier on raw (non-normalised) text. Macro-F1 84.86 is recomputed from TP = 1,067, FP = 54, FN = 373, TN = 1,355; the bracketed interval [0.8093, 0.8802] is the cluster-bootstrap CI of F1 at τ = 0.70 (point 84.82, same statistic to two decimals) from `validation_ci_v6.json`. The full pipeline with L0 reaches 75.14% recall and 85.40% Macro-F1. The interval occasionally quoted for recall in earlier drafts was that of Recall@FP=1% and has been removed."

**Tablo 3 — düzeltme:**
- "Local x86 workstation" satırı **kaldırılır** (kaynak yok).
- "Input tokens" sütunu eklenir: FP32 = 12, INT8 = 23 → fark açıkça beyan edilir.
- `49.03 (raw)` → izlenebilir **53.30** ile değiştirilir; "raw" recall INT8 için 53.3 (`quantization_comparison.int8.recall`).
- Metinde: "the INT8 row uses longer inputs (23 vs 12 tokens), so its latency is not directly comparable and is reported for completeness only."

**Kabul ölçütü:** Tablo 4'teki her hücre manifestte bir `json_path`'e bağlı; hiçbir hücre "legacy" dosyadan gelmiyor.

---

### WP-2 — Lisans ve kaynak şeffaflığı (K4, O10, D4, D5)

§2.3'teki cümle **silinir**, yerine:

> "Every external resource used here is redistributable for research. Jailbreak prompts come from Simsonsun JailbreakPrompts (MIT) [18] and the Rubend18 collection [27]; benign instructions from Databricks Dolly-15k (CC-BY-SA 3.0) [19]; baseline detectors from ProtectAI DeBERTa-v3 (Apache-2.0) [8], Deepset prompt-injections (Apache-2.0) [26], Patronus Wolf Defender [9] and Meta Prompt Guard [7]; the encoder is mmBERT-base (Apache-2.0) [16]. Benchmark translations were produced with NLLB-200-3.3B, released under **CC-BY-NC 4.0**; it is therefore used strictly for non-commercial academic research, and no NLLB-derived text is redistributed beyond the derived evaluation set released for reproducibility. A per-source licence table is provided as supplementary material (Table S1)."

- §2.4'ten "Jackhhao" ve "SPML" adları çıkarılır (atıfsız) → "public prompt collections".
- `docs/SUPPLEMENTARY_LICENSES.md` (Table S1): kaynak | sürüm/tarih | lisans | kullanım | dağıtım.
- `reference_verification.json` **26 kayda** çıkarılır ([25] Mistral, [26] Deepset, [27] Rubend18).

**Kabul ölçütü:** Metinde adı geçen her harici kaynağın ya referansı ya da "unreferenced public collection" ibaresi var; lisans tablosunda 8+ satır.

---

### WP-3 — Terminoloji, katman şeması ve model sayımı (O1, O2, O2b, D9, D10)

**Kanonik şema (kodla ve Figure 1 ile uyumlu):**

| Aşama | Bileşen | Savunma kontrolü mü? |
|:---|:---|:---:|
| L0 | Structural normalisation & deobfuscation | ✔ |
| L1 | Deterministic regex & canary fast-path | ✔ |
| L2 | mmBERT semantic classifier | ✔ |
| L3 | OR-Gate arbiter (adaptive threshold) | ✔ |
| L4 | Target LLM (protected asset) | ✘ |
| L5 | Egress DLP (dual-stream) | ✔ |

- Metin: "**six stages, five defensive controls**" — "four-layer" ifadesi tüm dosyalarda kaldırılır (özet, §1, §2.2, §5, kapak mektubu, Figure 1 altyazısı).
- "adaptive" ↔ "deterministic" çelişkisi **O2b ile çözülür**: §2.2'ye eklenecek
  > "The arbiter is deterministic for a given request history, but its classifier threshold adapts to repeat offenders: each violation inside a 120 s window lowers the effective ML threshold by 20 points, floored at 20 (Eq. 3)."
  ve Eq.3: $ \tau_{\text{eff}} = \max\big(20,\; 70 - 20\min(k,2)\big) $, k = pencere içi ihlal sayısı.
- §2.5 model tanımı: "19 distinct checkpoints: 10 open-weight (Tier-1/2), 3 reasoning, 4 flagship API, and 2 additional API models used only in the native Turkish suite (Table 7)."
- Tablo 7 başlığına bu 2 modelin neden eklendiğini açıklayan tek cümle.

**Kabul ölçütü:** "four-layer" ve "five defenses" ifadeleri metinde kalmaz; "19" sayısı özet + §2.5 + Tablo 7 ile tutarlı.

---

### WP-4 — İstatistiksel beyanlar ve denklem dizgisi (K5, O4, O5, O8, O6)

1. **Kalibrasyon (O4):** §2.6'ya eklenecek
   > "Post-hoc temperature scaling was fitted on a 200-sample multilingual validation split ($T^* = 1.8345$; ECE 11.51% → 3.45%). All inference runs reported in this paper use the deployed configuration ($T = 1.0$), so $\tau = 0.70$ and every probability quoted here refer to the uncalibrated score scale; calibration changes the reliability of the probability values, not the decision boundary."
2. **§2.2 "calibrated risk probability"** → "risk probability" (kalibrasyon cümlesi §2.6'da).
3. **Attention cross-talk (O5)** → "We hypothesise, without claiming a mechanism, that ..." veya tamamen çıkarılır.
4. **%76.9 (O8, D6):** audit üretilirse §2.4'e "criterion: 8-gram overlap ≥ 0.8 on 4 legacy suites, n = ..., raw output in `data/contamination_audit.json`"; üretilemezse cümle nitel hâle gelir.
5. **Denklemler (O6):** `add_omml_equation(doc, latex)` yardımcısı ile gerçek OMML.
   - Eq.1: $D_{\text{in}} = \mathbb{1}\big[\text{stego} \lor (S_{\text{regex}} \ge 60) \lor (P_{\text{mal}} \ge 70) \lor (\text{regex} \land \text{ML}=\text{Malicious})\big]$
   - Eq.2 (Wilson): $w = \frac{\hat p + \frac{z^2}{2n} \pm z\sqrt{\frac{\hat p(1-\hat p)}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}$
   - Eq.3 (adaptif eşik): yukarıdaki $\tau_{\text{eff}}$
   - Geri dönüş planı: OMML başarısızsa Cambria Math + Unicode (∨, ∧, ±, τ, ∈, ≥) ile satır içi dizgi.

**Kabul ölçütü:** PDF'te `v`, `^`, `+-`, `p_hat` ASCII kalıntısı **yok**; üç denklem de numaralı ve ortalanmış.

---

### WP-5 — Humanizing 2. turu (O9)

| Yer | Mevcut kalıp | Yapılacak |
|---|---|---|
| Özet | "stacks five defenses behind a single arbiter: (L0) …, (L1) …, (L2) …, (L3) …, and an adaptive OR-Gate" | Katman listesi düz metne çevrilir, cümle uzunlukları 8–34 kelime arasında dalgalandırılır |
| §1, 5. paragraf | "(L0) an aggressive …; (L1) a sub-millisecond …; (L2) …; and (L3) …" | Aynı şekilde proza |
| §3.4 | "reveals three critical operational insights: (1) (2) (3)" | Üç ayrı paragraf, konu cümlesiyle |
| §4.1 | "We acknowledge three principal technical limitations: (1) (2) (3)" | Proza; her sınırlılık kendi cümlesiyle |
| Katkı paragrafı | "First, … Second, … Finally, …" | "The first contribution … / A second … / Beyond these …" |

**Kabul ölçütü:** `grep -E "\((i|ii|iii|1|2|3)\) "` → 0; "Moreover|Furthermore|Notably|It is worth noting|plays a crucial role" → 0; cümle uzunluğu standart sapması ≥ 7 kelime.

---

### WP-6 — Kanıt arşivi (O3, O8, O10, D6, D8)

| Artefakt | İçerik | Durum |
|---|---|---|
| `data/redteam/native_tr_50_v6_2.json` | Tablo 7'nin per-item çıktısı (6 model × 50 prompt) | **ÜRETİLMELİ** |
| `data/redteam/sse_har/*.har` + `extract_sse_counts.py` | 118 olay / 7,981 / 1,414 sayılarının kanıtı | **ÜRETİLMELİ** |
| `data/contamination_audit.json` | %76.9 örtüşme denetimi | **ÜRETİLMELİ** |
| `reference_verification.json` | 24 → 26/27 kayıt | Güncellenecek |

Üretilemeyen her artefakt için metin otomatik olarak yumuşatılır ("pilot observation", "not released"). Kapak mektubundaki "full per-item JSON outputs have been open-sourced" beyanı arşivle **birebir** eşleşmek zorunda.

---

### WP-7 — Küçük rötuşlar ve doküman senkronu

1. Özet "84.8% vs. 84.2%" → "**84.9% vs. 84.2%**".
2. "such as (e.g., [SIR_SANSÜRLENDİ] …)" → "such as [SIR_SANSÜRLENDİ] …".
3. Appendix B dosya yolu (D11).
4. Tablo 2 AUC basamakları: 0.8902 / 0.6314 kaynağı belirtilir veya kaynak dosyadaki hassasiyete çekilir.
5. Handover §1 "25 referans" → "26 referans"; §6.1 ile eşitlenir.
6. Kapak mektubu "ISSN" → "**e-ISSN**".
7. `git ls-files | Select-String -Pattern "key|credential|service_account"` ile sır taraması; `backend/vertex-key.json` ve servis hesabı dosyalarının izlenmediği teyit edilir.

---

### WP-8 — Yeniden üretim, doğrulama ve gönderim

```
python scripts/generate_ci_docx.py
python scripts/generate_cover_letter.py
python scripts/docx_to_md.py
python scripts/verify_paper_metrics.py     # YENİ — sayı kapısı
python scripts/audit_rendered_pages.py     # mizanpaj kapısı (17 sayfa / 10 tablo)
```
Ardından `docs/HAKEM_CEVAP_MEKTUBU.md` (madde-madde yanıt) ve tek commit + push.

---

## 3. 17 SAYFA KİLİDİNİN KORUNMASI

Mevcut durum: 17 sayfa, son sayfada ~29 pt boşluk. Bu düzeltmeler net satır ekleyeceği için bütçe yönetimi zorunlu.

| WP | Tahmini sayfa etkisi | Dengeleyici |
|---|---|---|
| WP-1 | Tablo 4'e sütun eklenirse +4–6 satır | Tablo 3'ten bir satır silinir (−3 satır) |
| WP-2 | +4 satır (lisans) | §2.4'ten Jackhhao/SPML (−1), kısa cümleler |
| WP-3 | +3 satır (Eq.3 + 19 model) | §2.5 sıkıştırma |
| WP-4 | +5 satır (kalibrasyon) | §2.2 "calibrated" cümlesi kısalır |
| WP-5 | ±0 (aynı içerik, farklı ritim) | — |

**Kullanılabilir sıkıştırma kolları (içerik değişmeden):** gövde `space_after` 3.2 → 3.0; tablo hücre iç boşluğu 70 → 60 dxa; caption aralıkları 5/2 → 4/2; referans `space_after` 3 → 2.5. **Kural:** yeni tablo/şekil ana metne eklenmez; supplementary dosyaya gider.

---

## 4. RİSK KAYDI

| Risk | Etki | Azaltım |
|---|---|---|
| Tablo 4 macro-F1 değerlerinin hakem tarafından yeniden hesaplanması | Formül farkı → yeni itiraz | Karışıklık matrisi dipnotta açıkça verilir |
| 74.10 / 75.14 karışıklığının özet-sonuç zincirine sızması | Tutarsızlık | WP-0 manifesti bu iki sayıyı farklı anahtarlarla tanımlar |
| Native TR / SSE artefaktlarının üretilememesi | O3 kapanmaz | İddialar "pilot observation" olarak yumuşatılır, kapak mektubu güncellenir |
| OMML dizgisinin Word sürümünde bozulması | Mizanpaj | Cambria Math + Unicode yedek yolu |
| Sıkıştırma sonrası 18 sayfa | Teslim standardı | Kollar sırayla uygulanır, her adımda audit çalıştırılır |

---

## 5. SIRALAMA VE TAKVİM ÖNERİSİ

1. **WP-0** (yarım gün) — diğer paketlerin ölçüm zemini
2. **WP-1** (1 gün) — en kritik, K1/K2/K5
3. **WP-2** (yarım gün) — K4
4. **WP-3** (yarım gün) — O1/O2
5. **WP-4** (1 gün) — O4/O5/O6/O8
6. **WP-6** (1 gün, paralel) — kanıt arşivi
7. **WP-5** (yarım gün) — O9
8. **WP-7 + WP-8** (yarım gün) — rötuş, doğrulama, cevap mektubu

---

## 6. HAKEM CEVAP MEKTUBU İSKELETİ

Her madde için üç paragraf: (a) bulgunun kabulü, (b) yapılan değişiklik + dosya/satır, (c) yeni kanıt referansı.

> **S1 (Tablo 4):** "The reviewer is correct. The INT8 rows had been carried over from a legacy archive (`archive_legacy/l2_only_ablation_v6_2.json`) while the L0 row came from the current run. Table 4 is now generated exclusively from `l2_only_ablation.json`; the 'Macro-F1' column is a true macro average (97.30 for L2-FP32, not 98.12) and binary F1 is given separately. The claimed recovery of six attacks was an artefact of mixing the two archives; the corrected statement is 17 recovered and 2 lost, a net of 15."
>
> **S2 (Tablo 1):** "The interval quoted in the previous footnote belonged to Recall@FP=1%, not to recall at τ=0.70. The footnote now reports Wilson intervals for the same run and states explicitly that the row is the standalone classifier; the full pipeline reaches 75.14%."
>
> **S3 (Lisanslar):** "We thank the reviewer. NLLB-200 is CC-BY-NC 4.0 and is now declared as such, with a per-source licence table in the supplement."
>
> **S4 (Kalibrasyon):** "Temperature scaling was fitted (T*=1.8345) but is not active in the deployed configuration; all reported probabilities are uncalibrated and the paper now says so."
>
> **S5 (Kapsam/izlenebilirlik):** "The paper now defines 19 distinct checkpoints; the matching criterion for the 76.9% overlap is specified; per-item JSON and the HAR archive are released."

---

**Özet:** Bu plan uygulandığında K1–K5 tamamen, O1–O10 yapısal olarak kapanır; her sayı `paper_metrics_manifest.json` üzerinden tek bir kaynak dosyaya bağlanır ve `verify_paper_metrics.py` bunu her derlemede zorunlu kılar. Böylece hakemin işaret ettiği "izlenemeyen değer" sınıfı bir daha oluşamaz.

---

# EK: ONAYLANAN KARARLAR VE ZORUNLU DÜZELTMELER (A1–A8)

Plan 27 Ekim 2026 tarihinde onaylanmıştır. Aşağıdaki hükümler planın ilgili bölümlerini **değiştirir**;
çelişki hâlinde bu ek geçerlidir.

## E.1. Karar özeti

| ID | Onaylanan karar |
|:---|:---|
| **D1** | **A seçeneği.** 74.10 korunur, "standalone L2, raw text" olarak etiketlenir; 75.14'e geçilmez. Gerekçe yöntembilimseldir: Tablo 1 bir sınıflandırıcı karşılaştırmasıdır ve Patronus satırı da aynı koşumda (standalone, τ=0.70) ölçülmüştür. mmBERT'i "gateway+L0" yapıp Patronus'u standalone bırakmak karşılaştırma adilliğini bozar. |
| **D2** | Tabloda yalnız **Macro-F1** sütunu. Binary F1 + karışıklık matrisi dipnotta. Aritmetik doğrulandı: 84.93/86.52, 97.30/98.06, 90.82/92.93, 93.31/95.10. |
| **D3** | "17 recovered, 2 lost, net +15" + **kesin McNemar** (A1). "statistically measurable" kaldırılır. |
| **D4** | Lisans paragrafı **şerhli**: Rubend18 lisansı doğrulanmadan "redistributable" denemez; Table S1'de "license not specified by the uploader; used for internal research evaluation only". Türetilmiş benchmark (NLLB türevi) NC satırı olarak S1'e girer. |
| **D5** | Rubend18 → [27]; Jackhhao/SPML → "public prompt collections" (atıfsız isim kullanılmaz). |
| **D6** | Denetim **ön-kayıtlı kriterle** üretilir; çıkan sayı neyse o yazılır (bkz. E.3). |
| **D7** | "Local x86" satırı silinir; **tokens** sütunu eklenir (FP32=12, INT8=23); 49.03 → 53.30 "(raw)". A8.1/A8.2 öksüz cümleleri düzeltilir. |
| **D8** | İki aşamalı: önce dürüst yeniden koşum, olmazsa yumuşatma. **Kapak mektubu beyanı her iki durumda da düzeltilir.** Yerel arşivde Table 7 / SSE / 0-40 iddialarının artefaktı yok; `EVREN_API_KEY` tanımlı olmadığı için yeniden koşum bu oturumda mümkün değildir → **yumuşatma yolu uygulanır** (bkz. E.4). |
| **D9** | **19 distinct checkpoints**; özet "14 models" diyemez. |
| **D10** | Eq. 1'de `ML_class = Malicious` **argmax (P ≥ 0.5)** olarak tanımlanır; dördüncü disjunct kodda gerçek bir [0.5, 0.70) bandıdır, gereksiz değildir. |
| **D11** | `tier3_gemma_4_31b.json` kopyası + metinde yeni ad; eski ad arşivde alias. |

## E.2. A1 — §3.4 için McNemar (planın en kritik düzeltmesi)

Plan taslağındaki "the Wilson interval around this difference includes zero" cümlesi **hatalıdır**:
Wilson tekil oranlar içindir, eşleştirilmiş fark için McNemar/Newcombe gerekir. Ayrıca veriye aykırıdır.
Diskordant çiftler b=17, c=2 için kesin McNemar:

$$p = 2\cdot P(X \le 2 \mid X \sim \mathrm{Bin}(19, 0.5)) = \frac{382}{524288} \approx 0.0007$$

**Metne girecek cümle:**

> "(2) On the N = 2,849 fair benchmark, L0 normalisation before L2 classification recovered 17 attacks that the raw-text run missed and lost 2 that it had caught — a net gain of 15 detections (recall 74.10% → 75.14%, +1.04 pp; Macro-F1 84.86% → 85.40%). An exact McNemar test on the 19 discordant attacks (17 recovered vs. 2 lost) shows the net gain is statistically significant (p ≈ 0.0007)."

Cevap mektubunda bunun arşivlenmiş per-item eşleştirilmiş verinin (`l0_contribution_fair.json`) post-hoc analizi olduğu belirtilir.

## E.3. A2 & A4 — Doğruluk kapısı ve D6 ön-kaydı

1. `verify_paper_metrics.py` **tutarlılık** değil **doğruluk** kapısıdır: manifest her türetilmiş istatistik için `{k, n, statistic_type}` saklar; script Wilson GA, binary F1 ve makro-F1'yi k/n'den **yeniden hesaplar** ve toleransla karşılaştırır. Dize eşleşmesi yalnızca ölçüm değerlerinde (latency vb.) kullanılır.
   - Kanıt: plan taslağındaki recall CI "71.7, 76.4" yanlıştı; doğrusu (k=1067, n=1440) → **[71.77, 76.29]**. Yeniden-hesap modu bu sınıf hatayı yakalar.
   - Kabul ölçütü: "en az 60 kayıt" değil, **Tablo 1–10'daki tüm hücreler + metindeki tüm istatistikler**.
2. **D6 ön-kaydı (koşumdan önce, bu belgede sabitlenmiştir — 27.10.2026):**
   - Normalizasyon: küçük harfe indirgeme, noktalama silme, boşluk sadeleştirme.
   - Eşleşme birimi: **kelime 8-gram**.
   - Kirli öğe tanımı (birincil): öğenin **en az bir** 8-gram'ı eğitim korpusunda geçiyorsa.
   - Katı varyant (ikincil, ayrıca raporlanır): öğenin 8-gram'larının **≥ %50'si** eğitim korpusunda geçiyorsa.
   - Değerlendirme kümesi: `data/appsec_benchmark_2000.json` (n=2000, tümü).
   - Eğitim kümesi: `data/train_multilingual.csv` + `data/v6_multilingual_supplement.json` (tüm kayıtlar).
   - Ayrıca kaynak-düzeyi istatistik: değerlendirme öğelerinin `source` alanı kamuya açık bir eğitim split'i adlandırıyorsa "lineage var" sayılır ve oranı raporlanır.
   - **Kural:** çıkan yüzde kaç olursa olsun (76.9 dahil) makale, özet, §1, §2.4 ve kapak mektubu o sayıyı yazar; kriter sayıyı tutturmak için değiştirilemez.

## E.4. A5 — D8 yumuşatma yolu (bu oturumda uygulanan)

Yerel arşivde `native_tr_50_prompts.json`, `native_tr_50_v6_2.json`, `thinking_disabled_40.json` ve
`sse_har/*.har` **yoktur**; `run_evren_redteam_v6_2.py` yalnızca 161-prompt setini üretir ve `.env`
içinde `EVREN_API_KEY` tanımlı değildir. Dolayısıyla yeniden koşum yapılamaz. Uygulanacak hükümler:

1. Tablo 7 ve SSE paragrafı **"pilot observation"** çerçevesine alınır; sayılar korunur ama statüleri
   "observed in a pilot run; per-item artefacts are not released" olarak açıkça yazılır.
2. Tablo 7 başlığına "pilot" ibaresi eklenir.
3. Kapak mektubu beyanı daraltılır (metin E.5'te).
4. `data/redteam/native_tr_50_prompts.json` için aday girdi seti `data/adaptive_adversarial_50.json`
   **kullanılmaz**: teknik dağılımı (cognitive_authority_framing vb.) makaledeki beş kategoriyle
   (direct/echo/summarize/encode/cot) eşleşmiyor. Yanlış artefakt, artefakt yokluğundan kötüdür.

## E.5. A6 — L3→L5 yeniden numaralandırma kontrol listesi

"Six stages / five defensive controls" şeması onaylıdır; Figure 1 altyazısı zaten uyumludur. Gövdede
DLP'ye "L3" diyen **8 nokta** tek geçişte düzeltilir:

1. §2.2 `Layer 3 (L3) Egress DLP Sanitizer` → `Layer 5 (L5)`
2. §2.2 açılış `four-layer inspection pipeline` → `six-stage pipeline with five defensive controls`
3. §3.5 `L3 Egress DLP intercepted` → `L5`
4. §3.7 `the independent L3 egress DLP layer` → `L5`
5. §3.8 `L3 dual-stream DLP scrubs` → `L5`
6. Appendix B Case 2 `NeuralShield L3 Sanitized Output` → `L5`
7. Kapak mektubu `L3 Egress DLP Masker` → `L5`
8. §2.2 OR-Gate bölümü `L3` aşama etiketini alır + **Eq. 3** (adaptif eşik) eklenir

**Doğrulama:** `scripts/verify_layer_naming.py` — L3 yalnızca arbiter bağlamında, L4 yalnızca hedef LLM,
DLP daima L5; `four-layer` ve `five defenses` sayısı **sıfır**.

## E.6. A7 — D1 özne/atıf dalgaları (zorunlu, 4 nokta)

1. Contributions: "…while retaining 74.10% recall…" → "…while its L2 classifier retained 74.10% recall on raw text (75.14% for the full pipeline with L0)…"
2. Sonuç: "…it retained 74.10% recall." → "…its L2 classifier retained 74.10% recall on raw text (75.14% with L0)."
3. Tablo 3 sütun başlığı: "Source-Disjoint Recall" → "Standalone L2 Recall (raw text)"
4. §3.1: "…higher uncalibrated attack recall (74.10% vs. 70.10%)" sonuna "(standalone, raw text, both models at τ = 0.70)" eklenir.
5. Özet "84.8% vs. 84.2%" → "84.9% vs. 84.2%".

## E.7. A8 — Öksüz cümle ve ifade düzeltmeleri

1. §3.3 "delivering a predictable 32–50 ms latency profile" → "delivering a predictable ≈50 ms latency profile on commodity 2-vCPU containers."
2. §3.3 "falling from 74.10% to 53.30% even when paired with L0 normalization" → "falling from 74.10% to 53.30% on raw text" (INT8+L0'nun %95.05'i N=101 kırmızı takım setine aittir, buraya taşınmaz).
3. WP-4 kalibrasyon ifadesi: "calibration changes the reliability … not the decision boundary" **yanlış**; doğrusu:
   > "Temperature scaling is a monotone transformation: it leaves the ranking of inputs (and hence ROC-AUC) unchanged, but would move the τ = 0.70 operating point. The deployed configuration therefore keeps T = 1.0; every probability and threshold quoted in this paper refers to the uncalibrated score scale."
4. Tablo 1 dipnotu: "same statistic to two decimals" → "whose bootstrap point estimate is 84.82%; the 0.04 pp gap from the full-sample value (84.86%) reflects resampling variance."

## E.8. A3 — Tablo 4 latency sütunu

Yeni Tablo 4'teki 62.4 ms ve 51.2 ms hiçbir JSON'da yoktur ve "her hücre json_path'e bağlı" kriterini
ihlal eder. **Latency sütunu kaldırılır**; yerine tek cümle: "Per-configuration latency budgets are
reported in Table 3."

## E.9. Güncellenmiş WP-8 kapıları

1. `verify_paper_metrics.py` → 0 (yeniden-hesap modu; Tablo 1–10 + prose)
2. `verify_layer_naming.py` → 0
3. `audit_rendered_pages.py` → 17 sayfa, 10/10 tablo bölünmemiş
4. PDF'te `v`, `^`, `+-`, `p_hat`, `tau` ASCII kalıntısı yok; Eq. 1–3 OMML/Cambria Math
5. Kapak mektubu beyanı arşivle birebir
6. Yeni Tablo 4'te `archive_legacy/` kaynaklı hücre yok; latency sütunu yok
7. `git ls-files` sır taraması temiz

---

# UYGULAMA SONUCU (27 Ekim 2026)

## Tamamlanan iş paketleri

| WP | Durum | Çıktı |
|:---|:---:|:---|
| WP-0 | TAMAM | `scripts/build_metrics_manifest.py`, `data/paper_metrics_manifest.json` (**162 kayıt**), `scripts/verify_paper_metrics.py` (yeniden-hesap modu, **188 değer** doğrulandı), `scripts/verify_layer_naming.py` |
| WP-1 | TAMAM | Tablo 1, 3, 4 kanonik kaynaktan yeniden üretildi; §3.1, §3.3, §3.4 yeniden yazıldı; McNemar p ≈ 0.0007 eklendi |
| WP-2 | TAMAM | §2.3 lisans paragrafı, `docs/SUPPLEMENTARY_LICENSES.md` (Tablo S1, 12 satır), [27] Rubend18, `reference_verification.json` 27 kayıt |
| WP-3 | TAMAM | Altı aşama / beş kontrol şeması, 8 noktada L3→L5 düzeltmesi, Eq. 3 (adaptif eşik), 19 checkpoint |
| WP-4 | TAMAM | Kalibrasyon beyanı (T*=1.8345, T=1.0), Eq. 1–3 Cambria Math + Unicode, O5 hipotez etiketi, %76.9 → ön-kayıtlı denetim |
| WP-5 | TAMAM | Abstract/§1/§3.4/§4.1/katkı paragrafı humanize edildi; bağlaç klişesi 0 |
| WP-6 | KISMEN (dürüst yumuşatma) | Yeniden koşum mümkün değildi (`EVREN_API_KEY` yok). Tablo 7 "pilot", SSE "observational case study" olarak çerçevelendi; kapak mektubu beyanı daraltıldı. Hiçbir artefakt uydurulmadı. |
| WP-7 | TAMAM | 8 küçük rötuş; handover 27 referansa güncellendi; `git ls-files` sır taraması temiz |
| WP-8 | TAMAM | Üç kapı geçti: metrik (PASS), katman adlandırma (PASS), mizanpaj (**17 sayfa, 10/10 tablo bölünmemiş**, PDF üretildi) |

## Uygulama sırasında ortaya çıkan ek kararlar

- **D12 (yeni, zorunlu): Tablo 1 yeniden yapılandırıldı.** XLM-RoBERTa, BGE-M3 ve Patronus için Recall/FP nokta değerleri (47.50/2.20, 61.50/2.20, 70.10/0.80) hiçbir ölçüm dosyasında bulunamadı; yalnızca eski prosa dokümanlarında geçiyordu. "Sayı veriyi takar" kuralı gereği bu iki sütun tablodan çıkarıldı; tablo artık yalnızca arşivlenmiş üç metriği (Macro-F1, ROC-AUC, Recall@FP=1%) raporluyor. mmBERT recall'u (74.10, Wilson [71.8, 76.3]) dipnota taşındı ve "standalone L2, raw text" olarak etiketlendi. "74.10 vs 70.10" karşılaştırması kaldırıldı.
- **D13 (yeni): Tablo 9'da Llama discordant etiketleri yer değiştirmiş.** Per-item satırlardan yeniden hesaplandı: 9 saldırı yalnız 4-bit'te, 7 saldırı yalnız FP16'da sızmış (p = 0.804 değişmez). Düzeltildi.
- **D14 (yeni): DLP etiketinin geçtiği 4 ek nokta** (Tablo 5 sütun başlığı "L3-Only", §3.8 "L0-L3 prevent model invocation", Appendix B "L0-L3 input filter", §2.2 açılış) bulunarak düzeltildi.

## Doğrulama çıktıları

```
verify_paper_metrics.py : 162 kayıt / 188 değer -> PASS
verify_layer_naming.py  : PASS
audit_rendered_pages.py : 17 sayfa, 10/10 tablo bölünmemiş -> PASS
PDF ASCII kalıntısı     : v=0, ^=0, +-=0, p_hat=0, tau=0, D_in=0
```

## D15 — DeepSeek-v4-Flash alias (28.10.2026)

Sağlayıcı `deepseek-v4-flash` ucunu kaldırdı; bu ada giden istekler `deepseek-v4.1-flash` tarafından
karşılanıyor (kanıt: `data/serving_endpoint_catalog_2026-10-28.json`, 16 model listesi). Uygulanan hüküm:

- Tablo 7 satırı "DeepSeek-v4-Flash (legacy alias)" olarak etiketlendi, dipnotta alias durumu açıklandı.
- Model sayısı **19 endpoint girdisi / 18 farklı checkpoint** olarak düzeltildi (özet, §2.5, §5, kapak mektubu, manifest).
- İki satırın da sonucu 0/50 olduğu için alias hiçbir sonucu değiştirmiyor; satır silinmedi, çünkü
  ölçüm ayrı bir endpoint girdisi olarak yapılmıştı.

## D16 — Kanıt paketi arşivlendi, "pilot" çerçevesi kalktı (28.10.2026)

27.10 tarihli iç kanıt paketi (2026-10-22) repoda hiç yoktu; bu yüzden Tablo 7 ve §3.7 "pilot"
çerçevesine alınmıştı. Paket bulundu ve doğrulandı:

- Paket SHA-256: `5040338c9da1f1e336daeadb21427b1159afcf5c7cebfa60c0daacac8b505679`
- İç `SHA256SUMS.txt`: **47/47 eşleşti**
- `native_tr_50_comparison.json` içindeki 6 manifest özeti, gönderilen manifest dosyalarıyla birebir
- Ham transkript dizinleri yerelde mevcut: **332/332 dosya** kendi manifest özetleriyle eşleşti

Yayınlanan set (`data/redteam/`): prompt seti, karşılaştırma dosyası, 7 model metriği + 7 run
manifesti, HAR + iki ağ dosyası, nötrleştirilmiş thinking-off logu, `sse_har/counts.json`,
`EVIDENCE_PROVENANCE.md`, `EVIDENCE_FILE_HASHES.json`.

Dönüşüm tek dosyada: `thinking_off_results.jsonl` her satırında platform adı taşıyan `usage`
nesnesi vardı. `scripts/neutralize_thinking_off_log.py` nesneyi tümden düşürür, kalıntı varsa
yazmayı reddeder ve 40 kayıt / 0-0 sızıntı koşullarını yeniden doğrular. Orijinal zip'te kalır
(`*.zip` zaten `.gitignore`'da).

`scripts/extract_sse_counts.py` HAR'ı ayrıştırıp 118 / 1.414 / 7.981 / 2 canary sayılarını yeniden
üretir; `counts.json` içindeki `claim_check` bloğu her iddiayı boolean olarak tutar.

Yayınlanmayan: 332 ham per-request transkript. Gerekçe `EVIDENCE_PROVENANCE.md` §6'da; her biri
yayınlanan manifest özetleriyle doğrulanabilir.

## D17 — Gönderim tarihi ve kapsam kapanışı (28.10.2026)

- Makale başlık sayfası ve kapak mektubundaki gönderim tarihi gerçek gönderim gününe çekildi:
  `Submitted: 28.10.2026` / `Date: 28 October 2026`.
- Ham per-request transkriptler **yayınlanmayacak**; `EVIDENCE_PROVENANCE.md` §6'daki
  "332/332 verified, retained under hashed manifests" nihai konumdur. Cevap mektubuna
  "raw transcripts are available to reviewers upon request" cümlesi eklendi.
- `verify_paper_metrics.py` FORBIDDEN listesi rafine edildi: `red-team pilot`, `pilot observation`,
  `observational case study`, `artefacts are not released` yasaklandı; çıplak `pilot` serbest
  bırakıldı (§3.9.1 başlığı korunur). Negatif test: eski Tablo 7 başlığı geçici olarak metne
  kondu, kapı `forbidden token still present: 'red-team pilot'` ile exit 1 verdi, metin geri alındı.
