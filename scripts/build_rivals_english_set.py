"""
Rakip (guardrail) kıyaslaması için İNGİLİZCE-only adil test seti.
Kaynak: appsec_benchmark_2000_shield.json (EN attack + EN benign).
Çıktı: data/rivals_english_set.json
"""
import json, sys, re
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from collections import Counter
ROOT = Path(r'C:\Users\Mustafa\OneDrive\Masaüstü\Akademik_yayın'); DATA = ROOT/'data'
CONFIG = json.load(open(ROOT/'backend'/'shield_config.json', encoding='utf-8'))
ML_T=CONFIG.get('ml_block_threshold',70); RX_T=CONFIG.get('regex_block_score_threshold',60)

d = json.load(open(DATA/'appsec_benchmark_2000_shield.json', encoding='utf-8'))
en = [x for x in d if x['language']=='en']
out=[]
for x in en:
    blocked = bool(x.get('hard_stego') or x.get('regex_score',0)>=RX_T or x.get('ml_risk',0)>=ML_T)
    out.append({
        "id": x['id'], "text": x['text'], "label": x['label'],
        "expected_label": "MALICIOUS" if x['label']==1 else "BENIGN",
        "attack_family": x.get('attack_family',''),
        "source": x['source'],
        "ml_risk": x.get('ml_risk'), "regex_score": x.get('regex_score'),
        "hard_stego": x.get('hard_stego'),
        "neural_shield_blocked": blocked,   # bizim kalkanın kararı (adil kıyas için)
    })
json.dump(out, open(DATA/'rivals_english_set.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
atk=[x for x in out if x['label']==1]; ben=[x for x in out if x['label']==0]
print(f"EN set: N={len(out)} | attack={len(atk)} benign={len(ben)}")
print("attack family:", dict(Counter(x['attack_family'] for x in atk).most_common(8)))
print("NeuralShield blok (attack):", sum(1 for x in atk if x['neural_shield_blocked']), "/", len(atk))
print("NeuralShield FP (benign):", sum(1 for x in ben if x['neural_shield_blocked']), "/", len(ben))
print("-> data/rivals_english_set.json")
