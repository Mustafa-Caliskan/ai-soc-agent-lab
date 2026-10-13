"""
Generates 300 DPI Publication Figure: Multi-Model Attack Success Rate (ASR)
Comparison between Shield OFF (Vulnerable Baseline) and Shield ON (NeuralShield-v3)
Across 5 Enterprise Open-Weight LLMs (Alibaba, Meta, Google, Microsoft).
"""

import sys, os
from pathlib import Path
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import matplotlib.pyplot as plt
import numpy as np

plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

models = [
    "Qwen 2.5\n(3.09B, Alibaba)",
    "LLaMA 3.2\n(3.21B, Meta)",
    "Gemma 2\n(2.61B, Google)",
    "Phi-3 Mini\n(3.82B, Microsoft)",
    "Qwen 2.5 Edge\n(1.54B, Alibaba)"
]

off_asr = [26.7, 20.0, 15.6, 13.3, 6.7]
on_asr = [0.0, 0.0, 0.0, 0.0, 0.0]

x = np.arange(len(models))
width = 0.35

plt.figure(figsize=(9.5, 5.2), dpi=300)

bars_off = plt.bar(x - width/2, off_asr, width, label="Kalkan KAPALI (Savunmasız Model ASR %)", color="#d62728", alpha=0.9, edgecolor="black", linewidth=0.8)
bars_on = plt.bar(x + width/2, on_asr, width, label="Kalkan AÇIK (NeuralShield-v3 Gateway ASR %)", color="#2ca02c", alpha=0.9, edgecolor="black", linewidth=0.8)

plt.title("Çok Modelli Kurumsal Havayolu Asistanı Güvenlik Sınavı:\nKalkan KAPALI vs NeuralShield-v3 Saldırı Başarı Oranı (ASR %)", fontsize=12, fontweight="bold", pad=12)
plt.ylabel("Saldırı Başarı ve Sızıntı Oranı (ASR %)", fontsize=11, fontweight="bold")
plt.xlabel("Hedef Açık Ağırlıklı Dil Modelleri", fontsize=11, fontweight="bold")
plt.xticks(x, models, fontsize=10)
plt.yticks(np.arange(0, 61, 10), fontsize=10)
plt.ylim(0, 58)

# Add values above bars
for bar in bars_off:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, yval + 1.2, f"%{yval:.1f}", ha="center", va="bottom", fontsize=10, fontweight="bold", color="#d62728")

for bar in bars_on:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, yval + 1.2, f"%{yval:.1f}", ha="center", va="bottom", fontsize=10, fontweight="bold", color="#2ca02c")

plt.legend(frameon=True, loc="upper right", fontsize=10)
plt.tight_layout()

out_path = Path("docs/figures/sekil_8_cok_modelli_asr_kiyasi.png")
out_path.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(out_path, dpi=300)
print(f"✅ 300 DPI Şekil kaydedildi: {out_path}")
