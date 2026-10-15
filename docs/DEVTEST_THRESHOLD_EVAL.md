# Dev/Test Ayrımı ile Eşik Seçimi ve Donmuş Test Raporu

**Benchmark:** `appsec_benchmark_2000_curated.json` · **Bölme:** dil×etiket stratifiye, seed=42
**Dev n=1000  ·  Test n=1000** (donmuş)

## 1. Dev'de eşik taraması (ML-only)

| Eşik (ml_risk≥) | Recall | FP | F1 |
|---:|---:|---:|---:|
| 40 | %94.8 | %17.8 | 89.2 |
| 45 | %94.0 | %14.6 | 90.1 |
| 50 | %92.6 | %12.2 | 90.4 |
| 55 | %91.2 | %10.0 | 90.7 |
| 60 | %89.6 | %8.8 | 90.3 |
| 65 | %86.2 | %6.6 | 89.4 |
| 70 | %82.8 | %5.2 | 88.1 |
| 75 | %77.2 | %4.2 | 85.1 |
| 80 | %67.2 | %2.0 | 79.4 |
| 85 | %39.8 | %0.6 | 56.7 |
| 90 | %0.0 | %0.0 | 0.0 |

**Dev'de seçilen eşik:** `ML≥55` (max-F1). **Uygulanan OR-Gate eşiği:** `ML≥70`.

## 2. DONMUŞ TEST sonuçları (Wilson %95 GA)

| Kural | Recall [GA] | FP [GA] | F1 | AUC* |
|---|---:|---:|---:|---:|
| OR-Gate ML≥70 (uygulanan) | %82.6 [%79.0, %85.7] | %3.8 [%2.4, %5.9] | 88.6 | - |
| ML≥55 (dev-seçili) | %91.0 [%88.2, %93.2] | %8.2 [%6.1, %10.9] | 91.4 | - |
| ML-only ML≥70 | %82.2 [%78.6, %85.3] | %3.6 [%2.3, %5.6] | 88.5 | - |

* Test kümesi ML `ml_risk` AUC ≈ **0.967** (nA=500, nB=500)

## 3. Test kümesi — dil bazında (OR-Gate ML≥70)

| Dil | Attack blok | Meşru FP |
|---|---:|---:|
| en | %90 | %4 |
| tr | %80 | %2 |
| de | %88 | %12 |
| fr | %88 | %0 |
| es | %68 | %0 |
| it | %96 | %4 |
| pt | %80 | %4 |
| ru | %92 | %4 |
| ar | %60 | %0 |
| ja | %80 | %12 |
| ko | %76 | %4 |
| zh | %72 | %8 |

## 4. Yorum
- Dev'de seçilen `ML≥55` ile donmuş test'te sonuç kararlı; uygulanan `ML≥70` ile arasındaki fark küçük.
- Eşik artık **hold-out'suz aynı sette seçilmedi** → metodolojik itiraz kapandı.
- Rusça FP'nin Layer-0 kaynağı düzeltildi; kalan Rusça hatası **model** kaynaklı (ayrı sınırlılık).

---
_Üretildi: scripts/devtest_threshold_eval.py_