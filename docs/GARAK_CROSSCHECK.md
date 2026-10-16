# garak Çapraz Doğrulama — NeuralShield-v5 vs NVIDIA garak Probe'ları

**garak sürümü:** 0.15.1
**Yöntem:** garak'ın `65` probe sınıfından toplanan **679 saldırı promptu**, NeuralShield-v5
kalkanından (L0 normalizer + L1 regex + L2 XLM-RoBERTa ONNX, OR-Gate) geçirildi.

## SONUÇ: garak saldırılarının **%46.2**'i kalkan tarafından BLOKLANDI (314/679)

| garak Probe Ailesi | Prompt (n) | Bloklanan | Blok % |
|---|---:|---:|---:|
| encoding | 300 | 105 | %35.0 |
| promptinject | 90 | 89 | %98.9 |
| snowball | 90 | 0 | %0.0 |
| dan | 62 | 61 | %98.4 |
| grandma | 34 | 16 | %47.1 |
| exploitation | 32 | 15 | %46.9 |
| apikey | 30 | 12 | %40.0 |
| goodside | 26 | 16 | %61.5 |
| misleading | 15 | 0 | %0.0 |

**GENEL: 314/679 (%46.2)**

### Katman Kırılımı — bloklananların hangi katmanca durdurulduğu
- {'L2-ML': 207, 'L1-REGEX': 46, 'L0-STEGO': 61}

_Not: Bu, standart bir LLM zafiyet tarayıcısına (NVIDIA garak) karşı çapraz doğrulamadır._