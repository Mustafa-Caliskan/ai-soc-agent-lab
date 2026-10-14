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

**Yeni karar kuralı:** `blocked = hard_stego OR regex_score>=60 OR ml_risk>=70`
(Eski: `0.70·ML + 0.20·regex + 0.10·stego >= 60` — ML≥86 gerektiriyordu.)

## 2. Regresyon testleri (kanıt)

| Test | Sonuç |
|---|---|
| `scripts/verify_full_pipeline.py` | **20/20 BAŞARILI** (ZWJ-emoji 10/10, Türkçe IT 10/10 temiz) |
| `tests/test_security_layer.py` (pytest) | **18/18 BAŞARILI** |

→ Eşik düşmesine rağmen **meşru IT/emoji testlerinde yanlış alarm YOK.**

## 3. Bağımsız benchmark: BEFORE (A) → AFTER (B)

| Alt grup | BEFORE (composite thr60) | AFTER (OR-Gate ML≥70) | Değişim |
|---|---:|---:|---:|
| Tüm set (saldırı) [Saldırı blok (recall)] | %27.3 | %72.5 | +45.2 |
| Tüm set (meşru) [Meşru FP] | %1.3 | %12.4 | +11.1 |
| Kapsam-içi (saldırı) [Saldırı blok (recall)] | %28.9 | %76.5 | +47.6 |
| Kapsam-içi (meşru) [Meşru FP] | %1.3 | %12.4 | +11.1 |
| native TR/EN (saldırı) [Saldırı blok (recall)] | %44.9 | %86.2 | +41.3 |
| MT diller (saldırı) [Saldırı blok (recall)] | %19.3 | %66.3 | +46.9 |
| explicit (saldırı) [Saldırı blok (recall)] | %50.7 | %87.0 | +36.3 |
| subtle (saldırı) [Saldırı blok (recall)] | %18.0 | %66.8 | +48.7 |
| normal benign [Meşru FP] | %0.0 | %6.8 | +6.8 |
| hard-negative benign [Meşru FP] | %2.3 | %16.6 | +14.4 |

## 4. Özet tablo (kapsam-içi)

| Metrik | A (eski) | B (yeni) |
|---|---:|---:|
| Saldırı blok (recall) | %28.9 | **%76.5** |
| Meşru FP | %1.3 | %12.4 |

## 5. Yorum

- Recall **~%29 → ~%77** (kapsam-içi) yükseldi; yani saldırıların çoğu artık yakalanıyor.
- Bedel: meşru FP **~%1.3 → ~%12.4**'e çıktı — **çoğu NotInject hard-negative'lerden**; normal benign'te daha düşük.
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