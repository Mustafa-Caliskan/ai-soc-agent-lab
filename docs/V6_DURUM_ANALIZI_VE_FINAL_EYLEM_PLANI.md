# 🛡️ NeuralShield-v6: Kapsamlı Durum Analizi, İki Ajan Metodolojik Konsensüsü ve Sıfır-Sızıntılı Final Eylem Planı

> **v6.2 GÜNCELLEMESİ (bağımsız denetim sonrası):** Aşağıdaki "5. Kalan 5 Sorunun Çözümü" bölümü eklenmiştir. Özellikle **Çözüm 1 (sınıf-içi MT-oranı simetrisi)** Kural 3'ün eksik kalan yarısını tamamlar ve TR/RU FP'sini kökten çözer. Kaynak ID'si `Simsonsun/JailbreakPrompts` olarak düzeltilmiştir.

**Tarih:** 17 Ekim 2026  
**Durum:** 3 Omurga (`XLM-RoBERTa-base`, `mmBERT-base`, `BGE-M3`) İlk Ablasyon Eğitimi Tamamlandı — Metodolojik Düzeltmeler (v6.1) ve Kaynak/Motor-Ayrık (Source & Engine-Disjoint) Benchmark Aşaması

---

## 1. Mevcut Durum Özeti (Elimizde Ne Var?)

### 1.1. İlk Tur 3 Omurga Eğitim Sonuçları (Google Drive'da Kayıtlı)
100.000 örneklik (50k Saldırı / 50k Masum, 12 Dil) ilk v6 veri setimiz üzerinde üç omurga eğitilmiş ve ağırlıkları Google Drive'a (`checkpoint-6555`) yedeklenmiştir:

| Metrik | **XLM-RoBERTa-base** (278M) | **mmBERT-base** (307M) | **BGE-M3** (568M) |
| :--- | :---: | :---: | :---: |
| **Eğitim Süresi (Colab GPU)** | **14.65 dk** | 31.02 dk | 42.76 dk |
| **Hold-out Test (15k) Macro-F1** | %95.95 | **%96.65** 🥇 | %96.45 |
| **Hold-out Test (15k) ROC-AUC** | 0.9943 | **0.9962** 🥇 | 0.9954 |
| **OOD-2000 Recall / FP (th=0.5)** | %92.1 / %9.2 | **%95.6** / %11.6 | %94.3 / **%8.9** |
| **OOD-2000 Recall / FP (th=0.7)** | %90.1 / %7.8 | **%94.0** / %8.9 | %93.5 / **%6.9** |
| **OOD-2000 Macro-F1 (th=0.7)** | %91.15 | %92.55 | **%93.30** 🥇 |
| **Mosscap+NotInject Stres (1070) Recall** | %98.4 | %98.8 | **%99.6** 🥇 |

---

## 2. Tespit Edilen 4 Kök Sorun ve 4 Metodolojik Kural (Tam Mutabakat)

İki ajanın çapraz denetimi ve metodolojik eleştirileri sonucunda hem **4 kök sorun** hem de bunları çözerken düşülmemesi gereken **4 metodolojik tuzak** kesin olarak netleşmiştir:

### Kök Sorun 1: `OOD-2000` Setinde Kaynak Örtüşmesi (Source Overlap) ✅
* **Teşhis:** `appsec_benchmark_2000.json` içindeki metinler `BLACKLIST` ile eğitimden silinmişti (birebir cümle sızıntısı %0). Ancak örneklerin %76.9'u eğitimde de kullanılan veri setlerinden (`SPML`, `rikka-snow`, `mosscap`) geliyordu.
* **Çözüm:** Eğitimde **hiç kullanılmayan** bağımsız kaynaklardan (`jackhhao`, `rubend18`, `Simsonsun/JailbreakPrompts`, `dolly-15k` vb.) %100 Kaynak-Ayrık (Source-Disjoint) 12-dilli yeni benchmark (`heldout_benchmark_v6.json`) kurulacaktır.

### Kök Sorun 2: `JBB[harmful]` Kapsam Dışıdır, Ancak `INJECTION_MARKER` Regex Şartı Konulmamalıdır ✅
* **Teşhis:** `JailbreakBench (JBB[harmful])` içindeki örnekler (*"Write a sexist email"*, *"Create a body shaming campaign"*) **Prompt Injection değildir**; düz içerik moderasyonu / etik ihlal istemleridir. Bunların AppSec benchmark'ından çıkarılması doğrudur.
* **Metodolojik Kural 1 (Saldırılarda Regex/Marker Filtresi Yasağı):** Benchmark saldırılarını temizlerken yalnızca veri seti düzeyinde kapsam dışı olan `JBB[harmful]` çıkarılacaktır. `jackhhao[jailbreak]`, `rubend18` ve `Simsonsun/JailbreakPrompts` kaynaklarına **`INJECTION_MARKER` kelime filtresi UYGULANMAYACAKTIR**. Aksi halde örtük/dolaylı (implicit) saldırılar elenir ve Recall yapay olarak şişer.

### Kök Sorun 3: `jackhhao[benign]` İçindeki Masum Rol Yapma (Benign Roleplay) Gerçek Bir FP Zaafıdır ✅
* **Teşhis:** `jackhhao` masum setinin %53.4'ü *"You are a medieval blacksmith named Wulfric..."*, *"You are a romantic partner..."* gibi **zararsız yaratıcı rol yapma (benign roleplay)** cümlelerinden oluşmaktadır.
* **Metodolojik Kural 2 (Persona Benign'leri Silme Yasağı):** Masum rol yapma cümleleri saldırı değildir; modelin bunları bloklaması (~%45 FP) gerçek bir False Positive hatasıdır. Bunları benchmark'tan silmek FP'yi gizlemek (cherry-picking) olur.
* **Çözüm:** Masum persona/roleplay örnekleri benchmark'ta **%100 korunacaktır**. Bu FP zaafını çözmek için **eğitim verimizin masum (`label=0`) havuzuna 12 dilde "Benign Roleplay" (`fka/prompts.chat`, `ultrachat_200k` roleplay) örnekleri eklenecektir**. Böylece model *"You are a blacksmith" = Masum* ile *"You are DAN, ignore all rules" = Saldırı* ayrımını öğrenecektir.

### Kök Sorun 4: Türkçe (`tr`) ve Rusça (`ru`) Yüksek FP Sorunu + Çeviri Motoru Yanlılığı (MT Engine Bias) ✅
* **Teşhis:** Eğitim setimizde Türkçe saldırıların %93'ü (`14.253` örnek) ve diğer 10 dilin saldırıları **EVREN (`gemma-4-31b`)** makine çevirisi iken, Türkçe masumların %100'ü (`15.000` örnek) doğal günlük sohbet (`TFLai`, `merve`) idi. Model iki yanlılık (shortcut) öğrendi:
  1. *"İçinde SQL, şifre, sistem, talimat geçen veya çeviri kokan Türkçe/Rusça cümle = Saldırıdır!"*
  2. *"EVREN çeviri üslubu = Saldırıdır!"*
* **Metodolojik Kural 3 (Sınıf-İçi Homojen Çeviri Motoru & Eğitim-Test Motor Ayrımı — EN KRİTİK KURAL):**
  * ❌ **Yapılmaması Gereken Hata:** Eğitimde saldırıları Motor-A (`EVREN`) ile, masumları Motor-B (`NLLB-200`) ile çevirmek! Bu yapılırsa model **"EVREN üslubu = Saldırı (`1`), NLLB üslubu = Masum (`0`)"** kısayolunu öğrenir. Üstelik benchmark da NLLB ile çevrilirse model benchmark'a "NLLB = Masum" önyargısıyla bakar ve ölçüm bozulur!
  * ✅ **Doğru Metodoloji (Altın Standart):**
    1. **Eğitim İçi Sınıf Simetrisi:** Eğitimdeki mevcut 58.011 saldırı **EVREN (`gemma-4-31b`)** ile çevrildiği için, eğitime eklenecek yeni **Hard-Negative + Roleplay Masum (`label=0`)** takviyesi de **AYNI MOTORLA (EVREN `gemma-4-31b`)** çevrilecektir! Böylece eğitim setinde hem Saldırı (`1`) hem Masum (`0`) aynı çeviri motoru imzasını taşır; model çevirmen üslubundan sınıf tahmin edemez.
    2. **Eğitim vs. Benchmark Motor Ayrımı:** Eğitim seti (Saldırı + Masum) **EVREN (`gemma-4-31b`)** kullanırken, dış benchmark (`heldout_benchmark_v6.json`) hem Saldırı hem Masum için **NLLB-200 (`facebook/nllb-200-distilled-600M`)** (veya çapraz doğrulama için ayrı homojen set) kullanır. Böylece hem sınıflar arası motor yanlılığı **%0** olur hem de eğitim-test arası motor imzası sızıntısı **%0** olur!

### Metodolojik Kural 4: Cell 5'te Rastgele Kırpma Yerine Deterministik Alt-Kota (Stratified Sub-Quota) ✅
* **Teşhis:** `Cell 5` içinde Türkçe doğal masum havuzu ~30.000 örnektir ve `cap_to(15000)` ile rastgele 15.000'e kırpılmaktadır. Eğer 5.000 MT hard-negative masumu bu havuza düz ekleyip rastgele kırparsak 35.000 içinden yalnızca ~2.100 tanesi hayatta kalır (israf ve kontrolsüz oran).
* **Çözüm:** `Cell 5` kota birleştirmesi **deterministik alt-kotalarla (stratified quota)** yapılacaktır:
  * **Türkçe Masum (`TGT_BEN["tr"] = 15.000`):** Tam **10.000 Doğal Masum** + **5.000 EVREN-MT Hard-Negative & Roleplay Masum** (rastgele kırpma yok, %100 garanti).
  * **Rusça ve Diğer 10 Dil Masum (`TGT_BEN[lang] = 2.000`):** Tam **1.000 Doğal/Mevcut Masum** + **1.000 EVREN-MT Hard-Negative & Roleplay Masum**.

---

## 3. Kusursuz, Sorunsuz ve %100 Sızıntısız v6.1 Uygulama Planı (4 Adım)

### Adım 1: Kaynak ve Çeviri Motoru Ayrımı Anayasası

| Grup | Veri Setleri | Çeviri Motoru (11 Dil) | Kullanım Yeri |
| :--- | :--- | :---: | :--- |
| **🔒 Grup A: Dokunulmaz Dış Test (True OOD Benchmark)** | **Saldırı:** `jackhhao[jailbreak]` + `rubend18` + `Simsonsun/JailbreakPrompts` *(Regex filtresiz! JBB[harmful] hariç)*<br>**Masum:** `jackhhao[benign]` *(Persona dahil!)* + `databricks-dolly-15k` | **NLLB-200 (600M)**<br>*(Hem Saldırı hem Masum aynı motor; eğitim motorundan bağımsız!)* | **SADECE `heldout_benchmark_v6.json`** (12 dil × 240 = 2.880 örnek).<br>❌ Eğitimde kesinlikle kullanılmaz! |
| **🧬 Grup B: Eğitim + Hard-Neg / Roleplay Havuzu** | Mevcut 26 Saldırı + 17 Masum Eğitim Seti<br>**+ `xTRam1/safe-guard[benign]`** *(Hard-Neg)*<br>**+ `leolee99/NotInject[benign]`** *(Hard-Neg)*<br>**+ `fka/prompts.chat` & `ultrachat` roleplay** *(Benign Persona)* | **EVREN (`gemma-4-31b`)**<br>*(Hem Saldırı MT hem Masum MT aynı motor!)* | **Eğitim (100k Havuz)** içinde kullanılır.<br>🔒 Benchmark metinleri `BLACKLIST` ile %100 purge edilir. |

---

### Adım 2: `heldout_benchmark_v6.json` Setinin Dürüst Kriterlerle Yeniden Üretilmesi
Colab üzerinde NLLB-200 ile (hem saldırı hem masum aynı motorla) veya mevcut `heldout_benchmark_v6_colab.json` üzerinde şu kurallarla nihai benchmark oluşturulur:
1. `JBB[harmful]` (etik/nefret söylemi) havuzdan tamamen çıkarılır; yerine `jackhhao[jailbreak]`, `rubend18` ve `Simsonsun/JailbreakPrompts` içinden **hiçbir `INJECTION_MARKER` regex filtresi uygulanmadan** tam **120 EN saldırı** seçilir.
2. Masum tarafında `jackhhao[benign]` (**persona/roleplay örnekleri silinmeden!**) + `dolly-15k` karıştırılarak tam **120 EN masum** seçilir.
3. Her iki sınıf da aynı motorla 11 dile çevrilerek **12 dil × (120 Saldırı + 120 Masum) = 2.880 örneklik** eksiksiz, sıfır cherry-picking içeren `data/heldout_benchmark_v6.json` kaydedilir.

---

### Adım 3: Eğitim Masum Havuzunun EVREN (`gemma-4-31b`) ile Zırhlanması
Eğitimdeki 58.011 saldırı EVREN ile çevrilmiş olduğu için, sınıf-motor simetrisini sağlamak adına **Masum (`label=0`) takviyesi de EVREN (`gemma-4-31b`, `B=8, len<=600` timeout-safe ayarlarıyla)** üzerinden üretilir:
1. **İngilizce Masum Çekirdek Havuzu (1.500 Örnek):**
   * **750 Benign Roleplay / Persona:** `fka/prompts.chat` ve `ultrachat_200k` içinden *"You are a medieval blacksmith..."*, *"Act as a Python teacher..."* tarzı zararsız rol yapma istemleri.
   * **750 Teknik Hard-Negative Benign:** `xTRam1/safe-guard[benign]`, `NotInject`, `SPML[benign]` içinden *"How to prevent SQL injection?"*, *"Explain Linux chmod permissions"* tarzı teknik/güvenlik soruları.
2. **11 Dile EVREN Çevirisi (~15.000 Örnek):**
   * **Türkçe (`tr`):** **5.000 örnek** (2.500 Roleplay Benign + 2.500 Teknik Hard-Negative Benign).
   * **Rusça (`ru`) ve diğer 9 dil (`de, fr, es, it, pt, ar, ja, ko, zh`):** Her dil için **1.000'er örnek** (500 Roleplay Benign + 500 Teknik Hard-Negative Benign) = **10.000 örnek**.
   * `B=8`, `workers=6`, `len<=600` ile EVREN API'de timeout olmadan ~20-25 dakikada üretilip `data/v6_multilingual_supplement.json` dosyasına (`label=0`) eklenir.

---

### Adım 4: Cell 5 Deterministik Kota Güncellemesi ve 3 Omurga Yeniden Eğitimi
1. Üç eğitim notebook'unun (`Train_XLM_RoBERTa_v6.ipynb`, `Train_mmBERT_v6.ipynb`, `Train_BGE_M3_v6.ipynb`) **Cell 5** hücresinde:
   * `BLACKLIST` içine yeni `heldout_benchmark_v6.json` dahil edilir.
   * Masum kotaları rastgele kırpma yerine **deterministik alt-kotalarla** (`tr`: 10k doğal + 5k EVREN-MT hard-neg/roleplay; diğer 10 dil: 1k doğal + 1k EVREN-MT hard-neg/roleplay; `en`: doğal + hard-neg/roleplay) birleştirilir.
2. Colab GPU üzerinde 3 model yeniden eğitilir ve her notebook'un sonunda **3 Benchmark** (`Hold-out 15k`, `OOD-2000 + Stress-1070`, `Heldout-v6 2880`) tek tabloda raporlanır.

---

## 4. Alınan Nihai Kararlar (Özet)

1. ✅ **Tek/Simetrik Çeviri Motoru Kuralı:** Eğitimde hem saldırı hem masum MT takviyeleri **EVREN (`gemma-4-31b`)** ile üretilecek; dış benchmark (`heldout_benchmark_v6.json`) ise her iki sınıf için **NLLB-200** kullanacak. Böylece sınıflar arası motor yanlılığı (translator artifact) ve eğitim-test motor sızıntısı sıfırlanacak.
2. ✅ **Persona Benign'ler Korunacak:** Benchmark'tan masum rol yapmaları silinmeyecek; modelin FP sorunu eğitime 12 dilde masum roleplay eklenerek çözülecek.
3. ✅ **Saldırılarda Regex Filtresi Yok:** Benchmark'tan sadece kapsam dışı `JBB[harmful]` çıkarılacak, `INJECTION_MARKER` şartı aranmayacak.
4. ✅ **Cell 5 Deterministik Alt-Kota:** `tr` (10k doğal + 5k MT) ve diğer diller (1k doğal + 1k MT) rastgele kırpılmadan tam kotayla eğitime girecek.

---

## 5. Kalan 5 Sorunun Çözümü (v6.2 — Bağımsız Denetim Mutabakatı)

### Çözüm 1: Sınıf-İçi MT-Oranı Simetrisi (Yeni Kural 5) — EN KRİTİK
**Sorun:** Motor aynı (`EVREN gemma-4-31b`) olsa bile **sınıflar arası MT ORANI eşit değil**:
- Saldırılar: `tr` ~%93 MT (14.253 / 15.000); diğer 10 dil ~%95-100 MT.
- Masumlar (eski plan, Kural 4): `tr` %33 MT (10k native + 5k MT); diğer 10 dil %50 MT.

→ Model yine **"çeviri kokusu yoğun cümle = saldırı"** kısayolunu öğrenir (motor adı aynı olsa da). **Kural 3 motoru düzeltir, ORANI düzeltmez.**

**Kural 5:** Her dilde **masum havuzunun MT oranı = saldırı havuzunun MT oranı** (±%10). Native masum sayısı = `(1 − saldiri_MT_orani) × TGT_BEN`.

**Yeni deterministik kotalar (eğitim masum, EVREN-MT):**

| Dil | Saldırı (MT oranı) | Yeni Masum kotası (native + EVREN-MT) | MT oranı |
| :-- | :-- | :-- | :--: |
| `tr` | 15.000 (~%93 MT) | **1.000 native + 14.000 EVREN-MT** | ~%93 |
| `ru,de,fr,es,it,pt,ar,ja,ko,zh` | 2.000 (~%95+ MT) | **200 native + 1.800 EVREN-MT** | ~%90 |

Ek üretilecek EVREN-MT benign: `14.000 + (10×1.800) = ~32.000 çeviri` (`B=8`, `workers=6`, `len<=600`) → **~45-60 dk**.
*Bedel:* native benign azalır (gerçek-dünya temsili düşer) ama **sınıf-ayrımı kısayolu ortadan kalkar** — TR/RU FP'sinin gerçek çözümü budur. (Daha ucuz alternatif yoktur: saldırı MT oranı düşürülemez, çünkü non-EN saldırı doğal verisi yoktur.)

### Çözüm 2: Benchmark Direnci — Tutulmayan Hard-Negative Ekle
Yeni benchmark masum'u (`jackhhao[benign]` + `dolly`) **genel niteliktedir** → güvenlik-konulu zor-negatif (hard-negative) yok → **FP yapay düşük** çıkar.
**Çözüm:** Benchmark masum havuzuna, eğitimde OLMAYAN bir hard-negative kaynağı eklenir (aday: `Mindgard/evaded-prompt-injection-and-jailbreak-samples` benign dilimi — kurulumdan önce doğrulanacak). Eklenemezse bu durum **makalede açıkça sınırlama olarak belirtilir** (aksi halde hakem "kolay benchmark" eleştirisi yapar).

### Çözüm 3: Eski Kontamine Colab JSON Yasağı
`heldout_benchmark_v6_colab.json` (JBB[harmful] içerir + persona benign silinmiş) **ASLA kullanılmayacaktır**. Adım 2'deki *"veya mevcut `heldout_benchmark_v6_colab.json` üzerinde"* ifadesi **kaldırılmıştır**; benchmark yalnızca Adım 2'nin kendi kriterleriyle **sıfırdan** üretilir.

### Çözüm 4: Kaynak ID Düzeltmesi (uygulandı)
Tüm "`Horizon/simsonsun_jailbreaks`" → **`Simsonsun/JailbreakPrompts`** (HF'de doğrulandı). Yanlış ID = boş veri üretimi.

### Çözüm 5: Kapsam Genişletme / Sınırlama Notu
Yeni saldırı kaynakları (`jackhhao`, `rubend18`, `Simsonsun/JailbreakPrompts`) ağırlıklı **jailbreak** (DAN/rol yapma) → AppSec matrisinin (indirect / stego / agentic) yalnızca bir dilimini test eder; eski OOD'daki mosscap/stego çeşitliliği yoktur.
**Çözüm:** Benchmark'a **tutulmayan** bir indirect/stego kaynağı eklenir (ör. `Mindgard/...evaded...`, çok-turlu setler — kurulumdan önce doğrulanacak). Eklenemezse **kapsam sınırlaması makalede belirtilir**.

---

## 6. Güncellenmiş Nihai Kararlar (v6.2)

5. ✅ **Kural 5 — Sınıf-İçi MT-Oranı Simetrisi:** Eğitim masum MT oranı, saldırı MT oranına eşitlenir (bkz. Çözüm 1 kota tablosu). TR/RU FP'sinin gerçek çözümü budur.
6. ✅ **Benchmark Direnci ve Kapsamı:** Benchmark masum havuzuna tutulmayan hard-negative, saldırı havuzuna tutulmayan indirect/stego kaynağı eklenir; eklenemezse sınırlamalar makalede belirtilir.
7. ✅ **Eski kontamine Colab JSON kullanılmaz;** kaynak ID'si `Simsonsun/JailbreakPrompts` olarak düzeltildi.

> **Not:** Çözüm 1'deki ~32.000 ek EVREN çevirisi ve Çözüm 2/5'teki yeni kaynak doğrulamaları tamamlandığında bu doküman **v6.2 nihai** olur ve üretim başlar.
