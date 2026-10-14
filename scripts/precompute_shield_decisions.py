"""
Shield (Layer 0-2) kararlarını appsec_benchmark_2000.json için ÖNCEDEN hesaplar.
Colab notebook'u 278MB ONNX modeli taşımak zorunda kalmasın diye: her örnek için
shield_blocked / shield_risk / shield_clean_text alanları eklenir.
Çıktı: data/appsec_benchmark_2000_shield.json
"""
import json, sys, time
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))
from normalizer import normalize_for_analysis
from regex_rules import scan_text
from ml_model import MLSecurityModel
from shield_config import CONFIG

DATA = Path(__file__).resolve().parent.parent / "data"
d = json.load(open(DATA / "appsec_benchmark_2000.json", encoding="utf-8"))
ml = MLSecurityModel()
print(f"[i] {len(d)} örnek işlenecek...")

BLOCK = CONFIG["block_threshold"]
t0 = time.time()
for i, x in enumerate(d):
    nr = normalize_for_analysis(x["text"])
    at = nr["extended_text"]
    trig, pats, r_score = scan_text(at)
    hard = bool(nr["hard_stego_signal"])
    m = ml.predict(at)
    ml_risk = m.get("ml_risk_score", 0); ml_class = m.get("ml_class", "Benign")
    stego = 100 if hard else 0
    comp = CONFIG["weight_ml"]*ml_risk + CONFIG["weight_regex"]*r_score + CONFIG["weight_stego"]*stego
    if hard: risk = max(comp, CONFIG["hard_block_stego_score"])
    elif trig and ml_class == "Malicious": risk = max(comp, CONFIG["hard_block_regex_and_ml_score"])
    elif trig: risk = max(comp, CONFIG["regex_only_floor_score"])
    else: risk = comp
    risk = min(100, round(risk))
    blocked = risk >= BLOCK or (trig and ml_class == "Malicious")
    x["shield_blocked"] = bool(blocked)
    x["shield_risk"] = int(risk)
    x["shield_clean_text"] = nr["clean_text"]
    x["ml_risk"] = int(ml_risk)
    x["ml_class"] = ml_class
    x["regex_score"] = int(r_score)
    x["regex_triggered"] = bool(trig)
    x["hard_stego"] = bool(hard)
    if (i+1) % 250 == 0:
        print(f"  {i+1}/{len(d)}  ({time.time()-t0:.0f}s)")

json.dump(d, open(DATA / "appsec_benchmark_2000_shield.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
from collections import Counter
atk = [x for x in d if x["label"] == 1]
ben = [x for x in d if x["label"] == 0]
print(f"\n[OK] kaydedildi: appsec_benchmark_2000_shield.json")
print(f"  Saldırıların shield-blocked oranı : {sum(x['shield_blocked'] for x in atk)}/{len(atk)} ({sum(x['shield_blocked'] for x in atk)/len(atk)*100:.1f}%)")
print(f"  Meşruların shield-blocked (FP)     : {sum(x['shield_blocked'] for x in ben)}/{len(ben)} ({sum(x['shield_blocked'] for x in ben)/len(ben)*100:.1f}%)")
