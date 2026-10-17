# 🛡️ NeuralShield-v6.2: Kapsamlı Durum Analizi, Canlı Veri Ölçümleri ve Sıfır-Sızıntılı Final Eylem Planı

**Tarih:** 17 Ekim 2026  
**Sürüm:** `v6.2 (Nihai Mutabakat — Canlı Cell 3/5 Veri Ölçümleri Doğrulanmış)`  
**Durum:** 3 Omurga (`XLM-RoBERTa-base`, `mmBERT-base`, `BGE-M3`) İlk Ablasyon Eğitimi Tamamlandı — Metodolojik Düzeltmeler ve Kaynak/Motor-Ayrık (Source & Engine-Disjoint) Benchmark Aşaması

---

## 1. Mevcut Durum Özeti ve Canlı Veri Ölçümleri

### 1.1. İlk Tur 3 Omurga Eğitim Sonuçları (Google Drive `checkpoint-6555` Kayıtlı)
100.000 örneklik (50k Saldırı / 50k Masum, 12 Dil) ilk v6 veri setimiz üzerinde üç omurga eğitilmiş ve ağırlıkları Google Drive'a yedeklenmiştir:

| Metrik | **XLM-RoBERTa-base** (278M) | **mmBERT-base** (307M) | **BGE-M3** (568M) |
| :--- | :---: | :---: | :---: |
| **Eğitim Süresi (Colab GPU)** | **14.65 dk** | 31.02 dk | 42.76 dk |
| **Hold-out Test (15k) Macro-F1** | %95.95 | **%96.65** 🥇 | %96.45 |
| **Hold-out Test (15k) ROC-AUC** | 0.9943 | **%0.9962** 🥇 | 0.9954 |
| **OOD-2000 Recall / FP (th=0.5)** | %92.1 / %9.2 | **%95.6** / %11.6 | %94.3 / **%8.9** |
| **OOD-2000 Recall / FP (th=0.7)** | %90.1 / %7.8 | **%94.0** / %8.9 | %93.5 / **%6.9** |
| **OOD-2000 Macro-F1 (th=0.7)** | %91.15 | %92.55 | **%93.30** 🥇 |
| **Mosscap+NotInject Stres (1070) Recall** | %98.4 | %98.8 | **%99.6** 🥇 |

### 1.2. Çalışmış Notebook (`Cell 3` & `Cell 5`) Canlı Veri Ölçümleri (Doğrulanmış Rakamlar)
Tahmin yerine doğrudan `notebooks/calismis/Train_mmBERT_v6.ipynb` çıktılarından ve `data/v6_multilingual_supplement.json` dosyasından ölçülen kesin sayılar:
1. **Doğal Türkçe Saldırı Havuzu (`Cell 3` -> `Cell 5`):**
   * `3nesdeniz/turkish-conversation-prompt-injection`: `100` saldırı (`430` masum)
   * `AltaySec/turkish-llm-injection`: `299` saldırı
   * `halilneed/turkish-prompt-injection-benchmark`: `312` saldırı (`3.016` masum)
   * Çok dilli setlerden (`rikka-snow` vb.) gelen Türkçe saldırılar: `~299` saldırı
   * **Toplam Doğal Türkçe Saldırı (`A_by['tr']`):** Tam **`1.010`** örnek (`%6.7`).
   * **EVREN-MT Türkçe Saldırı (`supplement`):** Tam **`14.186`** örnek (`%93.3` — purge sonrası).
2. **Doğal Türkçe Masum Havuzu (`Cell 3`):**
   * Günlük/Sohbet: `TFLai` (`79.406`), `merve` (`51.530`), `kilicai` (`8.469`), `3nesdeniz/daily` (`3.950`), `emreseyhan` (`2.694`).
   * Doğal Türkçe Hard-Negative / False-Alarm: `halilneed/turkish-prompt-injection-benchmark[benign]` (`3.016`) + `halilneed/turkish-prompt-injection-false-alarm-benchmark` (`2.836`) = **`5.852`** doğal Türkçe zor-negatif masum!
   * **EVREN-MT Türkçe Masum (`supplement`):** **`0`** örnek (`%0` MT!).
3. **Diğer 10 Dil (`de, fr, es, it, pt, ru, ar, ja, ko, zh`) `supplement` Dağılımı:**
   * **Saldırı (`label=1`):** Dil başına `~1.908 – 1.997` örnek (**%100 EVREN-MT**; yalnız Rusça'da `Cell 3` içinde `dmtrdr/russian_prompt_injections` kaynaklı `21.278` yerel Rusça saldırı mevcuttur).
   * **Masum (`label=0`):** Dil başına `1.995 – 2.500` örnek (**%0 MT** — tamamı `oasst2` ve `aya_dataset` doğal insan metni!).
4. **İngilizce (`en`) Kaynak Havuzu Büyüklüğü (Çeviriye Kaynaklık Edecek Havuz):**
   * **Hard-Negative / Güvenlik Odaklı EN Masumlar:** `SPML[benign]` (`3.436`) + `S-Labs[benign]` (`6.263`) + `PromptShield[benign]` (`8.644`) + `tool-response[benign]` (`5.398`) + `agentic[benign]` (`1.741`) + `guardrail-hard-negatives` (`1.249`) + `xstest` (`424`) + `safe-guard[benign]` (`5.740`) + `NotInject` (`339`) = **`33.234` saf EN Hard-Negative Masum** (ek olarak `guychuk[benign]` içinde `20.519` genel/karma masum ve yerel `data/_appsec_pool_benign.json` içinde `12.960` EN masum mevcuttur).
   * **Roleplay / Persona EN Masumlar:** `fka/prompts.chat` (`1.607`) + `ultrachat_200k` / `oasst2` içindeki `"You are / Act as"` masumlar (`>10.000`).
   * **Genel / Günlük EN Masumlar:** `oasst2` (`114.221`) + `ultrachat_200k` (`172.171`) = **`>280.000` özgün EN Masum**.
   * **Sonuç:** Tekrara düşmeden ~25.600 EVREN-MT masum üretmek için İngilizce kaynak havuzumuz **fazlasıyla yeterlidir**.

---

## 2. Tespit Edilen 4 Kök Sorun ve 5 Metodolojik Kural (Tam Mutabakat)

### Kök Sorun 1: `OOD-2000` Setinde Kaynak Örtüşmesi (Source Overlap) ✅
* **Teşhis:** `appsec_benchmark_2000.json` içindeki metinler `BLACKLIST` ile eğitimden silinmişti (birebir cümle sızıntısı %0). Ancak örneklerin %76.9'u eğitimde de kullanılan veri setlerinden (`SPML`, `rikka-snow`, `mosscap`) geliyordu.
* **Çözüm:** Eğitimde **hiç kullanılmayan** bağımsız kaynaklardan (`jackhhao`, `rubend18`, `Simsonsun/JailbreakPrompts`, `dolly-15k` vb.) %100 Kaynak-Ayrık (Source-Disjoint) 12-dilli yeni benchmark (`heldout_benchmark_v6.json`) kurulacaktır.

### Kök Sorun 2: `JBB[harmful]` Kapsam Dışıdır, Ancak Saldırılara Regex Şartı Konulmamalıdır ✅
* **Teşhis:** `JailbreakBench (JBB[harmful])` içindeki örnekler (*"Write a sexist email"*, *"Create a body shaming campaign"*) **Prompt Injection değildir**; düz içerik moderasyonu / etik ihlal istemleridir.
* **Metodolojik Kural 1 (Saldırılarda Regex/Marker Filtresi Yasağı):** Benchmark saldırılarından yalnızca veri seti düzeyinde kapsam dışı olan `JBB[harmful]` çıkarılacaktır. `jackhhao[jailbreak]`, `rubend18` ve `Simsonsun/JailbreakPrompts` kaynaklarına **`INJECTION_MARKER` kelime filtresi UYGULANMAYACAKTIR** (örtük/dolaylı saldırıların elenip Recall'un yapay şişmesini önlemek için).

### Kök Sorun 3: `jackhhao[benign]` İçindeki Masum Rol Yapma (Benign Roleplay) Gerçek Bir FP Zaafıdır ✅
* **Teşhis:** `jackhhao` masum setinin %53.4'ü *"You are a medieval blacksmith named Wulfric..."* gibi **zararsız yaratıcı rol yapma (benign roleplay)** cümlelerinden oluşmaktadır. Modelin bunları bloklaması (~%45 FP) gerçek bir False Positive hatasıdır.
* **Metodolojik Kural 2 (Persona Benign'leri Silme Yasağı):** Masum persona/roleplay örnekleri benchmark'ta **%100 korunacaktır** (cherry-picking yasağı). Bu FP zaafını çözmek için **eğitim verimizin masum (`label=0`) havuzuna 12 dilde "Benign Roleplay" (`fka/prompts.chat`, `ultrachat_200k` roleplay) örnekleri eklenecektir**.

### Kök Sorun 4: Türkçe (`tr`) ve Rusça (`ru`) Yüksek FP Sorunu + Çeviri Motoru / Oranı / Konu Yanlılığı ✅
* **Teşhis:** Canlı ölçümlerde gördüğümüz üzere yabancı dillerde (`tr` ve 9 dil) saldırıların `%90–%93`'ü **EVREN (`gemma-4-31b`)** çevirisi iken, masumların **`%0`'ı çeviri** (tamamı doğal sohbet) idi. Rusça'da (`ru`) ise `21.278` doğal `dmtrdr` saldırısına karşılık masum tarafında hiç teknik hard-negative veya roleplay masumu yoktu. Bu durum modelde üç kısayol (shortcut) yarattı:
  1. **Motor Yanlılığı:** *"EVREN çeviri üslubu = Saldırıdır!"*
  2. **MT-Oranı Yanlılığı:** *"Çeviri kokan cümle = Saldırıdır!"*
  3. **Konu Yanlılığı:** *"İçinde SQL, şifre, sistem, talimat veya 'Sen bir ...sın / Ты ...' geçen cümle = Saldırıdır!"*

* **Metodolojik Kural 3 (Sınıf-İçi Homojen Çeviri Motoru & Çapraz Motor Doğrulaması):**
  1. **Eğitim İçi Motor Simetrisi:** Eğitimdeki mevcut saldırılar **EVREN (`gemma-4-31b`)** ile çevrildiği için, eğitime eklenecek yeni **Masum (`label=0`)** MT takviyesi de **AYNI MOTORLA (EVREN `gemma-4-31b`)** çevrilecektir. (Eğitimde saldırı=EVREN, masum=NLLB yapmak kesinlikle yasaktır).
  2. **Eğitim vs. Benchmark Motor Ayrımı + Kalite Kontrolü:** Dış benchmark (`heldout_benchmark_v6.json`) her iki sınıf için **NLLB-200 (`facebook/nllb-200-distilled-600M`)** kullanacaktır (eğitim-test motor imzası sızıntısını önlemek için). Ancak NLLB çeviri kalitesinin metrikleri bozup bozmadığını doğrulamak için **dil başına 40 örneklik (20 saldırı + 20 masum) bir alt-küme EVREN ile de çevrilip iki motor arasındaki fark makalede şeffafça raporlanacaktır**.

* **Metodolojik Kural 4 (Sınıf-İçi MT-Oranı Dengesi ve 3'lü Konu Karışımı):**
  1. **3'lü Konu Karışımı (Yeni Kısayolu Önleme):** Eğer EVREN ile çevrilen masumların tamamı sadece *hard-negative* ve *roleplay* olursa, model bu kez *"EVREN çevirisi + günlük konu = ??"* bölgesinde yanılabilir. Bu nedenle üretilecek EVREN-MT masum paketi şu **3'lü dengeli karışımdan** oluşacaktır:
     * **%40 Teknik Hard-Negative Masum** (`SPML[benign]`, `safe-guard[benign]`, `NotInject`, `PromptShield[benign]`, `guardrail-hard-negatives`)
     * **%30 Benign Roleplay / Persona** (`fka/prompts.chat`, `ultrachat_200k` `"You are / Act as"` masumları)
     * **%30 Genel / Günlük Talimat Masumu** (`oasst2`, `ultrachat_200k` genel EN istemleri)
  2. **Dil Grubuna Göre Doğal (Native) vs. EVREN-MT Oran Simetrisi:**
     * **Türkçe (`tr`):** Saldırılar MT-ağırlıklı (`%93.3 MT`) olduğu için masumlar da MT-ağırlıklı (`%73.3 MT`) yapılırken `4.000` doğal Türkçe masum korunur.
     * **Rusça (`ru` — Doğal Veri Zengini İstisna):** Rusça'da `dmtrdr` (`21.278` doğal saldırı) ve `oasst2/aya` (`2.500` doğal masum) bulunduğu için Rusça **Native-Ağırlıklı Simetrik** kurgulanır: Hem saldırı hem masum **`1.600–1.800` Doğal (%80–90) + `200–400` EVREN-MT (%10–20)** olarak eşitlenir! Böylece değerli doğal Rusça verisi çöpe atılmaz, MT oranı iki sınıfta da simetrik (`%10–20`) olur ve eklenen EVREN-MT masumlar Rusça'daki eksik hard-negative/roleplay boşluğunu doldurur.
     * **Diğer 9 Dil (`de,fr,es,it,pt,ar,ja,ko,zh`):** Saldırılar MT-ağırlıklı (`%90+ MT`) olduğu için masumlar da MT-ağırlıklı (`400 Doğal + 1.600 EVREN-MT = %80 MT`) yapılır.

| Dil Grubu | Saldırı Yapısı (`TGT_ATK`) | Yeni Deterministik Masum Kotası (`TGT_BEN`) | Saldırı / Masum MT Simetrisi |
| :--- | :--- | :--- | :---: |
| **`tr` (15.000)** | `1.010` Doğal (%7) + `13.990` EVREN-MT (%93) | **`4.000` Doğal** *(2.000 `halilneed` doğal hard-neg + 2.000 doğal diyalog)* **+ `11.000` EVREN-MT** *(4.4k Hard-Neg + 3.3k Roleplay + 3.3k Genel)* | **%93 vs %73 MT** *(P(Atk\|MT)=0.56)* |
| **`ru` (2.000 — Native-Ağırlıklı)** | **`1.800` Doğal (`dmtrdr`) + `200` EVREN-MT (%10 MT)** | **`1.800` Doğal (`oasst2/aya`) + `200` EVREN-MT** *(100 Hard-Neg + 60 Roleplay + 40 Genel)* | **%10 vs %10 MT** *(Tam Simetrik & Doğal Korunmuş)* |
| **`de,fr,es,it,pt,ar,ja,ko,zh` (9 Dil, 2.000/dil)** | `~50–200` Doğal + `~1.800–1.950` EVREN-MT (%90+ MT) | **`400` Doğal (`oasst2/aya`) + `1.600` EVREN-MT** *(640 Hard-Neg + 480 Roleplay + 480 Genel)* | **~%90 vs %80 MT** *(Dengeli, P(Atk\|MT)≈0.53)* |

* **Metodolojik Kural 5 (`Cell 5` Deterministik Alt-Kota Mekanizması):**
  * `Cell 5` içinde doğal havuz (`A_by`, `B_by`) ile `supplement` havuzu rastgele birleştirilip kırpılmayacaktır (`cap_to` öncesi rastgele erime yasağı).
  * Yukarıdaki tablodaki **Doğal** ve **EVREN-MT** sayıları `Cell 5` içinde iki ayrı alt-liste (`native_pool` ve `mt_pool`) olarak deterministik dilimlenip birleştirilecektir (`tr` masum: `4.000 doğal + 11.000 MT`; `ru` saldırı ve masum: `1.800 doğal + 200 MT`; diğer 9 dil masum: `400 doğal + 1.600 MT`).

---

## 3. Uygulama Planı (4 Adım)

### Adım 1: Kaynak ve Çeviri Motoru Ayrımı Tablosu

| Grup | Veri Setleri | Çeviri Motoru (11 Dil) | Kullanım Yeri |
| :--- | :--- | :---: | :--- |
| **🔒 Grup A: Dokunulmaz Dış Test (True OOD Benchmark)** | **Saldırı:** `jackhhao[jailbreak]` + `rubend18` + `Simsonsun/JailbreakPrompts` *(+ doğrulanırsa tutulmayan indirect/evaded aday kaynak; Regex filtresiz, `JBB[harmful]` hariç)*<br>**Masum:** `jackhhao[benign]` *(Persona dahil!)* + `databricks-dolly-15k` *(+ doğrulanırsa tutulmayan hard-neg aday kaynak)* | **NLLB-200 (600M)**<br>*(+ 40 örnek/dil EVREN çapraz kalite kontrolü)* | **SADECE `heldout_benchmark_v6.json`** (12 dil × 240 = 2.880 örnek).<br>❌ Eğitimde kesinlikle kullanılmaz! |
| **🧬 Grup B: Eğitim Havuzu (100k)** | Mevcut 26 Saldırı + 19 Masum Eğitim Seti<br>**+ EVREN-MT 3'lü Masum Paketi** *(Hard-Neg + Roleplay + Genel)* | **EVREN (`gemma-4-31b`)**<br>*(Hem Saldırı MT hem Masum MT aynı motor ve dengeli oran!)* | **Eğitim (50k/50k Havuz)** içinde kullanılır.<br>🔒 Benchmark metinleri `BLACKLIST` ile %100 purge edilir. |

> **Şeffaf Akademik Sınırlama Notu (Limitations):** Üretim öncesinde eğitimde kullanılmayan ek hard-negative / indirect kaynak adayları (`Mindgard/evaded-prompt-injection-and-jailbreak-samples` vb.) HuggingFace üzerinden kontrol edilecektir. Uygun ve temiz ayrık kaynak bulunursa Grup A'ya eklenecek; bulunamazsa `heldout_benchmark_v6.json` setinin ağırlıklı olarak doğrudan jailbreak/roleplay odaklı olduğu, indirect/stego ve zor-negatif sınır stresinin ise `STRESS-1070 (Mosscap+NotInject)` cetvelinde ölçüldüğü makalede açıkça belirtilecektir.

---

### Adım 2: `heldout_benchmark_v6.json` Setinin Sıfırdan Üretilmesi
Eski `heldout_benchmark_v6_colab.json` dosyası kesinlikle kullanılmayacaktır. Sıfırdan şu kurallarla üretilir:
1. `JBB[harmful]` tamamen hariç tutulur; Grup A saldırı kaynaklarından **hiçbir `INJECTION_MARKER` regex filtresi uygulanmadan** `SEED=42` ile homojen **120 EN saldırı** seçilir.
2. Grup A masum kaynaklarından (**persona/roleplay örnekleri silinmeden!**) homojen **120 EN masum** seçilir.
3. Her iki sınıf da aynı motorla (`NLLB-200`) 11 dile çevrilerek **12 dil × (120 Saldırı + 120 Masum) = 2.880 örneklik** `data/heldout_benchmark_v6.json` oluşturulur (ayrıca dil başına 40 örnek EVREN ile de çevrilerek motor-farkı duyarlılık analizi kaydedilir).

---

### Adım 3: Eğitim Masum Havuzunun EVREN (`gemma-4-31b`) ile Üretilmesi
Kural 4 tablosuna uygun olarak toplam **`25.600` EVREN-MT Masum (`label=0`)** örneği (`tr`: `11.000`, `ru`: `200`, diğer 9 dil: `9 × 1.600 = 14.400`) üretilir:
1. `Cell 3` kaynaklarından `BLACKLIST` dışı **11.000 özgün EN masum** (%40 Hard-Neg + %30 Roleplay + %30 Genel, `len<=600`) seçilir.
2. Tamamı Türkçe'ye (`11.000`), içinden `200` tanesi Rusça'ya (`ru`) ve `1.600`'er tanesi diğer 9 dile (`14.400`) **EVREN (`gemma-4-31b`, `B=8, workers=6`)** ile çevrilip `data/v6_multilingual_supplement.json` dosyasına kaydedilir.

---

### Adım 4: `Cell 5` Deterministik Kota Güncellemesi ve 3 Omurga Yeniden Eğitimi
1. Üç eğitim notebook'unun (`Train_XLM_RoBERTa_v6.ipynb`, `Train_mmBERT_v6.ipynb`, `Train_BGE_M3_v6.ipynb`) **Cell 4 & Cell 5** hücrelerinde:
   * `BLACKLIST` listesine `data/heldout_benchmark_v6.json` eklenir.
   * Kural 4 ve Kural 5'teki deterministik alt-kotalar (`tr` masum: 4.000 doğal + 11.000 EVREN-MT; `ru` saldırı & masum: 1.800 doğal + 200 EVREN-MT; 9 dil masum: 400 doğal + 1.600 EVREN-MT) kodlanır.
2. Colab GPU üzerinde 3 model yeniden eğitilir ve her model **3 Benchmark** (`Hold-out 15k`, `OOD-2000 + Stress-1070`, `Heldout-v6 2880`) üzerinde raporlanır.

---

## 4. Nihai Karar Özeti (v6.2)

1. ✅ **Kural 1 (Regex Yasağı):** Benchmark saldırılarından sadece `JBB[harmful]` çıkarılır, `INJECTION_MARKER` şartı aranmaz.
2. ✅ **Kural 2 (Persona Benign Korunur):** Benchmark'tan masum roleplay silinmez; eğitime 12 dilde masum roleplay eklenir.
3. ✅ **Kural 3 (Motor Simetrisi + Çapraz Kontrol):** Eğitimde Saldırı ve Masum MT aynı motoru (`EVREN`) kullanır; benchmark `NLLB-200` (+ 40 örnek/dil EVREN duyarlılık kontrolü) ile sıfırdan üretilir.
4. ✅ **Kural 4 (MT-Oranı Dengesi & 3'lü Konu Karışımı):** `tr` masum `4.000 Doğal + 11.000 EVREN-MT (%73.3 MT)`, **`ru` hem saldırı hem masum `1.800 Doğal + 200 EVREN-MT (%10 MT — Native-Ağırlıklı Simetrik)`**, diğer 9 dil masum `400 Doğal + 1.600 EVREN-MT (%80 MT)` olur ve MT masumlar **%40 Hard-Neg + %30 Roleplay + %30 Genel** karışımından oluşur.
5. ✅ **Kural 5 (Deterministik Alt-Kota):** `Cell 5` içinde doğal ve MT havuzları rastgele kırpılmaz, deterministik alt-kotayla birleştirilir.

