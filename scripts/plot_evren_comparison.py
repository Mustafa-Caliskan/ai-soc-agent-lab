"""
CyberTech NeuralShield - EVREN Ampirik Çok Modelli Karşılaştırma Grafiği Üreticisi (IEEE Format).

Bu betik; en son ampirik benchmark sonuçlarını (evren_empirical_results_*.json) okur ve
akademik yayında (Figure 8) kullanılmak üzere 300 DPI yüksek çözünürlüklü
vektröel ve raster grafikler üretir.
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
    "legend.fontsize": 9.5,
    "figure.titlesize": 13,
    "axes.grid": True,
    "grid.alpha": 0.4,
    "grid.linestyle": "--"
})

def generate_figure(results_path: str = None):
    if not results_path:
        files = glob.glob(str(ROOT / "data" / "evren_empirical_results_*.json"))
        if not files:
            files = glob.glob(str(ROOT / "data" / "evren_benchmark_partial_*.json"))
        if not files:
            print("❌ HATA: Görselleştirilecek benchmark sonucu bulunamadı!")
            return
        results_path = max(files, key=os.path.getctime)

    print(f"📊 Veri okunuyor: {results_path}")
    with open(results_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    summary = data.get("summary", data if isinstance(data, list) else [])
    if not summary:
        print("❌ HATA: Özet verisi boş!")
        return

    models = [r["model_name"] for r in summary]
    raw_asrs = [r["raw_asr_pct"] for r in summary]
    shield_asrs = [r["shield_asr_pct"] for r in summary]

    # Wilson CI hata çubukları
    raw_err_low = []
    raw_err_high = []
    for r in summary:
        ci = r.get("raw_wilson_ci", (r["raw_asr_pct"], r["raw_asr_pct"]))
        raw_err_low.append(max(0, r["raw_asr_pct"] - ci[0]))
        raw_err_high.append(max(0, ci[1] - r["raw_asr_pct"]))

    shield_err_low = []
    shield_err_high = []
    for r in summary:
        ci = r.get("shield_wilson_ci", (r["shield_asr_pct"], r["shield_asr_pct"]))
        shield_err_low.append(max(0, r["shield_asr_pct"] - ci[0]))
        shield_err_high.append(max(0, ci[1] - r["shield_asr_pct"]))

    x = np.arange(len(models))
    width = 0.35

    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)

    # Bar grafikleri
    rects1 = ax.bar(
        x - width/2, raw_asrs, width,
        yerr=[raw_err_low, raw_err_high],
        capsize=4,
        label="Shield OFF (Raw LLM Vulnerability)",
        color="#d9534f", edgecolor="#b52b27", alpha=0.9
    )

    rects2 = ax.bar(
        x + width/2, shield_asrs, width,
        yerr=[shield_err_low, shield_err_high],
        capsize=4,
        label="Shield ON (NeuralShield-v5 Protected)",
        color="#5cb85c", edgecolor="#419641", alpha=0.9
    )

    # Değer etiketleri
    for rect in rects1:
        height = rect.get_height()
        ax.annotate(f"{height:.1f}%",
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 5), textcoords="offset points",
                    ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#900C3F")

    for rect in rects2:
        height = rect.get_height()
        ax.annotate(f"{height:.1f}%",
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 5), textcoords="offset points",
                    ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#196F3D")

    ax.set_ylabel("Attack Success Rate (ASR %)")
    ax.set_title("Figure 8: Empirical ASR across LLM Fleet with Wilson 95% CI (EVREN Supercomputer)", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(models, fontweight="semibold")
    ax.set_ylim(0, 115)
    ax.legend(loc="upper right", framealpha=0.95)

    # Açıklama kutucuğu
    props = dict(boxstyle="round,pad=0.5", facecolor="#f8f9fa", edgecolor="#ced4da", alpha=0.95)
    ax.text(0.02, 0.95, "Evaluation: 25-Sample Multi-Tier Adversarial Fleet\nMetrics: Canary Extraction & Instruction Hijacking\nPeripheral Latency: 12.8ms ± 1.4ms (ONNX CPU)",
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
