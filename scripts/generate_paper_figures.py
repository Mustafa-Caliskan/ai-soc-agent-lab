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
    output_path = "docs/figures/figure1_architecture.png"
    # Set high quality academic styling
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
    
    fig, ax = plt.subplots(figsize=(14.0, 7.6), dpi=300)
    ax.set_xlim(0, 14.5)
    ax.set_ylim(0, 7.8)
    ax.axis('off')

    # Color Palette: Clean, professional, high-end academic
    # Backgrounds
    bg_canvas = '#FFFFFF'
    c_group_ingress = '#F8FAFC'
    c_group_egress = '#F0FDF4'
    c_group_exec = '#F8FAFC'
    
    c_input_bg = '#F1F5F9'
    c_l0_bg = '#EFF6FF'
    c_l1_bg = '#FFFBEB'
    c_l2_bg = '#FAF5FF'
    c_gate_bg = '#FEF2F2'
    c_llm_bg = '#F8FAFC'
    c_l3_bg = '#ECFDF5'
    c_refusal_bg = '#FEF2F2'
    c_out_bg = '#F0FDF4'
    
    # Borders
    border_slate = '#94A3B8'
    border_blue = '#2563EB'
    border_amber = '#D97706'
    border_purple = '#7C3AED'
    border_red = '#DC2626'
    border_green = '#059669'
    border_dark = '#334155'
    
    # Text colors
    tx_dark = '#0F172A'
    tx_body = '#334155'
    tx_sub = '#64748B'

    # Helper: Draw Container Group
    def draw_container(x, y, w, h, bg, border, label, label_col='#475569'):
        box = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.15",
                                     facecolor=bg, edgecolor=border, linewidth=1.2, linestyle='--')
        ax.add_patch(box)
        ax.text(x + 0.25, y + h - 0.28, label, fontsize=9.5, fontweight='bold', color=label_col,
                ha='left', va='top')

    # Helper: Draw Component Box
    def draw_component(x, y, w, h, bg, border, title, items, title_col=tx_dark, badge=""):
        box = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.12",
                                     facecolor=bg, edgecolor=border, linewidth=1.4)
        ax.add_patch(box)
        
        # Title
        ax.text(x + w/2, y + h - 0.22, title, fontsize=10.0, fontweight='bold', color=title_col,
                ha='center', va='top')
        
        # Optional Badge
        if badge:
            bx = x + w - 0.15
            by = y + h - 0.15
            ax.text(bx, by, badge, fontsize=7.5, fontweight='bold', color='#FFFFFF',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor=title_col, edgecolor='none'),
                    ha='right', va='top')
            
        # Items / Description
        if items:
            item_text = "\n".join([f"•  {it}" for it in items])
            ax.text(x + 0.2, y + 0.18, item_text, fontsize=8.2, color=tx_body,
                    ha='left', va='bottom', linespacing=1.4)

    # -------------------------------------------------------------
    # 1. CONTAINERS (ZONING)
    # -------------------------------------------------------------
    # Ingress Gateway Container
    draw_container(2.7, 0.4, 6.0, 7.0, c_group_ingress, '#CBD5E1',
                   "NEURALSHIELD INGRESS SECURITY GATEWAY (Pre-LLM Inspection)", '#1E40AF')
    
    # -------------------------------------------------------------
    # 2. COMPONENTS
    # -------------------------------------------------------------
    # [A] Untrusted Input Channel
    draw_component(0.3, 3.1, 2.0, 2.4, c_input_bg, border_slate,
                   "Untrusted Input\nChannel",
                   ["User Chat Prompts", "RAG Documents", "Web / Tool Payloads", "Adversarial Prompts"],
                   title_col=tx_dark)

    # [B] Layer 0: Structural Normalizer
    draw_component(3.0, 2.6, 2.3, 3.3, c_l0_bg, border_blue,
                   "Layer 0 (L0)\nStructural Normalizer",
                   ["Unicode NFKC Normalize", "Zero-Width & Tag Strip", "Recursive Base64/Hex/ROT",
                    "Cyrillic Homoglyph Fold", "Stego Signature Flagging", "Generates Extended Text"],
                   title_col=border_blue, badge="Fast L0")

    # [C] Layer 1: Deterministic Engine
    draw_component(5.8, 5.0, 2.6, 2.0, c_l1_bg, border_amber,
                   "Layer 1 (L1): Fast Regex",
                   ["Compiled Signature Rules", "Persona / DAN Traps", "Canary Exfiltration Detect", "<1.0 ms Heuristic Gate"],
                   title_col=border_amber, badge="< 1 ms")

    # [D] Layer 2: Semantic Transformer Classifier
    draw_component(5.8, 2.7, 2.6, 2.0, c_l2_bg, border_purple,
                   "Layer 2 (L2): mmBERT Classifier",
                   ["307M mmBERT-base ONNX", "12-Language Multilingual", "Calibrated P_malicious (0-100)", "Threshold tau >= 0.70"],
                   title_col=border_purple, badge="CPU ~50ms")

    # [E] Deterministic OR-Gate Arbiter
    draw_component(5.8, 0.6, 2.6, 1.8, c_gate_bg, border_red,
                   "Adaptive OR-Gate Arbiter",
                   ["D_in = 1  if: (Stego OR S_reg>=60", "OR P_ml>=70 OR (Regex & ML>=50))", "Strict Asymmetric Policy", "Zero False Dismissals"],
                   title_col=border_red, badge="Arbiter")

    # [F] Safe Refusal Gateway (Threat Detected)
    draw_component(9.3, 5.4, 2.3, 1.8, c_refusal_bg, border_red,
                   "Safe Refusal Gateway\n(Threat Abort)",
                   ["HTTP 403 Forbidden", "Sanitized Security Warning", "Zero LLM GPU Compute", "Security Event Logged"],
                   title_col=border_red, badge="BLOCK")

    # [G] Target LLM Execution Engine
    draw_component(9.3, 0.8, 2.3, 2.4, c_llm_bg, border_dark,
                   "Target LLM Engine\n(Context Isolated)",
                   ["Enterprise / Edge LLM", "Greedy / Sampled Inference", "Private System Canary",
                    "Dual Generation Streams:", " - Final Content Stream", " - Internal CoT Reasoning"],
                   title_col=tx_dark, badge="LLM RUN")

    # [H] Layer 3: Egress DLP Sanitizer
    draw_component(9.3, 3.4, 2.3, 1.8, c_l3_bg, border_green,
                   "Layer 3 (L3): Egress DLP\nDual-Stream Sanitizer",
                   ["Real-Time Canary Masker", "Secret Registry [REDACTED]", "Dual-Stream SSE Scrubbing", "Suppresses Silent CoT Leak"],
                   title_col=border_green, badge="POST-DLP")

    # [I] Sanitized Output to User
    draw_component(12.2, 3.4, 1.9, 1.8, c_out_bg, border_green,
                   "Sanitized Delivery\nto Client / System",
                   ["Confidentiality Preserved", "Canaries Fully Redacted", "Safe User Response", "Verified Safe Egress"],
                   title_col=border_green, badge="CLEAN")

    # -------------------------------------------------------------
    # 3. ROUTED ARROWS (NO OVERLAPS, STRICT CLEAN PATHS)
    # -------------------------------------------------------------
    arrow_gray = dict(arrowstyle="-|>", lw=1.6, color="#475569", mutation_scale=12)
    arrow_red = dict(arrowstyle="-|>", lw=2.0, color="#DC2626", mutation_scale=14)
    arrow_green = dict(arrowstyle="-|>", lw=2.0, color="#059669", mutation_scale=14)

    # 1. Input -> L0
    ax.annotate("", xy=(3.0, 4.25), xytext=(2.3, 4.25), arrowprops=arrow_gray)
    ax.text(2.65, 4.45, "Raw Ingress\nPayload", fontsize=7.8, color=tx_sub, ha='center', fontweight='semibold')

    # 2. L0 -> L1 (Top branch inside Ingress)
    ax.annotate("", xy=(5.8, 6.0), xytext=(5.3, 5.0),
                arrowprops=dict(arrowstyle="-|>", lw=1.5, color=border_blue, mutation_scale=12,
                                connectionstyle="angle,angleA=0,angleB=90,rad=4"))
    ax.text(5.52, 5.75, "Text", fontsize=7.5, color=border_blue, ha='center', backgroundcolor='#FFFFFF')

    # 3. L0 -> L2 (Direct branch inside Ingress)
    ax.annotate("", xy=(5.8, 3.7), xytext=(5.3, 3.7), arrowprops=dict(arrowstyle="-|>", lw=1.5, color=border_blue, mutation_scale=12))
    ax.text(5.55, 3.9, "Normalized", fontsize=7.5, color=border_blue, ha='center', backgroundcolor='#FFFFFF')

    # 4. L1 -> Arbiter (Downwards)
    ax.annotate("", xy=(7.1, 2.4), xytext=(7.1, 5.0),
                arrowprops=dict(arrowstyle="-|>", lw=1.4, color=border_amber, mutation_scale=12, linestyle=':'))
    ax.text(7.1, 4.75, "Regex Score S_reg", fontsize=7.2, color=border_amber, ha='center',
            bbox=dict(boxstyle='square,pad=0.15', facecolor='#FFFFFF', edgecolor='#FCD34D', lw=0.8))

    # 5. L2 -> Arbiter (Downwards)
    ax.annotate("", xy=(6.5, 2.4), xytext=(6.5, 2.7),
                arrowprops=dict(arrowstyle="-|>", lw=1.4, color=border_purple, mutation_scale=12))
    ax.text(6.5, 2.55, "P_malicious", fontsize=7.2, color=border_purple, ha='center', backgroundcolor='#FFFFFF')

    # 6. Arbiter Branch A: Threat Detected -> Safe Refusal (Red Path)
    # Routes out right of Arbiter, curves up to Safe Refusal
    ax.annotate("", xy=(9.3, 6.3), xytext=(8.4, 1.5),
                arrowprops=dict(arrowstyle="-|>", lw=2.0, color=border_red, mutation_scale=14,
                                connectionstyle="arc3,rad=-0.35"))
    ax.text(8.85, 4.3, "THREAT DETECTED\n(D_in = 1 : Abort)", fontsize=8.0, fontweight='bold', color=border_red,
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#FEF2F2', edgecolor='#FCA5A5', lw=1.0))

    # 7. Arbiter Branch B: Clean / Passed -> Target LLM (Green Path)
    ax.annotate("", xy=(9.3, 1.5), xytext=(8.4, 1.2),
                arrowprops=dict(arrowstyle="-|>", lw=2.0, color=border_green, mutation_scale=14))
    ax.text(8.85, 1.45, "CLEAN (Passed)\nD_in = 0", fontsize=7.8, fontweight='bold', color=border_green,
            ha='center', va='bottom',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='#F0FDF4', edgecolor='#86EFAC', lw=0.8))

    # 8. Target LLM -> Layer 3 DLP (Upwards flow from LLM to DLP Sanitizer)
    ax.annotate("", xy=(10.45, 3.4), xytext=(10.45, 3.2),
                arrowprops=dict(arrowstyle="-|>", lw=1.8, color="#0284C7", mutation_scale=12))
    ax.text(10.45, 3.3, "Raw Generation Streams (Content + CoT)", fontsize=7.2, color='#0369A1',
            ha='center', va='center', backgroundcolor='#FFFFFF', fontweight='semibold')

    # 9. Layer 3 DLP -> Sanitized Delivery (Out to client)
    ax.annotate("", xy=(12.2, 4.3), xytext=(11.6, 4.3), arrowprops=arrow_green)
    ax.text(11.9, 4.5, "Dual-Sanitized\nEgress Stream", fontsize=7.5, color=border_green, ha='center', fontweight='semibold')

    plt.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=bg_canvas)
    plt.close()
    print(f"Academic Figure 1 generated successfully: {output_path}")


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
