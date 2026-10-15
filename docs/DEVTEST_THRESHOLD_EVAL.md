# Dev/Test Ayrımı ile Eşik Seçimi ve Donmuş Test Raporu

**Benchmark:** `appsec_benchmark_2000_curated.json` · **Bölme:** dil×etiket stratifiye, seed=42
**Dev n=1000  ·  Test n=1000** (donmuş)

## 1. Dev'de eşik taraması (ML-only)

| Eşik (ml_risk≥) | Recall | FP | F1 |
|---:|---:|---:|---:|
| 40 | %89.6 | %29.2 | 81.9 |
| 45 | %87.2 | %25.0 | 82.2 |
| 50 | %85.2 | %22.4 | 82.1 |
| 55 | %82.4 | %19.4 | 81.7 |
| 60 | %80.0 | %18.2 | 80.7 |
| 65 | %77.0 | %16.2 | 79.7 |
| 70 | %71.8 | %13.0 | 77.7 |
| 75 | %65.6 | %11.2 | 74.2 |
| 80 | %54.4 | %7.0 | 67.4 |
| 85 | %31.4 | %1.8 | 47.1 |
| 90 | %0.0 | %0.0 | 0.0 |

**Dev'de seçilen eşik:** `ML≥45` (max-F1). **Uygulanan OR-Gate eşiği:** `ML≥70`.

## 2. DONMUŞ TEST sonuçları (Wilson %95 GA)

| Kural | Recall [GA] | FP [GA] | F1 | AUC* |
|---|---:|---:|---:|---:|
| OR-Gate ML≥70 (uygulanan) | %72.4 [%68.3, %76.1] | %11.6 [%9.1, %14.7] | 78.7 | - |
| ML≥45 (dev-seçili) | %87.0 [%83.8, %89.7] | %22.2 [%18.8, %26.0] | 83.2 | - |
| ML-only ML≥70 | %72.0 [%67.9, %75.8] | %10.4 [%8.0, %13.4] | 78.9 | - |

* Test kümesi ML `ml_risk` AUC ≈ **0.891** (nA=500, nB=500)

## 3. Test kümesi — dil bazında (OR-Gate ML≥70)

| Dil | Attack blok | Meşru FP |
|---|---:|---:|
| en | %88 | %20 |
| tr | %68 | %3 |
| de | %80 | %12 |
| fr | %64 | %8 |
| es | %64 | %20 |
| it | %88 | %8 |
| pt | %72 | %20 |
| ru | %84 | %16 |
| ar | %36 | %12 |
| ja | %64 | %0 |
| ko | %52 | %16 |
| zh | %64 | %4 |

## 4. Yorum
- Dev'de seçilen `ML≥45` ile donmuş test'te sonuç kararlı; uygulanan `ML≥70` ile arasındaki fark küçük.
- Eşik artık **hold-out'suz aynı sette seçilmedi** → metodolojik itiraz kapandı.
- Rusça FP'nin Layer-0 kaynağı düzeltildi; kalan Rusça hatası **model** kaynaklı (ayrı sınırlılık).

---
_Üretildi: scripts/devtest_threshold_eval.py_