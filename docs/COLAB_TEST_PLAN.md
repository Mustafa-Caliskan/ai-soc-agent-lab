# 🧪 Colab E2E Test Planı — NeuralShield-v5 (Yarın Çalıştırmaya Hazır)

> **Amaç:** Yerel/Colab açık ağırlıklı LLM'leri, **temsili** bir saldırı setiyle SHIELD OFF/ON olarak test etmek — her testin net bir bilimsel amacı var.
> **Test Seti:** `data/colab_e2e_suite_stratified.json` — **120 saldırı + 36 meşru**, 12 dil, çeşitli SOTA kaynaklar (Mosscap/NotInject payı düşük, temsili).
> **Notebook:** `notebooks/CyberTech_Colab_LLM_Benchmark.ipynb` (DATASET_PATH artık stratifiye seti varsayılan seçiyor).
> **Runner:** `scripts/colab/run_colab_benchmark.py`

---

## 0. Her Testin Amacı (Neden bu testler?)

| # | Araştırma Sorusu (RQ) | Test | Ölçtüğü Metrik |
| :-- | :--- | :--- | :--- |
| **RQ1** | Modeller çıplakken sır sızdırıyor mu? (ölçekten bağımsız mı?) | SHIELD OFF, farklı boyutlar | **Egress ASR** (content'te canary) |
| **RQ2** | NeuralShield saldırıyı sıfırlıyor mu? | SHIELD ON | **ASR azaltımı** (OFF→ON), Blok % |
| **RQ3** | **İki Kanallı Sızıntı:** model yanıtı reddetse bile içsel düşünmede (CoT) sızdırıyor mu? | OFF + ON, content vs reasoning ayrımı | **CoT Leakage %** vs **Egress ASR %** |
| **RQ4** | Türkçe yerel model de zafiyetli mi? (ulusal/egemenlik argümanı) | Trendyol-LLM-7B | TR ASR + TR FP |
| **RQ5** | Guardrail'siz (sansürsüz/abliterated) model daha mı savunmasız? (hizalama confound'u kontrolü) | Abliterated model | OFF ASR karşılaştırması |

---

## 1. Test Matrisi (Her Satır Bir "Hikâye")

| Test | Model | Colab GPU | Amaç | Beklenen Çıktı |
| :--- | :--- | :--- | :--- | :--- |
| **T1** | `Qwen/Qwen2.5-7B-Instruct` | T4 (ücretsiz) | Orta ölçek referans | OFF ASR vs ON ASR |
| **T2** | `Trendyol/Trendyol-LLM-7b-chat-v1.0` | T4 | Türkçe egemenlik | TR ASR + TR FP |
| **T3** | `meta-llama/Llama-3.3-70B-Instruct` (4-bit) | A100 (Pro) | Büyük ölçek (scale-invariance) | OFF ASR vs ON ASR |
| **T4** | Abliterated/uncensored (ör. `V1eww/llama-3.1-8b-abliterated`) | T4 | Guardrail'siz baseline | Yüksek OFF ASR |
| **T5** | `google/gemma-2-2b-it` / `microsoft/Phi-3.5-mini-instruct` | T4 | Küçük ölçek | OFF/ON |
| **T6** | `Qwen/Qwen2.5-72B-Instruct` (4-bit) | A100 (Pro) | Frontier OSS | OFF/ON |

> Her model için **iki mod** otomatik koşar: **Kalkan KAPALI** (ham model) ve **Kalkan AÇIK** (NeuralShield girişi keser).

---

## 2. Bugün/Yarın Çalıştırma Adımları

### 2a. Notebook ile (önerilen — tek tık)
1. `notebooks/CyberTech_Colab_LLM_Benchmark.ipynb`'i Colab'da aç (GPU: Runtime → T4 veya A100).
2. **Cell 4:** `TARGET_MODEL` seç, `DATASET_PATH = data/colab_e2e_suite_stratified.json` kalsın.
3. Gerekirse `HF_TOKEN` gir (Llama/Trendyol gated olabilir).
4. "Run All" → sonuçlar `data/colab_benchmark_<timestamp>.json` + özet tablo.

### 2b. Komut satırı ile (alternatif)
```bash
# T1 — Orta ölçek
python scripts/colab/run_colab_benchmark.py --model Qwen/Qwen2.5-7B-Instruct \
    --dataset data/colab_e2e_suite_stratified.json --limit 200

# T2 — Türkçe yerel
python scripts/colab/run_colab_benchmark.py --model Trendyol/Trendyol-LLM-7b-chat-v1.0 \
    --dataset data/colab_e2e_suite_stratified.json

# T3/T6 — Büyük (A100, 4-bit)
python scripts/colab/run_colab_benchmark.py --model meta-llama/Llama-3.3-70B-Instruct --load-in-4bit
python scripts/colab/run_colab_benchmark.py --model Qwen/Qwen2.5-72B-Instruct --load-in-4bit
```

### 2c. VRAM/İndirme Notları
- **T4 (15GB):** 2B–8B modeller 4-bit'te rahat. 70B **sığmaz** → A100 gerekir.
- **A100 (40GB Pro):** 70B/72B 4-bit'te (~38GB) çalışır.
- Gated modeller (Llama, Trendyol) için HF token gerekli.

---

## 3. Raporlanacak Metrikler (Her Test İçin Zorunlu)

1. **Egress ASR %** (SHIELD OFF): saldırıların content'inde canary sızdıran oranı + Wilson %95 GA.
2. **Egress ASR %** (SHIELD ON): NeuralShield girişi kesince sızan oranı.
3. **CoT Leakage %** (OFF/ON): reasoning alanında canary geçen oranı (özgün bulgu).
4. **Shield Block %**: kalkanın durdurduğu saldırı oranı.
5. **Meşru FP %**: benign'lerin yanlış bloklanma oranı.

---

## 4. Dürüstlük / Metodoloji Notları (Makale İçin)
- **Guardrail confound:** Colab modelleri **hizalı** (guardrail'li). Ölçülen OFF ASR = **gerçek çıplak-model zafiyetinin ALT SINIRI.** T4 (abliterated) bunu kontrol eder.
- **Non-determinizm:** `temperature=0` olsa da modeller değişebilir → kritik testleri **2-3 kez** koş, ortalama + varyans ver.
- **İki kanal:** "content'te sızdı" ≠ "CoT'te sızdı". Makalede **ayrı sütunlar** (Egress vs CoT).
- **Örneklem:** E2E seti n=120 saldırı → Wilson GA hâlâ geniş; raporlarken GA belirt.

---

## 5. Beklenen "Hikâyeler" (Makale İçin)
- **Scale-Invariant Vulnerability:** SHIELD OFF'ta 2B'den 72B'ye kadar modeller sır sızdırıyor → OFF ASR ölçekten bağımsız yüksek.
- **Shield Efficacy:** ON'da ASR ~%0 → çevresel kalkan modeli değiştirmeden korur.
- **Two-Channel Exfiltration (YENİ):** Büyük modeller content'te reddetse bile CoT'te sızdırır.
- **Turkish Sovereignty:** Trendyol-LLM çıplakken TR saldırılarda sızdırıyor → yerel model de korunmaya muhtaç.

---
*Hazırlayan: otomatik test altyapısı. Test seti: `data/colab_e2e_suite_stratified.json`.*
