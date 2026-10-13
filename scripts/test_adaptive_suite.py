"""
Test script for independent 50-sample unseen adaptive dataset (Section 3).
Evaluates Layer 0 + Layer 1 and Full Pipeline detection rates.
"""
import asyncio
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

import security_layer as sl
from ml_model import MLSecurityModel

async def evaluate():
    data_path = ROOT / "data" / "adaptive_adversarial_50.json"
    with open(data_path, "r", encoding="utf-8") as f:
        cases = json.load(f)

    print("=" * 80)
    print("🛡️ ADAPTİF VE GÖRÜLMEMİŞ SALDIRI KÜMESİ SINAVI (n=50)")
    print("=" * 80)

    ml = MLSecurityModel(model_path=str(ROOT / "backend" / "models" / "neuralshield_v3"))
    blocked_count = 0
    layer0_hits = 0
    layer1_hits = 0
    layer2_hits = 0

    missed = []

    for item in cases:
        cid = item["id"]
        prompt = item["prompt"]
        tech = item["technique"]

        res = await sl.analyze(
            text=prompt,
            pdf_base64=None,
            url=None,
            security_enabled=True,
            gemini_model=None,
            ml_model=ml,
            user_behavior_score=0
        )

        decision = res["decision"]
        risk = res["risk_score"]
        l0_alert = len(res.get("layer0_alerts", [])) > 0
        l1_hit = res.get("regex_triggered", False)
        l2_hit = res.get("ml_class") == "Malicious"

        if l0_alert:
            layer0_hits += 1
        if l1_hit:
            layer1_hits += 1
        if l2_hit:
            layer2_hits += 1

        if decision == "BLOCKED":
            blocked_count += 1
        else:
            missed.append((cid, tech, prompt[:60], risk, res["ml_class"]))

    block_rate = (blocked_count / len(cases)) * 100.0

    print(f"\nToplam Test Örneği           : {len(cases)}")
    print(f"Katman 0 (Stego/Normalizer)   : {layer0_hits} / {len(cases)} (%{(layer0_hits/len(cases))*100:.1f})")
    print(f"Katman 1 (Heuristic / Regex)  : {layer1_hits} / {len(cases)} (%{(layer1_hits/len(cases))*100:.1f})")
    print(f"Katman 2 (XLM-RoBERTa Model)  : {layer2_hits} / {len(cases)} (%{(layer2_hits/len(cases))*100:.1f})")
    print(f"Nihai Engelleme Oranı (BLOCKED): {blocked_count} / {len(cases)} (%{block_rate:.1f})")
    print("=" * 80)

    if missed:
        print(f"\n⚠️ KAÇAN SALDIRILAR ({len(missed)} adet):")
        for cid, tech, p, r, mlc in missed:
            print(f"  [{cid}] {tech:<30} -> Risk: {r} (ML: {mlc}) | {p}")
    else:
        print("\n🏆 MÜKEMMEL: Tüm adaptif saldırılar başarıyla engellendi (%100 BLOCKED)!")

if __name__ == "__main__":
    asyncio.run(evaluate())
