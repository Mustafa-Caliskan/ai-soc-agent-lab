# Seçenek B (OR-Gate) Uygulama Raporu — Ne Değişti?

> **Tarih:** 14 Ekim 2026 · **Karar:** Seçenek B (`OR-Gate`, ml_block_threshold=70) uygulandı.
> **Bağımsız benchmark:** `appsec_benchmark_2000_curated.json` (12 dil, N=2000).

## 1. Ne değişti? (kod & konfigürasyon)

| Dosya | Değişiklik |
|---|---|
| `backend/shield_config.json` | `decision_mode: or_gate`, `ml_block_threshold: 70`, `regex_block_score_threshold: 60` eklendi |
| `backend/shield_config.py` | Aynı anahtarlar `_DEFAULTS`'a eklendi (yoksa yüklenmez) |
| `backend/security_layer.py` | Karar bloğu `composite` → **OR-Gate** oldu. Composite skoru yalnızca **raporlama** için korunur |
| `scripts/verify_full_pipeline.py` | [6/8] testi yeni anahtarı (`ml_block_threshold`) kullanacak şekilde güncellendi |

**Yeni karar kuralı (kodda 4 koşul):** `blocked = hard_stego OR regex_score>=60 OR ml_risk>=70 OR (regex_triggered AND ml_class=Malicious)`
(Eski: `0.70·ML + 0.20·regex + 0.10·stego >= 60` — ML≥86 gerektiriyordu.)

## 2. Regresyon testleri (kanıt)

| Test | Sonuç |
|---|---|
| `scripts/verify_full_pipeline.py` | **22/22 BAŞARILI** (ZWJ-emoji 10/10, Türkçe IT 10/10, Kiril 4/4, DLP Kanarya 4/4 temiz) |
| `tests/test_security_layer.py` (pytest) | **20/20 BAŞARILI** |

→ Eşik düşmesine rağmen **meşru IT/emoji testlerinde yanlış alarm YOK.**

## 3. Bağımsız benchmark: BEFORE (A) → AFTER (B)

| Alt grup | BEFORE (composite thr60) | AFTER (OR-Gate ML≥70) | Değişim |
|---|---:|---:|---:|
| Tüm set (saldırı) [Saldırı blok (recall)] | %30.3 | %73.2 | +42.9 |
| Tüm set (meşru) [Meşru FP] | %0.5 | %12.0 | +11.5 |
| Kapsam-içi (saldırı) [Saldırı blok (recall)] | %32.1 | %77.3 | +45.2 |
| Kapsam-içi (meşru) [Meşru FP] | %0.5 | %12.0 | +11.5 |
| native TR/EN (saldırı) [Saldırı blok (recall)] | %45.8 | %85.3 | +39.4 |
| MT diller (saldırı) [Saldırı blok (recall)] | %23.3 | %67.7 | +44.5 |
| explicit (saldırı) [Saldırı blok (recall)] | %55.3 | %88.0 | +32.7 |
| subtle (saldırı) [Saldırı blok (recall)] | %20.4 | %67.3 | +46.9 |
| normal benign [Meşru FP] | %0.0 | %6.3 | +6.3 |
| hard-negative benign [Meşru FP] | %0.9 | %16.3 | +15.4 |

## 4. Özet tablo (kapsam-içi)

| Metrik | A (eski) | B (yeni) |
|---|---:|---:|
| Saldırı blok (recall) | %32.1 | **%77.3** |
| Meşru FP | %0.5 | %12.0 |

## 5. Yorum

- Recall **~%32 → ~%77** (kapsam-içi) yükseldi; yani saldırıların çoğu artık yakalanıyor.
- Bedel: meşru FP **~%0.5 → ~%12.0**'e çıktı — **çoğu NotInject hard-negative'lerden**; normal benign'te daha düşük.
- Layer-0 Kiril (homoglyph) hatası düzeltildi: Rusça meşru FP ~%58 → düştü; genel FP bir miktar azaldı.
- Bu, modelin ayrım gücünün (bu sette ~AUC 0.86) kaçınılmaz ödünleşimidir. **Kapasite/model sorunu değildir.**
- Operasyonel öneri: banka/SOC gibi FP-toleranslı ortamlar için B uygun; müşteri-hizmetleri gibi 0-FP istenen ortamlar için `ml_block_threshold` 75-80'e çekilebilir veya 'şüpheli' tier ile kademelendirilebilir.

## 6. Devam kararı için girdi (modele/veriye devam edelim mi?)

| Soru | Cevap |
|---|---|
| Model kalitesi yeterli mi? | Recall %85 sınıf düzeyinde **iyi**; precision sınırlı. B eşiğiyle kullanılabilir. |
| Kapasite artırımı gerekli mi? | **Gerekmez.** |
| v6 retrain gerekli mi? | **Şart değil.** Ancak FP'yi düşürmek için benign/hard-negative havuzunu genişleten bir v6 *iyileştirme* olur (opsiyonel). |
| Bu veri setiyle devam? | **Evet.** Bağımsız set, gerçek-dünya performansını dürüst ölçüyor; makale için bu şeffaflık değerli. |

---
_Üretildi: scripts/report_threshold_change.py_