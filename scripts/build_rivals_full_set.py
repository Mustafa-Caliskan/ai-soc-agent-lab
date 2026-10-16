"""Rakip kıyaslama için TAM set (2000, çok dilli) — neural_shield_blocked gömülü."""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
ROOT = Path(r'C:\Users\Mustafa\OneDrive\Masaüstü\Akademik_yayın'); DATA = ROOT/'data'
CONFIG = json.load(open(ROOT/'backend'/'shield_config.json', encoding='utf-8'))
ML_T=CONFIG.get('ml_block_threshold',70); RX_T=CONFIG.get('regex_block_score_threshold',60)
d = json.load(open(DATA/'appsec_benchmark_2000_shield.json', encoding='utf-8'))
out=[]
for x in d:
    blocked = bool(x.get('hard_stego') or x.get('regex_score',0)>=RX_T or x.get('ml_risk',0)>=ML_T)
    out.append({"id":x['id'],"text":x['text'],"label":x['label'],
                "expected_label":"MALICIOUS" if x['label']==1 else "BENIGN",
                "language":x['language'],"source":x['source'],"attack_family":x.get('attack_family',''),
                "ml_risk":x.get('ml_risk'),"regex_score":x.get('regex_score'),"hard_stego":x.get('hard_stego'),
                "neural_shield_blocked":blocked})
json.dump(out, open(DATA/'rivals_full_set.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
from collections import Counter
print("rivals_full_set: N=",len(out),"| lang:",dict(Counter(x['language'] for x in out)))
print("-> data/rivals_full_set.json")
