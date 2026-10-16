# garak Çapraz Doğrulama — NeuralShield-v5 vs NVIDIA garak Probe'ları

**garak sürümü:** 0.15.1
**Yöntem:** garak'ın `65` probe sınıfından toplanan **679 saldırı promptu**, NeuralShield-v5
kalkanından (L0 normalizer + L1 regex + L2 XLM-RoBERTa ONNX, OR-Gate) geçirildi.

## SONUÇ: garak saldırılarının **%48.9**'i kalkan tarafından BLOKLANDI (332/679)

| garak Probe Ailesi | Prompt (n) | Bloklanan | Blok % |
|---|---:|---:|---:|
| encoding | 300 | 118 | %39.3 |
| promptinject | 90 | 90 | %100.0 |
| snowball | 90 | 0 | %0.0 |
| dan | 62 | 62 | %100.0 |
| grandma | 34 | 16 | %47.1 |
| exploitation | 32 | 15 | %46.9 |
| apikey | 30 | 15 | %50.0 |
| goodside | 26 | 16 | %61.5 |
| misleading | 15 | 0 | %0.0 |

**GENEL: 332/679 (%48.9)**

_Not: Bu, standart bir LLM zafiyet tarayıcısına (NVIDIA garak) karşı çapraz doğrulamadır._