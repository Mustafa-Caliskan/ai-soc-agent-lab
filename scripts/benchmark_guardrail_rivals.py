"""
CyberTech Neural Shield v5 - SOTA Guardrail Kıyaslama ve Karşılaştırmalı Değerlendirme Paketi.

Akademik Bütünlük İlkeleri:
  1. Kesinlikle simüle/uydurma rakip veri üretilmez. Yalnızca canlı çalışan modeller Tablo II-A'ya girer.
  2. Bütün oranlar için Wilson Score %95 Güven Aralığı ([Lower, Upper]) hesaplanır.
  3. "4-Katmanlı Savunma Hattı" ile "Tekil ML/LLM Modelleri" arasındaki mimari fark açıkça ayrıştırılır.
  4. Yerel olarak çalıştırılamayan modeller Tablo II-B (Yayınlanmış Literatür Referansı) olarak sunulur.
"""
import os
import sys
import time
import json
import math
import argparse
import logging
from typing import Dict, Any, List, Optional, Tuple

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "backend"))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from backend.normalizer import normalize_for_analysis
from backend.regex_rules import scan_text
from backend.ml_model import MLSecurityModel
from backend.shield_config import CONFIG
from backend.evren_client import EvrenClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("GuardrailBenchmark")

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def wilson_ci(k: int, n: int, z: float = 1.95996) -> Tuple[float, float, float]:
    """
    Wilson Score %95 Güven Aralığı (Wilson, 1927).
    Döndürür: (point_pct, lower_pct, upper_pct)
    """
    if n <= 0:
        return 0.0, 0.0, 0.0
    p = k / n
    denominator = 1.0 + (z ** 2) / n
    centre = (p + (z ** 2) / (2 * n)) / denominator
    margin = (z * math.sqrt((p * (1.0 - p) + (z ** 2) / (4 * n)) / n)) / denominator
    lower = max(0.0, centre - margin) * 100.0
    upper = min(1.0, centre + margin) * 100.0
    return p * 100.0, lower, upper


class BaseGuardrailEvaluator:
    def __init__(self, name: str, architecture_type: str):
        self.name = name
        self.architecture_type = architecture_type
        self.is_active = True

    def evaluate(self, prompt: str) -> Dict[str, Any]:
        raise NotImplementedError


class NeuralShieldV5FullPipelineEvaluator(BaseGuardrailEvaluator):
    """
    CyberTech NeuralShield-v5 Tam 4-Katmanlı Savunma Hattı:
    Katman 0: Normalizasyon + De-obfuscation (Base64/ROT13/Tag) + JSON/Tool-call Unpacker
    Katman 1: Çok Dilli Regex & Heuristic Kural Motoru
    Katman 2: XLM-RoBERTa ONNX INT8 Kayan Pencere + Sıcaklık Kalibrasyonu
    Katman 3: DLP / PII Maskeleme & Checksum Doğrulama
    """
    def __init__(self):
        super().__init__(
            name="NeuralShield-v5 (Tam 4-Katmanlı Savunma Hattı)",
            architecture_type="4-Katmanlı Savunma Hattı (Defense-in-Depth Pipeline)"
        )
        self.ml_model = MLSecurityModel()

    def evaluate(self, prompt: str) -> Dict[str, Any]:
        t0 = time.perf_counter()

        # Katman 0: Normalizasyon, Steganografi & Yapılandırılmış JSON/URL Açıcı
        norm_res = normalize_for_analysis(prompt)
        analysis_text = norm_res["extended_text"]
        hard_stego = bool(norm_res["hard_stego_signal"])

        # Katman 1: Regex & Heuristic
        r_trig, r_pats, r_score = scan_text(analysis_text)

        # Katman 2: XLM-RoBERTa ONNX INT8 (Kayan Pencere + Kalibre Edilmiş Sıcaklık)
        ml_res = self.ml_model.predict(analysis_text, sliding_window=True)
        ml_risk = ml_res.get("ml_risk_score", 0)
        ml_class = ml_res.get("ml_class", "Benign")

        stego_score = 100 if hard_stego else 0
        composite_score = (
            CONFIG["weight_ml"] * ml_risk
            + CONFIG["weight_regex"] * r_score
            + CONFIG["weight_stego"] * stego_score
        )

        if hard_stego:
            final_risk = max(composite_score, CONFIG["hard_block_stego_score"])
        elif r_trig and ml_class == "Malicious":
            final_risk = max(composite_score, CONFIG["hard_block_regex_and_ml_score"])
        elif r_trig:
            final_risk = max(composite_score, CONFIG["regex_only_floor_score"])
        else:
            final_risk = composite_score

        is_blocked = final_risk >= CONFIG["block_threshold"]
        latency_ms = (time.perf_counter() - t0) * 1000.0

        return {
            "is_blocked": is_blocked,
            "risk_score": round(final_risk, 1),
            "latency_ms": round(latency_ms, 2),
            "details": {
                "ml_risk": ml_risk,
                "regex_score": r_score,
                "hard_stego": hard_stego,
                "chunks": ml_res.get("chunks_analyzed", 1),
            }
        }


class NeuralShieldLayer2OnlyEvaluator(BaseGuardrailEvaluator):
    """
    NeuralShield Katman 2: Yalnızca XLM-RoBERTa ONNX INT8 Modeli.
    Katman 0 ön-işleme (steganografi çözme vb.) ve Katman 1 regex kuralları DEVRE DIŞIDIR.
    Doğrudan ham metin sınıflandırması yapar. Bu sınıflandırıcı, tekil modellerle
    (ProtectAI, Patronus) kafa kafaya saf model karşılaştırması sağlamak için eklenmiştir.
    """
    def __init__(self):
        super().__init__(
            name="NeuralShield-v5 (Yalnızca Katman 2 ML Modeli)",
            architecture_type="Tekil Model (Standalone ONNX INT8 Classifier)"
        )
        self.ml_model = MLSecurityModel()

    def evaluate(self, prompt: str) -> Dict[str, Any]:
        t0 = time.perf_counter()
        ml_res = self.ml_model.predict(prompt, sliding_window=True)
        latency_ms = (time.perf_counter() - t0) * 1000.0
        ml_class = ml_res.get("ml_class", "Benign")
        is_blocked = (ml_class == "Malicious")
        return {
            "is_blocked": is_blocked,
            "risk_score": round(ml_res.get("ml_risk_score", 0), 1),
            "latency_ms": round(latency_ms, 2),
            "details": ml_res
        }


class Qwen3GuardEvaluator(BaseGuardrailEvaluator):
    """
    Alibaba Qwen3-Guard-4B: Canlı EVREN API H200 GPU Üzerinde Çalışan Standalone Guardrail LLM.
    """
    def __init__(self):
        super().__init__(
            name="Qwen3-Guard-4B (EVREN API H200)",
            architecture_type="Tekil LLM Guardrail (4B Parameter LLM via API)"
        )
        self.client = EvrenClient()
        self.is_active = self.client.is_configured

    def evaluate(self, prompt: str) -> Dict[str, Any]:
        if not self.is_active:
            return {"is_blocked": False, "risk_score": 0.0, "latency_ms": 0.0, "details": {"error": "EVREN not configured"}}

        t0 = time.perf_counter()
        try:
            res = self.client.generate_chat(prompt, model="qwen3-guard-4b", max_tokens=64, temperature=0.0)
            latency_ms = (time.perf_counter() - t0) * 1000.0
            content = res.get("content", "").strip()

            is_blocked = ("Controversial" in content or "Unsafe" in content or "Jailbreak" in content)
            risk = 95.0 if is_blocked else 5.0

            return {
                "is_blocked": is_blocked,
                "risk_score": risk,
                "latency_ms": round(latency_ms, 2),
                "details": {"raw_response": content}
            }
        except Exception as e:
            latency_ms = (time.perf_counter() - t0) * 1000.0
            return {
                "is_blocked": False,
                "risk_score": 0.0,
                "latency_ms": round(latency_ms, 2),
                "details": {"error": str(e)}
            }


class ProtectAIEvaluator(BaseGuardrailEvaluator):
    """
    ProtectAI DeBERTa-v3 Prompt Injection v2 (HuggingFace).
    Yalnızca yerel diskte weights varsa çalışır; asla uydurma veri üretmez.
    """
    def __init__(self, download_weights: bool = False):
        super().__init__(
            name="ProtectAI DeBERTa-v3 (HuggingFace)",
            architecture_type="Tekil Model (Standalone DeBERTa Classifier)"
        )
        self.pipeline = None
        self.is_active = False
        self._init_model(download_weights)

    def _init_model(self, download_weights: bool):
        try:
            from transformers import pipeline
            if not download_weights:
                self.pipeline = pipeline(
                    "text-classification",
                    model="protectai/deberta-v3-base-prompt-injection-v2",
                    local_files_only=True,
                    truncation=True,
                    max_length=512,
                    device="cpu"
                )
                self.is_active = True
                logger.info("✅ ProtectAI modeli yerel önbellekten yüklendi.")
            else:
                logger.info("ProtectAI DeBERTa-v3 indiriliyor...")
                self.pipeline = pipeline(
                    "text-classification",
                    model="protectai/deberta-v3-base-prompt-injection-v2",
                    truncation=True,
                    max_length=512,
                    device="cpu"
                )
                self.is_active = True
        except Exception:
            self.is_active = False
            logger.info("ℹ️ ProtectAI yerel önbellekte bulunamadı. Akademik dürüstlük gereği simülasyon yapılmayacaktır.")

    def evaluate(self, prompt: str) -> Dict[str, Any]:
        if not self.is_active or not self.pipeline:
            return {"is_blocked": False, "risk_score": 0.0, "latency_ms": 0.0, "details": {"status": "not_loaded"}}
        t0 = time.perf_counter()
        res = self.pipeline(prompt[:1000])
        latency_ms = (time.perf_counter() - t0) * 1000.0
        label = res[0].get("label", "").upper()
        score = float(res[0].get("score", 0.0))
        is_blocked = ("INJECTION" in label and score >= 0.5)
        return {
            "is_blocked": is_blocked,
            "risk_score": round(score * 100.0, 1) if is_blocked else round((1.0 - score) * 100.0, 1),
            "latency_ms": round(latency_ms, 2),
            "details": {"label": label, "prob": score}
        }


class PatronusWolfEvaluator(BaseGuardrailEvaluator):
    """
    Patronus AI Wolf Defender (ModernBERT).
    Yalnızca yerel diskte weights varsa çalışır; asla uydurma veri üretmez.
    """
    def __init__(self, download_weights: bool = False):
        super().__init__(
            name="Patronus Wolf Defender (ModernBERT)",
            architecture_type="Tekil Model (Standalone ModernBERT Classifier)"
        )
        self.pipeline = None
        self.is_active = False
        self._init_model(download_weights)

    def _init_model(self, download_weights: bool):
        try:
            from transformers import pipeline
            if not download_weights:
                self.pipeline = pipeline(
                    "text-classification",
                    model="patronus-studio/wolf-defender-prompt-injection",
                    local_files_only=True,
                    truncation=True,
                    device="cpu"
                )
                self.is_active = True
                logger.info("✅ Patronus Wolf Defender yerel önbellekten yüklendi.")
            else:
                logger.info("Patronus Wolf Defender indiriliyor...")
                self.pipeline = pipeline(
                    "text-classification",
                    model="patronus-studio/wolf-defender-prompt-injection",
                    truncation=True,
                    device="cpu"
                )
                self.is_active = True
        except Exception:
            self.is_active = False
            logger.info("ℹ️ Patronus Wolf Defender yerel önbellekte bulunamadı. Akademik dürüstlük gereği simülasyon yapılmayacaktır.")

    def evaluate(self, prompt: str) -> Dict[str, Any]:
        if not self.is_active or not self.pipeline:
            return {"is_blocked": False, "risk_score": 0.0, "latency_ms": 0.0, "details": {"status": "not_loaded"}}
        t0 = time.perf_counter()
        res = self.pipeline(prompt[:2000])
        latency_ms = (time.perf_counter() - t0) * 1000.0
        label = res[0].get("label", "").upper()
        score = float(res[0].get("score", 0.0))
        is_blocked = ("INJECTION" in label or "ATTACK" in label or label == "LABEL_1")
        return {
            "is_blocked": is_blocked,
            "risk_score": round(score * 100.0, 1),
            "latency_ms": round(latency_ms, 2),
            "details": {"label": label, "prob": score}
        }


def load_dataset(dataset_path: str, max_samples: Optional[int] = None) -> List[Dict[str, Any]]:
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Veriseti dosyası bulunamadı: {dataset_path}")

    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if max_samples and max_samples < len(data):
        from collections import defaultdict
        by_subcat = defaultdict(list)
        for item in data:
            subcat = item.get("subcategory") or (
                "malicious" if item.get("label") == 1 or item.get("expected_label") == "MALICIOUS" else "benign"
            )
            by_subcat[subcat].append(item)

        selected = []
        n_cats = len(by_subcat)
        per_cat = max(1, max_samples // n_cats)
        for subcat, items in by_subcat.items():
            selected.extend(items[:per_cat])

        if len(selected) < max_samples:
            remaining = [x for x in data if x not in selected]
            selected.extend(remaining[:max_samples - len(selected)])
        data = selected[:max_samples]

    logger.info(f"📂 Veriseti yüklendi: {len(data)} örnek ({os.path.basename(dataset_path)})")
    return data


def run_benchmark(dataset: List[Dict[str, Any]], evaluators: List[BaseGuardrailEvaluator]) -> Dict[str, Any]:
    # Yalnızca aktif (modeli gerçekten yüklü olan) evaluator'ları çalıştır
    active_evaluators = [e for e in evaluators if e.is_active]

    print(f"\n{BOLD}{CYAN}======================================================================{RESET}")
    print(f"{BOLD}{CYAN}🛡️  SOTA GÜVENLİK DUVARI KARŞILAŞTIRMA BENCHMARK'I BAŞLIYOR{RESET}")
    print(f"{BOLD}{CYAN}======================================================================{RESET}")
    print(f"Toplam Test Örneği: {len(dataset)}")
    print(f"Canlı Çalıştırılan Modeller ({len(active_evaluators)}):")
    for ev in active_evaluators:
        print(f"  • {ev.name} [{ev.architecture_type}]")
    print()

    results_by_evaluator = {}
    for ev in active_evaluators:
        results_by_evaluator[ev.name] = {
            "evaluator_name": ev.name,
            "architecture_type": ev.architecture_type,
            "total_tested": 0,
            "malicious_total": 0,
            "malicious_blocked": 0,
            "stego_total": 0,
            "stego_blocked": 0,
            "tr_total": 0,
            "tr_blocked": 0,
            "benign_total": 0,
            "benign_false_positives": 0,
            "latencies_ms": [],
        }

    for idx, item in enumerate(dataset, start=1):
        prompt = item.get("text") or item.get("prompt", "")
        # Label tespiti
        label_val = item.get("label")
        exp_str = str(item.get("expected_label", "")).upper()
        cat_str = str(item.get("category", "")).upper()
        subcat = str(item.get("subcategory", "")).lower()

        is_malicious = (label_val == 1) or ("MALICIOUS" in exp_str) or ("ATTACK" in cat_str)
        is_stego = (subcat == "unicode_steganography") or any(0xE0000 <= ord(c) <= 0xE007F for c in prompt) or ("stego" in subcat)
        is_tr = ("tr" in subcat) or item.get("language") == "tr"

        preview = prompt.replace("\n", " ")[:60]
        status_tag = f"{RED}ATTACK{RESET}" if is_malicious else f"{GREEN}BENIGN{RESET}"
        print(f"[{idx:03d}/{len(dataset):03d}] {status_tag} | \"{preview}...\"")

        for ev in active_evaluators:
            res = ev.evaluate(prompt)
            stats = results_by_evaluator[ev.name]

            stats["total_tested"] += 1
            stats["latencies_ms"].append(res["latency_ms"])

            if is_malicious:
                stats["malicious_total"] += 1
                if res["is_blocked"]:
                    stats["malicious_blocked"] += 1
                if is_stego:
                    stats["stego_total"] += 1
                    if res["is_blocked"]:
                        stats["stego_blocked"] += 1
                if is_tr:
                    stats["tr_total"] += 1
                    if res["is_blocked"]:
                        stats["tr_blocked"] += 1
            else:
                stats["benign_total"] += 1
                if res["is_blocked"]:
                    stats["benign_false_positives"] += 1

            status_str = f"{RED}BLOCKED{RESET}" if res["is_blocked"] else f"{GREEN}ALLOWED{RESET}"
            print(f"   ↳ {ev.name[:45]:45s} -> {status_str} ({res['latency_ms']:.1f} ms)")

    # İstatistikler ve Wilson %95 Güven Aralıkları
    summary_table = []
    for ev in active_evaluators:
        stats = results_by_evaluator[ev.name]
        m_tot = stats["malicious_total"]
        b_tot = stats["benign_total"]
        st_tot = stats["stego_total"]
        tr_tot = stats["tr_total"]

        # ASR = Saldırının Başarısı (Engellenememe Oranı)
        m_blocked = stats["malicious_blocked"]
        m_bypassed = m_tot - m_blocked
        asr_p, asr_l, asr_u = wilson_ci(m_bypassed, m_tot)

        # TR Yakalama Oranı
        tr_p, tr_l, tr_u = wilson_ci(stats["tr_blocked"], tr_tot)

        # Stego Yakalama Oranı
        st_p, st_l, st_u = wilson_ci(stats["stego_blocked"], st_tot)

        # False Positive (IT Yanlış Alarm) Oranı
        fp_p, fp_l, fp_u = wilson_ci(stats["benign_false_positives"], b_tot)

        lats = stats["latencies_ms"]
        avg_lat = float(np.mean(lats)) if lats else 0.0
        std_lat = float(np.std(lats)) if lats else 0.0

        summary_table.append({
            "name": ev.name,
            "arch_type": ev.architecture_type,
            "tested_samples": stats["total_tested"],
            "asr_point": round(asr_p, 2),
            "asr_ci": f"%{asr_p:.1f} [%{asr_l:.1f}, %{asr_u:.1f}]",
            "tr_block_point": round(tr_p, 2),
            "tr_block_ci": f"%{tr_p:.1f} [%{tr_l:.1f}, %{tr_u:.1f}]",
            "stego_block_point": round(st_p, 2),
            "stego_block_ci": f"%{st_p:.1f} [%{st_l:.1f}, %{st_u:.1f}]",
            "fp_point": round(fp_p, 2),
            "fp_ci": f"%{fp_p:.1f} [%{fp_l:.1f}, %{fp_u:.1f}]",
            "avg_latency_ms": round(avg_lat, 2),
            "std_latency_ms": round(std_lat, 2),
        })

    return {
        "benchmark_timestamp": time.time(),
        "dataset_size": len(dataset),
        "active_models_count": len(active_evaluators),
        "summary": summary_table,
    }


def print_academic_tables(results: Dict[str, Any]):
    summary = results["summary"]
    n_samples = results["dataset_size"]

    print(f"\n{BOLD}{GREEN}========================================================================================{RESET}")
    print(f"{BOLD}{GREEN}📊 TABLO II-A: CANLI AMPİRİK KIYASLAMA VE GÜVEN ARALIKLARI (N = {n_samples}){RESET}")
    print(f"{BOLD}{GREEN}========================================================================================{RESET}\n")

    md_a = "| Güvenlik Mimarisi / Model | Mimari Tipi | TR Yakalama [%95 GA] | Stego Yakalama [%95 GA] | Saldırı Başarısı (ASR) [%95 GA] | Yanlış Alarm (FP) [%95 GA] | Gecikme (ms) |\n"
    md_a += "| :--- | :--- | :---: | :---: | :---: | :---: | :---: |\n"
    for r in summary:
        md_a += (
            f"| **{r['name']}** | {r['arch_type']} | "
            f"{r['tr_block_ci']} | {r['stego_block_ci']} | "
            f"**{r['asr_ci']}** | {r['fp_ci']} | "
            f"**{r['avg_latency_ms']:.1f} ± {r['std_latency_ms']:.1f} ms** |\n"
        )
    print(md_a)

    print(f"\n{BOLD}{CYAN}========================================================================================{RESET}")
    print(f"{BOLD}{CYAN}📚 TABLO II-B: YAYINLANMIŞ LİTERATÜR & RESMİ MODEL KARTI REFERANSLARI{RESET}")
    print(f"{BOLD}{CYAN}========================================================================================{RESET}\n")

    md_b = (
        "| Model Adı | Temel Mimari | Bildirilen Başarı / F1 | Bağlam Uzunluğu | Notlar & Sınırlamalar |\n"
        "| :--- | :--- | :---: | :---: | :--- |\n"
        "| **Patronus Wolf Defender** | ModernBERT (base) | %98.44 F1 (Resmi Kart) | 8.192 token | Çok dilli ve Base64 sentetik veri ile eğitilmiştir. Tekil metin sınıflandırıcısıdır. |\n"
        "| **ProtectAI DeBERTa-v3 v2** | DeBERTa-v3 (base) | >%99.0 Doğruluk (Resmi Kart) | 512 token | Saf İngilizce prompt injection için optimize edilmiştir. Jailbreak ve Türkçe desteklemez. |\n"
        "| **Qualifire Prompt Sentinel** | ModernBERT (large) | SOTA Gatekeeper | 8.192 token | Kurumsal LLM kapı bekçisi olarak eğitilmiştir. |\n"
    )
    print(md_b)


import numpy as np


def main():
    parser = argparse.ArgumentParser(description="CyberTech Neural Shield SOTA Guardrail Benchmark Suite")
    parser.add_argument("--dataset", default=os.path.join(ROOT_DIR, "data", "benchmark_300.json"), help="Dataset path")
    parser.add_argument("--max-samples", type=int, default=50, help="Max test samples to run")
    parser.add_argument("--output", default=os.path.join(ROOT_DIR, "data", "guardrail_rivals_benchmark_results.json"), help="Results JSON path")
    parser.add_argument("--include-qwen", action="store_true", default=True, help="Include Qwen3-Guard-4B live API")
    args = parser.parse_args()

    evaluators: List[BaseGuardrailEvaluator] = [
        NeuralShieldV5FullPipelineEvaluator(),
        NeuralShieldLayer2OnlyEvaluator(),
    ]

    if args.include_qwen:
        qwen_ev = Qwen3GuardEvaluator()
        if qwen_ev.is_active:
            evaluators.append(qwen_ev)
        else:
            logger.warning("⚠️ Qwen3-Guard API anahtarı yapılandırılmadığı için atlanıyor.")

    # ProtectAI ve Patronus: Yalnızca diskte varsa ekle, yoksa simülasyon YAPMA
    evaluators.append(ProtectAIEvaluator(download_weights=False))
    evaluators.append(PatronusWolfEvaluator(download_weights=False))

    dataset = load_dataset(args.dataset, max_samples=args.max_samples)
    results = run_benchmark(dataset, evaluators)

    print_academic_tables(results)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    logger.info(f"✅ Benchmark sonuçları kaydedildi: {args.output}")


if __name__ == "__main__":
    main()
