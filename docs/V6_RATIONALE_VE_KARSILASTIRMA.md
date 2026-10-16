# 📋 NeuralShield v5 → v6: Ne Yaptık, Neden Yeni Model, Rakip Kıyaslaması

> **Tarih:** 16 Ekim 2026 · **Yazarlar:** Mustafa ÇALIŞKAN & Prof. Dr. Ali Hakan IŞIK
> **Amaç:** Bu belge, v5'ten bugüne yapılanları, v6 kararının gerekçesini ve rakiplerle ampirik kıyaslamayı tek yerde toplar. **Ajan incelemesi için hazırlanmıştır.**

---

## 1. NE YAPTIK? (Kronoloji)

1. **v5 modeli doğrulandı:** XLM-RoBERTa INT8 ONNX, 4 katmanlı kalkan (L0 normalizer + L1 regex + L2 ML + L3 DLP), CyberFocalLoss, 71.440 örnek.
2. **Bağımsız denetimler (2 harici reviewer):**
   - Rusça Layer-0 bug'ı (saf Kiril → yanlış homoglyph) **bulundu ve düzeltildi**.
   - `content` vs `reasoning` (CoT) sızıntı ayrımı **keşfedildi** → özgün akademik bulgu.
   - Sızıntı (leakage) denetimi + arındırılmış benchmark.
3. **Benchmark temizliği:** slicing-bug düzeltildi, mosscap/NotInect bağımlılığı %50'den ~%10'a indi, OnerAYTAS/etik içerik çıkarıldı → **v4 dengeli 2000-seti** (12 dil, 0 sızıntı).
4. **Karar motoru:** muhafazakâr composite → **OR-Gate** (`stego ∨ regex≥60 ∨ ML≥70`) → recall %29→%73.
5. **Standart-araç çapraz doğrulama:** NVIDIA **garak** (679 probe) → promptinject **%98.9**, dan **%98.4**; genel (kapsam-dışı aileler dahil) **%46.2**.
6. **Rakip kıyaslaması (adil, İngilizce + çok dilli):** ProtectAI / Patronus / (Llama-Guard bekliyor).
7. **Karar:** v6 = **`mmBERT` (çok dilli ModernBERT)** — çünkü rakipler de mmBERT kullanıyor ve bizim Arapça zayıflığımız var.

---

## 2. NEDEN YENİ MODEL (v6)?

| Gerekçe | Kanıt |
|---|---|
| **Arapça zayıflığı** | v5: ar recall **%54**; Patronus (mmBERT): **%88** |
| **Eski mimari** | v5 = XLM-R (2020). Rakipler = **mmBERT (2024)** — daha uzun bağlam, verimli, çok dilli |
| **Rakip çok dilli** | Patronus/Horizon mmBERT ile bizden iyi FP + Arapça |
| **Veri seçiciliği** | v5'te ethics/junk karışmıştı → v6'da kapsam-temiz + dengeli 12 dil |
| **"Bizim model" argümanı** | v6 = bizim eğittiğimiz bağımsız model (rakibin fine-tune'u değil) |

---

## 3. RAKİP KIYASLAMA SONUÇLARI (ampirik)

### İngilizce (adil — rakipler İngilizce modeli)
| Model | Recall | FP | Precision | Donanım |
|---|---:|---:|---:|---|
| **NeuralShield-v5** | **91.2** | 5.2 | 94.6 | CPU |
| ProtectAI DeBERTa-v3 | 84.4 | 12.0 | 87.6 | GPU |
| Patronus Wolf Defender | 84.0 | **2.8** | 96.8 | GPU |

### Çok dilli (2000-set)
| Model | Recall | FP | Precision |
|---|---:|---:|---:|
| **NeuralShield-v5** | **83.2** | 4.5 | 94.9 |
| Patronus Wolf Defender | 79.9 | **1.9** | 97.7 |
| ProtectAI DeBERTa-v3 | 71.7 | **22.4** | 76.2 |

**Kritik:** ProtectAI çok dillide **FP patlatıyor** (ar FP %70, tr FP %41) → "recall" yanıltıcı (her şeye saldırı diyor). Patronus (mmBERT) çok dilli ve **Arapça'da bizden iyi** (88 vs 54). → **v6'da Patronus'u geçmek hedef.**

---

## 4. RAKİPLERİN EĞİTİM REÇETELERİ (model kartlarından)

| Rakip | Taban | Kaynak yaklaşımı |
|---|---|---|
| **Horizon-Labs prompt-injection-guard** | **mmBERT** (bizim v6 tabanı!) | ~280k, **yalnızca izinli kaynak**, 30 dil **sentetik**, evasion augmentasyon, ticari-dışı atılmış |
| **Patronus Wolf Defender** | **mmBERT** | Çok dilli + Base64/homoglyph augmentasyon, **NOT**Inject/OR-Bench hard-negatif |
| **ProtectAI DeBERTa-v3** | deberta-v3 | **İngilizce-only** (kendisi de "jailbreak/non-EN algılamaz" diyor) |

**⇒ Çıkarım:** Rakiplerin en iyisi (Horizon/Patronus) **mmBERT + izinli veri + sentetik çok dillilik** kullanıyor. **Bizim v6 = aynı taban + bizim kapsam-içi veri + Türkçe gücümüz.**

### İzinli (permissive) rakip kaynakları (v6'ya eklendi)
Attack: `neuralchemy`, `S-Labs`, `wambosec(-subtle)`, `Lakera/gandalf`, `hendzh/PromptShield`, `3nesdeniz/*`, `TrustAIRLab/in-the-wild`, `JailbreakV-28K`, `NVIDIA Nemotron`, `rgeada/tool-response-injections`, `microsoft/llmail-inject`, `yanismiraoui`, `deepset`, `reshahbs/SPML`, `Lakera/mosscap`
Benign: `oasst2`, `ultrachat_200k`, `prompts.chat`, `glaive-function-calling`, `aya_dataset`, `xstest`, `Salad-Data`, `FineWeb-2 (24 dil)`
(Model kartları: NAMAA Arapça'yı **İngilizce'den çevirerek** üretmiş → **MT yaklaşımımız doğrulanmış.**)

---

## 5. v6 REÇETESİ (kanıtlanmış)

| Bileşen | Karar |
|---|---|
| Taban | `jhu-clsp/mmBERT-base` |
| Veri | ~100k, dengeli 12 dil, kapsam-temiz, izinli kaynaklar |
| Eksik diller | MT (EVREN) veya sentetik (FineWeb-2 + Qwen) |
| Augmentasyon | homoglyph/zero-width/full-width (L0 robustness) |
| Hard-negatif | NotInject/OR-Bench tarzı |
| Kayıp | CyberFocalLoss (γ=2.0) |
| Hedef | Arapça >%80, çok dilli >%88, Patronus'u geçmek |

---

## 6. ÖZET KARAR
- **v5 yayına hazır** (recall'da önde, CPU-only, dürüst OOD).
- **v6 = dergi/bir sonraki yayın** (mmBERT + kapsam-temiz 100k → Arapça + çok dilli).
- **İkisi çelişmez:** v5 = konferans; v6 = Q1 dergi genişletmesi.
