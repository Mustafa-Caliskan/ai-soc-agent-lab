"""
Builds data/paper_metrics_manifest.json — the provenance spine of the manuscript.

Every statistic reported in Tables 1-10 and in the prose is recorded here with
either
  * a direct source  (file + JSON path), or
  * a derivation     (k/n for proportions, tp/fp/fn for F1, b/c for McNemar),
which scripts/verify_paper_metrics.py recomputes independently.

`renders` lists the exact strings that must appear in docs/CI_MANUSCRIPT_EN.md;
this is what catches prose drifting away from the tables.

status:
  measured          - sourced, recomputable, must match
  pilot-observation - archived outputs unavailable (softened in the text)
  declared          - a design constant (dataset size, model count), presence-checked
"""

import io
import json
import math
import os


def load(path):
    with io.open(path, encoding="utf-8") as handle:
        return json.load(handle)


def wilson(k, n, z=1.96):
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return round((centre - half) * 100, 2), round((centre + half) * 100, 2)


def f1_binary(tp, fn, fp):
    return 2 * tp / (2 * tp + fp + fn)


def f1_macro(tp, fn, fp, tn):
    f_mal = 2 * tp / (2 * tp + fp + fn)
    f_ben = 2 * tn / (2 * tn + fp + fn)
    return (f_mal + f_ben) / 2, f_mal, f_ben


def mcnemar_exact(b, c):
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(min(b, c) + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def main():
    entries = []

    def add(mid, value, unit, where, definition, renders, source=None,
            derive=None, status="measured", source_scale=1.0, tol=None):
        entries.append({
            "id": mid,
            "value": value,
            "unit": unit,
            "where": where,
            "definition": definition,
            "renders": renders,
            "source": source,
            "source_scale": source_scale,
            "derive": derive,
            "status": status,
            "tol": tol,
        })

    # ── Table 1: source-disjoint fair benchmark, archived metrics ───────────
    ci = load("data/validation_ci_v6.json")
    models = {
        "xlmr": ("XLM-RoBERTa-base", "XLM-R v6.2"),
        "bge": ("BGE-M3", "BGE-M3 v6.2"),
        "mmbert": ("NeuralShield (mmBERT)", "mmBERT v6.2"),
        "patronus": ("Patronus Wolf Defender", "Patronus"),
    }
    by_name = {row["Model"]: row for row in ci["overall"]}
    for key, (label, src_name) in models.items():
        row = by_name[src_name]
        idx = ci["overall"].index(row)
        base = f"data/validation_ci_v6.json#overall[{idx}]"
        add(f"t1.{key}.f1", round(row["F1@0.7"] * 100, 2), "%", "Table 1",
            "Macro-F1 at tau=0.70, cluster-bootstrap point estimate",
            [f"{row['F1@0.7'] * 100:.2f}", f"{row['F1_CI'][0]:.3f}", f"{row['F1_CI'][1]:.3f}"],
            source={"file": "data/validation_ci_v6.json", "path": f"overall[{idx}].F1@0.7"},
            source_scale=100)
        add(f"t1.{key}.auc", row["AUC"], "ratio", "Table 1",
            "ROC-AUC, cluster-bootstrap point estimate",
            [f"{row['AUC']:.4f}", f"{row['AUC_CI'][0]:.3f}", f"{row['AUC_CI'][1]:.3f}"],
            source={"file": "data/validation_ci_v6.json", "path": f"overall[{idx}].AUC"})
        add(f"t1.{key}.r1fp", round(row["Recall@FP=1%"] * 100, 2), "%", "Table 1",
            "Recall at 1% false-positive operating point",
            [f"{row['Recall@FP=1%']:.4f}"],
            source={"file": "data/validation_ci_v6.json", "path": f"overall[{idx}].Recall@FP=1%"},
            source_scale=100)

    l0 = load("data/l0_contribution_fair.json")
    add("t1.mmbert.recall_raw", l0["raw"]["recall"], "%", "Table 1, Table 3, Sections 1, 3.1, 3.4, 5",
        "Recall at tau=0.70 for the standalone L2 classifier on raw (non-normalised) text",
        [f"{l0['raw']['recall']:.2f}"],
        source={"file": "data/l0_contribution_fair.json", "path": "raw.recall"},
        derive={"statistic": "pct", "k": l0["raw"]["tp"], "n": 1440})
    add("t1.mmbert.fp_raw", l0["raw"]["fp"], "%", "Table 1",
        "False-positive rate for the standalone L2 classifier on raw text",
        [f"{l0['raw']['fp']:.2f}"],
        source={"file": "data/l0_contribution_fair.json", "path": "raw.fp"},
        derive={"statistic": "pct", "k": l0["raw"]["fp_n"], "n": 1409})
    w_rec = wilson(l0["raw"]["tp"], 1440)
    w_fp = wilson(l0["raw"]["fp_n"], 1409)
    add("t1.mmbert.recall_ci", w_rec, "%", "Table 1 footnote",
        "Wilson 95% interval for the same recall run",
        [f"[{w_rec[0]:.1f}, {w_rec[1]:.1f}]"],
        derive={"statistic": "wilson", "k": l0["raw"]["tp"], "n": 1440})
    add("t1.mmbert.fp_ci", w_fp, "%", "Table 1",
        "Wilson 95% interval for the same false-positive run",
        [],
        derive={"statistic": "wilson", "k": l0["raw"]["fp_n"], "n": 1409})

    e2e = load("data/e2e_layer_test_v6_2.json")
    add("t1.mmbert.bootstrap_f1", round(ci["overall"][0]["F1@0.7"] * 100, 2), "%",
        "Table 1 footnote", "Cluster-bootstrap point estimate of F1 (84.82)",
        ["84.82"], source={"file": "data/validation_ci_v6.json", "path": "overall[0].F1@0.7"},
        source_scale=100)
    add("t1.pipeline.recall", e2e["shield"]["recall"], "%", "Table 1 footnote, Sections 3.1, 3.4, 5",
        "Full pipeline (L0 + L2) recall on the fair benchmark",
        [f"{e2e['shield']['recall']:.2f}"],
        source={"file": "data/e2e_layer_test_v6_2.json", "path": "shield.recall"},
        derive={"statistic": "pct", "k": l0["ext"]["tp"], "n": 1440})
    add("t1.pipeline.f1", e2e["shield"]["macro_f1"], "%", "Table 1 footnote, Sections 3.4, 5",
        "Full pipeline Macro-F1 on the fair benchmark",
        [f"{e2e['shield']['macro_f1']:.2f}"],
        source={"file": "data/e2e_layer_test_v6_2.json", "path": "shield.macro_f1"})
    add("t1.mmbert.macro_f1_full", e2e["quantization_comparison"]["fp32"]["macro_f1"], "%",
        "Table 1", "Macro-F1 of the standalone FP32 classifier on raw text",
        [f"{e2e['quantization_comparison']['fp32']['macro_f1']:.2f}"],
        source={"file": "data/e2e_layer_test_v6_2.json", "path": "quantization_comparison.fp32.macro_f1"})
    add("t1.mmbert.auc_raw", e2e["quantization_comparison"]["fp32"]["auc"], "ratio", "Table 1",
        "ROC-AUC of the standalone FP32 classifier on raw text",
        [f"{e2e['quantization_comparison']['fp32']['auc']:.4f}"],
        source={"file": "data/e2e_layer_test_v6_2.json", "path": "quantization_comparison.fp32.auc"})

    # ── Table 2: native held-out corpora ────────────────────────────────────
    native = load("data/native_eval_v6.json")
    native_map = {(r["Model"], r["dil"]): r for r in native}
    for lang, n_items in (("tr", 1077), ("ru", 16636)):
        for key, label in (("v6.2", "shield"), ("Patronus", "patronus")):
            row = native_map[(key, lang)]
            idx = native.index(row)
            add(f"t2.{lang}.{label}.recall", row["recall@0.7"], "%", "Table 2",
                f"Recall at tau=0.70 on the native {lang} corpus",
                [f"{row['recall@0.7']:.2f}"],
                source={"file": "data/native_eval_v6.json", "path": f"[{idx}].recall@0.7"})
            add(f"t2.{lang}.{label}.fp", row["fp@0.7"], "%", "Table 2",
                f"False-positive rate at tau=0.70 on the native {lang} corpus",
                [f"{row['fp@0.7']:.2f}"],
                source={"file": "data/native_eval_v6.json", "path": f"[{idx}].fp@0.7"})
            add(f"t2.{lang}.{label}.auc", row["AUC"], "ratio", "Table 2",
                f"ROC-AUC on the native {lang} corpus (three decimals, source precision)",
                [f"{row['AUC']:.3f}"],
                source={"file": "data/native_eval_v6.json", "path": f"[{idx}].AUC"})

    # ── Table 3: latency, storage, quantisation ─────────────────────────────
    s2 = load("data/summary2.json")
    s1 = load("data/summary.json")
    add("t3.fp32.median", e2e["latency_fp32"]["median_ms"], "ms", "Table 3, Sections 1, 3.3, 5",
        "FP32 ONNX median latency, 2-vCPU container, 12 tokens",
        [f"{e2e['latency_fp32']['median_ms']:.2f}"],
        source={"file": "data/e2e_layer_test_v6_2.json", "path": "latency_fp32.median_ms"})
    add("t3.fp32.p95", e2e["latency_fp32"]["p95_ms"], "ms", "Table 3",
        "FP32 ONNX p95 latency, 2-vCPU container, 12 tokens",
        [f"{e2e['latency_fp32']['p95_ms']:.2f}"],
        source={"file": "data/e2e_layer_test_v6_2.json", "path": "latency_fp32.p95_ms"})
    add("t3.fp32.tokens", e2e["latency_fp32"]["tokens"], "tokens", "Table 3",
        "Input length used for the FP32 latency measurement", ["12"],
        source={"file": "data/e2e_layer_test_v6_2.json", "path": "latency_fp32.tokens"})
    add("t3.int8.median", s2["results"]["sdpa"]["median_ms"], "ms", "Table 3, Section 3.3",
        "INT8 dynamic PTQ median latency, 2-vCPU container, 23 tokens",
        [f"{s2['results']['sdpa']['median_ms']:.2f}"],
        source={"file": "data/summary2.json", "path": "results.sdpa.median_ms"})
    add("t3.int8.p95", s2["results"]["sdpa"]["p95_ms"], "ms", "Table 3",
        "INT8 dynamic PTQ p95 latency, 2-vCPU container, 23 tokens",
        [f"{s2['results']['sdpa']['p95_ms']:.2f}"],
        source={"file": "data/summary2.json", "path": "results.sdpa.p95_ms"})
    add("t3.int8.tokens", s2["results"]["sdpa"]["tokens"], "tokens", "Table 3",
        "Input length used for the INT8 latency measurement", ["23"],
        source={"file": "data/summary2.json", "path": "results.sdpa.tokens"})
    add("t3.storage.fp32", 1.17, "GB", "Table 3, Section 3.3",
        "FP32 ONNX artefact size in GB (1173.7 MB)", ["1.17"],
        source={"file": "data/summary.json", "path": "fp32_mb"}, source_scale=0.001, tol=0.01)
    add("t3.storage.int8", 294, "MB", "Table 3, Section 3.3",
        "INT8 ONNX artefact size in MB (294.2 MB)", ["294"],
        source={"file": "data/summary.json", "path": "int8_mb"}, tol=0.5)
    add("t3.int8.recall_raw", e2e["quantization_comparison"]["int8"]["recall"], "%", "Table 3, Section 3.3",
        "INT8 recall on raw text at tau=0.70",
        [f"{e2e['quantization_comparison']['int8']['recall']:.2f}"],
        source={"file": "data/e2e_layer_test_v6_2.json", "path": "quantization_comparison.int8.recall"})

    # ── Table 4: layer ablation, canonical source only ──────────────────────
    abl = load("data/redteam/l2_only_ablation.json")
    rows4 = [
        ("l0l1", "L0+L1 only (model-free fast path)", "L0+L1 only (model YOK)", (0, 60)),
        ("l2fp32", "L2-only, mmBERT FP32, raw text", "L2-FP32 / ham metin  (SADECE MODEL)", (4, 56)),
        ("l2int8", "L2-only, mmBERT INT8, raw text", "L2-INT8 / ham metin  (SADECE MODEL)", (5, 55)),
        ("dual", "L0 + L2-INT8, dual-channel max(P_raw,P_ext)", "L2-INT8 / max(ham, normalize)", (6, 54)),
        ("full", "NeuralShield full (FP32)", "TAM: L0+L1+L2+L3 (FP32)", (4, 56)),
    ]
    for key, label, src_key, (fp_n, tn) in rows4:
        row = abl["rows"][src_key]
        k = row["tp"]
        macro, f_mal, f_ben = f1_macro(k, 101 - k, fp_n, tn)
        add(f"t4.{key}.recall", round(100.0 * k / 101, 2), "%", "Table 4, Section 3.4",
            f"Attack catch rate for {label} (N=101)",
            [f"{100.0 * k / 101:.2f}"],
            source={"file": "data/redteam/l2_only_ablation.json", "path": f"rows.{src_key}.recall"},
            derive={"statistic": "pct", "k": k, "n": 101})
        add(f"t4.{key}.fp", round(100.0 * fp_n / 60, 2), "%", "Table 4",
            f"Benign false positives for {label} (N=60)",
            [f"{100.0 * fp_n / 60:.2f}"],
            source={"file": "data/redteam/l2_only_ablation.json", "path": f"rows.{src_key}.fp"},
            derive={"statistic": "pct", "k": fp_n, "n": 60})
        add(f"t4.{key}.macro_f1", round(macro * 100, 2), "%", "Table 4",
            f"Macro-F1 for {label}: mean of class F1 over TP={k}, FN={101 - k}, FP={fp_n}, TN={tn}",
            [f"{macro * 100:.2f}"],
            derive={"statistic": "f1_macro", "tp": k, "fn": 101 - k, "fp": fp_n, "tn": tn})
        add(f"t4.{key}.binary_f1", round(f_mal * 100, 2), "%", "Table 4 footnote",
            f"Malicious-class (binary) F1 for {label}",
            [f"{f_mal * 100:.2f}"],
            derive={"statistic": "f1_binary", "tp": k, "fn": 101 - k, "fp": fp_n})
        add(f"t4.{key}.ci", abl["wilson"][src_key]["ci"], "%", "Table 4",
            f"Wilson 95% interval for {label}",
            [f"[{abl['wilson'][src_key]['ci'][0]:.1f}, {abl['wilson'][src_key]['ci'][1]:.1f}]"],
            derive={"statistic": "wilson", "k": k, "n": 101})

    _norm = abl["rows"]["L2-INT8 / L0-normalize metin"]
    add("t4.l0.int8.normalized_recall", round(100.0 * _norm["tp"] / 101, 2), "%",
        "Table 4, Section 3.4", "INT8 recall when L2 receives L0-normalised text only",
        [f"{100.0 * _norm['tp'] / 101:.2f}"],
        source={"file": "data/redteam/l2_only_ablation.json", "path": "rows.L2-INT8 / L0-normalize metin.recall"},
        derive={"statistic": "pct", "k": _norm["tp"], "n": 101})

    # ── L0 contribution arithmetic and its McNemar test ─────────────────────
    rescued = l0["rescued_by_l0"]
    broken = l0["broken_by_l0"]
    add("s34.rescued", rescued, "count", "Section 3.4",
        "Attacks recovered by L0 normalisation on the fair benchmark", [str(rescued)],
        source={"file": "data/l0_contribution_fair.json", "path": "rescued_by_l0"})
    add("s34.broken", broken, "count", "Section 3.4",
        "Attacks lost by L0 normalisation on the fair benchmark", [str(broken)],
        source={"file": "data/l0_contribution_fair.json", "path": "broken_by_l0"})
    add("s34.net", rescued - broken, "count", "Section 3.4",
        "Net gain in detections", [str(rescued - broken)],
        derive={"statistic": "difference", "a": rescued, "b": broken})
    p_l0 = mcnemar_exact(rescued, broken)
    add("s34.mcnemar_p", round(p_l0, 6), "p-value", "Section 3.4",
        f"Exact two-sided McNemar on b={rescued}, c={broken}", ["0.0007"],
        derive={"statistic": "mcnemar", "b": rescued, "c": broken})
    add("s34.delta_pp", round(l0["ext"]["recall"] - l0["raw"]["recall"], 2), "pp", "Section 3.4",
        "Recall delta from L0 normalisation", ["+1.04"],
        derive={"statistic": "difference", "a": l0["ext"]["recall"], "b": l0["raw"]["recall"]})
    add("s34.f1_gain", round(e2e["shield"]["macro_f1"] - e2e["quantization_comparison"]["fp32"]["macro_f1"], 2),
        "pp", "Section 3.4", "Macro-F1 gain from L0 normalisation", [],
        derive={"statistic": "difference", "a": e2e["shield"]["macro_f1"],
                "b": e2e["quantization_comparison"]["fp32"]["macro_f1"]})

    # ── Table 5: open-weight red team ───────────────────────────────────────
    rr = load("data/redteam/redteam_v6_2_summary.json")
    labels5 = {
        "qwen25_15b": "Qwen2.5-1.5B", "phi3_mini": "Phi-3-mini", "gemma2_2b": "Gemma-2-2B",
        "llama32_3b": "Llama-3.2-3B", "qwen25_3b": "Qwen2.5-3B", "gemma2_9b": "Gemma-2-9B",
        "qwen25_14b": "Qwen2.5-14B", "llama31_8b": "Llama-3.1-8B", "qwen25_7b": "Qwen2.5-7B",
        "mistral_7b": "Mistral-7B-v0.3",
    }
    core = rr["core"]
    for key, label in labels5.items():
        if key not in core:
            continue
        row = core[key]
        add(f"t5.{key}.asr", row["off_asr"], "%", "Table 5, Section 3.5",
            f"Shield-OFF ASR for {label} (N=101)", [f"{row['off_asr']:.2f}"],
            source={"file": "data/redteam/redteam_v6_2_summary.json", "path": f"core.{key}.off_asr"},
            derive={"statistic": "pct", "k": row["off_leaks"], "n": 101})
        add(f"t5.{key}.ci", row["off_wilson"], "%", "Table 5",
            f"Wilson 95% interval for {label}",
            [f"[{row['off_wilson'][0]:.1f}, {row['off_wilson'][1]:.1f}]"],
            derive={"statistic": "wilson", "k": row["off_leaks"], "n": 101})
        add(f"t5.{key}.params", row["params"], "params", "Table 5",
            f"Parameter count of {label}", [row["params"]],
            source={"file": "data/redteam/redteam_v6_2_summary.json", "path": f"core.{key}.params"})

    # ── Table 6: reasoning models ───────────────────────────────────────────
    for key, label in (("qwen3_4b_think", "Qwen3-4B-Thinking"),
                       ("r1_distill_15b", "R1-Distill-Qwen-1.5B"),
                       ("r1_distill_7b", "R1-Distill-Qwen-7B")):
        row = rr["reasoning"][key]
        add(f"t6.{key}.cot", row["cot_leak_pct"], "%", "Table 6, Section 3.6",
            f"CoT leak rate for {label} (768-token budget, N=24)", [f"{row['cot_leak_pct']:.2f}"],
            source={"file": "data/redteam/redteam_v6_2_summary.json", "path": f"reasoning.{key}.cot_leak_pct"},
            derive={"statistic": "pct", "k": row["cot_leak_any"], "n": 24})
        add(f"t6.{key}.final", row["final_leak_pct"], "%", "Table 6, Section 3.6",
            f"Final-content leak rate for {label} (768-token budget, N=24)", [f"{row['final_leak_pct']:.2f}"],
            source={"file": "data/redteam/redteam_v6_2_summary.json", "path": f"reasoning.{key}.final_leak_pct"},
            derive={"statistic": "pct", "k": row["final_leak_any"], "n": 24})

    # ── Table 8: flagship models ────────────────────────────────────────────
    ev = load("data/redteam/evren_v6_2_summary.json")["evren_models"]
    for key, label in (("deepseek_v4_1_flash", "DeepSeek-v4.1-Flash"),
                       ("glm_5_3", "GLM-5.3 Flagship"),
                       ("qwen3_8_flash_next", "Qwen3.8-Flash-Next"),
                       ("gemma_4_31b", "Gemma-4-31B Dense")):
        row = ev[key]
        add(f"t8.{key}.final", row["off_asr"], "%", "Table 8, Section 3.8",
            f"Final-content ASR for {label} (N=101)", [f"{row['off_asr']:.2f}"],
            source={"file": "data/redteam/evren_v6_2_summary.json", "path": f"evren_models.{key}.off_asr"},
            derive={"statistic": "pct", "k": row["off_leaks"], "n": 101})
        add(f"t8.{key}.cot", row["off_cot_asr"], "%", "Table 8, Section 3.8",
            f"Reasoning CoT ASR for {label} (N=101)", [f"{row['off_cot_asr']:.2f}"],
            source={"file": "data/redteam/evren_v6_2_summary.json", "path": f"evren_models.{key}.off_cot_asr"},
            derive={"statistic": "pct", "k": row["off_cot_leaks"], "n": 101})
        add(f"t8.{key}.cot_ci", row["off_cot_wilson"], "%", "Table 8",
            f"Wilson 95% interval for the CoT ASR of {label}",
            [f"[{row['off_cot_wilson'][0]:.1f}, {row['off_cot_wilson'][1]:.1f}]"],
            derive={"statistic": "wilson", "k": row["off_cot_leaks"], "n": 101})

    # ── Table 9: ablations and exact McNemar ────────────────────────────────
    q = load("data/redteam/quant_and_prompt_ablation_n101.json")
    mistral = q["fp16_vs_4bit"]["Mistral-7B-v0.3"]
    llama = q["fp16_vs_4bit"]["Llama-3.1-8B"]
    for key, row, label in (("mistral", mistral, "Mistral-7B-v0.3"), ("llama", llama, "Llama-3.1-8B")):
        add(f"t9.{key}.4bit", row["bit4_asr"], "%", "Table 9, Section 3.9",
            f"4-bit NF4 ASR for {label} (N=101)", [f"{row['bit4_asr']:.2f}"],
            source={"file": "data/redteam/quant_and_prompt_ablation_n101.json",
                    "path": f"fp16_vs_4bit.{label}.bit4_asr"},
            derive={"statistic": "pct", "k": row["bit4_leaks"], "n": 101})
        add(f"t9.{key}.fp16", row["fp16_asr"], "%", "Table 9, Section 3.9",
            f"FP16 ASR for {label} (N=101)", [f"{row['fp16_asr']:.2f}"],
            source={"file": "data/redteam/quant_and_prompt_ablation_n101.json",
                    "path": f"fp16_vs_4bit.{label}.fp16_asr"},
            derive={"statistic": "pct", "k": row["fp16_leaks"], "n": 101})
        add(f"t9.{key}.delta", row["delta"], "pp", "Table 9, Table 10, Section 3.9",
            f"ASR delta (4-bit minus FP16) for {label}", [f"{row['delta']:+.2f}"],
            source={"file": "data/redteam/quant_and_prompt_ablation_n101.json",
                    "path": f"fp16_vs_4bit.{label}.delta"},
            derive={"statistic": "difference", "a": row["fp16_asr"], "b": row["bit4_asr"]})

    ph = q["prompt_hardening"]
    add("t9.hardening.standard", ph["standard_asr"], "%", "Table 9, Section 3.9",
        "Standard-prompt ASR for Qwen2.5-3B (N=101)", [f"{ph['standard_asr']:.2f}"],
        source={"file": "data/redteam/quant_and_prompt_ablation_n101.json", "path": "prompt_hardening.standard_asr"},
        derive={"statistic": "pct", "k": ph["standard_leaks"], "n": 101})
    add("t9.hardening.hardened", ph["hardened_asr"], "%", "Table 9, Section 3.9",
        "Hardened-prompt ASR for Qwen2.5-3B (N=101)", [f"{ph['hardened_asr']:.2f}"],
        source={"file": "data/redteam/quant_and_prompt_ablation_n101.json", "path": "prompt_hardening.hardened_asr"},
        derive={"statistic": "pct", "k": ph["hardened_leaks"], "n": 101})
    add("t9.hardening.benign_leak", ph["hardened_benign_fp_pct"], "%", "Table 9, Section 3.9",
        "Benign-query canary leakage under the hardened prompt (N=60)", [f"{ph['hardened_benign_fp_pct']:.2f}"],
        source={"file": "data/redteam/quant_and_prompt_ablation_n101.json",
                "path": "prompt_hardening.hardened_benign_fp_pct"})
    add("t9.hardening.delta", ph["delta"], "pp", "Table 9, Table 10, Section 3.9",
        "ASR delta from prompt hardening", [f"{ph['delta']:+.2f}"],
        source={"file": "data/redteam/quant_and_prompt_ablation_n101.json", "path": "prompt_hardening.delta"})

    # McNemar recomputed from per-item rows where the archive allows it.
    def discordant(rows_base, rows_candidate):
        """Returns (n, base_only, candidate_only).

        Called as discordant(rows_fp16, rows_bit4): base_only is what leaked
        under FP16 but not under 4-bit, candidate_only is what leaked under
        4-bit but not under FP16. Table 9 names them "(4-bit only)" and
        "(FP16 only)" respectively, so the caller maps candidate_only -> b.
        """
        base = {r["id"]: bool(r.get("vulnerable")) for r in rows_base}
        cand = {r["id"]: bool(r.get("vulnerable")) for r in rows_candidate}
        ids = set(base) & set(cand)
        return (len(ids),
                sum(1 for i in ids if base[i] and not cand[i]),
                sum(1 for i in ids if cand[i] and not base[i]))

    if "rows_bit4" in llama:
        n_l, fp16_only, bit4_only = discordant(llama["rows_fp16"], llama["rows_bit4"])
        tot_fp16 = sum(1 for r in llama["rows_fp16"] if r.get("vulnerable"))
        tot_bit4 = sum(1 for r in llama["rows_bit4"] if r.get("vulnerable"))
        add("t9.llama.discordant", [bit4_only, fp16_only], "count", "Table 9",
            "Discordant pairs for Llama: (4-bit-only leaks, FP16-only leaks)", ["7 (4-bit only)", "9 (FP16 only)"],
            source={"file": "data/redteam/quant_and_prompt_ablation_n101.json",
                    "path": "fp16_vs_4bit.Llama-3.1-8B.rows_bit4"},
            derive={"statistic": "discordant", "b": bit4_only, "c": fp16_only,
                    "tot_base": tot_fp16, "tot_candidate": tot_bit4, "n": n_l})
        add("t9.llama.mcnemar_p", round(mcnemar_exact(bit4_only, fp16_only), 3), "p-value",
            "Table 9, Section 3.9",
            f"Exact McNemar from b={bit4_only}, c={fp16_only}", ["0.804"],
            derive={"statistic": "mcnemar", "b": bit4_only, "c": fp16_only})
    n_h, b_h, c_h = discordant(ph["rows_standard"], ph["rows_hardened"])
    add("t9.hardening.discordant", [b_h, c_h], "count", "Table 9",
        "Discordant pairs for prompt hardening (standard-only, hardened-only)", [f"{b_h}", f"{c_h}"],
        source={"file": "data/redteam/quant_and_prompt_ablation_n101.json",
                "path": "prompt_hardening.rows_hardened"})
    add("t9.hardening.mcnemar_p", round(mcnemar_exact(b_h, c_h), 3), "p-value", "Table 9, Section 3.9",
        f"Exact McNemar from b={b_h}, c={c_h}", ["0.115"],
        derive={"statistic": "mcnemar", "b": b_h, "c": c_h})
    # Mistral per-item 4-bit rows are absent; the reported b/c are checked arithmetically.
    add("t9.mistral.mcnemar_p", round(mcnemar_exact(21, 10), 3), "p-value", "Table 9, Section 3.9",
        "Exact McNemar from the reported discordant counts b=21, c=10 (per-item 4-bit rows not archived)",
        ["0.071"], derive={"statistic": "mcnemar", "b": 21, "c": 10})

    # ── Contamination audit: replaces the previously unsourced 76.9% ────────
    ca = load("data/contamination_audit.json")
    add("s24.primary_contamination", ca["rates_pct"]["primary_contamination"], "%",
        "Section 1, Section 2.4, cover letter",
        "Share of legacy OOD items sharing at least one 8-gram with the v6 training corpus",
        [f"{ca['rates_pct']['primary_contamination']:.1f}"],
        source={"file": "data/contamination_audit.json", "path": "rates_pct.primary_contamination"})
    add("s24.strict_contamination", ca["rates_pct"]["strict_contamination"], "%",
        "Section 2.4",
        "Share of legacy OOD items with at least 50% of 8-grams in the training corpus",
        [f"{ca['rates_pct']['strict_contamination']:.1f}"],
        source={"file": "data/contamination_audit.json", "path": "rates_pct.strict_contamination"})
    add("s24.public_source", ca["rates_pct"]["public_source_lineage"], "%",
        "Section 1, Section 2.4",
        "Share of legacy OOD items whose source field names a public training repository",
        [f"{ca['rates_pct']['public_source_lineage']:.2f}"],
        source={"file": "data/contamination_audit.json", "path": "rates_pct.public_source_lineage"})
    add("s24.audited_items", ca["counts"]["evaluation_items"], "count", "Section 2.4",
        "Items in the audited legacy OOD suite", [f"{ca['counts']['evaluation_items']:,}".replace(",", ",")],
        source={"file": "data/contamination_audit.json", "path": "counts.evaluation_items"})
    add("s24.training_records", ca["counts"]["training_records"], "count", "Section 2.4",
        "Records in the audited training corpus", [f"{ca['counts']['training_records']:,}"],
        source={"file": "data/contamination_audit.json", "path": "counts.training_records"})

    # ── Table 7 and the SSE case study: pilot observations, no released items ─
    pilot = [
        ("t7.gemma.reasoning", 31, "count", "Table 7",
         "Reasoning-channel leaks for Gemma-4-31B out of 50 native Turkish prompts", "31/50"),
        ("t7.gemma.rate", 62.0, "%", "Table 7, Section 3.7",
         "Leak rate for Gemma-4-31B on the native Turkish pilot (31/50)", "62.0"),
        ("t7.qwen38.reasoning", 4, "count", "Table 7",
         "Reasoning-channel leaks for Qwen3.8-Flash-Next out of 50", "4/50"),
        ("t7.qwen38.rate", 8.0, "%", "Table 7", "Leak rate for Qwen3.8-Flash-Next (4/50)", "8.0"),
        ("t7.glm.reasoning", 1, "count", "Table 7",
         "Reasoning-channel leaks for GLM-5.3 out of 50", "1/50"),
        ("t7.glm.rate", 2.0, "%", "Table 7", "Leak rate for GLM-5.3 (1/50)", "2.0"),
        ("t7.content_leaks", 0, "count", "Table 7, Section 3.7",
         "Content-channel leaks for all six pilot models", "0/50"),
        ("s37.sse_events", 118, "events", "Section 3.7",
         "Reasoning events containing canaries observed in the SSE session", "118"),
        ("s37.sse_network_chars", 7981, "characters", "Section 3.7",
         "Total network characters in the event stream", "7,981"),
        ("s37.sse_reasoning_chars", 1414, "characters", "Section 3.7",
         "Characters belonging to reasoning payloads", "1,414"),
        ("s37.thinking_disabled", 0, "count", "Section 3.7",
         "Content-channel canary leaks with thinking disabled, out of 40 targeted attacks", "0/40"),
    ]
    for mid, value, unit, where, definition, rendered in pilot:
        add(mid, value, unit, where, definition, [], status="pilot-observation")
        entries[-1]["rendered_text"] = rendered

    # ── Declared design constants ───────────────────────────────────────────
    declared = [
        ("ds.records", 98606, "dataset records", "Sections 2.3, Abstract", ["98,606"]),
        ("ds.malicious", 48627, "malicious samples", "Section 2.3", ["48,627"]),
        ("ds.benign", 49979, "benign samples", "Section 2.3", ["49,979"]),
        ("ds.en", 29983, "English records", "Section 2.3", ["29,983"]),
        ("ds.tr", 29011, "Turkish records", "Section 2.3", ["29,011"]),
        ("ds.train", 69021, "training split", "Section 2.3", ["69,021"]),
        ("ds.val", 14794, "validation split", "Section 2.3", ["14,794"]),
        ("ds.test", 14791, "test split", "Section 2.3", ["14,791"]),
        ("fair.n", 2849, "fair benchmark items", "Sections 2.4, 3.1, 5", ["2,849"]),
        ("fair.attacks", 1440, "fair benchmark attacks", "Sections 2.4, 3.4", ["1,440"]),
        ("fair.benign", 1409, "fair benchmark benign items", "Sections 2.4, 3.4", ["1,409"]),
        ("rt.attacks", 101, "curated attacks", "Sections 2.5, 3.4-3.9", ["101"]),
        ("rt.benign", 60, "curated benign queries", "Sections 2.5, 3.4-3.9", ["60"]),
        ("rt.total", 161, "curated suite size", "Sections 2.5, 3.8", ["161"]),
        ("models.total", 18, "distinct checkpoints", "Abstract, Section 2.5, Section 5",
         ["18 distinct", "18 distinct checkpoints"]),
        ("models.endpoints", 19, "endpoint entries", "Abstract, Section 2.5, Section 5", ["19 endpoint entries"]),
        ("native.tr.n", 1077, "native Turkish items", "Sections 3.2, 4.1", ["1,077"]),
        ("native.ru.n", 16636, "native Russian items", "Sections 3.2, 4.1", ["16,636"]),
        ("calib.t", 1.8345, "fitted temperature", "Section 2.6", ["1.8345"]),
        ("calib.ece_before", 11.51, "ECE before", "Section 2.6", ["11.51"]),
        ("calib.ece_after", 3.45, "ECE after", "Section 2.6", ["3.45"]),
    ]
    for mid, value, unit, where, renders in declared:
        add(mid, value, unit, where, unit, renders, status="declared")

    manifest = {
        "generated_by": "scripts/build_metrics_manifest.py",
        "rule": "data rules the number; the number never rules the data",
        "entry_count": len(entries),
        "entries": entries,
    }
    with io.open("data/paper_metrics_manifest.json", "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2)
    print(f"manifest written: data/paper_metrics_manifest.json ({len(entries)} entries)")


if __name__ == "__main__":
    main()
