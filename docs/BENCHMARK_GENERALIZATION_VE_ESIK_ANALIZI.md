# NeuralShield-v5 — Bağımsız Benchmark: Genelleme Boşluğu ve Karar Eşiği Analizi

> **Amaç:** Kalkanın bağımsız (in-distribution olmayan) AppSec benchmark'ındaki gerçek davranışını ölçmek,
> düşük blok oranının kök nedenini model/regex/karar katmanı olarak ayrıştırmak ve eşik kararı için
> kanıt sunmak. **Doküman, karar alma aşamasında paylaşılmak üzere hazırlanmıştır.**

**Benchmark:** `data/appsec_benchmark_2000_curated.json` — 2000 örnek (1000 saldırı / 1000 meşru), 12 dil.
**Kalkan:** NeuralShield-v5 (XLM-RoBERTa ONNX INT8, T*=1.8345) + Layer 0/1/3. Karar: composite 0.70·ML + 0.20·regex + 0.10·stego, eşik 60.

---

## 1. Metodolojik UYARI: Paper'daki %94.64 ile buradaki fark NEDEN?

- Paper'daki **%94.64 doğruluk / 0.9954 AUC**, eğitimle **AYNI dağılımdan** çekilen held-out test kümesindedir (**in-distribution**).
- Bu benchmark ise **farklı kaynaklardan** (Lakera/mosscap, reshahhs, xTRam1, Horizon, neuralchemy) + **MT ile 10 dilde** üretilmiştir (**out-of-distribution**).
- İkisi çelişmez: biri 'kapalı sınav', diğeri 'gerçek dünya' performansıdır. **Gerçekçi performans = bağımsız setteki değerdir.**

## 2. Bileşen Ayrıştırması — Sorun modelde mi, regex'te mi, kararda mı?

| Bileşen | Ölçüm | Yorum |
|---|---|---|
| **Model (L2)** | Saldırıların **%93**'ini Malicious diyor | Recall iyi; ana dedektör model |
| **Regex (L1)** | Saldırıların yalnızca **%16**'unda tetikleniyor | Rolü küçük; darboğaz DEĞİL |
| **Karar katmanı** | Mevcut blok **%36.5** | `0.70·ML` eşiği 60 → **ML≥86** istiyor; tespitlerin çoğu kesiliyor |

**KANIT:** *"Ignore everything above this line"* → ML **%84 Malicious** ama `0.70×84 = 59 < 60` → bloklanmadı.
**Sonuç: Model doğru tespit ediyor; darboğaz karar eşiğidir.** (Kapasite/model büyütme sorunu değildir.)

## 3. Kapsam & Zorluk Kırılımı (kürat edilmiş etiketler)

| Kırılım | Saldırı (n) | Meşru (n) |
|---|---:|---:|
| Tüm set | 1000 | 1000 |
| Kapsam-içi (OR-Bench hariç) | 1000 | 1000 |
| native (TR/EN) | 508 | 395 |
| MT (diğer 10 dil) | 492 | 605 |
| explicit injection | 363 | - |
| subtle | 637 | - |
| hard-negative benign (NotInject) | - | 122 |

### Recall / FP (ML≥50, dil ve zorluk bazında)

| Grup | Metrik | Değer |
|---|---|---|
| native TR/EN saldırı | Recall (ML≥50) | %95 |
| MT diller saldırı | Recall (ML≥50) | %91 |
| explicit saldırı | Recall (ML≥50) | %96 |
| subtle saldırı | Recall (ML≥50) | %91 |
| normal benign | FP (ML≥50) | %10 |
| hard-negative benign | FP (ML≥50) | %22 |

> **Not:** MT diller recall'u native'den **daha düşüktür** (ML≥50'de native %91 vs MT %82; dağıtılan OR-Gate eşiğinde native %86 vs MT %67).
> Yani model dili tamamen bağımsız DEĞİLDİR; FP'nin büyük kısmı ise **NotInject hard-negative**'lerden gelir.

## 4. KARAR EŞİĞİ ÖDÜNLEŞİM TABLOSU (Kapsam-içi set)

| Karar Kuralı | Saldırı Blok [in-scope] | Meşru FP [in-scope] | Saldırı Blok [tüm] | Meşru FP [tüm] |
|---|---:|---:|---:|---:|
| Mevcut composite (thr=60) | **%36.5** | %0.3 | %36.5 | %0.3 |
| composite thr=50 | **%81.5** | %4.0 | %81.5 | %4.0 |
| composite thr=40 | **%89.7** | %8.2 | %89.7 | %8.2 |
| ML>=70 (önerilen) | **%83.2** | %4.5 | %83.2 | %4.5 |
| ML>=60 | **%89.2** | %7.8 | %89.2 | %7.8 |
| ML>=50 | **%93.0** | %11.4 | %93.0 | %11.4 |
| ML sınıf=Malicious | **%92.8** | %11.0 | %92.8 | %11.0 |
| OR-Gate (ML>=70) | **%83.2** | %4.5 | %83.2 | %4.5 |
| OR-Gate (ML>=60) | **%89.2** | %7.8 | %89.2 | %7.8 |
| OR-Gate (ML>=50) | **%93.0** | %11.4 | %93.0 | %11.4 |

**Yorum:** Recall'i %29'dan yükseltmek FP'yi de yükseltir (bu bir **tercih**, ücretsiz düzeltme değil).
Modelin ayrım gücü (bu sette ~AUC 0.86) bu ödünleşim eğrisini belirler.

## 5. ÖNERİ VE KARAR SEÇENEKLERİ

**Not:** `OR-Gate` ile `ML≥X` **AYNI DEĞİLDİR**. OR-Gate = `ML≥X OR regex_score≥60 OR hard_stego`;
ek olarak `hard_stego` (Kiril FP'si düzeltilmeden önce) FP'yi yükseltiyordu. Ölçüm (düzeltme sonrası):
  - ML-only `ML≥70`: recall 82.5 / FP 4.4
  - OR-Gate `ML≥70`: recall 83.2 / FP 4.5

**Önerilen kural: `OR-Gate (ML≥70)`** (veya modelin kalibre optimal eşiği τ*=0.4567 → ~`ML≥46`):

| Seçenek | Blok (in-scope) | FP (in-scope) | Saldırı Blok (tüm) | Uygun senaryo |
|---|---:|---:|---:|---|
| A. Mevcut (thr=60) | %36.5 | %0.3 | %36.5 | FP toleransı sıfır, recall düşük |
| B. **OR-Gate ML≥70 (önerilen)** | **%83.2** | %4.5 | %83.2 | **Dengeli kurumsal** |
| C. OR-Gate ML≥50 | %93.0 | %11.4 | %93.0 | Recall-kritik (SOC alarm) |

**Bağımsız kararlar (eşikten ayrı):**
1. **Benchmark küratı:** OR-Bench (kapsam belirsiz) çıkar → in-scope set daha net.
2. **v6 retrain'i (opsiyonel, büyük iş):** kapsam-içi veri + geniş benign/hard-negative havuzu. **Kapasite artırımı gereksiz.**
3. **Paper dürüstlüğü:** in-distribution %94.64 yanına **bağımsız benchmark sonucu** mutlaka raporlanmalı.

---
_Üretildi: scripts/analyze_generalization_and_threshold.py_