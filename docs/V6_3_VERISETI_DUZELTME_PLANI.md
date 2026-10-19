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

### 5.1 Arapça (ve zayıf diller) native takviye — EN YÜKSEK ÖNCELİK
- `ar` **saldırı ve masum aynı kaynak türünden** olmalı (native ise ikisi de native; MT ise ikisi de MT). Aksi halde aynı stil kısayolu Arapça'da doğar.
- Aday kaynaklar (eğitimde OLMAYAN, önce doğrulanacak): Arapça injection/guardrail setleri + Arapça native benign.
- **Hedef:** ar native oranı ≥%50; `ar` recall ±CI içinde ≥80, FP ≤%6.
- Kaynak bulunamazsa → **sınırlama yaz** (uydurma yok).

### 5.2 İngilizce saldırı çeşitliliği + hedefli hard-neg
- **Saldırı:** subtle/örtük jailbreak & injection; şablon çoğaltma yok.
- **Masum (hard-neg):** güvenlik dokümanı, kod/markup/konfig, sistem-prompt/politika, saldırı **açıklaması**, leksik benzer ama yönlendirmeyen masum. **Genel roleplay değil.**
- **+3.000–5.000** hedefli hard-neg (mevcut 15k'yı bozmadan, ölçülü).

### 5.3 Üretici-stili kısayolunu önle (counterfactual) — ZORUNLU
- Sentetik/LLM ile üretilen her hard-neg için **aynı üretici ve aynı şablonla eşleşen bir sentetik saldırı** üret (counterfactual çift). Yoksa *"LLM yazımı = masum"* kısayolu doğar (MT hatasının analogu).
- Augmentasyon (Unicode/homoglyph/Base64/leet/case) **her iki sınıfa eşit** uygulanır.

### 5.4 Türkçe: native-ağırlıklı (MT ≤ %30)
- v6.2'de tr benign %73 MT idi → tr recall düştü. **Geri al**; `halilneed` doğal hard-neg korunur.

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

### 6.2 Metrikler (gürültüye dayanıklı)
- **Birincil:** **Recall@FP=1%** (eşikten bağımsız) + **AUC** + bootstrap **%95 CI**.
- İkincil: Macro-F1 (CI ile), Recall/FP sabit eşikte.
- **Hold-out 15k kriteri KALDIRILDI** (rastgele bölme aynı kaynakları paylaşır; %97 yanıltıcı). Sadece bilgi amaçlı raporlanır.

### 6.3 Checkpoint/eşik seçimi
- Model seçimi **zor OOD dev** setinde (yalnızca val değil).
- Eşik dev setinde kalibre edilir; final test'e sabit uygulanır.

### 6.4 Başarı kriterleri (v6.3)
- [ ] **Recall@FP=1% (final test): Patronus'un CI üst sınırı içinde veya daha iyi** (yani "denk veya üstün").
- [ ] **AUC ≥ 0.960** (şu an 0.949; sıralama açığı kapanmalı).
- [ ] **ar recall (CI ile) ≥ 80**; **en ≥ 80**.
- [ ] ru FP ≤ %6; tr recall ≥ %50.
- [ ] Sızıntı: eğitim ↔ benchmark **tam+yakın-kopya = 0**.
- [ ] 687 çelişki **silinmemiş**, audit raporunda; **50 örnek elle** incelenip gürültü oranı raporlanmış.
- [ ] CPU ONNX ≤ 10 ms (mmBERT).

> **Not:** "Patronus'u geç" yerine **"CI içinde denk veya üstün, Recall@FP=1%'de daha iyi"** — dürüst ve savunulabilir.

### 6.5 Durma Kuralı (Ön-Kayıt / Pre-Registration)
Aşağıdakiler **veri/eğitim başlamadan sabitlenir** (sonradan değiştirilmez):

| Karar | Kural |
|---|---|
| **Birincil metrik** | Recall@FP=1% (final test) + AUC + bootstrap %95 CI |
| **Karşılaştırma** | Patronus aynı final testte ölçülür; CI'lar karşılaştırılır |
| **Dur (başarı)** | Recall@FP=1% CI_alt ≥ Patronus CI_üst **VEYA** AUC ≥ 0.96 ve ar ≥ 80 |
| **Aşama A durur** | Veri değişikliği tek başına AUC'yi ≥0.955'e çıkardıysa → B'ye geç |
| **Aşama A→C** | A hâlâ AUC<0.955 veya ar<80 ise → hata analizinin gösterdiği **spesifik** açığa C uygulanır (körlemesine veri eklenmez) |
| **Aşama B durur** | AUC ≥0.96 ve Recall@FP=1% Patronus CI'sına girdiyse → dur |
| **Aşama C durur** | 2 iterasyondan sonra ilerleme yoksa → dur, sınırlamaları yaz |
| **Asla** | Benchmark'a uyum için tekrar tekrar eğitim (dev dışında iterasyon yok) |

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
| 7 | **Aşama C (KOŞULLU):** hata analizinin gösterdiği açığa göre veri ekleme (uzun EN jailbreak / Arapça native / yeni insan-yazımı kaynak) | +2–3 saat |
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
> v6.3: **önce hata analizi** (uzunluk + ru/tr etiket gürültüsü + **MT-tohum çeşitliliği** + sızıntı), sonra **küme-bazlı bölünmüş genişletilmiş dev** ve **≥300 saldırı/≥1.000 masum + zor-benign içeren dokunulmaz final test**; ru/tr tam Qwen denetimi; Arapça native (her iki sınıf aynı origin), counterfactual-eşleşmeli hedefli hard-neg, tr native-ağırlıklı; **Aşama A yalnız veri → Aşama B +contrastive/FreeLB → (koşullu) Aşama C**; **ön-kayıtlı durma kuralı** (Recall@FP=1% + AUC + bootstrap CI; "Patronus'a CI içinde denk veya üstün"). Hold-out kriteri kaldırıldı. Mevcut: mmBERT adil F1 84.8 / AUC 0.949; Patronus 84.2 / 0.977 (kontamine 86.9 sızıntıydı).
>
> **Makale konumlandırması (öneri):** "her metrikte geçtik" değil; **çok dilli dayanıklılık** (de +20, ja +21.7, zh +15.8 — CI dışı), **benchmark sızıntısı bulgusu**, **adil kaynak-ayrık değerlendirme**, **8 ms CPU gecikmesi**, **kontrollü ablasyonlar**.
