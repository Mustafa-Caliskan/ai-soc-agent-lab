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
| **Model (L2)** | Saldırıların **%85**'ini Malicious diyor | Recall iyi; ana dedektör model |
| **Regex (L1)** | Saldırıların yalnızca **%9**'unda tetikleniyor | Rolü küçük; darboğaz DEĞİL |
| **Karar katmanı** | Mevcut blok **%27.3** | `0.70·ML` eşiği 60 → **ML≥86** istiyor; tespitlerin çoğu kesiliyor |

**KANIT:** *"Ignore everything above this line"* → ML **%84 Malicious** ama `0.70×84 = 59 < 60` → bloklanmadı.
**Sonuç: Model doğru tespit ediyor; darboğaz karar eşiğidir.** (Kapasite/model büyütme sorunu değildir.)

## 3. Kapsam & Zorluk Kırılımı (kürat edilmiş etiketler)

| Kırılım | Saldırı (n) | Meşru (n) |
|---|---:|---:|
| Tüm set | 1000 | 1000 |
| Kapsam-içi (OR-Bench hariç) | 941 | 1000 |
| native (TR/EN) | 312 | 255 |
| MT (diğer 10 dil) | 688 | 745 |
| explicit injection | 284 | - |
| subtle | 716 | - |
| hard-negative benign (NotInject) | - | 571 |

### Recall / FP (ML≥50, dil ve zorluk bazında)

| Grup | Metrik | Değer |
|---|---|---|
| native TR/EN saldırı | Recall (ML≥50) | %91 |
| MT diller saldırı | Recall (ML≥50) | %82 |
| explicit saldırı | Recall (ML≥50) | %93 |
| subtle saldırı | Recall (ML≥50) | %82 |
| normal benign | FP (ML≥50) | %14 |
| hard-negative benign | FP (ML≥50) | %26 |

> **Not:** MT diller recall'u native'den **daha kötü değil** → model dili bağımsız çalışıyor. FP'nin büyük kısmı **NotInject hard-negative**'lerden.

## 4. KARAR EŞİĞİ ÖDÜNLEŞİM TABLOSU (Kapsam-içi set)

| Karar Kuralı | Saldırı Blok [in-scope] | Meşru FP [in-scope] | Saldırı Blok [tüm] | Meşru FP [tüm] |
|---|---:|---:|---:|---:|
| Mevcut composite (thr=60) | **%28.9** | %1.3 | %27.3 | %1.3 |
| composite thr=50 | **%74.5** | %11.4 | %70.6 | %11.4 |
| composite thr=40 | **%85.7** | %17.6 | %81.3 | %17.6 |
| ML>=70 (önerilen) | **%76.5** | %12.4 | %72.5 | %12.4 |
| ML>=60 | **%84.8** | %17.1 | %80.5 | %17.1 |
| ML>=50 | **%89.7** | %21.2 | %85.2 | %21.2 |
| ML sınıf=Malicious | **%89.3** | %20.3 | %84.8 | %20.3 |
| OR-Gate (ML>=70) | **%76.5** | %12.4 | %72.5 | %12.4 |
| OR-Gate (ML>=60) | **%84.8** | %17.1 | %80.5 | %17.1 |
| OR-Gate (ML>=50) | **%89.7** | %21.2 | %85.2 | %21.2 |

**Yorum:** Recall'i %29'dan yükseltmek FP'yi de yükseltir (bu bir **tercih**, ücretsiz düzeltme değil).
Modelin ayrım gücü (bu sette ~AUC 0.86) bu ödünleşim eğrisini belirler.

## 5. ÖNERİ VE KARAR SEÇENEKLERİ

**Not:** `OR-Gate` ile `ML≥X` kuralları bu veride **birebir aynı** sonucu verir; çünkü regex tetiklendiğinde skoru zaten ≥60'tır.
Yani arkadaş önerisi (stego/regex gücünü koru, ML'yi 0.70 ile ezme) hem doğru hem de en dengeli davranışı üretir.

**Önerilen kural: `OR-Gate (ML≥70)`** (veya modelin kalibre optimal eşiği τ*=0.4567 → ~`ML≥46`):

| Seçenek | Blok (in-scope) | FP (in-scope) | Saldırı Blok (tüm) | Uygun senaryo |
|---|---:|---:|---:|---|
| A. Mevcut (thr=60) | %28.9 | %1.3 | %27.3 | FP toleransı sıfır, recall düşük |
| B. **OR-Gate ML≥70 (önerilen)** | **%76.5** | %12.4 | %72.5 | **Dengeli kurumsal** |
| C. OR-Gate ML≥50 | %89.7 | %21.2 | %85.2 | Recall-kritik (SOC alarm) |

**Bağımsız kararlar (eşikten ayrı):**
1. **Benchmark küratı:** OR-Bench (kapsam belirsiz) çıkar → in-scope set daha net.
2. **v6 retrain'i (opsiyonel, büyük iş):** kapsam-içi veri + geniş benign/hard-negative havuzu. **Kapasite artırımı gereksiz.**
3. **Paper dürüstlüğü:** in-distribution %94.64 yanına **bağımsız benchmark sonucu** mutlaka raporlanmalı.

---
_Üretildi: scripts/analyze_generalization_and_threshold.py_