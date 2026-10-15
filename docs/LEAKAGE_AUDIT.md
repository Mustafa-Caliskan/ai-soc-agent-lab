# Sızıntı (Leakage) Re-Audit — v5 Eğitim Kaynaklarına Karşı

> **Not:** Gerçek v5 eğitim havuzu (71.440) Colab'da üretildi ve yerelde yok;
> bu denetim erişilebilen **v5 kaynaklarının** normalize birebir eşleşmesini arar → **ALT SINIR**.
> Gated/kapalı ve ~20 diğer kaynak taranmadı; yakın-kopya (near-dup) ve çapraz-dil (MT) aranmadı.

**Benchmark:** `appsec_benchmark_2000_curated.json` (N=2000)

| v5 eğitim adayı kaynak | Birebir örtüşen benchmark kaydı |
|---|---:|
| 3nesdeniz/turkish-conversation-prompt-injection | 0 |
| 3nesdeniz/turkish-daily-dialogues-5k | 0 |
| AltaySec/turkish-llm-injection | 0 |
| MAlmasabi/Indirect-Prompt-Injection-BIPIA-GPT | ERR:Dataset 'MAlmasabi/Indirect-Prompt-Injection-BIPIA |
| S-Labs/prompt-injection-dataset | 0 |
| deepset/prompt-injections | 0 |
| guychuk/benign-malicious-prompt-classification | 6 |
| iamabhishekpanda/enterprise-prompt-injection-dataset | 0 |
| imoxto/prompt_injection_hackaprompt_gpt35 | 0 |
| jackhhao/jailbreak-classification | 0 |
| jayavibhav/prompt-injection | 67 |
| jayavibhav/prompt-injection-safety | 0 |
| prodnull/prompt-injection-repo-dataset | ERR:Dataset 'prodnull/prompt-injection-repo-dataset' i |
| fevziegeyurtsevenler/turkish-prompt-injection | 0 |
| beratcmn/turkish-prompt-injections | 0 |
| Necent/llm-jailbreak-prompt-injection-dataset | ERR:Dataset 'Necent/llm-jailbreak-prompt-injection-dat |
| walledai/JailbreakHub | 1 |
| cgoosen/prompt_injection_ctf_dataset_3 | 2 |
| TrustAIRLab/in-the-wild-jailbreak-prompts | ERR:Config name is missing.
Please pick one among the  |

**Toplam birebir örtüşen: 76 / 2000 (%3.8).**

Arındırılmış kopya: `data/appsec_benchmark_2000_purged.json` → **N=1924** (örtüşenler çıkarıldı).

## Yorum
- Örtüşme, benchmark'ın bağımsız olmadığını gösterir (özellikle agregatör setler).
- Yayın için: ya arındırılmış kopyayı kullan, ya da örtüşen kayıtları 'eğitim-görülmüş' olarak ayrı raporla.
- Gerçek havuzla tam denetim Colab çıktısı gerektirir (train/val/test export).

_Üretildi: scripts/leakage_audit_and_purge.py_