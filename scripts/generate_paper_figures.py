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
    # High-resolution publication styling
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Segoe UI', 'Helvetica']
    
    # 16:9 ratio, broad width for horizontal pipeline
    fig, ax = plt.subplots(figsize=(15.5, 6.8), dpi=300)
    ax.set_xlim(0, 15.5)
    ax.set_ylim(0, 6.8)
    ax.axis('off')

    # Color Palette: Minimalist Mermaid-style (Corporate Slate / Clean Monochrome + Soft Branch Accents)
    bg_canvas = '#FFFFFF'
    
    # Node Backgrounds
    node_bg_default = '#F8FAFC'  # Very soft slate
    node_bg_highlight = '#F1F5F9'
    node_bg_block = '#FEF2F2'    # Soft muted red
    node_bg_clean = '#F0FDF4'    # Soft muted green
    
    # Borders (Mermaid standard: subtle 1-1.5px lines)
    border_default = '#64748B'   # Neutral slate
    border_container = '#94A3B8' # Dashed container border
    border_block = '#DC2626'     # Muted crimson
    border_clean = '#16A34A'     # Muted forest green
    border_accent = '#2563EB'    # Subtle tech blue
    
    # Typography colors
    text_title = '#0F172A'       # Slate 900
    text_desc = '#334155'        # Slate 700
    text_meta = '#64748B'        # Slate 500

    # Helper: Draw Container Subgraph (Mermaid subgraph box)
    def draw_subgraph(x, y, w, h, label, bg='#F8FAFC', border='#CBD5E1'):
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.15",
                                      facecolor=bg, edgecolor=border, linewidth=1.2, linestyle='--')
        ax.add_patch(rect)
        # Subgraph title tag at top-left
        ax.text(x + 0.25, y + h - 0.25, label, fontsize=9.0, fontweight='bold', color='#475569',
                ha='left', va='top')

    # Helper: Draw Mermaid Node
    def draw_node(x, y, w, h, title, items=None, subtitle=None, bg=node_bg_default, border=border_default, title_col=text_title):
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.1",
                                      facecolor=bg, edgecolor=border, linewidth=1.4)
        ax.add_patch(rect)
        
        # Center title
        title_y = y + h - 0.25 if (items or subtitle) else y + h/2
        va_mode = 'top' if (items or subtitle) else 'center'
        ax.text(x + w/2, title_y, title, fontsize=9.5, fontweight='bold', color=title_col,
                ha='center', va=va_mode)
        
        # Subtitle (optional badge/latency)
        curr_y = title_y - 0.28
        if subtitle:
            ax.text(x + w/2, curr_y, subtitle, fontsize=7.8, fontweight='semibold', color=text_meta,
                    ha='center', va='top')
            curr_y -= 0.25
            
        # Items / bullets
        if items:
            item_text = "\n".join([f"• {it}" for it in items])
            ax.text(x + 0.18, y + 0.15, item_text, fontsize=7.8, color=text_desc,
                    ha='left', va='bottom', linespacing=1.35)

    # -------------------------------------------------------------
    # 1. MERMAID SUBGRAPHS (INGRESS & EGRESS)
    # -------------------------------------------------------------
    # Ingress Subgraph
    draw_subgraph(2.35, 0.4, 6.3, 6.0, "subgraph Ingress_Security_Gateway [NeuralShield Ingress Pipeline]")

    # Egress Subgraph
    draw_subgraph(11.1, 0.4, 4.15, 3.4, "subgraph Egress_Security_Gateway [NeuralShield Egress DLP]")

    # -------------------------------------------------------------
    # 2. NODES (7 STRICT COLUMNS, NO OVERLAPS)
    # -------------------------------------------------------------
    # Col 1: Untrusted Input Channel (x = 0.3)
    draw_node(0.3, 2.3, 1.7, 2.3,
              "Untrusted Input\nChannel",
              items=["User Chat Prompts", "RAG Documents", "Tool / Web Payloads", "Adversarial Inputs"],
              subtitle="[Ingress Source]")

    # Col 2: Layer 0: Structural Normalizer (x = 2.6)
    draw_node(2.6, 2.0, 1.9, 2.9,
              "Layer 0 (L0)\nStructural Normalizer",
              items=["Unicode NFKC Normalize", "Zero-Width / Tag Stripping", "Recursive Base64/Hex/ROT",
                     "Cyrillic Homoglyph Fold", "Stego Signature Flagging", "Extended Payload Gen."],
              subtitle="[Fast Pre-Filter]",
              border=border_accent)

    # Col 3: Parallel Detection Engines (x = 4.85)
    # Top: Layer 1 Regex
    draw_node(4.85, 3.75, 2.1, 2.2,
              "Layer 1 (L1)\nDeterministic Regex",
              items=["Signature Rule Automata", "Jailbreak / DAN Traps", "Canary Leakage Detection", "Fast-Path Execution"],
              subtitle="[Heuristic: < 1.0 ms]")

    # Bottom: Layer 2 mmBERT Classifier
    draw_node(4.85, 0.85, 2.1, 2.5,
              "Layer 2 (L2)\nmmBERT Classifier",
              items=["307M mmBERT ONNX", "12-Language Multilingual", "Calibrated P_malicious (0-100)", "Reject Threshold tau >= 0.70"],
              subtitle="[Semantic: CPU ~50 ms]",
              border=border_accent)

    # Col 4: Adaptive OR-Gate Arbiter (x = 7.3)
    draw_node(7.3, 2.0, 1.15, 2.8,
              "Adaptive\nOR-Gate\nArbiter",
              subtitle="[Decision]",
              items=["Stego == 1\nv S_reg >= 60\nv P_ml >= 70\nv (Regex & ML)"],
              bg='#FEF2F2', border=border_block, title_col=border_block)

    # Col 5: Branches (x = 9.0)
    # Top Branch: Safe Refusal (Blocked)
    draw_node(9.0, 4.3, 1.8, 1.9,
              "Safe Refusal\nGateway",
              items=["HTTP 403 Forbidden", "Sanitized Alert Msg", "Zero LLM Compute", "Event Logged"],
              subtitle="[THREAT DETECTED]",
              bg=node_bg_block, border=border_block, title_col=border_block)

    # Bottom Branch: Target LLM Engine (Clean / Passed)
    draw_node(9.0, 0.9, 1.8, 2.3,
              "Target LLM\nExecution Engine",
              items=["Enterprise / Edge LLM", "Isolated Context Runtime", "Private Canary Secrets",
                     "Streams Emitted:", " - User Content Stream", " - Internal CoT Reasoning"],
              subtitle="[CLEAN / PASSED]",
              bg=node_bg_default, border=border_default)

    # Col 6: Layer 3: Egress DLP Sanitizer (x = 11.35)
    draw_node(11.35, 0.9, 2.0, 2.3,
              "Layer 3 (L3)\nEgress DLP Sanitizer",
              items=["Real-Time Canary Masker", "Secret Registry Check", "Dual-Stream Scrubbing", "Suppresses Silent CoT", "Pre-Client Token Filter"],
              subtitle="[Egress Protection]",
              bg=node_bg_clean, border=border_clean, title_col=border_clean)

    # Col 7: Sanitized Delivery Output (x = 13.65)
    draw_node(13.65, 0.9, 1.45, 2.3,
              "Sanitized\nDelivery",
              items=["Confidentiality", "Zero Leakage", "Clean Response", "Client Safe"],
              subtitle="[End User / App]",
              bg=node_bg_clean, border=border_clean, title_col=border_clean)

    # -------------------------------------------------------------
    # 3. MERMAID CONNECTORS (CLEAN ORTHOGONAL & HORIZONTAL ARROWS)
    # -------------------------------------------------------------
    arrow_std = dict(arrowstyle="-|>", lw=1.5, color="#475569", mutation_scale=12)
    arrow_red = dict(arrowstyle="-|>", lw=1.8, color=border_block, mutation_scale=13)
    arrow_green = dict(arrowstyle="-|>", lw=1.8, color=border_clean, mutation_scale=13)

    # (1) Input -> L0
    ax.annotate("", xy=(2.6, 3.45), xytext=(2.0, 3.45), arrowprops=arrow_std)

    # (2) L0 -> L1 (Step connector to top)
    ax.annotate("", xy=(4.85, 4.85), xytext=(4.5, 4.85), arrowprops=arrow_std)
    ax.plot([4.5, 4.5], [3.8, 4.85], color="#475569", lw=1.5)
    ax.plot([4.5, 4.85], [4.85, 4.85], color="#475569", lw=1.5)

    # (3) L0 -> L2 (Step connector to bottom)
    ax.annotate("", xy=(4.85, 2.1), xytext=(4.5, 2.1), arrowprops=arrow_std)
    ax.plot([4.5, 4.5], [3.1, 2.1], color="#475569", lw=1.5)
    ax.plot([4.5, 4.85], [2.1, 2.1], color="#475569", lw=1.5)

    # (4) L1 -> Arbiter (Step connector down to Arbiter)
    ax.annotate("", xy=(7.3, 3.8), xytext=(7.05, 3.8), arrowprops=arrow_std)
    ax.plot([6.95, 7.05], [4.85, 4.85], color="#475569", lw=1.5)
    ax.plot([7.05, 7.05], [4.85, 3.8], color="#475569", lw=1.5)
    ax.text(7.05, 4.4, "S_reg", fontsize=7.2, color='#475569', ha='center',
            bbox=dict(boxstyle='square,pad=0.15', facecolor='#FFFFFF', edgecolor='#CBD5E1', lw=0.6))

    # (5) L2 -> Arbiter (Step connector up to Arbiter)
    ax.annotate("", xy=(7.3, 2.8), xytext=(7.05, 2.8), arrowprops=arrow_std)
    ax.plot([6.95, 7.05], [2.1, 2.1], color="#475569", lw=1.5)
    ax.plot([7.05, 7.05], [2.1, 2.8], color="#475569", lw=1.5)
    ax.text(7.05, 2.35, "P_ml", fontsize=7.2, color='#475569', ha='center',
            bbox=dict(boxstyle='square,pad=0.15', facecolor='#FFFFFF', edgecolor='#CBD5E1', lw=0.6))

    # (6) Arbiter -> Safe Refusal (Branch 1: Threat Detected / Red Path)
    # Right-angle elbow connector: Up from Arbiter, then Right to Safe Refusal
    ax.annotate("", xy=(9.0, 5.25), xytext=(8.7, 5.25), arrowprops=arrow_red)
    ax.plot([8.45, 8.7], [3.8, 3.8], color=border_block, lw=1.8)
    ax.plot([8.7, 8.7], [3.8, 5.25], color=border_block, lw=1.8)
    ax.plot([8.7, 9.0], [5.25, 5.25], color=border_block, lw=1.8)
    ax.text(8.7, 4.5, "D_in = 1\n(Threat)", fontsize=7.2, fontweight='bold', color=border_block, ha='center',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='#FEF2F2', edgecolor='#FCA5A5', lw=0.8))

    # (7) Arbiter -> Target LLM (Branch 2: Clean / Passed / Green Path)
    # Right-angle elbow connector: Down from Arbiter, then Right to Target LLM
    ax.annotate("", xy=(9.0, 2.05), xytext=(8.7, 2.05), arrowprops=arrow_green)
    ax.plot([8.45, 8.7], [2.8, 2.8], color=border_clean, lw=1.8)
    ax.plot([8.7, 8.7], [2.8, 2.05], color=border_clean, lw=1.8)
    ax.plot([8.7, 9.0], [2.05, 2.05], color=border_clean, lw=1.8)
    ax.text(8.7, 2.45, "D_in = 0\n(Clean)", fontsize=7.2, fontweight='bold', color=border_clean, ha='center',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='#F0FDF4', edgecolor='#86EFAC', lw=0.8))

    # (8) Target LLM -> Layer 3 Egress DLP (Straight horizontal arrow)
    ax.annotate("", xy=(11.35, 2.05), xytext=(10.8, 2.05), arrowprops=arrow_std)
    ax.text(11.08, 2.25, "Raw Streams\n(Content + CoT)", fontsize=6.8, color='#475569', ha='center',
            bbox=dict(boxstyle='square,pad=0.15', facecolor='#FFFFFF', edgecolor='#CBD5E1', lw=0.6))

    # (9) Layer 3 DLP -> Sanitized Delivery (Straight horizontal arrow)
    ax.annotate("", xy=(13.65, 2.05), xytext=(13.35, 2.05), arrowprops=arrow_green)
    ax.text(13.5, 2.25, "Clean\nTokens", fontsize=6.8, color=border_clean, ha='center',
            bbox=dict(boxstyle='square,pad=0.15', facecolor='#FFFFFF', edgecolor='#86EFAC', lw=0.6))

    plt.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=bg_canvas)
    plt.close()
    print(f"Mermaid-style Figure 1 generated successfully: {output_path}")


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
