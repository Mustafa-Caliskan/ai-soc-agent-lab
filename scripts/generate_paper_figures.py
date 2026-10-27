"""
Publication-grade figures for the Computers and Informatics (C&I) manuscript.

Figure 1: NeuralShield layered gateway architecture (L0-L5) with a side
          evaluation/benchmark module. Emitted at 3600x2200 px.
Figure 2: Empirical vulnerability across model scale (open-weight ASR and
          Tier-3 Silent CoT exfiltration).
Figure 3: Methodological ablations (quantization invariance, prompt hardening).
Figure S: Three-phase system pipeline flow (offline preparation, online
          defense, empirical validation). Emitted at 3600x2180 px.

Both architecture drawings are authored in physical points (1 unit = 1/72 in)
so that a 446 pt canvas maps 1:1 onto the 6.2 in text column of the journal
template: a 6 pt label in the drawing prints at 6 pt on paper. The canvas is
rasterised at ~581 DPI, which yields the required 3600 px width.
"""

import os

import fitz
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

os.makedirs("docs/figures", exist_ok=True)

plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"] = ["Times New Roman", "DejaVu Serif"]
plt.rcParams["mathtext.fontset"] = "stix"
plt.rcParams["font.size"] = 10
plt.rcParams["axes.labelsize"] = 11
plt.rcParams["axes.titlesize"] = 12
plt.rcParams["xtick.labelsize"] = 9.5
plt.rcParams["ytick.labelsize"] = 9.5
plt.rcParams["legend.fontsize"] = 9.5
plt.rcParams["figure.titlesize"] = 13

FONT = "Helvetica"


# --------------------------------------------------------------------------- #
# SVG helpers (all coordinates in points)                                     #
# --------------------------------------------------------------------------- #
def _defs():
    return """
  <defs>
    <marker id="arrow-slate" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5"
            markerHeight="5" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#475569" />
    </marker>
    <marker id="arrow-green" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5"
            markerHeight="5" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#16A34A" />
    </marker>
    <marker id="arrow-blue" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5"
            markerHeight="5" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#2563EB" />
    </marker>
    <marker id="arrow-teal" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5"
            markerHeight="5" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#0F766E" />
    </marker>
    <marker id="arrow-violet" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5"
            markerHeight="5" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#7C3AED" />
    </marker>
    <marker id="arrow-slate-s" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="4"
             markerHeight="4" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#64748B" />
    </marker>
  </defs>
"""


def _text(x, y, s, size=5.2, color="#334155", weight="400", anchor="start",
          style="normal", family=None):
    fam = family or FONT
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}" '
            f'text-anchor="{anchor}" font-style="{style}">{s}</text>')


def _chip(x, y, w, h, label, size=5.0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w}" height="{h}" rx="2.5" '
            f'fill="#FFFFFF" stroke="#CBD5E1" stroke-width="0.5" />'
            + _text(x + w / 2, y + h / 2 + size * 0.36, label, size=size,
                    color="#334155", anchor="middle"))


# --------------------------------------------------------------------------- #
# Figure 1: layered gateway architecture                                      #
# --------------------------------------------------------------------------- #
def generate_svg_architecture():
    W, H = 446.0, 272.5
    layers = [
        dict(tag="L0", color="#16A34A",
             title="Structural Normalization & Input Sanitization",
             chips=["Unicode NFKC", "Zero-width strip", "Base64/Hex/ROT13"]),
        dict(tag="L1", color="#0F766E",
             title="Rule & Canary Fast-Path (&lt;1 ms)",
             chips=["Multilingual regex", "Canary probes", "S_regex &gt;= 60"]),
        dict(tag="L2", color="#7C3AED",
             title="Multilingual Semantic Classifier",
             chips=["mmBERT 307M", "12 languages", "P_mal, tau = 0.70"]),
        dict(tag="L3", color="#EA580C",
             title="Adaptive Decision Gate (OR-Gate Arbiter)",
             chips=["D_in = 1: HTTP 403", "D_in = 0: forward", "Zero LLM compute"]),
        dict(tag="L4", color="#2563EB",
             title="Target LLM Orchestration",
             chips=["Canary-bound prompt", "Content stream", "Reasoning stream"]),
        dict(tag="L5", color="#DC2626",
             title="Egress DLP Layer (Dual-Stream)",
             chips=["Secret registry", "CoT reasoning scrub", "Luhn / TCKN"]),
    ]

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
         f'width="{W}" height="{H}">', _defs(),
         '<rect width="100%" height="100%" fill="#FFFFFF" />']

    # ---- Untrusted input card -------------------------------------------- #
    p.append('<rect x="6" y="12" width="62" height="179" rx="3" fill="#FFFFFF" '
             'stroke="#64748B" stroke-width="0.7" />')
    p.append('<rect x="6" y="12" width="62" height="15" rx="3" fill="#F1F5F9" />')
    p.append(_text(37, 22.5, "Untrusted Input", size=6.2, color="#0F172A",
                   weight="700", anchor="middle"))
    for i, item in enumerate(["Chat prompts", "RAG passages", "Tool payloads",
                              "Uploaded files", "Encoded text", "Stego/Unicode"]):
        p.append(_text(11, 39 + i * 9.5, item, size=5.0))
    p.append('<path d="M 11 100 L 63 100" stroke="#E2E8F0" stroke-width="0.5" />')
    p.append(_text(11, 110, "Threat classes", size=5.0, color="#64748B",
                   weight="700"))
    for i, item in enumerate(["Direct injection", "Indirect document",
                              "Encoding", "Steganography"]):
        p.append(_text(11, 121 + i * 9.5, item, size=5.0))

    # ---- Input arrow ------------------------------------------------------ #
    p.append('<path d="M 68 25 L 74 25" fill="none" stroke="#475569" '
             'stroke-width="0.8" marker-end="url(#arrow-slate)" />')

    # ---- Layer bands ------------------------------------------------------ #
    y0, h, gap = 12.0, 24.0, 7.0
    for i, L in enumerate(layers):
        y = y0 + i * (h + gap)
        p.append(f'<rect x="74" y="{y}" width="258" height="{h}" rx="3" '
                 f'fill="#F8FAFC" stroke="{L["color"]}" stroke-width="0.8" />')
        p.append(f'<rect x="74" y="{y}" width="26" height="{h}" rx="3" '
                 f'fill="{L["color"]}" />')
        p.append(_text(87, y + 11.5, L["tag"], size=8.0, color="#FFFFFF",
                       weight="700", anchor="middle"))
        p.append(_text(105, y + 11, L["title"], size=6.4, color="#0F172A",
                       weight="700"))
        for c in range(3):
            p.append(_chip(105 + c * 73, y + 13, 70, 9, L["chips"][c]))
        if i < len(layers) - 1:
            p.append(f'<path d="M 203 {y + h} L 203 {y + h + gap}" fill="none" '
                     f'stroke="#475569" stroke-width="0.8" '
                     f'marker-end="url(#arrow-slate)" />')

    # ---- Evaluation module ------------------------------------------------ #
    p.append('<rect x="338" y="12" width="102" height="179" rx="3" '
             'fill="#F8FAFC" stroke="#334155" stroke-width="0.7" />')
    p.append('<rect x="338" y="12" width="102" height="15" rx="3" fill="#E2E8F0" />')
    p.append(_text(389, 22.5, "Evaluation &amp; Benchmark", size=5.8,
                   color="#0F172A", weight="700", anchor="middle"))
    items = [
        ("Benchmark pool", "N = 2,849 source-disjoint"),
        ("Red-team pool", "101 attacks + 60 benign"),
        ("Uncertainty", "Wilson 95% CI, bootstrap"),
        ("Paired tests", "Exact McNemar, N = 101"),
        ("Model fleet", "14 LLMs, Tier-1 to Tier-3"),
    ]
    for i, (a, b) in enumerate(items):
        yy = 38 + i * 30
        p.append(f'<path d="M 342 {yy - 6} L 436 {yy - 6}" stroke="#E2E8F0" '
                 f'stroke-width="0.5" />')
        p.append(_text(343, yy, a, size=5.4, color="#0F172A", weight="700"))
        p.append(_text(343, yy + 8, b, size=5.1, color="#475569"))

    # ---- Delivery card ---------------------------------------------------- #
    p.append('<path d="M 203 191 L 203 198" fill="none" stroke="#16A34A" '
             'stroke-width="0.8" marker-end="url(#arrow-green)" />')
    p.append('<rect x="74" y="198" width="366" height="23" rx="3" fill="#F0FDF4" '
             'stroke="#16A34A" stroke-width="0.7" />')
    p.append(_text(80, 207.5, "Sanitized Delivery to Client", size=6.4,
                   color="#15803D", weight="700"))
    p.append(_text(80, 216.5,
                   "Content and reasoning channels both scrubbed; exact-match "
                   "canary count = 0; blocked traffic never reaches the LLM.",
                   size=5.1, color="#334155"))

    # ---- OR-gate equation bar -------------------------------------------- #
    p.append('<rect x="74" y="226" width="366" height="24" rx="3" fill="#FFFFFF" '
             'stroke="#CBD5E1" stroke-width="0.6" />')
    p.append(_text(80, 235, "Deterministic OR-Gate (Eq. 1)", size=5.4,
                   color="#0F172A", weight="700"))
    p.append(_text(80, 244.5,
                   "D_in = 1 if stego OR (S_regex &gt;= 60) OR "
                   "(P_malicious &gt;= 0.70) OR (regex_hit AND ML = malicious)",
                   size=5.1, color="#334155"))

    p.append(_text(6, 264, "Ingress path: L0-L3. Egress path: L4-L5. Latencies "
                   "measured on a 2-thread x86 CPU under FP32 ONNX (Table 3).",
                   size=5.1, color="#64748B", style="italic"))
    p.append("</svg>")
    return "\n".join(p)


def _render_svg(svg_data, output_path, target_w, target_h):
    from PIL import Image

    doc = fitz.open(stream=svg_data.encode("utf-8"), filetype="svg")
    page = doc[0]
    dpi = target_w * 72.0 / page.rect.width
    pix = page.get_pixmap(dpi=int(dpi) + 1)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pix.save(output_path)
    doc.close()

    im = Image.open(output_path)
    if im.size != (target_w, target_h):
        im = im.resize((target_w, target_h), Image.LANCZOS)
        im.save(output_path)
    print(f"Successfully rendered SVG to {output_path} ({target_w}x{target_h})")


def generate_figure1():
    _render_svg(generate_svg_architecture(), "docs/figures/figure1_architecture.png",
                3600, 2200)


# --------------------------------------------------------------------------- #
# Figure S: three-phase pipeline flow                                         #
# --------------------------------------------------------------------------- #
def generate_svg_pipeline():
    W, H = 446.0, 270.0
    phases = [
        dict(tag="PHASE A", color="#2563EB", bg="#EFF6FF", stroke="#93C5FD",
             title="Offline Data Preparation and Model Fine-Tuning",
             nodes=[("Open Sources", "JailbreakPrompts (MIT)", "Dolly-15k (CC-BY-SA)"),
                    ("Symmetric Generation", "One teacher model", "both classes"),
                    ("Quality Control", "DeBERTa + Deepset", "+ Wolf ensemble"),
                    ("Stratified Split", "70 / 15 / 15", "69,021 / 14,794 / 14,791"),
                    ("mmBERT Fine-Tuning", "307M, focal loss", "12 languages"),
                    ("ONNX FP32 Export", "1.23 GB artifact", "CPU deployment")],
             note="Output: a calibrated 12-language classifier exported for CPU inference."),
        dict(tag="PHASE B", color="#0F766E", bg="#ECFDF5", stroke="#5EEAD4",
             title="Online Real-Time Ingress and Egress Defense",
             nodes=[("Client Request", "chat, RAG, tool", "untrusted payload"),
                    ("L0 Normalize", "NFKC, homoglyphs", "recursive decoding"),
                    ("L1 Regex", "compiled automata", "S_regex &gt;= 60"),
                    ("L2 mmBERT", "P_malicious", "tau = 0.70"),
                    ("L3 OR-Gate", "1 -&gt; HTTP 403", "0 -&gt; forward"),
                    ("L4 Target LLM", "isolated context", "content + CoT"),
                    ("L5 Egress DLP", "dual-stream", "0 canary egress")],
             note="Output: allow/deny decision at ingress, dual-stream sanitisation at egress."),
        dict(tag="PHASE C", color="#7C3AED", bg="#F5F3FF", stroke="#C4B5FD",
             title="Empirical Validation and Red-Team Campaign",
             nodes=[("Model Fleet (14)", "Tier-1 and Tier-2", "Tier-3 on H200"),
                    ("Shield OFF / ON", "paired runs", "greedy, T = 0.0"),
                    ("Leak Detection", "exact and separator-", "normalized match"),
                    ("Uncertainty", "95% Wilson CI", "bootstrap B = 1,000"),
                    ("Paired Tests", "exact McNemar", "N = 101 pairs"),
                    ("Evidence", "Tables 1-10, Fig. 1-3", "per-item JSON logs")],
             note="Output: paired evidence with confidence intervals and p-values."),
    ]

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
         f'width="{W}" height="{H}">', _defs(),
         '<rect width="100%" height="100%" fill="#FFFFFF" />']

    band_y = [6.0, 92.0, 178.0]
    band_h = 82.0
    for bi, ph in enumerate(phases):
        y = band_y[bi]
        p.append(f'<rect x="4" y="{y}" width="438" height="{band_h}" rx="4" '
                 f'fill="{ph["bg"]}" stroke="{ph["stroke"]}" stroke-width="0.7" />')
        p.append(f'<rect x="4" y="{y}" width="40" height="12" rx="3" '
                 f'fill="{ph["color"]}" />')
        p.append(_text(24, y + 8.6, ph["tag"], size=5.2, color="#FFFFFF",
                       weight="700", anchor="middle"))
        p.append(_text(48, y + 9, ph["title"], size=5.8, color=ph["color"],
                       weight="700"))

        n = len(ph["nodes"])
        margin = 5.0
        avail = 438 - 2 * margin
        w = 56.0 if n == 7 else 66.0
        gap = (avail - n * w) / (n - 1)
        for i, (title, l1, l2) in enumerate(ph["nodes"]):
            x = 4 + margin + i * (w + gap)
            ny = y + 16
            p.append(f'<rect x="{x:.1f}" y="{ny:.1f}" width="{w}" height="42" '
                     f'rx="2.5" fill="#FFFFFF" stroke="{ph["stroke"]}" '
                     f'stroke-width="0.6" />')
            p.append(f'<rect x="{x:.1f}" y="{ny:.1f}" width="{w}" height="2.6" '
                     f'rx="1.3" fill="{ph["color"]}" />')
            p.append(_text(x + 3, ny + 12, title, size=5.0, color="#0F172A",
                           weight="700"))
            p.append(_text(x + 3, ny + 23, l1, size=4.8, color="#475569"))
            p.append(_text(x + 3, ny + 33, l2, size=4.8, color="#64748B"))
            if i < n - 1:
                ax1 = x + w + 1
                ax2 = x + w + gap - 1
                my = ny + 21
                p.append(f'<path d="M {ax1:.1f} {my:.1f} L {ax2:.1f} {my:.1f}" '
                         f'fill="none" stroke="{ph["color"]}" stroke-width="0.7" '
                         f'marker-end="url(#arrow-blue)" />')

        p.append(_text(48, y + band_h - 8, ph["note"], size=5.1,
                       color="#64748B", style="italic"))

    p.append('<path d="M 223 88 L 223 92" fill="none" stroke="#475569" '
             'stroke-width="0.8" marker-end="url(#arrow-slate)" />')
    p.append('<path d="M 223 174 L 223 178" fill="none" stroke="#475569" '
             'stroke-width="0.8" marker-end="url(#arrow-slate)" />')
    p.append(_text(4, 266, "Each phase is reproducible from the archived scripts "
                   "and per-item JSON logs released with the manuscript.",
                   size=5.1, color="#64748B", style="italic"))
    p.append("</svg>")
    return "\n".join(p)


def generate_pipeline_figure():
    _render_svg(generate_svg_pipeline(), "docs/figures/figure2_pipeline_flow.png",
                3600, 2180)


# --------------------------------------------------------------------------- #
# Figure 2: empirical ASR across model scale                                  #
# --------------------------------------------------------------------------- #
def generate_figure2():
    """Generates Figure 2: Empirical Attack Success Rate (ASR) across Model Scale and CoT Leakage."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.2), dpi=300, gridspec_kw={'width_ratios': [1.8, 1.2]})

    models_core = [
        'Qwen2.5-1.5B', 'Phi-3-mini\n(3.8B)', 'Gemma-2-2B', 'Llama-3.2-3B', 'Qwen2.5-3B',
        'Gemma-2-9B', 'Qwen2.5-14B', 'Llama-3.1-8B', 'Qwen2.5-7B', 'Mistral-7B\n-v0.3'
    ]
    asr_off = [4.95, 7.92, 8.91, 13.86, 25.74, 8.91, 10.89, 14.85, 18.81, 40.59]
    ci_low = [2.1, 4.1, 4.8, 8.4, 18.2, 4.8, 6.2, 9.2, 12.4, 31.5]
    ci_high = [11.1, 14.9, 16.1, 21.9, 35.0, 16.1, 18.5, 23.1, 27.5, 50.3]
    err_low = [a - l for a, l in zip(asr_off, ci_low)]
    err_high = [h - a for a, h in zip(asr_off, ci_high)]
    yerr = [err_low, err_high]

    asr_on = [0.0] * 10

    x = np.arange(len(models_core))
    width = 0.38

    ax1.bar(x - width/2, asr_off, width, yerr=yerr, capsize=3.5,
            label='Shield OFF (Unprotected LLM)', color='#DC2626', alpha=0.85, edgecolor='#991B1B')
    ax1.bar(x + width/2, asr_on, width,
            label='NeuralShield ON (Multi-Layer)', color='#16A34A', alpha=0.9, edgecolor='#166534')

    ax1.set_ylabel('Attack Success Rate (ASR %)', fontweight='bold')
    ax1.set_title('(a) Open-Weight Models (Tier-1 & Tier-2, N=101)', fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(models_core, rotation=35, ha='right', fontsize=8.5)
    ax1.set_ylim(-1, 55)
    ax1.grid(axis='y', linestyle='--', alpha=0.4)
    ax1.legend(loc='upper left', framealpha=0.95)

    ax1.annotate('Scale Invariance:\n14B safer than 3B/7B\n(Indirect Doc 42.3%)',
                 xy=(6, 11), xytext=(4.5, 38),
                 arrowprops=dict(facecolor='#1E293B', shrink=0.08, width=1, headwidth=5),
                 fontsize=8, ha='center', bbox=dict(boxstyle='round,pad=0.3', facecolor='#F8FAFC', edgecolor='#CBD5E1'))

    ax1.annotate('Severe Vulnerability:\nMistral-7B 40.59%',
                 xy=(9, 41), xytext=(8.0, 48),
                 arrowprops=dict(facecolor='#991B1B', shrink=0.08, width=1, headwidth=5),
                 fontsize=8, ha='center', bbox=dict(boxstyle='round,pad=0.3', facecolor='#FEF2F2', edgecolor='#FCA5A5'))

    # --- Panel B: Tier-3 flagship API models ---
    models_api = ['DeepSeek\n-v4.1-Flash', 'GLM-5.3\nFlagship', 'Qwen3.8\n-Flash-Next', 'Gemma-4\n-31B']
    api_final = [0.0, 0.0, 0.0, 0.0]
    api_cot = [0.0, 1.98, 14.85, 66.34]
    api_cot_ci_low = [0.0, 0.5, 9.2, 56.7]
    api_cot_ci_high = [3.7, 6.9, 23.1, 74.8]
    cot_err = [[c - l for c, l in zip(api_cot, api_cot_ci_low)],
               [h - c for c, h in zip(api_cot, api_cot_ci_high)]]

    x2 = np.arange(len(models_api))
    width2 = 0.36

    ax2.bar(x2 - width2/2, api_final, width2,
            label='Final Content ASR (Refusal)', color='#3B82F6', alpha=0.85, edgecolor='#1D4ED8')
    ax2.bar(x2 + width2/2, api_cot, width2, yerr=cot_err, capsize=3.5,
            label='Silent CoT Leakage ASR', color='#D97706', alpha=0.85, edgecolor='#B45309')

    ax2.set_ylabel('Exfiltration Rate (%)', fontweight='bold')
    ax2.set_title('(b) Flagship API Models (Tier-3, N=101)', fontweight='bold')
    ax2.set_xticks(x2)
    ax2.set_xticklabels(models_api, rotation=25, ha='right', fontsize=8.5)
    ax2.set_ylim(-1, 80)
    ax2.grid(axis='y', linestyle='--', alpha=0.4)
    ax2.legend(loc='upper left', framealpha=0.95)

    ax2.annotate('Silent CoT Exfiltration:\nContent Refused (0.0%)\nSecret Leaked in CoT (66.3%)',
                 xy=(3 + width2/2, 66.34), xytext=(1.8, 68),
                 arrowprops=dict(facecolor='#B45309', shrink=0.08, width=1, headwidth=5),
                 fontsize=8, ha='center', bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFFBEB', edgecolor='#FDE68A'))

    plt.tight_layout()
    fig.savefig("docs/figures/figure2_scale_vulnerability.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Figure 2 generated successfully: docs/figures/figure2_scale_vulnerability.png")


# --------------------------------------------------------------------------- #
# Figure 3: quantization invariance and prompt hardening                      #
# --------------------------------------------------------------------------- #
def generate_figure3():
    """Generates Figure 3: Quantization Invariance (FP16 vs NF4) & Prompt Hardening Trade-off."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.8), dpi=300)

    models_quant = ['Mistral-7B-v0.3', 'Llama-3.1-8B']
    asr_4bit = [40.59, 14.85]
    ci_4bit = [[40.59 - 31.5, 14.85 - 9.2], [50.3 - 40.59, 23.1 - 14.85]]

    asr_fp16 = [29.70, 16.83]
    ci_fp16 = [[29.70 - 21.7, 16.83 - 10.8], [39.2 - 29.70, 25.3 - 16.83]]

    xq = np.arange(len(models_quant))
    wq = 0.32

    ax1.bar(xq - wq/2, asr_4bit, wq, yerr=ci_4bit, capsize=4,
            label='4-bit NF4 Quantized', color='#6366F1', alpha=0.85, edgecolor='#4338CA')
    ax1.bar(xq + wq/2, asr_fp16, wq, yerr=ci_fp16, capsize=4,
            label='Unquantized Pure FP16', color='#06B6D4', alpha=0.85, edgecolor='#0891B2')

    ax1.set_ylabel('Attack Success Rate (ASR %)', fontweight='bold')
    ax1.set_title('(a) Quantization Invariance (N=101 Full Set)', fontweight='bold')
    ax1.set_xticks(xq)
    ax1.set_xticklabels(models_quant, fontsize=9.5)
    ax1.set_ylim(0, 60)
    ax1.grid(axis='y', linestyle='--', alpha=0.4)
    ax1.legend(loc='upper right', framealpha=0.95)

    ax1.text(0, 52, 'Overlapping CIs:\nQuantization does not\ninduce vulnerability',
             ha='center', fontsize=8, bbox=dict(boxstyle='round,pad=0.3', facecolor='#F8FAFC', edgecolor='#CBD5E1'))
    ax1.text(1, 28, 'Delta: +1.98%\nFP16 strictly >= 4-bit',
             ha='center', fontsize=8, bbox=dict(boxstyle='round,pad=0.3', facecolor='#F8FAFC', edgecolor='#CBD5E1'))

    # --- Panel B: System Prompt Hardening Trade-off (Qwen2.5-3B, N=161) ---
    conditions = ['Standard Prompt', 'Hardened Prompt', 'NeuralShield (ON)']
    asr_p = [24.75, 16.83, 0.0]
    asr_p_ci = [[24.75 - 17.4, 16.83 - 10.8, 0.0], [34.0 - 24.75, 25.3 - 16.83, 3.7]]
    fp_benign = [0.0, 1.67, 0.0]  # Benign canary leakage (secret leak, not over-refusal)

    xp = np.arange(len(conditions))
    wp = 0.35

    ax2_twin = ax2.twinx()

    ax2.bar(xp - wp/2, asr_p, wp, yerr=asr_p_ci, capsize=4,
            label='Attack ASR % (N=101)', color='#EF4444', alpha=0.85, edgecolor='#B91C1C')
    ax2_twin.bar(xp + wp/2, fp_benign, wp,
                 label='Benign Canary Leakage % (N=60)', color='#F59E0B', alpha=0.85, edgecolor='#D97706')

    ax2.set_ylabel('Attack Success Rate (ASR %)', color='#B91C1C', fontweight='bold')
    ax2_twin.set_ylabel('Benign Canary Leakage (%)', color='#D97706', fontweight='bold')
    ax2.set_title('(b) System Prompt Hardening Cost (Qwen2.5-3B)', fontweight='bold')
    ax2.set_xticks(xp)
    ax2.set_xticklabels(conditions, fontsize=9.0)
    ax2.set_ylim(-1, 40)
    ax2_twin.set_ylim(-0.2, 5.0)
    ax2.grid(axis='y', linestyle='--', alpha=0.4)

    lines, labels = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper right', framealpha=0.95)

    ax2.annotate('Residual Leak: 16.83%\nBenign Leakage: +1.67%',
                 xy=(1 - wp/2, 16.83), xytext=(1.2, 28),
                 arrowprops=dict(facecolor='#B91C1C', shrink=0.08, width=1, headwidth=4),
                 fontsize=8, bbox=dict(boxstyle='round,pad=0.3', facecolor='#FEF2F2', edgecolor='#FCA5A5'))

    plt.tight_layout()
    fig.savefig("docs/figures/figure3_ablations.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Figure 3 generated successfully: docs/figures/figure3_ablations.png")


if __name__ == "__main__":
    generate_figure1()
    generate_figure2()
    generate_figure3()
    generate_pipeline_figure()
