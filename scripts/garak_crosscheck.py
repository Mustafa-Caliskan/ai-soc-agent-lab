"""
garak Köprüsü: NVIDIA garak'ın probe promptlarını bizim kalkandan (L0-L2, OR-Gate) geçirir
ve "kalkan garak saldırılarının %X'ini yakalıyor" raporunu üretir.
Çıktı: docs/GARAK_CROSSCHECK.md + data/garak_crosscheck_results.json
"""
import os, sys, json, re, time
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from collections import defaultdict, Counter
ROOT = Path(r'C:\Users\Mustafa\OneDrive\Masaüstü\Akademik_yayın')
sys.path.insert(0, str(ROOT / 'backend'))

import garak._plugins as gp
from normalizer import normalize_for_analysis
from regex_rules import scan_text
from ml_model import MLSecurityModel
from shield_config import CONFIG

MAX_PER_PROBE = 15          # her probe sınıfından en fazla kaç prompt
# Kapsam-içi (injection/jailbreak/encoding/exfil) probe aileleri — ağır/harici olanlar atlanır
FAMILIES = {
    "promptinject", "dan", "encoding", "apikey", "goodside", "grandma",
    "exploitation", "xss", "snowball", "misleading", "knownbadsignatures",
}
ml = MLSecurityModel()
print("[i] ML model yüklendi.", flush=True)

def shield_block(text):
    nr = normalize_for_analysis(text)
    at = nr["extended_text"]
    trig, _, r = scan_text(at)
    hard = bool(nr["hard_stego_signal"])
    m = ml.predict(at)
    ml_risk = m.get("ml_risk_score", 0); mlc = m.get("ml_class", "Benign")
    return bool(hard or r >= CONFIG.get("regex_block_score_threshold", 60)
                or ml_risk >= CONFIG.get("ml_block_threshold", 70)
                or (trig and mlc == "Malicious"))

# garak probe sınıflarını topla (yalnızca kapsam-içi aileler)
specs = [name for name, active in gp.enumerate_plugins("probes")
         if name.count(".") >= 2 and name.split(".")[1] in FAMILIES]
print(f"[i] {len(specs)} kapsam-içi probe sınıfı yükleniyor...", flush=True)

results = {}
all_prompts = []
for i, spec in enumerate(specs, 1):
    try:
        obj = gp.load_plugin(spec)
        prompts = getattr(obj, "prompts", None) or getattr(obj, "prompt", None)
        if isinstance(prompts, str): prompts = [prompts]
        if not prompts: continue
        prompts = [str(p) for p in prompts if isinstance(p, (str, bytes)) and len(str(p)) >= 8][:MAX_PER_PROBE]
        if not prompts: continue
        fam = spec.split(".")[1]
        blocked = sum(1 for p in prompts if shield_block(p))
        d = results.setdefault(fam, {"probes": 0, "blocked": 0})
        d["probes"] += len(prompts); d["blocked"] += blocked
        print(f"  [{i}/{len(specs)}] {spec}: n={len(prompts)} blok={blocked}", flush=True)
    except Exception as e:
        print(f"  [{i}/{len(specs)}] {spec}: atlandı ({str(e)[:40]})", flush=True)

# Rapor
tot = sum(d["probes"] for d in results.values())
blk = sum(d["blocked"] for d in results.values())
print(f"\n[i] Toplam garak prompt: {tot} | Kalkan tarafından BLOKLANAN: {blk} ({100*blk/tot:.1f}%)")

L=[]
def w(s=""): L.append(s)
w("# garak Çapraz Doğrulama — NeuralShield-v5 vs NVIDIA garak Probe'ları")
w()
w(f"**garak sürümü:** {__import__('garak').__version__}")
w(f"**Yöntem:** garak'ın `{len(specs)}` probe sınıfından toplanan **{tot} saldırı promptu**, NeuralShield-v5")
w("kalkanından (L0 normalizer + L1 regex + L2 XLM-RoBERTa ONNX, OR-Gate) geçirildi.")
w()
w(f"## SONUÇ: garak saldırılarının **%{100*blk/tot:.1f}**'i kalkan tarafından BLOKLANDI ({blk}/{tot})")
w()
w("| garak Probe Ailesi | Prompt (n) | Bloklanan | Blok % |")
w("|---|---:|---:|---:|")
for fam, d in sorted(results.items(), key=lambda kv: -kv[1]["probes"]):
    w(f"| {fam} | {d['probes']} | {d['blocked']} | %{100*d['blocked']/d['probes']:.1f} |")
w()
w(f"**GENEL: {blk}/{tot} (%{100*blk/tot:.1f})**")
w()
w("_Not: Bu, standart bir LLM zafiyet tarayıcısına (NVIDIA garak) karşı çapraz doğrulamadır._")

(ROOT/'docs'/'GARAK_CROSSCHECK.md').write_text("\n".join(L), encoding='utf-8')
json.dump({"total":tot,"blocked":blk,"rate_pct":round(100*blk/tot,2),"by_family":results},
          open(ROOT/'data'/'garak_crosscheck_results.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print("\n".join(L))
print("\n[OK] -> docs/GARAK_CROSSCHECK.md")
