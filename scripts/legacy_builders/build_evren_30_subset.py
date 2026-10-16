"""Bağımsız 2000-setinden stratifiye 30 saldırı alt-kümesi (EVREN runner şeması)."""
import json, sys, random
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from collections import defaultdict, Counter
ROOT = Path(r'C:\Users\Mustafa\OneDrive\Masaüstü\Akademik_yayın'); DATA = ROOT/'data'
random.seed(7)
d = json.load(open(DATA/'appsec_benchmark_2000.json', encoding='utf-8'))
atk = [x for x in d if x['label']==1]
by = defaultdict(list)
for x in atk: by[x['language']].append(x)

quota = {"en":5,"tr":5}
for lg in ["de","fr","es","it","pt","ru","ar","ja","ko","zh"]: quota[lg]=2

sel=[]
for lg,n in quota.items():
    items = by.get(lg, [])
    random.shuffle(items)
    sel += items[:n]
print("seçilen:", len(sel), dict(Counter(x['language'] for x in sel)))

out=[]
for i,x in enumerate(sel,1):
    out.append({"id": f"INDEP_{i:02d}", "tier": 2, "category": x.get('attack_family',''),
                "attack_family": x.get('attack_family',''), "language": x['language'],
                "source": x['source'], "type": "attack", "label": 1,
                "expected_label": "MALICIOUS", "prompt": x['text']})
json.dump(out, open(DATA/'evren_benchmark_30_independent.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print("-> data/evren_benchmark_30_independent.json yazıldı")
