"""
CyberTech Neural Shield - Red-Team Sonuc Analizi ve Figur Uretimi.

redteam_benchmark.py ciktisini (JSON) okur; aile bazli ASR dususunu,
katman atfini ve False Refusal oranini tablolar + grafikler halinde uretir.

Kullanim:
    python scripts/analyze_redteam_results.py
    python scripts/analyze_redteam_results.py --results data/redteam/redteam_results.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parent.parent

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    HAS_MPL = True
except Exception:
    HAS_MPL = False


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def family_order(summary: dict) -> List[str]:
    fams = set()
    for cfg in summary.get("by_family", {}):
        fams.update(summary["by_family"][cfg].keys())
    return sorted(f for f in fams if f != "benign")


def build_markdown(data: dict) -> str:
    s = data["summary"]
    off = s["by_family"].get("off", {})
    on = s["by_family"].get("on", {})
    fams = family_order(s)

    lines = []
    lines.append("# CyberTech Neural Shield — Red-Team Sonuçları")
    lines.append("")
    lines.append(f"- Tarih: {data['metadata'].get('generated_at')}")
    lines.append(f"- Tekrar (k): {data['metadata'].get('repeats')}  |  "
                 f"Konfig: {data['metadata'].get('configs')}")
    lines.append(f"- Korpus: `{data['metadata'].get('corpus')}`")
    lines.append("")
    lines.append("> ASR = Attack Success Rate (sentetik canary'nin kullanıcıya "
                 "dönen çıktıda sızma oranı). Düşük olması iyidir.")
    lines.append("")
    lines.append("| Saldırı Ailesi | n | ASR OFF % | ASR ON % | Düşüş (puan) | "
                 "Blok % (ON) | L3-Kurtarım % (ON) | Gecikme ms (ON) |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for fam in fams:
        o = off.get(fam, {})
        n = on.get(fam, {})
        ao, an = o.get("asr_pct", 0.0), n.get("asr_pct", 0.0)
        lines.append(
            f"| {fam} | {n.get('n', 0)} | {ao:.2f} | {an:.2f} | "
            f"{ao - an:.2f} | {n.get('block_rate_pct', 0):.2f} | "
            f"{n.get('l3_saved_pct', 0):.2f} | {n.get('avg_latency_ms', 0)} |"
        )
    # Genel
    for cfg in ("off", "on"):
        o = s["overall"].get(cfg)
        if o:
            lines.append(f"| **GENEL ({cfg.upper()})** | {o['n']} | "
                         f"{o['asr_pct']:.2f} | {o['asr_pct']:.2f} | - | "
                         f"{o['block_rate_pct']:.2f} | {o['l3_saved_pct']:.2f} | "
                         f"{o['avg_latency_ms']} |")
    lines.append("")
    # Benign / FRR
    if "benign" in on or "benign" in off:
        bo = off.get("benign", {})
        bn = on.get("benign", {})
        lines.append("### Benign Kontrol / False Refusal")
        lines.append(f"- Benign (saldırısız) örneklerde yanlış bloklama (FRR, ON): "
                     f"**{bn.get('block_rate_pct', 0):.2f}%** (n={bn.get('n', 0)})")
        lines.append(f"- Benign'lerde canary sızması (OFF): {bo.get('asr_pct', 0):.2f}%")
    lines.append("")
    lines.append("*Not: Bu değerlendirme lab ortamında, sentetik canary sırları ve "
                 "kendi uygulama katmanımıza (OWASP LLM01) karşı yapılmıştır.*")
    return "\n".join(lines)


def make_figures(data: dict, outdir: Path) -> List[str]:
    if not HAS_MPL:
        print("[!] matplotlib yok, figur atlandi.")
        return []
    s = data["summary"]
    off = s["by_family"].get("off", {})
    on = s["by_family"].get("on", {})
    fams = family_order(s)
    made = []

    # Fig 1: ASR OFF vs ON
    x = range(len(fams))
    asr_off = [off.get(f, {}).get("asr_pct", 0) for f in fams]
    asr_on = [on.get(f, {}).get("asr_pct", 0) for f in fams]
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.bar([i - 0.2 for i in x], asr_off, width=0.4, label="Savunma KAPALI (OFF)", color="#d9534f")
    ax.bar([i + 0.2 for i in x], asr_on, width=0.4, label="Savunma AÇIK (ON)", color="#5bc0de")
    ax.set_ylabel("Attack Success Rate (%)")
    ax.set_title("Saldırı Ailesine Göre Canary Sızma Oranı (OFF vs ON)")
    ax.set_xticks(list(x))
    ax.set_xticklabels(fams, rotation=40, ha="right")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    p = outdir / "redteam_asr.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    made.append(str(p))

    # Fig 2: ON savunma atfi (blok vs L3-kurtarim vs sizinti) stacked
    blocked = [on.get(f, {}).get("block_rate_pct", 0) for f in fams]
    l3 = [on.get(f, {}).get("l3_saved_pct", 0) for f in fams]
    leaked = [on.get(f, {}).get("asr_pct", 0) for f in fams]
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.bar(fams, blocked, label="L1/L2 Blok", color="#5cb85c")
    ax.bar(fams, l3, bottom=blocked, label="L3 DLP Maskeledi", color="#f0ad4e")
    ax.bar(fams, leaked, bottom=[b + l for b, l in zip(blocked, l3)],
           label="Sızdı (Savunmasız)", color="#d9534f")
    ax.set_ylabel("Örnek Oranı (%)")
    ax.set_title("Savunma AÇIK iken Katman Atfı (Blok / L3-Maske / Sızıntı)")
    ax.tick_params(axis="x", rotation=40)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    p2 = outdir / "redteam_attribution.png"
    fig.savefig(p2, dpi=150)
    plt.close(fig)
    made.append(str(p2))
    return made


def build_local_markdown(data: dict) -> str:
    s = data["summary"]
    on = s.get("on", {})
    fams = sorted(k for k in on if k != "ALL")
    lines = []
    lines.append("# CyberTech Neural Shield — Yerel Filtre Testi (Layer 1+2)")
    lines.append("")
    lines.append(f"- Tarih: {data['metadata'].get('generated_at')}")
    lines.append(f"- Not: {data['metadata'].get('note')}")
    lines.append("")
    lines.append("| Saldırı Ailesi | n | Blok % | Regex (L1) % | L2 Malicious % | L2 Gecikme ms |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for fam in fams:
        d = on[fam]
        lines.append(f"| {fam} | {d['n']} | {d['block_rate_pct']:.2f} | {d['regex_hit_pct']:.2f} | "
                     f"{d['l2_malicious_pct']:.2f} | {d['avg_l2_latency_ms'] or 0} |")
    # Saldırı aileleri toplamı vs genel doğruluk
    attack_fams = [f for f in fams if f != "benign"]
    attack_n = sum(on[f]["n"] for f in attack_fams)
    attack_blk = sum(on[f]["n"] * (on[f]["block_rate_pct"] / 100.0) for f in attack_fams)
    attack_recall = (attack_blk / attack_n * 100.0) if attack_n else 0.0

    ben = on.get("benign", {})
    ben_n = ben.get("n", 0)
    ben_blk = ben_n * (ben.get("block_rate_pct", 0) / 100.0)
    fpr = (ben_blk / ben_n * 100.0) if ben_n else 0.0
    total_acc = ((attack_blk + (ben_n - ben_blk)) / (attack_n + ben_n) * 100.0) if (attack_n + ben_n) else 0.0

    lines.append(f"| **SALDIRILAR TOPLAMI (Attack Recall)** | {attack_n} | **{attack_recall:.2f}%** | - | - | - |")
    lines.append(f"| **GENEL DOĞRULUK (Accuracy)** | {attack_n + ben_n} | **{total_acc:.2f}%** | - | - | - |")
    lines.append("")
    lines.append(f"- **Saldırı Yakalama Oranı (Attack Recall / True Positive Rate):** **{attack_recall:.2f}%** ({int(round(attack_blk))}/{attack_n} saldırı engellendi)")
    lines.append(f"- **False Positive Oranı (Yanlış Alarm / Benign Blok):** **{fpr:.2f}%** ({int(round(ben_blk))}/{ben_n} meşru istek engellendi)")
    lines.append(f"- **Sistem Genel Doğruluğu (Overall Accuracy):** **{total_acc:.2f}%** ({attack_n + ben_n}/{attack_n + ben_n})")
    lines.append("")
    lines.append("*Not: Yerel test yalnızca Layer 1+2 tespitini ölçer; LLM sızıntısı (ASR) için `redteam_benchmark.py --engine http` kullanılmalıdır.*")
    return "\n".join(lines)


def make_local_figure(data: dict, outdir: Path) -> List[str]:
    if not HAS_MPL:
        print("[!] matplotlib yok, figur atlandi.")
        return []
    on = data["summary"].get("on", {})
    fams = sorted(k for k in on if k != "ALL")
    blocks = [on[f]["block_rate_pct"] for f in fams]
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.bar(fams, blocks, color="#5cb85c")
    ax.set_ylim(0, 105)
    ax.set_ylabel("Blok Oranı (%)")
    ax.set_title("Yerel Filtre Başarımı — Aile Bazlı Blok Oranı (Layer 1+2)")
    ax.tick_params(axis="x", rotation=40)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    p = outdir / "redteam_local_block.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    return [str(p)]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=None)
    ap.add_argument("--md-out", default=None)
    ap.add_argument("--fig-dir", default=str(ROOT / "docs" / "figures"))
    args = ap.parse_args()

    base = ROOT / "data" / "redteam"
    if args.results is None:
        http_p = base / "redteam_results.json"
        local_p = base / "redteam_results_local.json"
        args.results = str(http_p if http_p.exists() else local_p)

    res_path = Path(args.results)
    if not res_path.exists():
        print(f"[!] Sonuc dosyasi bulunamadi: {res_path}")
        print("    Once kosun:  python redteam_benchmark.py --configs off,on --repeats 3")
        return

    data = load(res_path)
    if data.get("dry_run"):
        print("[!] Bu dosya dry-run ciktisi. Gercek benchmark kosun.")
        return

    is_local = data.get("metadata", {}).get("engine") == "local"
    md = build_local_markdown(data) if is_local else build_markdown(data)
    if args.md_out is None:
        fname = "REDTEAM_RESULTS_LOCAL.md" if is_local else "REDTEAM_RESULTS.md"
        args.md_out = str(ROOT / "docs" / fname)
    md_path = Path(args.md_out)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(md, encoding="utf-8")
    print(md)
    print(f"\n[OK] Markdown -> {md_path}")

    fig_dir = Path(args.fig_dir)
    fig_dir.mkdir(parents=True, exist_ok=True)
    figs = make_local_figure(data, fig_dir) if is_local else make_figures(data, fig_dir)
    for f in figs:
        print(f"[OK] Figur -> {f}")


if __name__ == "__main__":
    main()
