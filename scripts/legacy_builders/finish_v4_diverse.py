"""data/appsec_benchmark_v2_diverse.json içindeki kalan cümleleri yerel havuzlardan %100 hedef dilde tamamlar."""
import json, re, sys
from pathlib import Path
from collections import Counter

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

d = json.load(open(DATA / "appsec_benchmark_v2_diverse.json", encoding="utf-8"))
p_old = json.load(open(DATA / "appsec_benchmark_2000_purged.json", encoding="utf-8"))
pool_atk = json.load(open(DATA / "_appsec_pool_attacks.json", encoding="utf-8"))

# 1) TR benign 249 -> 250 tamamla
if len(d) == 1999:
    used = {x["text"] for x in d}
    tr_add = [x for x in p_old if x["language"] == "tr" and x["label"] == 0 and x["text"] not in used][0]
    d.append({
        "text": tr_add["text"], "label": 0, "language": "tr",
        "source": tr_add["source"], "attack_family": tr_add.get("attack_family", "technical_it_support"),
        "difficulty": tr_add.get("difficulty", "level_1_direct"), "id": "APPSEC_2000"
    })

used = {x["text"] for x in d}

# Portekizce doğal rikka-snow havuzu
has_cjk = lambda s: bool(re.search(r"[\u3040-\u30FF\u4E00-\u9FFF\uAC00-\uD7A3]", s))
pure_pt = lambda s: not has_cjk(s) and bool(re.search(r"\b(não|uma|para|com|todas|você|como|mais|são|dos|das|pelo)\b", s, re.I)) and bool(re.search(r"[ãõçê]", s, re.I)) and not bool(re.search(r"\b(the|and|your|previous|instructions)\b", s, re.I))
pt_rikka_atk = [
    dict(r, language="pt", source="HF/rikka-snow/multilingual[native-pt]")
    for r in pool_atk if "rikka-snow" in r["source"] and pure_pt(r["text"]) and r["text"] not in used
]

def is_wrong_script(lg, t):
    if lg == "ru": return not bool(re.search(r"[\u0400-\u04FF]", t))
    if lg == "ar": return not bool(re.search(r"[\u0600-\u06FF]", t))
    if lg == "ko": return not bool(re.search(r"[\uAC00-\uD7A3]", t))
    if lg == "pt": return bool(re.search(r"\b(the|and|your|ignore|previous|instructions)\b", t, re.I))
    return False

for idx, x in enumerate(d):
    lg = x["language"]
    if lg in ("ru", "ar", "ko", "pt") and is_wrong_script(lg, x["text"]):
        if lg == "pt" and x["label"] == 1 and pt_rikka_atk:
            chosen = pt_rikka_atk.pop(0)
        else:
            # Önce mosscap/notinject olmayanları tercih et, sonra ayrık dilimden al
            cands_pref = [r for r in p_old if r["language"] == lg and r["label"] == x["label"] and r["text"] not in used and not is_wrong_script(lg, r["text"]) and "mosscap" not in r["source"].lower() and "notinject" not in r["source"].lower() and "orbench" not in r["source"].lower()]
            cands_any = [r for r in p_old if r["language"] == lg and r["label"] == x["label"] and r["text"] not in used and not is_wrong_script(lg, r["text"]) and "orbench" not in r["source"].lower()]
            cands = cands_pref or cands_any
            chosen = cands[0] if cands else None
        if chosen:
            used.add(chosen["text"])
            d[idx]["text"] = chosen["text"]
            d[idx]["source"] = chosen["source"]
            d[idx]["attack_family"] = chosen.get("attack_family", d[idx].get("attack_family", "direct_injection"))

for idx, x in enumerate(d, 1):
    x["id"] = f"APPSEC_{idx:04d}"

json.dump(d, open(DATA / "appsec_benchmark_v2_diverse.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"[OK] data/appsec_benchmark_v2_diverse.json kaydedildi! N={len(d)} | Etiket: {dict(Counter(x['label'] for x in d))}")
for lg in ["en", "tr", "de", "fr", "es", "it", "pt", "ru", "ar", "ja", "ko", "zh"]:
    cnt_a = sum(1 for x in d if x["language"] == lg and x["label"] == 1)
    cnt_b = sum(1 for x in d if x["language"] == lg and x["label"] == 0)
    bad = sum(1 for x in d if x["language"] == lg and is_wrong_script(lg, x["text"]))
    print(f"  {lg}: {cnt_a}/{cnt_b} (wrong_script={bad})")

base_src = lambda s: re.sub(r"\[.*?\]", "", s)
print("\nSaldırı kaynak dağılımı (N=1000):")
for k, v in Counter(base_src(r["source"]) for r in d if r["label"] == 1).most_common():
    print(f"  {k:38s}: {v:3d} (%{v/10:.1f})")

print("\nMeşru kaynak dağılımı (N=1000):")
for k, v in Counter(base_src(r["source"]) for r in d if r["label"] == 0).most_common():
    print(f"  {k:38s}: {v:3d} (%{v/10:.1f})")
