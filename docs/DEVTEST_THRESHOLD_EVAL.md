# Dev/Test Ayrımı ile Eşik Seçimi ve Donmuş Test Raporu

**Benchmark:** `appsec_benchmark_2000_curated.json` · **Bölme:** dil×etiket stratifiye, seed=42
**Dev n=1000  ·  Test n=1000** (donmuş)

## 1. Dev'de eşik taraması (ML-only)

| Eşik (ml_risk≥) | Recall | FP | F1 |
|---:|---:|---:|---:|
| 40 | %89.2 | %26.6 | 82.7 |
| 45 | %86.6 | %22.6 | 82.8 |
| 50 | %85.2 | %19.4 | 83.3 |
| 55 | %83.4 | %16.4 | 83.5 |
| 60 | %81.0 | %15.0 | 82.7 |
| 65 | %78.8 | %12.6 | 82.3 |
| 70 | %72.8 | %11.0 | 79.2 |
| 75 | %66.0 | %9.0 | 75.4 |
| 80 | %52.6 | %5.2 | 66.7 |
| 85 | %29.6 | %1.0 | 45.3 |
| 90 | %0.0 | %0.0 | 0.0 |

**Dev'de seçilen eşik:** `ML≥55` (max-F1). **Uygulanan OR-Gate eşiği:** `ML≥70`.

## 2. DONMUŞ TEST sonuçları (Wilson %95 GA)

| Kural | Recall [GA] | FP [GA] | F1 | AUC* |
|---|---:|---:|---:|---:|
| OR-Gate ML≥70 (uygulanan) | %72.0 [%67.9, %75.8] | %12.8 [%10.2, %16.0] | 77.9 | - |
| ML≥55 (dev-seçili) | %81.8 [%78.2, %84.9] | %19.6 [%16.4, %23.3] | 81.2 | - |
| ML-only ML≥70 | %71.2 [%67.1, %75.0] | %12.4 [%9.8, %15.6] | 77.6 | - |

* Test kümesi ML `ml_risk` AUC ≈ **0.873** (nA=500, nB=500)

## 3. Test kümesi — dil bazında (OR-Gate ML≥70)

| Dil | Attack blok | Meşru FP |
|---|---:|---:|
| en | %85 | %22 |
| tr | %63 | %2 |
| de | %80 | %24 |
| fr | %88 | %12 |
| es | %68 | %4 |
| it | %88 | %24 |
| pt | %68 | %12 |
| ru | %76 | %16 |
| ar | %48 | %8 |
| ja | %60 | %8 |
| ko | %64 | %12 |
| zh | %60 | %16 |

## 4. Yorum
- Dev'de seçilen `ML≥55` ile donmuş test'te sonuç kararlı; uygulanan `ML≥70` ile arasındaki fark küçük.
- Eşik artık **hold-out'suz aynı sette seçilmedi** → metodolojik itiraz kapandı.
- Rusça FP'nin Layer-0 kaynağı düzeltildi; kalan Rusça hatası **model** kaynaklı (ayrı sınırlılık).

---
_Üretildi: scripts/devtest_threshold_eval.py_