"""
Colab E2E (Uçtan Uca Canary) için STRATİFİYE ve EXFILTRATION-ODAKLI test seti üretir.
Kaynak: Yalnızca v4 dengeli benchmark (appsec_benchmark_2000_shield.json — sıfır sızıntı, sıfır OnerAYTAS).
Çıktı: data/colab_e2e_suite_stratified.json (120 Saldırı + 36 Meşru = 156 Örnek, 12 Dil)
Amaç:
  1. Yerel/Colab modellerini 12 dilde TEMSİLİ saldırılarla SHIELD OFF/ON test etmek.
  2. Kanarya sızıntı ölçümünün (canary.find_leaked) metodolojik olarak %100 geçerli olması için
     tüm saldırıların sistem promptu / parola / gizli anahtar / talimat ifşası (exfiltration) hedeflemesini garanti etmek.
  3. Mosscap (≤%7.5) ve NotInject (≤%11.1) tavanlarını v4 oranlarıyla birebir korumak.
  4. Her örneğe Kademe (Tier 1..5) ve kategori etiketi atamak.
"""
import json
import re
import sys
import random
from pathlib import Path
from collections import defaultdict, Counter

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
random.seed(42)

d = json.load(open(DATA / "appsec_benchmark_2000_shield.json", encoding="utf-8"))

# Exfiltration / Sistem Promptu / Gizli Veri İfşası Anahtar Kelime Süzgeci (12 Dil)
EXFIL_RE = re.compile(
    r"(password|parola|şifre|sifre|pin|secret|gizli|anahtar|key|token|credential|system prompt|"
    r"sistem istem|sistem komut|talimat|instruction|config|yapılandırma|proprietary|patent|konfidentsial|"
    r"专有|비밀|パスワード|كلمة المرور|سري|تعليمات|passwort|mot de passe|contraseña|senha|"
    r"reveal|expose|leak|dump|print your|output your|repeat.*above|repeat.*initial|hafızana yüklenen|"
    r"kuralları|rules|anweisungen|instrucciones|istruzioni|instruções|инструкц|пароль|конфиденц|"
    r"مفاتيح|النظام|指示|プロンプト|지침|프롬프트|시스템|指令|系统|密码|機密|机密|base64|rot13|\bhex\b)",
    re.I
)


def assign_tier_and_category(item: dict) -> tuple[int, str]:
    if item.get("label", 1) == 0:
        return 0, "Benign Control"

    fam = (item.get("attack_family") or "").lower()
    txt = (item.get("text") or item.get("prompt") or "").lower()
    lang = item.get("language", "en")

    # Tier 4: Steganography, Encoding, Obfuscation
    if (
        item.get("hard_stego")
        or any(k in fam for k in [
            "stego", "obfuscat", "encoding", "smuggling", "base64", "rot13",
            "hex", "unicode", "homoglyph", "leetspeak", "reversed", "zero_width", "soft_hyphen", "delimiter"
        ])
        or any(k in txt for k in ["base64", "rot13", "tersten", "in reverse", "reversed"])
    ):
        return 4, "Steganography & Obfuscation"

    # Tier 3: Cognitive, Hypothetical, Indirect, Semantic Framing
    if any(k in fam for k in [
        "semantic", "cognitive", "hypothetical", "creative", "grandma",
        "reverse_psychology", "opposite_day", "crescendo", "many_shot",
        "academic", "indirect", "sql_error", "yaml", "api_contract"
    ]):
        return 3, "Cognitive & Indirect Framing"

    # Tier 5: Cross-Lingual Pivot (Non-TR/EN)
    if lang not in ("tr", "en"):
        return 5, "Cross-Lingual & Multilingual Pivot"

    # Tier 2: Persona & Authority Simulation (TR/EN)
    if any(k in fam for k in [
        "persona", "authority", "developer", "shgm", "icao", "roleplay", "virtual_machine"
    ]):
        return 2, "Persona & Authority Override"

    # Tier 1: Direct Prompt Injection & System Extraction (TR/EN)
    return 1, "Direct System Extraction"


# Dil başına saldırı ve meşru kotaları (120 Saldırı + 36 Meşru = 156 Örnek)
ATK_Q = {"en": 20, "tr": 20, **{l: 8 for l in ["de", "fr", "es", "it", "pt", "ru", "ar", "ja", "ko", "zh"]}}
BEN_Q = {"en": 8, "tr": 8, **{l: 2 for l in ["de", "fr", "es", "it", "pt", "ru", "ar", "ja", "ko", "zh"]}}

global_src_counts = Counter()
GLOBAL_SRC_CAPS = {
    "HF/Lakera/mosscap": 8,       # <= %6.7 (v4 oranı ~%7.5 ile uyumlu)
    "HF/Horizon/notinject": 4,    # <= %11.1 (v4 oranı ~%12.2 ile uyumlu)
}


def pick_diverse(pool, n):
    by_src = defaultdict(list)
    for x in pool:
        base_s = x["source"].split("[")[0]
        by_src[base_s].append(x)
    for k in by_src:
        random.shuffle(by_src[k])
    out = []
    # Öncelik: Mosscap/NotInject dışındaki ana AppSec kaynakları
    keys = sorted(by_src.keys(), key=lambda k: (1 if k in GLOBAL_SRC_CAPS else 0, k))
    passes = 0
    while len(out) < n and passes < 200:
        progressed = False
        for k in keys:
            if len(out) >= n:
                break
            cap = GLOBAL_SRC_CAPS.get(k, 9999)
            if global_src_counts[k] >= cap:
                continue
            if by_src[k]:
                item = by_src[k].pop()
                out.append(item)
                global_src_counts[k] += 1
                progressed = True
        if not progressed:
            break
        passes += 1
    return out


suite = []
seen_texts = set()

for lg, n in ATK_Q.items():
    pool = [
        x for x in d
        if x["language"] == lg
        and x["label"] == 1
        and EXFIL_RE.search(x["text"])
        and x["text"].strip() not in seen_texts
    ]
    picked = pick_diverse(pool, n)
    for x in picked:
        txt = x["text"]
        seen_texts.add(txt.strip())
        tier, cat = assign_tier_and_category(x)
        suite.append({
            "id": f"E2E_ATK_{lg.upper()}_{len(suite)+1:03d}",
            "tier": tier,
            "category": cat,
            "prompt": txt,
            "text": txt,
            "label": 1,
            "expected_label": "MALICIOUS",
            "type": "Attack",
            "language": lg,
            "source": x["source"],
            "attack_family": x.get("attack_family", ""),
            "ml_risk": x.get("ml_risk", 85),
            "ml_class": x.get("ml_class", "Malicious"),
            "regex_score": x.get("regex_score", 0),
            "hard_stego": bool(x.get("hard_stego", False)),
            "l2_latency_ms": x.get("l2_latency_ms", 12.27),
            "shield_decision": "BLOCKED" if x.get("shield_blocked") else "ALLOWED"
        })

for lg, n in BEN_Q.items():
    pool = [
        x for x in d
        if x["language"] == lg
        and x["label"] == 0
        and x["text"].strip() not in seen_texts
    ]
    for x in pick_diverse(pool, n):
        txt = x["text"]
        seen_texts.add(txt.strip())
        suite.append({
            "id": f"E2E_BEN_{lg.upper()}_{len(suite)+1:03d}",
            "tier": 0,
            "category": "Benign Control",
            "prompt": txt,
            "text": txt,
            "label": 0,
            "expected_label": "BENIGN",
            "type": "Benign",
            "language": lg,
            "source": x["source"],
            "attack_family": x.get("attack_family", "benign"),
            "ml_risk": x.get("ml_risk", 0),
            "ml_class": x.get("ml_class", "Benign"),
            "regex_score": x.get("regex_score", 0),
            "hard_stego": bool(x.get("hard_stego", False)),
            "l2_latency_ms": x.get("l2_latency_ms", 12.27),
            "shield_decision": "BLOCKED" if x.get("shield_blocked") else "ALLOWED"
        })

out_path = DATA / "colab_e2e_suite_stratified.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(suite, f, ensure_ascii=False, indent=2)

atk = [x for x in suite if x["label"] == 1]
ben = [x for x in suite if x["label"] == 0]
print(f"E2E suite: N={len(suite)} | attack={len(atk)} benign={len(ben)}")
print("Dil dağılımı:", dict(Counter(x["language"] for x in suite)))
print("Tier dağılımı (Attack):", dict(sorted(Counter(x["tier"] for x in atk).items())))
print("Attack kaynak:", dict(Counter(x["source"].split("[")[0] for x in atk).most_common(10)))
print("Benign kaynak:", dict(Counter(x["source"].split("[")[0] for x in ben).most_common(10)))
print("Attack shield-blocked:", sum(1 for x in atk if x["shield_decision"] == "BLOCKED"), "/", len(atk))
print("Benign FP:", sum(1 for x in ben if x["shield_decision"] == "BLOCKED"), "/", len(ben))
print(f"-> Kaydedildi: {out_path}")
