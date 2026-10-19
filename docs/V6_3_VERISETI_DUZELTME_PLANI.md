# 📋 NeuralShield-v6.3 — Verisetini Düzeltme Planı (Gerekçe + Uygulama + Hedefler)

**Tarih:** 17 Ekim 2026 · **Sürüm:** v6.3-plan (peer-review düzeltmeleri dahil)
**Durum:** v6.2 eğitimleri bitti; **adil (source-disjoint) benchmark** ile gerçek konum ölçüldü. Bu belge veri düzenlemelerini, gerekçesini, bakılacak yerleri ve **ölçülebilir** başarı koşullarını tanımlar.

---

## 0. Peer-Review Düzeltme Notu (v6.3-plan)

Önceki taslak iki noktada düzeltildi:

1. **"mmBERT, Patronus'u geçti" ifadesi fazla iddialıydı.** Adil benchmark 2.849 satır olsa da bunlar **240 benzersiz cümlenin 12 dile çevirisidir**; saldırı tarafında yalnızca **120 benzersiz** örnek (119'u tek kaynak: Simsonsun). Recall için %95 güven aralığı **±~8 puan**. F1 84.8 vs 84.2 → **beraberlik**. Patronus **AUC (0.977 vs 0.949)** ve **sıralama kalitesinde** önde.
2. **"F1≥86, ar≥85" gibi kesin eşikler bu gürültüde ölçülemez.** Başarı, **bootstrap güven aralığı** ve **eşikten bağımsız Recall@FP=1%** ile ifade edilecek (bkz. Bölüm 6).

---

## 1. Proje Amacı

**NeuralShield**, LLM uygulamalarına giden istemleri koruyan **4 katmanlı AppSec geçididir** (L0 normalizer → L1 regex → L2 ML sınıflandırıcı → L3 DLP), OR-Gate kararıyla.

- **Kapsam:** Prompt injection, jailbreak, talimat iptali, sistem-prompt sızdırma, indirect/agentic injection, steganografi, exfiltration.
- **Kapsam dışı:** İçerik moderasyonu / etik / nefret (delege).
- **Hedef:** 12 dilde dengeli, **kaynak-ayrık**, düşük FP + yüksek recall ile **rakiplerle adil kıyas** ve yayınlanabilir ablasyon.
- **Omurgalar:** XLM-R-base (278M), mmBERT-base (307M, **şampiyon adayı**), BGE-M3 (568M, ablasyon).

---

## 2. Mevcut Durum (v6.2, adil benchmark)

### 2.1 Adil benchmark — th=0.70 (⚠️ küçük örneklem, bkz. Bölüm 0)
Kaynak: `heldout_benchmark_v6_fair.json` (Simsonsun + rubend18 / dolly; NLLB 12-dil; **jackhhao YOK**)

| Model | Recall | FP | Macro-F1 | AUC |
|---|---|---|---|---|
| **mmBERT v6.2** | 74.0 | 3.8 | 84.8 | 0.9494 |
| Patronus Wolf Defender | 70.1 | 0.8 | 84.2 | 0.9767 |
| BGE-M3 v6.2 | 61.5 | 2.2 | 78.8 | 0.9347 |
| XLM-R v6.2 | 47.5 | 2.2 | 70.6 | 0.8916 |

> **Yorum:** F1'de beraberlik; **AUC ve sıralamada Patronus önde.** BGE-M3 hold-out'ta en iyi ama adilde zayıf (aşırı-uydurma) → şampiyon değil.

### 2.2 Kontaminasyon bulgusu
Eski `heldout_benchmark_v6_clean.json` (jackhhao ağırlıklı) **Patronus'un eğitim kaynağıdır**. Patronus'un oradaki 86.9 F1'i şişikti; adilde 84.2. → **Kıyas yalnızca kaynak-ayrık benchmark ile.**

### 2.3 Kalan açıklar (mmBERT, @0.7)
`ar 65.0 vs 91.7 (-26.7)`, `en 75.8 vs 86.7 (-10.9)`, `tr 46.7 vs 51.7`, `ru FP 12.5 vs 0.8`, `AUC 0.949 vs 0.977`.

---

## 3. Neden Verisetini Düzenliyoruz? (Kök nedenler)

1. **Arapça zayıf:** Eğitimde ar saldırılar neredeyse tamamen MT; native çeşitlilik yok.
2. **İngilizce açık:** EN saldırı çeşitliliği + hedefli hard-neg eksik; ayrıca **uzunluk farkı** olabilir (eğitim `len≤600` vs benchmark ≤1200).
3. **FP/AUC:** Patronus **simetrik augmentasyon + hedefli hard-neg + contrastive + FreeLB** kullanıyor (model kartı).
4. **Geçmiş hata:** v6.2'de benign tek taraflı MT/roleplay ile dolduruldu → stil kısayolu + recall düşüşü. Tekrarlanmayacak.
5. **Değerlendirme hijyeni:** Benchmark hiçbir değerlendirilen modelin eğitiminde olmamalı; ayrıca benchmark'a **aşırı-uydurma** riski yönetilmeli.

**Patronus model kartı:** `https://huggingface.co/patronus-studio/wolf-defender-prompt-injection`
- mmBERT, 2048 token, 3 epoch, LR 1e-5, BF16.
- **Contrastive (0.05, temp 0.07) + FreeLB (3 adım, 0.01, max norm 0.1).**
- **Her iki sınıfa** augmentasyon; **counterfactual** çiftler; **hedefli hard-neg** (güvenlik dokümanı, kod, politika, saldırı açıklaması); 90% dedup; Smooth-Max.

---

## 4. Uygulamadan ÖNCE: Hata Analizi Kapısı (yeni, zorunlu)

> Veri üretmeden önce mmBERT'in adil benchmark'taki yanlışlarını dök ve hipotezleri test et. **Süre: ~15 dk.**

1. **Uzunluk hipotezi:** Eğitim `ok()` filtresi `len≤600`; benchmark ≤1200. Yüksek recall açığı uzun jailbreak'lerden mi? → yanlışların uzunluk dağılımı.
2. **Rusça/tr etiket gürültüsü:** Hücre 6'da silinen ilk 15'in neredeyse tamamı ru/tr idi (zararlı ama injection olmayan, "saldırı" etiketli). Qwen yalnızca en şüpheli 800'ü inceledi → gerçek gürültü daha yüksek olabilir.
3. **Rusça sistematik FP:** ru FP üç modelde de yüksek (12.5/11.7/7.5) → sistematik veri sorunu sinyali.
4. **Sızıntı kontrolü:** `heldout_benchmark_v6_fair.json` ↔ `train_v6_clean.parquet` **tam ve yakın-kopya** eşleşmesi (2 dk). Ayrıca "dolly/Simsonsun Patronus'ta yok" **model kartından çıkarım**, kesin değil — belirtilecek.
5. **MT çeşitliliği (kritik):** 34.063 MT saldırının **kaç benzersiz İngilizce tohumdan** türediğini ölç (tohum imzası / benzerlik kümeleme). Az sayıda tohumdan çoğaltılmışsa **gerçek çeşitlilik görünenden düşüktür** → yeni çeviri eklemek aynı tohumu çoğaltır; **benzersiz insan-yazımı saldırı** gerekir.

**Karar kapısı:** Bu analiz, veri düzenlemesinin **ne kadarının etiket temizliği, ne kadarının yeni veri** olacağını belirler.

### 4.1 ru/tr tam etiket denetimi (hata analizinin çıktısı)
- Qwen yargıcı **ru ve tr native saldırı satırlarının tamamında** çalıştır (~4.000 örnek, birkaç dk).
- Yüksek-gürültü kaynağı varsa eğitimden çıkar. **Bu, Arapça veri toplamaktan daha ucuz ve muhtemelen daha etkili.**

---

## 5. Veri Düzenlemeleri (v6.3) — Tasarım Kuralları

> **İlke:** Dengeli (50k/50k) iskeleti koru. Saldırı sayısını bozmadan açık dillere native çeşitlilik + hedefli hard-neg ekle. Benign'i roleplay ile DOLDURMA.

### 4.3 Hata Analizi Sonuçları (v6.3, YÜRÜTÜLDÜ — `notebooks/Error_Analysis_v6_3.ipynb`)
- **Sızıntı ≈ 0:** tam 2/2849, yakın-kopya (MinHash Jaccard≥0.85) 2/2849 (**%0.1**). Benchmark temiz → **yeniden kurmaya gerek yok** (sadece final'i büyüt/küme-ayır).
- **Uzunluk hipotezi ELENDİ:** FN medyan **356** = TP medyan **357.5**; >600 char saldırılarda kaçma %19.8 ≈ genel %26 → **uzunluk etkisi yok**; uzun-jailbreak verisi **gereksiz**.
- **FP'nin %98'i KISA metin (<150 char):** 53/54 → en yüksek getiri **kısa benign hard-neg**.
- **Recall = dil yeteneği (kaynak değil):** aynı 119 EN jailbreak çevirileri → ru 95, it 81, es 81, zh 78, de/fr 77, ja 76, pt 72, **ar 65, ko 60, tr 46**.
- **MT çeşitliliği:** çeviri-metni benzersiz küme oranı **%88–99** → ciddi duplikasyon yok. *(Not: bu, İngilizce tohum sayısını doğrudan kanıtlamaz.)*
- **Düzeltme:** "Batı dilleri Patronus'u eziyor" **en için geçersiz** (Patronus EN 86.7 > bizim 75.8); de/fr/es/it/pt'de evet öndeyiz.

---

## 5. Veri Düzenlemeleri (v6.3) — Hata Analizine Göre Revize

> **İlke:** Dengeli (50k/50k) iskeleti koru. **Nokta atışı** ekleme yap; benign'i roleplay ile DOLDURMA.

### 5.1 Kısa benign hard-negative (FP) — EN YÜKSEK ÖNCELİK
- FP'nin **%98'i <150 karakter** masum. → oasst2/aya + yerel havuzdan **dil başına kısa (<150 char) native benign** ekle (**MT değil**).
- Hedef: **+5.000–8.000** kısa benign (12 dil), `src=native`, `tier=0`, marker `short_benign`.
- Başarı: FP **3.8 → ≤1.5**.

### 5.2 tr / ar / ko native takviye (recall) — zayıf diller
- Aynı saldırıların çevirisi: **tr 46 / ko 60 / ar 65** → dil yeteneği zayıf.
- **tr:** native saldırı+masum mevcut (3nesdeniz/AltaySec/halilneed/TFLai); **tr benign'i native-ağırlıklı** yap (MT ≤%30).
- **ar / ko:** native saldırı kaynağı **önce doğrulanır**; yoksa daha fazla (MT) saldırı + **native benign** ile dengele ve **sınırlama yaz**. Native bulunursa **iki sınıf da aynı origin**.
- Başarı: tr ≥55; ar nokta ≥85 (CI_alt ≥78); ko ≥70 (CI ile).

### 5.3 İngilizce hedefli hard-neg (FP/AUC)
- Güvenlik dokümanı, kod/markup/konfig, sistem-prompt/politika, saldırı açıklaması, leksik benzer ama yönlendirmeyen masum. **Genel roleplay değil.**
- **+3.000–5.000** hedefli hard-neg (mevcut 15k'yı bozmadan, ölçülü).

### 5.4 Üretici-stili kısayolunu önle (counterfactual) — ZORUNLU
- Sentetik/LLM hard-neg için **aynı üretici/şablonla eşleşen sentetik saldırı** üret; augmentasyon **her iki sınıfa eşit**.

### 5.5 Kontrollü ablasyon (tek seferde çok değişken değiştirme)
- **Aşama A:** Yalnızca **veri** değişsin → mmBERT eğit.
- **Aşama B:** Aynı veriyle **contrastive + FreeLB** ekle → yeniden eğit.
- Böylece hangi değişikliğin işe yaradığı ayrılır; makalede ayrı katkı olur.

### 5.6 Yapılmayacaklar
- Sentetik persona şablonları (benchmark sızıntısı: `Wulfric`/`medieval blacksmith` yasak).
- 687 etiket-çelişkisini otomatik silme (en zor örnekler).
- Benign'i tek taraflı doldurma.

---

## 6. Değerlendirme Protokolü ve Başarı Koşulları (ölçülebilir)

### 6.1 Benchmark hiyerarşisi (aşırı-uydurmayı önle)
1. **GENİŞLETİLMİŞ DEV benchmark:** Havuzdaki **tüm benzersiz** saldırılar (~1.400) + dolly masum (~14.500) dillere dağıtılıp NLLB ile çevrilir. İterasyon **yalnızca dev** üzerinde.
2. **FINAL TEST (dokunulmaz ve YETERİNCE BÜYÜK):**
   - **Yakın-kopya (near-dup) kümeleme** (MinHash/SimHash, eşik ~%90) yapılır ve **bölme kümeler düzeyinde** yapılır → aynı şablonun varyantları iki tarafa düşmez.
   - **Hedef: ≥300 benzersiz saldırı + ≥1.000 masum.** (rubend18'deki ~79 ile yetinilmez → CI ±11 puan olur.)
   - **Zor-masum bileşeni ZORUNLU:** güvenlik dokümanı, kod/markup, sistem-prompt/politika, saldırı açıklaması (dolly'nin kolay talimatına ek). Aksi halde **Recall@FP=1% iyimser ve eşik kararsız** olur.
   - Kaynaklar: Simsonsun (küme-ayrık) + rubend18 + diğer tutulmayan kaynaklar; benign: dolly + zor-benign.
3. **Kaynak-düzeyi sızıntı:** benchmark kaynakları eğitimle **0 ortak**; ayrıca near-dup kontrolü yapılır.
4. **NATIVE / İNSAN-YAZIMI çok dilli alt küme (kanıt için ZORUNLU):** `tr, ar, de, ru` için dil başına **50–100 native** örnek (**çeviri DEĞİL**). Çok dilli üstünlük iddiası **yalnızca bu alt kümede de tutarsa** savunulabilir; aksi halde **"çeviri artefaktı (translationese)"** çekincesi makalede yazılır.

### 6.2 Metrikler (gürültüye dayanıklı)
- **Birincil:** **Recall@FP=1%** (eşikten bağımsız) + **AUC** + bootstrap **%95 CI**.
- İkincil: Macro-F1 (CI ile), Recall/FP sabit eşikte.
- **Hold-out 15k kriteri KALDIRILDI** (rastgele bölme aynı kaynakları paylaşır; %97 yanıltıcı). Sadece bilgi amaçlı raporlanır.

### 6.3 Checkpoint/eşik seçimi
- Model seçimi **zor OOD dev** setinde (yalnızca val değil).
- Eşik dev setinde kalibre edilir; final test'e sabit uygulanır.

### 6.4 Başarı düzeyleri (üç kademe) — Patronus'a göre
Her metrik **aynı final testte**, aynı kalibrasyon protokolüyle **Patronus'a karşı** değerlendirilir:

1. **ÜSTÜN (superior):** Recall@FP=1% için **CI_alt(biz) > CI_üst(Patronus)**.
2. **DENK (non-inferior):** CI'lar örtüşür **ve** fark önceden yazılan marj içinde: `Recall@FP=1% ≥ Patronus − 2 puan` **ve** `AUC ≥ Patronus − 0.01`.
3. **BAŞARISIZ:** ne üstün ne denk.

**Ek zorunlu (Patronus karşılaştırmasından bağımsız):**
- AUC ≥ 0.960
- `ar` **nokta tahmin ≥ 85** ve **CI_alt ≥ 78**; `en` ≥ 80
- ru FP ≤ %6; tr recall ≥ %50
- Sızıntı: eğitim ↔ benchmark **tam + yakın-kopya = 0**
- 687 çelişki **silinmemiş**, audit raporunda; **50 örnek elle** incelenip gürültü oranı raporlanmış
- CPU ONNX ≤ 10 ms (mmBERT)

> **Not:** "AUC≥0.96 & ar≥80" **tek başına** başarı ilanı **değildir**; mutlaka **Patronus karşılaştırması** gerekir. "Patronus'u geç" değil; **üstün/denk/başarısız** kademeleri raporlanır.

### 6.5 Ölçüm kuralları ve Durma Kuralı (Ön-Kayıt)

**Ölçüm kuralları (veri/eğitimden önce sabit):**
- **Bootstrap KÜME düzeyinde:** aynı cümlenin 12 çevirisi bağımlıdır → **near-dup kümesi / benzersiz öğe** düzeyinde yeniden örnekle (satır düzeyinde DEĞİL).
- **Eşik şeffaflığı:** Recall@FP=1% iki şekilde raporlanır:
  - (a) final testte **oracle** eşik (yalnız bilgi),
  - (b) **dev'de seçilen** eşiğin final testteki **gerçek Recall/FP** (birincil).
- **FP=1% gürültüsü:** 1.000 masumda %1 = 10 örnek → gürültülü. **FP=2%** ve **pAUC** da raporlanır.
- **ar tanımı:** "ar ≥ 80" = **nokta tahmin ≥ 85, CI_alt ≥ 78** (yalnız alt sınır değil).
- **Patronus adilliği (sınırlama):** Patronus **2048 token + kendi eşiği**, biz **512**. Eğitim kaynakları kesin değil; final testin ona **sızıntısız olduğu garanti değil** → makalede sınırlama olarak yazılır.

**Durma kuralı:**

| Karar | Kural |
|---|---|
| **Birincil metrik** | Recall@FP=1% (final test, dev-eşiği) + AUC + **küme**-bootstrap %95 CI |
| **Karşılaştırma** | Patronus **aynı final test** + aynı eşik protokolü |
| **ÜSTÜN** | `CI_alt(biz) > CI_üst(Patronus)` (Recall@FP=1%) |
| **DENK** | CI örtüşür **ve** `Recall@FP=1% ≥ Patronus−2` **ve** `AUC ≥ Patronus−0.01` |
| **Aşama A durur** | Veri tek başına `AUC ≥ 0.955` **ve** `ar nokta ≥ 82` → B'ye geç |
| **Aşama A→C** | A hâlâ `AUC<0.955` veya `ar<82` ise → hata analizinin gösterdiği **spesifik** açığa C |
| **Aşama B durur** | `AUC ≥ 0.96` **ve** Recall@FP=1% **DENK/ÜSTÜN** → dur |
| **Aşama C durur** | 2 iterasyondan sonra ilerleme yoksa → dur, sınırlamaları yaz |
| **Asla** | Dev dışında iterasyon / final teste uyum için yeniden eğitim |

---

## 7. Diğer Ajan Nereye Bakmalı? (Dosya + Anahtar Değerler)

### 7.1 Eğitim verisi
- `data/v6_multilingual_supplement.json` (83.611): `label {1:34.063, 0:49.548}`, `src {mt:34.063, native:23.948}`, MT benign **25.600** (tier=2)
- `scripts/build_v6_multilingual_supplement.py`: `TGT_BEN_MT` (~30), `build_en_benign_3way()` (~136), `ok()` (len≤600, ~180)
- **v6.3'te eklenecek:** Arapça native (her iki sınıf aynı origin), counterfactual hard-neg, tr MT oranı düşürme

### 7.2 Notebook (veri fabrikası + QC)
- `notebooks/Master_Dataset_QC_and_Builder_v6.ipynb`: H2 benchmark, H4 MT (repo fallback/EVREN), H5 deterministik kota + şablon budama, H6 jüri+Qwen (OUT_OF_SCOPE sil / 687 silme), H7 parquet
- `scripts/build_v6_notebook.py`: Cell4 BLACKLIST, Cell5 `ATK_NAT/ATK_MT/BEN_NAT/BEN_MT` + `_src` fallback, Cell8 `FocalTrainer`
- Eğitim defterleri (`Train_*_v6.ipynb`): Cell3 `MASTER_READY`, Cell5 skip, Cell6 `read_parquet`, Cell12 3 benchmark

### 7.3 Benchmark
- `heldout_benchmark_v6_clean.json` → **kontamine** (jackhhao; Patronus eğitiminde) — sadece iç rapor
- `heldout_benchmark_v6_fair.json` → **dev** (2849; Simsonsun/rubend18/dolly)
- **v6.3'te:** **genişletilmiş dev** + **dokunulmaz final test**
- `notebooks/Build_Fair_Benchmark_v6.ipynb` → benchmark + 4 model kıyası

### 7.4 Ölçümler
- Adil @0.7: mmBERT 74.0/3.8/84.8/0.9494; Patronus 70.1/0.8/84.2/0.9767
- Hold-out: mmBERT 96.8, BGE 97.0, XLM-R 96.15 (bilgi amaçlı)
- CPU ONNX: mmBERT 8.09ms/266MB; BGE 24.27ms/543MB

---

## 8. Uygulama Sırası ve Gerçekçi Süre

| # | Adım | Süre |
|---|---|---|
| 1 | **Hata analizi + sızıntı kontrolü** | ~15 dk |
| 2 | **Genişletilmiş adil benchmark (dev + final test)** | ~30 dk |
| 3 | **ru/tr tam etiket denetimi (Qwen)** | ~15 dk |
| 4 | Eşleşmeli hard-neg + counterfactual + Arapça native | ~1,5 saat |
| 5 | **Aşama A:** mmBERT, yalnızca veri | ~30 dk |
| 6 | **Aşama B:** mmBERT + contrastive/FreeLB | **~1,5–2 saat** (FreeLB 3–4× yavaşlatır) |
| 7 | **Aşama C (KOŞULLU):** hata analizine göre açık kalan yere veri (kısa benign / tr-ar-ko native / insan-yazımı kaynak) | +2–3 saat |
| 8 | (koşullu) mmBERT yeniden eğitim | +~30 dk |

**Gerçekçi toplam: ~5–6 saat (A+B); Aşama C yalnızca A/B hedefi tutmazsa.** Önceki "30 dk" tahmini geçersiz.

---

## 9. Riskler ve Önlemler

| Risk | Önlem |
|---|---|
| Benign aşırı doldurma → recall↓ | Hedefli, ölçülü ekleme; native oranı korunur |
| Üretici-stili kısayolu | Counterfactual çift (aynı üretici/şablon) |
| Arapça: native benign + MT saldırı | Her iki sınıf aynı origin; yoksa sınırlama |
| Çok değişken | Aşama A (veri) / B (+loss) ayrı |
| Benchmark'a aşırı-uydurma | dev vs dokunulmaz final test |
| MT motoru asimetrisi | Eğitim tek motor (EVREN); benchmark NLLB |
| Qwen gürültüsü | Yalnız OUT_OF_SCOPE sil; çelişki logla |
| Overfitting (BGE örneği) | Adil/CI birincil; hold-out kriteri yok |

---

## 10. Tek Cümlelik Özet (diğer ajan için)
> v6.3 hata analizi **yürütüldü**: **sızıntı %0.1 (temiz)**, **uzunluk hipotezi elendi**, **FP'nin %98'i <150 char kısa benign**, **zayıf diller tr46/ko60/ar65 (dil yeteneği)**, MT çeşitliliği yüksek. → **Aşama A:** (1) kısa benign hard-neg, (2) tr/ar/ko native + tr native-ağırlıklı, (3) EN hedefli hard-neg → mmBERT. **Aşama B:** +contrastive/FreeLB. **Aşama C:** yalnızca gerekirse. Başarı: **Recall@FP=1% + AUC + küme-bootstrap CI** ile üstün/denk; **native alt küme** (tr/ar/de/ru) zorunlu. Uzun-jailbreak ve benchmark-yeniden-kur **kaldırıldı** (veri desteklemedi).
>
> **Makale konumlandırması (öneri):** "her metrikte geçtik" değil; **çok dilli dayanıklılık** (de +20, ja +21.7, zh +15.8 — CI dışı), **benchmark sızıntısı bulgusu**, **adil kaynak-ayrık değerlendirme**, **8 ms CPU gecikmesi**, **kontrollü ablasyonlar**.
>
> **⚠️ Ana risk / çekince:** Hem eğitim (EVREN-MT) hem benchmark (NLLB) **çeviri metin** içeriyor → "translationese" kısayolu olabilir; çok dilli farkların bir kısmı buradan gelebilir. Bu yüzden **native/insan-yazımı alt küme** (§6.1-4) zorunlu; orada da tutmazsa üstünlük iddiası **çeviri artefaktı** olarak sınırlandırılır. Ayrıca Patronus'un Türkçe/Korece'de düşük, Arapça'da çok yüksek çıkması NLLB-artefaktı şüphesini artırır.
