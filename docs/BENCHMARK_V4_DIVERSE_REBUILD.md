# 📊 AppSec-2000 Benchmark v4 (Diverse Rebuild) — Metodolojik Onarım ve Kaynak Dengesi Raporu

**Tarih:** 15 Ekim 2026  
**Üretilen Dosyalar:**
- Ana Dengeli OOD Benchmark (`N=2.000`, 12 Dil): `data/appsec_benchmark_v2_diverse.json` (ve senkronize SSOT kopyaları: `appsec_benchmark_2000.json`, `appsec_benchmark_2000_shield.json`, `appsec_benchmark_2000_curated.json`, `appsec_benchmark_2000_purged.json`, `benchmark_master_2000.json`, `live_2000_audit_results.json`)
- Ayrı Sınır / Bağlam Stres Testi (`N=1.070`): `data/stress_boundary_mosscap_notinject.json` (499 `Lakera/Mosscap` + 571 `Horizon/NotInject`)
- Önceki Sürüm Yedeği: `data/appsec_benchmark_2000_v3_backup.json`

---

## 1. Neden Yeniden İnşa Edildi? (Stage-2 Slicing Bug Teşhisi)

`scripts/build_appsec_benchmark_v2_stage2.py` (satır 128–134 ve 173–175) incelendiğinde **iki yapısal dilimleme hatası (slicing bug)** tespit edilmiştir:

1. **Aynı 50 Cümlenin 10 Dile Tekrar Çevrilmesi (`L173–174`):**
   ```python
   a_src = en_attacks[:need_atk_per[lang]]   # 10 dilin TAMAMI aynı ilk 50 İngilizce saldırıyı alıyordu
   b_src = en_benign[:need_ben_per[lang]]     # 10 dilin TAMAMI aynı ilk 50 İngilizce meşruyu alıyordu
   ```
2. **Kaynak Tavanı Sıralama Kilidi (`L128–134`):**
   - `en_attacks` oluşturulurken ilk 40 sıraya `HF/Lakera/mosscap` (Gandalf şifre bulmaca oyunu) yerleştiği için, `en_attacks[:50]` dilimi **40 Mosscap + 7 SPML + 2 xTRam1 + 1 simsonsun** içeriyordu.
   - Bu ilk 50 cümle 10 dile aynen çevrilince, toplam 1.000 saldırının **499'u (%49.9)** aynı 40 `Mosscap` bilmecesinin tekrarından oluştu.
   - Benzer şekilde `en_benign[:50]` içinde `HF/Horizon/notinject` önceliklendirildiği için toplam 1.000 meşru örneğin **571'i (%57.1)** aşırı kelime tuzaklı `NotInject` örneklerinden oluştu.

---

## 2. v4 (`appsec_benchmark_v2_diverse.json`) Tasarım İlkeleri ve Hijyen Garantileri

Yeni `v4` veri seti (`scripts/build_benchmark_v4_diverse.py`), skoru maksimize etmek için değil, **temsili, sızıntısız ve tekil kaynak domine etmeyen** bir OOD dağılımı kurmak için şu 5 katı kuralla inşa edilmiştir:

1. **Dil Çeşitliliği ve Ayrık Dilimleme (Disjoint Slicing):**
   - `de, fr, es, it, pt, ja, zh` dillerinde yerel havuzdaki `HF/rikka-snow/multilingual` kaynağından **doğal (native)** örnekler dahil edilmiş; MT dolgularında ise her dil **kesişmeyen (disjoint)** `SPML`, `simsonsun_jailbreaks`, `boundary_pairs_test` ve `xTRam1` dilimleri almıştır. Hiçbir İngilizce cümle 10 dile birden kopyalanmamıştır.
2. **İlkeli Kaynak Dengesi:**
   - Hiçbir tekil kaynak toplam 2.000 örneğin %20'sini geçmez. `Mosscap` saldırıların **%7.5'i (75/1000)**, `NotInject` ise meşru örneklerin **%12.2'si (122/1000)** düzeyinde tutulmuştur.
   - Eski setteki 499 `Mosscap` ve 571 `NotInject` (`N=1.070`) silinmemiş; **`data/stress_boundary_mosscap_notinject.json`** olarak ayrı bir **"Boundary & Context-Dependent Stress Test"** dosyasında korunmuştur.
3. **Sıfır Eğitim Sızıntısı (`0 / 2.000` Overlap):**
   - `docs/LEAKAGE_AUDIT.md` içinde tespit edilen 76 örtüşen kayıt ve yerel `train/val/test_multilingual.csv` + `redteam_corpus.json` içindeki tüm kayıtlar baştan kara listeye alınmıştır (**0/2000 sızıntı**).
4. **Sıfır Kapsam-Dışı / Gürültülü Kaynak (`OnerAYTAS = 0`, `orbench = 0`, `ETHICS_PAT = 0`):**
   - `benchmark_multilingual_1200.json` (`OnerAYTAS`, `JailbreakBench`, `LibrAI/do-not-answer`) **hiç okunmamıştır (0 kayıt)**.
   - 12 dilde intihar, soykırım, terör, bomba, uyuşturucu, ırkçılık, nefret söylemi (`Odio a`, `Ich hasse`, `Je déteste`), politikacılar (`Hitler`, `Trump`, `Steinmeier` vb.), 11 Eylül ve din konularını tarayan `ETHICS_PAT` regex filtresi kod seviyesinde zorunlu tutulmuştur (**ihlaller = 0**).
5. **Simetrik 12 Dil Yapısı:**
   - `N = 2.000` (`1.000 Saldırı / 1.000 Meşru`): `en` (250/250), `tr` (250/250) ve `de, fr, es, it, pt, ru, ar, ja, ko, zh` (her biri 50/50; yanlış alfabe/script = **0**).

---

## 3. Yeni Kaynak Dağılımı (`N = 2.000`)

### A. Saldırı Kaynakları (`label = 1`, $N = 1.000$)
| Kaynak | Örnek Sayısı ($n$) | Saldırı Payı (%) | Toplam Set Payı (%) |
| :--- | :---: | :---: | :---: |
| `HF/reshabhs/SPML` (Sistem Promptu & Chatbot Enjeksiyonu) | 261 | %26.1 | %13.1 |
| `HF/Horizon/simsonsun_jailbreaks` (DAN, Persona & Jailbreak) | 194 | %19.4 | %9.7 |
| `HF/rikka-snow/multilingual` (Doğal Çok Dilli Enjeksiyon) | 184 | %18.4 | %9.2 |
| `HF/xTRam1/safe-guard` (Sızıntıdan Arındırılmış Enjeksiyon) | 84 | %8.4 | %4.2 |
| `HF/Lakera/mosscap` (Gandalf Şifre Sızdırma) | 75 | %7.5 | %3.8 |
| `HF/Horizon/boundary_pairs_test` (Sınır Enjeksiyonları) | 53 | %5.3 | %2.7 |
| `Local/adaptive_adversarial_50` (Sinsi Kurgu & Stego - TR) | 49 | %4.9 | %2.5 |
| `Local/benchmark_300` (TR/EN AppSec) | 43 | %4.3 | %2.2 |
| `HF/neuralchemy[original]` (Doğrudan & Dolaylı Enjeksiyon) | 42 | %4.2 | %2.1 |
| `Local/elite_suite` (Kurumsal Kırmızı Takım - TR) | 15 | %1.5 | %0.8 |

### B. Meşru Kaynakları (`label = 0`, $N = 1.000$)
| Kaynak | Örnek Sayısı ($n$) | Meşru Payı (%) | Toplam Set Payı (%) |
| :--- | :---: | :---: | :---: |
| `HF/xTRam1/safe-guard` (Sızıntısız Normal Meşru) | 384 | %38.4 | %19.2 |
| `HF/reshabhs/SPML` (Normal Chatbot & Kurumsal Diyalog) | 224 | %22.4 | %11.2 |
| `HF/rikka-snow/multilingual` (Doğal Çok Dilli Meşru) | 140 | %14.0 | %7.0 |
| `HF/Horizon/notinject` (Kelime Tuzaklı Hard-Negative) | 122 | %12.2 | %6.1 |
| `Local/legacy_handcrafted` (Teknik IT & Sistem Yönetimi) | 61 | %6.1 | %3.1 |
| `Local/benchmark_300` (TR/EN Kurumsal & Yolcu) | 42 | %4.2 | %2.1 |
| `HF/neuralchemy[original]` (Teknik Destek) | 22 | %2.2 | %1.1 |
| `Local/elite_suite` (Kurumsal Meşru) | 5 | %0.5 | %0.3 |

---

## 4. Deneysel Sonuçlar: Operasyonel OOD (`v4`) vs. Boundary Stres Testi (`Mosscap + NotInject`)

Tek geçişli canlı ONNX INT8 çıkarımı (`scripts/run_live_2000_audit.py` ve `scripts/devtest_threshold_eval.py`) ile elde edilen **SSOT (Single Source of Truth)** sonuçları:

| Değerlendirme Kümesi | Örneklem ($N$) | Saldırı Blok (Recall) [Wilson %95 GA] | Yanlış Alarm (FP) [Wilson %95 GA] | Kesinlik (Prec) | Macro F1 | Doğruluk (Acc) | ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Dengeli OOD Benchmark (v4 Tüm Set)** | **2.000** (1000/1000) | **%83.20** [%80.76–%85.39] | **%4.50** [%3.38–%5.97] | **%94.87** | **%88.65** | **%89.35** | **0.958** |
| **2. Donmuş Test Kümesi (Stratifiye %50 Split)** | **1.000** (500/500) | **%82.60** [%79.0–%85.7] | **%3.80** [%2.4–%5.9] | **%95.60** | **%88.60** | **%89.40** | **0.967** |
| **3. Ana Odak: İngilizce (`en`) Alt Kümesi** | **500** (250/250) | **%91.20** (228/250) | **%5.20** (13/250) | %94.61 | %92.87 | %93.00 | — |
| **4. Ana Odak: Türkçe (`tr`) Alt Kümesi** | **500** (250/250) | **%80.80** (202/250) | **%1.60** (4/250) | **%98.06** | %88.60 | %89.60 | — |
| **5. Ekstrem Sınır Stres Testi (`stress_boundary`)** | **1.070** (499 Atk / 571 Ben) | **%67.74** (338/499 `Mosscap`) | **%16.29** (93/571 `NotInject`) | %78.42 | %72.69 | %75.98 | 0.842 |

### 12 Dil Bazında Performans Kırılımı (`v4` Tüm Set, OR-Gate `ML≥70`):
| Dil | Saldırı Yakalama (Recall) | Masum Yanlış Alarm (FP) |
| :--- | :---: | :---: |
| **İngilizce (`en`)** | **%91.2** (228/250) | **%5.2** (13/250) |
| **Türkçe (`tr`)** | **%80.8** (202/250) | **%1.6** (4/250) |
| **Rusça (`ru`)** | **%94.0** (47/50) | **%4.0** (2/50) |
| **İtalyanca (`it`)** | **%90.0** (45/50) | **%6.0** (3/50) |
| **Almanca (`de`)** | **%86.0** (43/50) | **%6.0** (3/50) |
| **Fransızca (`fr`)** | **%82.0** (41/50) | **%2.0** (1/50) |
| **Korece (`ko`)** | **%82.0** (41/50) | **%4.0** (2/50) |
| **Portekizce (`pt`)** | **%82.0** (41/50) | **%6.0** (3/50) |
| **İspanyolca (`es`)** | **%80.0** (40/50) | **%8.0** (4/50) |
| **Japonca (`ja`)** | **%80.0** (40/50) | **%10.0** (5/50) |
| **Çince (`zh`)** | **%74.0** (37/50) | **%8.0** (4/50) |
| **Arapça (`ar`)** | **%54.0** (27/50) | **%2.0** (1/50) |

---

## 5. Doğrulama ve SSOT Garantisi
- `shield.json`, `curated.json`, `purged.json` ve `live_2000_audit_results.json` arasındaki `ml_risk` ve karar farkı: **0 / 2.000**.
- `python scripts/verify_full_pipeline.py`: **23 / 23 BAŞARILI**.
- `pytest tests/`: **20 / 20 BAŞARILI**.
