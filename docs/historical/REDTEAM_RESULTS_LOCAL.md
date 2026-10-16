# CyberTech Neural Shield — Yerel Filtre Testi (Layer 1+2)

- Tarih: 2026-10-12 01:37:57
- Not: Yerel filtre testi: yalnizca KATMAN 1+2 tespitini olcer; LLM sizintisi/ASR icin --engine http kullanin.

| Saldırı Ailesi | n | Blok % | Regex (L1) % | L2 Malicious % | L2 Gecikme ms |
|---|---:|---:|---:|---:|---:|
| benign | 60 | 0.00 | 0.00 | 0.00 | 16.32 |
| homoglyph | 15 | 100.00 | 100.00 | 73.33 | 56.59 |
| indirect_doc | 15 | 100.00 | 0.00 | 100.00 | 58.97 |
| obfuscation_base64 | 15 | 100.00 | 26.67 | 100.00 | 117.63 |
| obfuscation_reverse | 15 | 100.00 | 0.00 | 100.00 | 61.6 |
| pdf_hidden | 15 | 100.00 | 100.00 | 100.00 | 83.77 |
| persona | 15 | 100.00 | 100.00 | 100.00 | 39.94 |
| semantic | 15 | 100.00 | 0.00 | 100.00 | 52.43 |
| stego_emoji_vs | 15 | 100.00 | 100.00 | 0.00 | 17.73 |
| stego_unicode_tags | 15 | 100.00 | 100.00 | 0.00 | 17.61 |
| stego_zerowidth | 15 | 100.00 | 100.00 | 100.00 | 80.38 |
| **SALDIRILAR TOPLAMI (Attack Recall)** | 150 | **100.00%** | - | - | - |
| **GENEL DOĞRULUK (Accuracy)** | 210 | **100.00%** | - | - | - |

- **Saldırı Yakalama Oranı (Attack Recall / True Positive Rate):** **100.00%** (150/150 saldırı engellendi)
- **False Positive Oranı (Yanlış Alarm / Benign Blok):** **0.00%** (0/60 meşru istek engellendi)
- **Sistem Genel Doğruluğu (Overall Accuracy):** **100.00%** (210/210)

*Not: Yerel test yalnızca Layer 1+2 tespitini ölçer; LLM sızıntısı (ASR) için `redteam_benchmark.py --engine http` kullanılmalıdır.*