"""
Script to generate publication-grade 300 DPI figures for the Computers and Informatics (C&I) manuscript.
Figure 1: NeuralShield Defense Architecture Pipeline
Figure 2: Empirical Vulnerability across Model Scale (Open-Weight vs Flagship CoT)
Figure 3: Methodological Ablation Experiments (Quantization Invariance & Prompt Hardening)
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Ensure output directory exists
os.makedirs("docs/figures", exist_ok=True)

# Set global matplotlib styles for scientific publishing
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9.5
plt.rcParams['ytick.labelsize'] = 9.5
plt.rcParams['legend.fontsize'] = 9.5
plt.rcParams['figure.titlesize'] = 13


def generate_figure1():
    """Generates Figure 1: NeuralShield Multi-Layer Pipeline Architecture."""
    fig, ax = plt.subplots(figsize=(10.5, 6.2), dpi=300)
    ax.axis('off')

    # Color palette
    c_input = '#EBF3FB'
    c_l0 = '#E0F2FE'
    c_l1 = '#FEF3C7'
    c_l2 = '#EDE9FE'
    c_gate = '#FEE2E2'
    c_llm = '#F1F5F9'
    c_l3 = '#DCFCE7'
    c_out = '#F0FDF4'
    c_block = '#FFE4E6'
    
    border_dark = '#334155'
    border_blue = '#0284C7'
    border_amber = '#D97706'
    border_purple = '#7C3AED'
    border_red = '#DC2626'
    border_green = '#16A34A'

    # Box Helper
    def draw_box(x, y, w, h, bg, border, title, desc, title_col='#0F172A', rad=0.03):
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad={rad}",
                                      facecolor=bg, edgecolor=border, linewidth=1.5)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h - 0.16, title, ha='center', va='top',
                fontsize=10.5, fontweight='bold', color=title_col)
        ax.text(x + w/2, y + 0.12, desc, ha='center', va='bottom',
                fontsize=8.5, color='#334155', linespacing=1.35)

    # 1. Incoming Untrusted Input
    draw_box(0.05, 0.68, 0.22, 0.24, c_input, border_dark,
             "Untrusted Input\nChannel",
             "• User Chat Prompts\n• Untrusted Documents\n• Tool / Web Payloads",
             '#0F172A')

    # 2. Layer 0: Structural Normalization
    draw_box(0.32, 0.68, 0.29, 0.24, c_l0, border_blue,
             "Layer 0: Structural Normalizer",
             "• NFKC Normalization\n• Zero-Width & Tag Stripping\n• Base64 / Hex / ROT13 Decode\n• Homoglyph Canonicalization",
             border_blue)

    # 3. Layer 1: Deterministic Pattern & Canary
    draw_box(0.66, 0.68, 0.29, 0.24, c_l1, border_amber,
             "Layer 1: Deterministic Engine",
             "• Multilingual Injection Patterns\n• Persona & Jailbreak Regex\n• Canary Token Leakage Traps\n• <1 ms Fast-Path Execution",
             border_amber)

    # 4. Layer 2: Multilingual Transformer Classifier
    draw_box(0.32, 0.36, 0.29, 0.24, c_l2, border_purple,
             "Layer 2: Semantic Transformer",
             "• mmBERT-base (307M) ONNX\n• 12-Language Multilingual Scope\n• Calibrated Risk Score (0-100)\n• Rejection Threshold: tau >= 0.70",
             border_purple)

    # 5. OR-Gate Arbiter
    draw_box(0.66, 0.36, 0.29, 0.24, c_gate, border_red,
             "Deterministic OR-Gate Arbiter",
             "hard_stego OR regex >= 60\nOR ml_risk >= 70\nOR (regex_hit AND ml_risk >= 50)",
             border_red)

    # 6. Target LLM Execution Barrier
    draw_box(0.32, 0.05, 0.29, 0.22, c_llm, border_dark,
             "Target LLM Execution",
             "• Context-Isolated Runtime\n• Greedy / Sampling Inference\n• Internal CoT + Content Streams",
             '#0F172A')

    # 7. Layer 3: Egress DLP Sanitizer
    draw_box(0.66, 0.05, 0.29, 0.22, c_l3, border_green,
             "Layer 3: Egress DLP Sanitizer",
             "• Real-Time Canary Token Trap\n• API Key & Credential Masking\n• Luhn / TCKN Checksum DLP\n• CoT & SSE Stream Scrubbing",
             border_green)

    # 8. Safe Refusal (Blocked)
    draw_box(0.05, 0.36, 0.22, 0.24, c_block, border_red,
             "Safe Refusal Gateway\n(Immediate Abort)",
             "• HTTP 403 Forbidden\n• Sanitized Security Warning\n• Zero LLM Computation Cost",
             border_red)

    # 9. Clean Output
    draw_box(0.05, 0.05, 0.22, 0.22, c_out, border_green,
             "Sanitized Output\nto User / System",
             "• Confidentiality Guaranteed\n• Neutralized Injections\n• Zero Data Exfiltration",
             border_green)

    # Connective Arrows
    arrow_style = dict(arrowstyle="->", lw=1.8, color="#475569")
    red_arrow = dict(arrowstyle="->", lw=2.0, color="#DC2626")
    green_arrow = dict(arrowstyle="->", lw=2.0, color="#16A34A")

    # Flow arrows
    # Input -> L0
    ax.annotate("", xy=(0.32, 0.80), xytext=(0.27, 0.80), arrowprops=arrow_style)
    # L0 -> L1
    ax.annotate("", xy=(0.66, 0.80), xytext=(0.61, 0.80), arrowprops=arrow_style)
    # L0 -> L2 (normalized text)
    ax.annotate("", xy=(0.465, 0.60), xytext=(0.465, 0.68), arrowprops=arrow_style)
    # L1 -> OR-Gate
    ax.annotate("", xy=(0.805, 0.60), xytext=(0.805, 0.68), arrowprops=arrow_style)
    # L2 -> OR-Gate
    ax.annotate("", xy=(0.66, 0.48), xytext=(0.61, 0.48), arrowprops=arrow_style)

    # OR-Gate -> Blocked
    ax.annotate("", xy=(0.27, 0.48), xytext=(0.66, 0.48), arrowprops=red_arrow)
    ax.text(0.29, 0.50, "Threat Detected (Blocked)", color='#DC2626', fontsize=8.5, fontweight='bold')

    # OR-Gate -> Target LLM
    ax.annotate("", xy=(0.465, 0.27), xytext=(0.75, 0.36),
                arrowprops=dict(arrowstyle="->", lw=1.8, color="#16A34A",
                                connectionstyle="arc3,rad=-0.2"))
    ax.text(0.56, 0.30, "Clean (Passed)", color='#16A34A', fontsize=8.5, fontweight='bold')

    # Target LLM -> Layer 3 DLP
    ax.annotate("", xy=(0.66, 0.16), xytext=(0.61, 0.16), arrowprops=arrow_style)
    ax.text(0.62, 0.18, "Raw Stream", color='#475569', fontsize=8, ha='center')

    # Layer 3 DLP -> Clean Output
    ax.annotate("", xy=(0.27, 0.16), xytext=(0.66, 0.16), arrowprops=green_arrow)
    ax.text(0.465, 0.18, "DLP Masked & Sanitized", color='#16A34A', fontsize=8.5, fontweight='bold', ha='center')

    plt.tight_layout()
    fig.savefig("docs/figures/figure1_architecture.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Figure 1 generated successfully: docs/figures/figure1_architecture.png")


def generate_figure2():
    """Generates Figure 2: Empirical Attack Success Rate (ASR) across Model Scale and CoT Leakage."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.2), dpi=300, gridspec_kw={'width_ratios': [1.8, 1.2]})

    # --- Panel A: 10 Open-Weight Models (Tier-1 and Tier-2) ---
    models_core = [
        'Qwen2.5-1.5B', 'Phi-3-mini\n(3.8B)', 'Gemma-2-2B', 'Llama-3.2-3B', 'Qwen2.5-3B',
        'Gemma-2-9B', 'Qwen2.5-14B', 'Llama-3.1-8B', 'Qwen2.5-7B', 'Mistral-7B\n-v0.3'
    ]
    asr_off = [4.95, 7.92, 8.91, 13.86, 25.74, 8.91, 10.89, 14.85, 18.81, 40.59]
    # 95% Wilson Confidence Intervals
    ci_low = [2.1, 4.1, 4.8, 8.4, 18.2, 4.8, 6.2, 9.2, 12.4, 31.5]
    ci_high = [11.1, 14.9, 16.1, 21.9, 35.0, 16.1, 18.5, 23.1, 27.5, 50.3]
    err_low = [a - l for a, l in zip(asr_off, ci_low)]
    err_high = [h - a for a, h in zip(asr_off, ci_high)]
    yerr = [err_low, err_high]

    asr_on = [0.0] * 10

    x = np.arange(len(models_core))
    width = 0.38

    bars1 = ax1.bar(x - width/2, asr_off, width, yerr=yerr, capsize=3.5,
                    label='Shield OFF (Unprotected LLM)', color='#DC2626', alpha=0.85, edgecolor='#991B1B')
    bars2 = ax1.bar(x + width/2, asr_on, width,
                    label='NeuralShield ON (Multi-Layer)', color='#16A34A', alpha=0.9, edgecolor='#166534')

    ax1.set_ylabel('Attack Success Rate (ASR %)', fontweight='bold')
    ax1.set_title('(a) Open-Weight Models (Tier-1 & Tier-2, N=101)', fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(models_core, rotation=35, ha='right', fontsize=8.5)
    ax1.set_ylim(-1, 55)
    ax1.grid(axis='y', linestyle='--', alpha=0.4)
    ax1.legend(loc='upper left', framealpha=0.95)

    # Highlight scale non-monotonicity
    ax1.annotate('Scale Invariance:\n14B safer than 3B/7B\n(Indirect Doc 42.3%)',
                 xy=(6, 11), xytext=(4.5, 38),
                 arrowprops=dict(facecolor='#1E293B', shrink=0.08, width=1, headwidth=5),
                 fontsize=8, ha='center', bbox=dict(boxstyle='round,pad=0.3', facecolor='#F8FAFC', edgecolor='#CBD5E1'))

    # Highlight Mistral spike
    ax1.annotate('Severe Vulnerability:\nMistral-7B 40.59%',
                 xy=(9, 41), xytext=(8.0, 48),
                 arrowprops=dict(facecolor='#991B1B', shrink=0.08, width=1, headwidth=5),
                 fontsize=8, ha='center', bbox=dict(boxstyle='round,pad=0.3', facecolor='#FEF2F2', edgecolor='#FCA5A5'))

    # --- Panel B: Tier-3 Flagship API Models (EVREN H200 Supercomputer) ---
    models_api = ['DeepSeek\n-v4.1-Flash', 'GLM-5.3\nFlagship', 'Qwen3.8\n-Flash-Next', 'Gemma-4\n-31B']
    api_final = [0.0, 0.0, 0.0, 0.0]
    api_cot = [0.0, 1.98, 14.85, 66.34]
    api_cot_ci_low = [0.0, 0.5, 9.2, 56.7]
    api_cot_ci_high = [3.7, 6.9, 23.1, 74.8]
    cot_err = [[c - l for c, l in zip(api_cot, api_cot_ci_low)],
               [h - c for c, h in zip(api_cot, api_cot_ci_high)]]

    x2 = np.arange(len(models_api))
    width2 = 0.36

    b_final = ax2.bar(x2 - width2/2, api_final, width2,
                      label='Final Content ASR (Refusal)', color='#3B82F6', alpha=0.85, edgecolor='#1D4ED8')
    b_cot = ax2.bar(x2 + width2/2, api_cot, width2, yerr=cot_err, capsize=3.5,
                    label='Silent CoT Leakage ASR', color='#D97706', alpha=0.85, edgecolor='#B45309')

    ax2.set_ylabel('Exfiltration Rate (%)', fontweight='bold')
    ax2.set_title('(b) Flagship API Models (Tier-3, N=101)', fontweight='bold')
    ax2.set_xticks(x2)
    ax2.set_xticklabels(models_api, rotation=25, ha='right', fontsize=8.5)
    ax2.set_ylim(-1, 80)
    ax2.grid(axis='y', linestyle='--', alpha=0.4)
    ax2.legend(loc='upper left', framealpha=0.95)

    # Highlight Silent CoT Exfiltration
    ax2.annotate('Silent CoT Exfiltration:\nContent Refused (0.0%)\nSecret Leaked in CoT (66.3%)',
                 xy=(3 + width2/2, 66.34), xytext=(1.8, 68),
                 arrowprops=dict(facecolor='#B45309', shrink=0.08, width=1, headwidth=5),
                 fontsize=8, ha='center', bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFFBEB', edgecolor='#FDE68A'))

    plt.tight_layout()
    fig.savefig("docs/figures/figure2_scale_vulnerability.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Figure 2 generated successfully: docs/figures/figure2_scale_vulnerability.png")


def generate_figure3():
    """Generates Figure 3: Quantization Invariance (FP16 vs NF4) & Prompt Hardening Trade-off."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.8), dpi=300)

    # --- Panel A: FP16 vs 4-Bit NF4 (N=101) ---
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

    # Invariance text
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

    bar_asr = ax2.bar(xp - wp/2, asr_p, wp, yerr=asr_p_ci, capsize=4,
                      label='Attack ASR % (N=101)', color='#EF4444', alpha=0.85, edgecolor='#B91C1C')
    bar_fp = ax2_twin.bar(xp + wp/2, fp_benign, wp,
                          label='Benign Canary Leakage % (N=60)', color='#F59E0B', alpha=0.85, edgecolor='#D97706')

    ax2.set_ylabel('Attack Success Rate (ASR %)', color='#B91C1C', fontweight='bold')
    ax2_twin.set_ylabel('Benign Canary Leakage (%)', color='#D97706', fontweight='bold')
    ax2.set_title('(b) System Prompt Hardening Cost (Qwen2.5-3B)', fontweight='bold')
    ax2.set_xticks(xp)
    ax2.set_xticklabels(conditions, fontsize=9.0)
    ax2.set_ylim(-1, 40)
    ax2_twin.set_ylim(-0.2, 5.0)
    ax2.grid(axis='y', linestyle='--', alpha=0.4)

    # Combined legend
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
