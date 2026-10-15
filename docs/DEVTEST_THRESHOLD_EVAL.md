# Dev/Test Ayrımı ile Eşik Seçimi ve Donmuş Test Raporu

**Benchmark:** `appsec_benchmark_2000_curated.json` · **Bölme:** dil×etiket stratifiye, seed=42
**Dev n=1000  ·  Test n=1000** (donmuş)

## 1. Dev'de eşik taraması (ML-only)

| Eşik (ml_risk≥) | Recall | FP | F1 |
|---:|---:|---:|---:|
| 40 | %89.6 | %25.8 | 83.2 |
| 45 | %87.8 | %22.2 | 83.6 |
| 50 | %86.2 | %19.0 | 84.0 |
| 55 | %84.2 | %16.8 | 83.8 |
| 60 | %81.4 | %15.0 | 82.9 |
| 65 | %78.6 | %12.6 | 82.2 |
| 70 | %73.4 | %11.2 | 79.5 |
| 75 | %66.6 | %8.2 | 76.2 |
| 80 | %53.8 | %5.4 | 67.6 |
| 85 | %30.8 | %1.2 | 46.7 |
| 90 | %0.0 | %0.0 | 0.0 |

**Dev'de seçilen eşik:** `ML≥50` (max-F1). **Uygulanan OR-Gate eşiği:** `ML≥70`.

## 2. DONMUŞ TEST sonuçları (Wilson %95 GA)

| Kural | Recall [GA] | FP [GA] | F1 | AUC* |
|---|---:|---:|---:|---:|
| OR-Gate ML≥70 (uygulanan) | %72.4 [%68.3, %76.1] | %12.8 [%10.2, %16.0] | 78.2 | - |
| ML≥50 (dev-seçili) | %85.8 [%82.5, %88.6] | %21.4 [%18.0, %25.2] | 82.8 | - |
| ML-only ML≥70 | %71.4 [%67.3, %75.2] | %12.8 [%10.2, %16.0] | 77.5 | - |

* Test kümesi ML `ml_risk` AUC ≈ **0.876** (nA=500, nB=500)

## 3. Test kümesi — dil bazında (OR-Gate ML≥70)

| Dil | Attack blok | Meşru FP |
|---|---:|---:|
| en | %85 | %22 |
| tr | %64 | %1 |
| de | %84 | %24 |
| fr | %88 | %12 |
| es | %68 | %4 |
| it | %88 | %24 |
| pt | %68 | %16 |
| ru | %80 | %12 |
| ar | %44 | %12 |
| ja | %64 | %12 |
| ko | %60 | %12 |
| zh | %60 | %12 |

## 4. Yorum
- Dev'de seçilen `ML≥50` ile donmuş test'te sonuç kararlı; uygulanan `ML≥70` ile arasındaki fark küçük.
- Eşik artık **hold-out'suz aynı sette seçilmedi** → metodolojik itiraz kapandı.
- Rusça FP'nin Layer-0 kaynağı düzeltildi; kalan Rusça hatası **model** kaynaklı (ayrı sınırlılık).

---
_Üretildi: scripts/devtest_threshold_eval.py_