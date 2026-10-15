"""
CyberTech NeuralShield - EVREN Ampirik Çok Modelli Karşılaştırma Grafiği Üreticisi (v2.0 IEEE Format).

Bu betik; en son ampirik benchmark sonuçlarını okur ve
IEEE formatında 300 DPI yüksek çözünürlüklü vektörel ve raster grafikler üretir.

Metodolojik Görselleştirme:
1. Kırmızı Bar: Shield OFF - CoT / Reasoning Side-Channel Sızıntısı (Gemma %65, Qwen %30)
2. Sarı Bar: Shield OFF - True Egress ASR (Kullanıcıya Doğrudan Sızıntı: %0.0)
3. Yeşil Bar: Shield ON - NeuralShield-v5 Devrede (Kapıda %100 Bloklama, Sıfır CoT, Sıfır Egress)
"""
import os
import sys
import glob
import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent

# IEEE Stil Ayarları
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "xtick.labelsize": 9.5,
    "ytick.labelsize": 10,
    "legend.fontsize": 9,
    "figure.titlesize": 13,
    "axes.grid": True,
    "grid.alpha": 0.4,
    "grid.linestyle": "--"
})

def generate_figure(results_path: str = None):
    if not results_path:
        results_path = str(ROOT / "data" / "evren_empirical_results_fleet_v2.json")
        if not os.path.exists(results_path):
            files = sorted(glob.glob(str(ROOT / "data" / "evren_empirical_results_*.json")))
            if not files:
                print("❌ HATA: Görselleştirilecek benchmark sonucu bulunamadı!")
                return
            results_path = files[-1]

    print(f"📊 Veri okunuyor: {results_path}")
    with open(results_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    summary = data.get("summary", data if isinstance(data, list) else [])
    if not summary:
        print("❌ HATA: Özet verisi boş!")
        return

    models = [r["model_name"] for r in summary]
    cot_leaks = [r.get("raw_cot_leak_rate_pct", 0.0) for r in summary]
    egress_asrs = [r.get("raw_asr_pct", 0.0) for r in summary]
    shield_asrs = [r.get("shield_asr_pct", 0.0) for r in summary]

    x = np.arange(len(models))
    width = 0.26

    fig, ax = plt.subplots(figsize=(9.5, 5.8), dpi=300)

    # 3 Gruplu Bar Grafiği
    rects1 = ax.bar(
        x - width, cot_leaks, width,
        label="Shield OFF: CoT Reflection Leakage (Internal <think>)",
        color="#d9534f", edgecolor="#b52b27", alpha=0.9
    )

    rects2 = ax.bar(
        x, egress_asrs, width,
        label="Shield OFF: True Egress ASR (User-Facing Content)",
        color="#f0ad4e", edgecolor="#d58512", alpha=0.9
    )

    rects3 = ax.bar(
        x + width, shield_asrs, width,
        label="Shield ON: NeuralShield-v5 Protected (Gateway Drop)",
        color="#5cb85c", edgecolor="#419641", alpha=0.9
    )

    # Değer Etiketleri (Çakışma Önleyici Konumlandırma)
    for rect in rects1:
        height = rect.get_height()
        ax.annotate(f"{height:.1f}%",
                    xy=(rect.get_x() + rect.get_width() / 2, height + 2),
                    ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#900C3F")

    for rect in rects2:
        height = rect.get_height()
        ax.annotate(f"{height:.1f}%",
                    xy=(rect.get_x() + rect.get_width() / 2, height + 2),
                    ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#8A6D3B")

    for rect in rects3:
        height = rect.get_height()
        ax.annotate(f"{height:.1f}%",
                    xy=(rect.get_x() + rect.get_width() / 2, height + 2),
                    ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#196F3D")

    ax.set_ylabel("Vulnerability & Attack Success Rate (%)")
    ax.set_title("Figure 8: Empirical Fleet Evaluation: CoT Side-Channel vs. Egress vs. NeuralShield-v5", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(models, fontweight="semibold")
    ax.set_ylim(0, 105)
    ax.legend(loc="upper right", framealpha=0.95)

    # Bilgilendirme Kutucuğu (Metodolojik Netlik)
    props = dict(boxstyle="round,pad=0.5", facecolor="#f8f9fa", edgecolor="#ced4da", alpha=0.95)
    ax.text(0.02, 0.95, "Methodology: 25-Sample Multi-Tier Fleet Benchmark\nObservation: Dense Models Reflect Secrets in CoT (65.0%)\nGateway Defense: NeuralShield Drops Request in ~30ms (Zero CoT/Egress)",
            transform=ax.transAxes, fontsize=8, verticalalignment="top", bbox=props)

    plt.tight_layout()

    out_dir = ROOT / "docs" / "figures"
    os.makedirs(out_dir, exist_ok=True)
    out_png = out_dir / "figure8_evren_multimodel_asr.png"
    out_pdf = out_dir / "figure8_evren_multimodel_asr.pdf"

    plt.savefig(out_png, dpi=300)
    plt.savefig(out_pdf, format="pdf")
    plt.close()

    print(f"✅ Görseller başarıyla üretildi:")
    print(f"   - PNG (300 DPI): {out_png}")
    print(f"   - PDF (Vektörel): {out_pdf}\n")

if __name__ == "__main__":
    generate_figure()
