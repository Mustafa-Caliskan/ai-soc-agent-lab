# 🧬 NeuralShield-v6 — KUSURSUZ Veri Seti Mimarisi ve Eğitim Planı

> **Amaç:** v5'in bilinen zayıflıklarını (Arapça %54, veri seçiciliği, kapsam kayması) gideren, **12 dilli, dengeli, kapsam-temiz ~100.000 örnekli** master eğitim havuzu.
> **Temel model adayı:** `jhu-clsp/mmBERT-base` (çok dilli ModernBERT, ~300M) — Patronus'un tabanı.
> **Kapsam:** YALNIZCA AppSec (injection / system-extraction / evasion / stego / agentic / indirect / coercion). Pure ethics/harmful **hariç**.

---

## 1. TASARIM İLKELERİ (v5'ten dersler)

| İlke | Neden |
|---|---|
| **Kapsam-temiz** | v5'e ethics/jailbreak-harmful karışmıştı (kapsam kayması). v6'da yalnızca AppSec. |
| **Dengeli çok dilli** | v5'te Arapça azdı → %54. v6'da her dil yeterli temsil. |
| **Zorluk kademeli** | T1-T5 etiketli (hakem "kapsam" ve "zorluk" görmek ister). |
| **Hard-negative bol** | FP'yi düşürür (v5'te normal IT FP %6, hard-neg %16). |
| **Kaynak çeşitliliği + cap** | Tek kaynak domine etmesin (v4'teki slicing bug dersi). |
| **Sızıntı yok** | test seti eğitimden tamamen ayrık (leakage audit). |
| **Dürüst MT** | Native bulunamayan diller MT ile, `[MT]` etiketli. |

---

## 2. HEDEF KOMPOZİSYON (~100.000 örnek, 50k/50k)

| Dil | Attack | Benign | Not |
|---|---:|---:|---|
| en (İngilizce) | 15.000 | 15.000 | Native — en zengin kaynak |
| tr (Türkçe) | 15.000 | 15.000 | Native — proje ana odağı |
| de | 2.000 | 2.000 | MT + Aya |
| fr | 2.000 | 2.000 | MT + Aya |
| es | 2.000 | 2.000 | MT + Aya |
| it | 2.000 | 2.000 | MT + Aya |
| pt | 2.000 | 2.000 | MT + Aya |
| ru | 2.000 | 2.000 | Native (dmtrdr) + MT |
| ar | 2.000 | 2.000 | **MT + Aya + native benign (dev-hussein)** |
| ja | 2.000 | 2.000 | Native (masahiroid) + MT |
| ko | 2.000 | 2.000 | MT + MultiJail |
| zh | 2.000 | 2.000 | MultiJail + MT |
| **TOPLAM** | **50.000** | **50.000** | |

### Zorluk (Tier) dağılımı (attack tarafı)
| Tier | Tür | Hedef pay |
|---|---|---|
| T1 | Doğrudan injection (`ignore previous`, system override) | %30 |
| T2 | Persona/DAN/rol gaspı, yetki simülasyonu | %25 |
| T3 | Bilişsel/dolaylı çerçeveleme (hikaye, akademik, RAG) | %20 |
| T4 | Kodlama/stego (Base64/Hex/ROT13/Unicode-Tag/ZWSP/homoglyph) | %15 |
| T5 | Çapraz-dil + agentic/tool/MCP injection | %10 |

---

## 3. KAYNAK SEÇİMİ (Seçici!)

### ✅ KORUNACAK (v5'ten, kapsam-içi + kaliteli)
**Attack:** `3nesdeniz/agentic-prompt-injection-5k`, `AltaySec/turkish-llm-injection`, `MAlmasabi/Indirect-Prompt-Injection-BIPIA-GPT`, `S-Labs/prompt-injection-dataset`, `cgoosen/prompt_injection_ctf_dataset_3`, `deepset/prompt-injections`, `iamabhishekpanda/enterprise-prompt-injection-dataset`, `imoxto/prompt_injection_hackaprompt_gpt35`, `prodnull/prompt-injection-repo-dataset`, `jayavibhav/prompt-injection`, `3nesdeniz/turkish-conversation-prompt-injection`
**Benign:** `3nesdeniz/guardrail-hard-negatives`, `guychuk/benign-malicious-prompt-classification`, `rogue-security/real-world-benign-use-cases`, `3nesdeniz/turkish-daily-dialogues-5k`, `TFLai/Turkish-Dialog-Dataset`, `cisimcik/turkish-decisions-max-19k`, `emreseyhan/Turkish-customer-service-conversations`, `kilicai/turkish-sft-multi-turn-dialogue-10k`, `merve/turkish_instructions`, `CohereLabs/aya_collection_language_split`, `dev-hussein/saudi-arabic-cs-conversations`

### ❌ ÇIKARILACAK (kapsam-dışı ethics/harmful/junk)
`walledai/AdvBench` (CBRN), `allenai/wildjailbreak` + `walledai/WildJailbreak` (harmful jailbreak), `walledai/JailbreakHub`, `centrepourlasecuriteia/jailbreak-dataset`, `jackhhao/jailbreak-classification`, `Necent/llm-jailbreak-*` (ethics ağırlıklı), `CreitinGameplays/magpie-*` (alakasız reasoning), `fevziegeyurtsevenler/turkish-prompt-injection` + `beratcmn/turkish-prompt-injections` (kalite şüpheli — elle doğrula).

### 🆕 YENİ KAYNAKLAR (HF'de bulundu — v6 için)
| Kaynak | Dil | Neden |
|---|---|---|
| `rikka-snow/prompt-injection-multilingual` | çok dilli | Native çok dilli injection |
| `Octavio-Santana/prompt-injection-attack-detection-multilingual` | çok dilli | Multilingual |
| `fevzieygeyurtsevenler/multilingual-prompt-injection` | çok dilli | Multilingual |
| `darkknight25/Multilingual_Jailbreak_Dataset` | çok dilli | Multilingual jailbreak (framing) |
| `fevzieygeyurtsevenler/multilingual-jailbreak` | çok dilli | Multilingual |
| `DAMO-NLP-SG/MultiJail` | ar/ko/it/zh | **Native** çok dilli jailbreak |
| `masahiroid/japanese-indirect-prompt-injection-probes` | ja | **Native Japonca** IPI |
| `dmtrdr/russian_prompt_injections` | ru | **Native Rusça** |
| `halilneed/turkish-prompt-injection-benchmark` | tr | Native Türkçe |
| `halilneed/turkish-prompt-injection-false-alarm-benchmark` | tr | Türkçe FP hard-negative |
| `nvidia/Nemotron-RL-Agentic-Indirect-Prompt-Injection-v1` | en | **Agentic** IPI (yeni tehdit sınıfı) |
| `emgena/omnimcp_mcp_prompt_injection_guard_teaser` | en | **MCP/tool** injection |

---

## 4. VERİ AÇIĞI VE SENİN ARAMAN GEREKEN KELİMELER

Şu dillerde **native attack** bulamadım → MT gerekir (ama sen bulursan daha iyi):
**de, fr, es, it, pt, ar, ko, zh** (kısmen ja/ru/tr hariç).

Aşağıdaki **anahtar kelimeleri** HF'de ara (senin alanın olsun):
```
# Arapça
"arabic prompt injection" · "arabic jailbreak dataset" · "arabic llm security" · "arabic malicious prompts" · "arabic benign instructions"
# Almanca
"german prompt injection" · "deutsch jailbreak" · "german llm security"
# Fransızca
"french prompt injection" · "francais jailbreak" · "french llm jailbreak"
# İspanyolca / İtalyanca / Portekizce
"spanish prompt injection" · "italian prompt injection" · "portuguese prompt injection"
# Korece / Çince
"korean prompt injection" · "chinese prompt injection" · "chinese jailbreak dataset"
# Genel çok dilli
"multilingual prompt injection" · "cross-lingual jailbreak" · "multilingual LLM security"
```
Bulduklarını bana at → hedefe ekleyelim.

---

## 5. EĞİTİM PROTOKOLÜ (v6)

| Ayar | Değer |
|---|---|
| Taban model | `jhu-clsp/mmBERT-base` (çok dilli ModernBERT) |
| Kayıp | CyberFocalLoss (γ=2.0, α=0.65) — v5 ile aynı |
| max_length | 512 (ModernBERT destekler; gerekirse 1024) |
| Split | %70 train / %15 val / %15 test (stratified: dil × etiket × tier) |
| Epoch | 3, EarlyStopping patience=2 |
| LR | 2e-5, warmup %10, weight_decay 0.01, fp16/bf16 |
| Batch | per_device 16 × grad_accum 2 |
| **Sızıntı** | train/val/test **disjoint** (fuzzy dedup) |
| Kalibrasyon | val üzerinde temperature scaling |
| Değerlendirme | hold-out + **bağımsız OOD** (mevcut 2000-seti) + dil bazında |

### Karşılaştırma (v6 notebook'ta olacak)
1. **v5 XLM-RoBERTa** (2 hücre: 1 eğit, 1 kıyasla) → sonra silinebilir.
2. **v6 mmBERT** (ana model).
3. Rakipler: ProtectAI / Patronus (adil, İngilizce + çok dilli).

### Beklenen kazanım
| | v5 (XLM-R) | v6 (mmBERT) |
|---|---|---|
| Çok dilli recall | %82.5 | hedef **> %88** |
| Arapça recall | %54 | hedef **> %80** |
| Gecikme | ~10 ms CPU | benzer |

---

## 6. v6 COLAB HÜCRE PLANI (13 hücre)
1. Kurulum + HF token
2. Kaynak listesi + **seçici veri havuzu** (keep/drop)
3. Çok dilli dengeleme + MT (eksik diller) + **dilin/tier dağılımı**
4. Fuzzy dedup + leakage audit + stratified split
5. Tokenizasyon + mmBERT yükleme
6. CyberFocalLoss ile model tanımı
7. Eğitim (EarlyStopping)
8. Hold-out değerlendirme + confusion matrix
9. Kalibrasyon (temperature scaling)
10. OOD (2000-seti) + dil bazında
11. Grafikler (loss/F1/ROC/confusion/dil kıyası/ASR)
12. **XLM-R (v5) karşılaştırma** (2. hücre — silinebilir)
13. ONNX INT8 export + bundle

---
*Bu belge v6 veri setinin resmi rehberidir. Onay sonrası notebook kodlanır.*
