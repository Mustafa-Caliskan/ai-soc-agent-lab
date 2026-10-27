import fitz
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


import fitz
import os

def generate_svg_architecture():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 720" width="1600" height="720">
  <defs>
    <!-- Markers for arrows -->
    <marker id="arrow-slate" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#475569" />
    </marker>
    <marker id="arrow-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#2563EB" />
    </marker>
    <marker id="arrow-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#DC2626" />
    </marker>
    <marker id="arrow-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#16A34A" />
    </marker>
    
    <!-- Filter for soft professional shadow -->
    <filter id="card-shadow" x="-5%" y="-5%" width="110%" height="115%" filterUnits="userSpaceOnUse">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#0F172A" flood-opacity="0.05" />
    </filter>
  </defs>

  <style>
    .font-title { font-family: 'Segoe UI', Arial, sans-serif; font-size: 14px; font-weight: 700; fill: #0F172A; }
    .font-subtitle { font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; font-weight: 600; }
    .font-badge { font-family: 'Segoe UI', Arial, sans-serif; font-size: 10px; font-weight: 600; fill: #64748B; }
    .font-bullet { font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; fill: #334155; }
    .font-tag { font-family: 'Segoe UI', Arial, sans-serif; font-size: 10px; font-weight: 700; }
    .font-pill { font-family: 'Segoe UI', Arial, sans-serif; font-size: 10.5px; font-weight: 600; fill: #334155; }
    .font-subgraph { font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; font-weight: 700; letter-spacing: 0.5px; }
  </style>

  <!-- Canvas Background -->
  <rect width="100%" height="100%" fill="#FFFFFF" />

  <!-- ===================================================================== -->
  <!-- 1. SUBGRAPH CONTAINERS (INGRESS & EGRESS)                             -->
  <!-- ===================================================================== -->
  <!-- Ingress Container -->
  <rect x="260" y="45" width="655" height="630" rx="16" fill="#F8FAFC" stroke="#94A3B8" stroke-width="1.5" stroke-dasharray="6,4" />
  <rect x="280" y="32" width="410" height="24" rx="6" fill="#EFF6FF" stroke="#3B82F6" stroke-width="1" />
  <text x="290" y="48" class="font-subgraph" fill="#1D4ED8">INGRESS SECURITY GATEWAY (Pre-LLM Inspection Pipeline)</text>

  <!-- Egress Container -->
  <rect x="1195" y="315" width="375" height="345" rx="16" fill="#F0FDF4" stroke="#86EFAC" stroke-width="1.5" stroke-dasharray="6,4" />
  <rect x="1215" y="302" width="280" height="24" rx="6" fill="#DCFCE7" stroke="#16A34A" stroke-width="1" />
  <text x="1225" y="318" class="font-subgraph" fill="#15803D">EGRESS DLP GATEWAY (Output Sanitization)</text>

  <!-- ===================================================================== -->
  <!-- 2. CONNECTING ARROWS (ORTHOGONAL / STEP, DRAWN FIRST BEHIND PILLS)   -->
  <!-- ===================================================================== -->
  <!-- (1) Input -> L0 -->
  <path d="M 225 350 L 285 350" fill="none" stroke="#475569" stroke-width="2" marker-end="url(#arrow-slate)" />

  <!-- (2) L0 -> L1 (Step Up) -->
  <path d="M 495 240 L 518 240 L 518 190 L 538 190" fill="none" stroke="#2563EB" stroke-width="1.8" marker-end="url(#arrow-blue)" />

  <!-- (3) L0 -> L2 (Step Down) -->
  <path d="M 495 470 L 518 470 L 518 500 L 538 500" fill="none" stroke="#2563EB" stroke-width="1.8" marker-end="url(#arrow-blue)" />

  <!-- (4) L1 -> Arbiter (Step Down) -->
  <path d="M 755 190 L 780 190 L 780 310 L 800 310" fill="none" stroke="#475569" stroke-width="1.8" marker-end="url(#arrow-slate)" />

  <!-- (5) L2 -> Arbiter (Step Up) -->
  <path d="M 755 500 L 780 500 L 780 400 L 800 400" fill="none" stroke="#475569" stroke-width="1.8" marker-end="url(#arrow-slate)" />

  <!-- (6) Arbiter -> Safe Refusal (Branch 1: Threat Detected / Red Path) -->
  <path d="M 890 310 L 925 310 L 925 200 L 955 200" fill="none" stroke="#DC2626" stroke-width="2.2" marker-end="url(#arrow-red)" />

  <!-- (7) Arbiter -> Target LLM (Branch 2: Clean / Green Path) -->
  <path d="M 890 400 L 925 400 L 925 500 L 955 500" fill="none" stroke="#16A34A" stroke-width="2.2" marker-end="url(#arrow-green)" />

  <!-- (8) Target LLM -> Layer 3 Egress DLP (Straight) -->
  <path d="M 1150 500 L 1215 500" fill="none" stroke="#475569" stroke-width="2" marker-end="url(#arrow-slate)" />

  <!-- (9) Layer 3 DLP -> Sanitized Delivery (Straight) -->
  <path d="M 1395 500 L 1420 500" fill="none" stroke="#16A34A" stroke-width="2" marker-end="url(#arrow-green)" />

  <!-- ===================================================================== -->
  <!-- 3. ARROW PILL LABELS (WITH WHITE BACKGROUND, NO OVERLAPS)             -->
  <!-- ===================================================================== -->
  <!-- Pill: Input to L0 -->
  <rect x="230" y="338" width="50" height="22" rx="4" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1" />
  <text x="255" y="353" class="font-pill" text-anchor="middle">Payload</text>

  <!-- Pill: S_reg -->
  <rect x="760" y="240" width="40" height="20" rx="4" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1" />
  <text x="780" y="254" class="font-pill" fill="#D97706" text-anchor="middle">S_reg</text>

  <!-- Pill: P_malicious -->
  <rect x="760" y="445" width="40" height="20" rx="4" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1" />
  <text x="780" y="459" class="font-pill" fill="#7C3AED" text-anchor="middle">P_ml</text>

  <!-- Pill: Threat Detected -->
  <rect x="888" y="240" width="74" height="26" rx="5" fill="#FEF2F2" stroke="#F87171" stroke-width="1" />
  <text x="925" y="256" class="font-tag" fill="#DC2626" text-anchor="middle">D_in = 1 (Threat)</text>

  <!-- Pill: Clean Passed -->
  <rect x="888" y="445" width="74" height="26" rx="5" fill="#F0FDF4" stroke="#4ADE80" stroke-width="1" />
  <text x="925" y="461" class="font-tag" fill="#16A34A" text-anchor="middle">D_in = 0 (Clean)</text>

  <!-- Pill: Raw Streams -->
  <rect x="1153" y="488" width="58" height="22" rx="4" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1" />
  <text x="1182" y="503" class="font-pill" text-anchor="middle">Streams</text>

  <!-- ===================================================================== -->
  <!-- 4. NODE CARDS (CLEAN MERMAID CARDS WITH EXACT COORDINATES)           -->
  <!-- ===================================================================== -->

  <!-- CARD 1: Untrusted Input Channel -->
  <g filter="url(#card-shadow)">
    <rect x="35" y="210" width="190" height="280" rx="8" fill="#FFFFFF" stroke="#64748B" stroke-width="1.5" />
    <rect x="35" y="210" width="190" height="36" rx="8" fill="#F1F5F9" />
    <path d="M 35 246 L 225 246" stroke="#E2E8F0" stroke-width="1" />
    <text x="130" y="233" class="font-title" text-anchor="middle">Untrusted Input</text>
    <text x="130" y="263" class="font-subtitle" fill="#475569" text-anchor="middle">[Ingress Channel]</text>
    
    <text x="50" y="300" class="font-bullet">• User Chat Prompts</text>
    <text x="50" y="330" class="font-bullet">• RAG Knowledge Passages</text>
    <text x="50" y="360" class="font-bullet">• Web / Tool Payloads</text>
    <text x="50" y="390" class="font-bullet">• Adversarial Injections</text>
    <text x="50" y="420" class="font-bullet">• Multi-turn Dialogues</text>
    <text x="50" y="450" class="font-bullet">• Untrusted Files / PDFs</text>
  </g>

  <!-- CARD 2: Layer 0 (L0) Structural Normalizer -->
  <g filter="url(#card-shadow)">
    <rect x="285" y="140" width="210" height="420" rx="8" fill="#FFFFFF" stroke="#2563EB" stroke-width="2" />
    <rect x="285" y="140" width="210" height="42" rx="8" fill="#EFF6FF" />
    <path d="M 285 182 L 495 182" stroke="#DBEAFE" stroke-width="1" />
    <text x="390" y="165" class="font-title" fill="#1D4ED8" text-anchor="middle">Layer 0 (L0)</text>
    <text x="390" y="202" class="font-subtitle" fill="#2563EB" text-anchor="middle">Structural Normalizer</text>
    <text x="390" y="222" class="font-badge" text-anchor="middle">Fast Pre-Filter (&lt;1 ms)</text>
    
    <text x="300" y="260" class="font-bullet">• Unicode NFKC Normalize</text>
    <text x="300" y="295" class="font-bullet">• Zero-Width &amp; Tag Strip</text>
    <text x="300" y="330" class="font-bullet">• Recursive Base64 Decode</text>
    <text x="300" y="365" class="font-bullet">• Hex / ROT13 Deobfuscate</text>
    <text x="300" y="400" class="font-bullet">• Cyrillic Homoglyph Fold</text>
    <text x="300" y="435" class="font-bullet">• Stego Signature Detection</text>
    <text x="300" y="470" class="font-bullet">• Extended Payload Emission</text>
    <text x="300" y="505" class="font-bullet">• Control Char Scrubbing</text>
    <text x="300" y="535" class="font-bullet">• Structural Delimiter Guard</text>
  </g>

  <!-- CARD 3: Layer 1 (L1) Deterministic Engine -->
  <g filter="url(#card-shadow)">
    <rect x="540" y="90" width="215" height="200" rx="8" fill="#FFFFFF" stroke="#D97706" stroke-width="1.8" />
    <rect x="540" y="90" width="215" height="38" rx="8" fill="#FEF3C7" />
    <path d="M 540 128 L 755 128" stroke="#FDE68A" stroke-width="1" />
    <text x="647" y="114" class="font-title" fill="#B45309" text-anchor="middle">Layer 1 (L1): Fast Regex</text>
    <text x="647" y="146" class="font-badge" fill="#92400E" text-anchor="middle">Compiled Rule Automata (&lt;1 ms)</text>
    
    <text x="555" y="175" class="font-bullet">• Multilingual Attack Regex</text>
    <text x="555" y="202" class="font-bullet">• Persona Hijack / DAN Traps</text>
    <text x="555" y="229" class="font-bullet">• Canary Exfiltration Traps</text>
    <text x="555" y="256" class="font-bullet">• Fast-Path Rejection Trigger</text>
  </g>

  <!-- CARD 4: Layer 2 (L2) Semantic Classifier -->
  <g filter="url(#card-shadow)">
    <rect x="540" y="380" width="215" height="240" rx="8" fill="#FFFFFF" stroke="#7C3AED" stroke-width="1.8" />
    <rect x="540" y="380" width="215" height="38" rx="8" fill="#EDE9FE" />
    <path d="M 540 418 L 755 418" stroke="#DDD6FE" stroke-width="1" />
    <text x="647" y="404" class="font-title" fill="#6D28D9" text-anchor="middle">Layer 2 (L2): mmBERT</text>
    <text x="647" y="436" class="font-badge" fill="#5B21B6" text-anchor="middle">Semantic Classifier (~50 ms CPU)</text>
    
    <text x="555" y="468" class="font-bullet">• 307M mmBERT-base ONNX</text>
    <text x="555" y="498" class="font-bullet">• 12 Typological Languages</text>
    <text x="555" y="528" class="font-bullet">• Calibrated P_malicious (0-100)</text>
    <text x="555" y="558" class="font-bullet">• Decision Threshold: τ ≥ 0.70</text>
    <text x="555" y="588" class="font-bullet">• Cross-lingual Generalization</text>
  </g>

  <!-- CARD 5: Adaptive OR-Gate Arbiter -->
  <g filter="url(#card-shadow)">
    <rect x="800" y="250" width="90" height="210" rx="8" fill="#FEF2F2" stroke="#DC2626" stroke-width="2" />
    <text x="845" y="280" class="font-title" fill="#991B1B" text-anchor="middle">OR-Gate</text>
    <text x="845" y="300" class="font-title" fill="#991B1B" text-anchor="middle">Arbiter</text>
    
    <line x1="810" y1="315" x2="880" y2="315" stroke="#FCA5A5" stroke-width="1" />
    
    <text x="845" y="338" class="font-subtitle" fill="#7F1D1D" text-anchor="middle">Policy Logic:</text>
    <text x="845" y="362" font-family="'Segoe UI', sans-serif" font-size="9px" fill="#991B1B" text-anchor="middle">Stego == 1</text>
    <text x="845" y="380" font-family="'Segoe UI', sans-serif" font-size="9px" fill="#991B1B" text-anchor="middle">∨ S_reg ≥ 60</text>
    <text x="845" y="398" font-family="'Segoe UI', sans-serif" font-size="9px" fill="#991B1B" text-anchor="middle">∨ P_ml ≥ 70</text>
    <text x="845" y="416" font-family="'Segoe UI', sans-serif" font-size="8.5px" fill="#991B1B" text-anchor="middle">∨ (Reg ∧ ML)</text>
    
    <rect x="812" y="432" width="66" height="18" rx="4" fill="#DC2626" />
    <text x="845" y="445" font-family="'Segoe UI', sans-serif" font-size="9px" font-weight="700" fill="#FFFFFF" text-anchor="middle">DECISION</text>
  </g>

  <!-- CARD 6: Safe Refusal Gateway (Threat Detected) -->
  <g filter="url(#card-shadow)">
    <rect x="955" y="90" width="195" height="200" rx="8" fill="#FEF2F2" stroke="#DC2626" stroke-width="2" />
    <rect x="955" y="90" width="195" height="38" rx="8" fill="#FEE2E2" />
    <path d="M 955 128 L 1150 128" stroke="#FECACA" stroke-width="1" />
    <text x="1052" y="114" class="font-title" fill="#991B1B" text-anchor="middle">Safe Refusal Gateway</text>
    <text x="1052" y="146" class="font-badge" fill="#B91C1C" text-anchor="middle">Immediate Abort (Threat)</text>
    
    <text x="970" y="175" class="font-bullet">• HTTP 403 Forbidden</text>
    <text x="970" y="202" class="font-bullet">• Neutral Security Advisory</text>
    <text x="970" y="229" class="font-bullet">• Zero Target LLM Compute</text>
    <text x="970" y="256" class="font-bullet">• SIEM Incident Logging</text>
  </g>

  <!-- CARD 7: Target LLM Execution Engine -->
  <g filter="url(#card-shadow)">
    <rect x="955" y="380" width="195" height="240" rx="8" fill="#FFFFFF" stroke="#334155" stroke-width="1.8" />
    <rect x="955" y="380" width="195" height="38" rx="8" fill="#F1F5F9" />
    <path d="M 955 418 L 1150 418" stroke="#E2E8F0" stroke-width="1" />
    <text x="1052" y="404" class="font-title" fill="#0F172A" text-anchor="middle">Target LLM Engine</text>
    <text x="1052" y="436" class="font-badge" fill="#475569" text-anchor="middle">Context-Isolated Runtime</text>
    
    <text x="970" y="468" class="font-bullet">• Enterprise / Edge LLM</text>
    <text x="970" y="498" class="font-bullet">• System Canary Injection</text>
    <text x="970" y="528" class="font-bullet">• Dual Generation Streams:</text>
    <text x="980" y="554" class="font-bullet" fill="#64748B">- User Content Stream</text>
    <text x="980" y="578" class="font-bullet" fill="#64748B">- Internal CoT Reasoning</text>
  </g>

  <!-- CARD 8: Layer 3 (L3) Egress DLP Sanitizer -->
  <g filter="url(#card-shadow)">
    <rect x="1215" y="375" width="180" height="250" rx="8" fill="#FFFFFF" stroke="#16A34A" stroke-width="2" />
    <rect x="1215" y="375" width="180" height="38" rx="8" fill="#DCFCE7" />
    <path d="M 1215 413 L 1395 413" stroke="#BBF7D0" stroke-width="1" />
    <text x="1305" y="399" class="font-title" fill="#15803D" text-anchor="middle">Layer 3 (L3): DLP</text>
    <text x="1305" y="431" class="font-badge" fill="#166534" text-anchor="middle">Dual-Stream Sanitizer</text>
    
    <text x="1227" y="462" class="font-bullet">• Real-Time Canary Masker</text>
    <text x="1227" y="492" class="font-bullet">• Secret Credential Registry</text>
    <text x="1227" y="522" class="font-bullet">• Luhn / PII Checksum DLP</text>
    <text x="1227" y="552" class="font-bullet">• Dual-Stream SSE Scrub</text>
    <text x="1227" y="582" class="font-bullet">• Suppresses Silent CoT</text>
    <text x="1227" y="608" class="font-bullet">• [REDACTED_SECRET]</text>
  </g>

  <!-- CARD 9: Sanitized Delivery Output -->
  <g filter="url(#card-shadow)">
    <rect x="1420" y="375" width="140" height="250" rx="8" fill="#F0FDF4" stroke="#16A34A" stroke-width="1.6" />
    <rect x="1420" y="375" width="140" height="38" rx="8" fill="#DCFCE7" />
    <path d="M 1420 413 L 1560 413" stroke="#BBF7D0" stroke-width="1" />
    <text x="1490" y="399" class="font-title" fill="#15803D" text-anchor="middle">Delivery</text>
    <text x="1490" y="431" class="font-badge" fill="#166534" text-anchor="middle">[Client / User]</text>
    
    <text x="1432" y="465" class="font-bullet">• Confidentiality</text>
    <text x="1432" y="500" class="font-bullet">• Zero Leakage</text>
    <text x="1432" y="535" class="font-bullet">• Safe Response</text>
    <text x="1432" y="570" class="font-bullet">• Verified Egress</text>
    <text x="1432" y="605" class="font-bullet">• Clean Delivery</text>
  </g>

</svg>'''
    return svg

def generate_figure1():
    output_path = "docs/figures/figure1_architecture.png"
    svg_data = generate_svg_architecture()
    doc = fitz.open(stream=svg_data.encode('utf-8'), filetype='svg')
    page = doc[0]
    # DPI 300 for crisp publication quality
    pix = page.get_pixmap(dpi=300)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pix.save(output_path)
    doc.close()
    print(f"Successfully rendered SVG to {output_path} ({pix.width}x{pix.height})")


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
