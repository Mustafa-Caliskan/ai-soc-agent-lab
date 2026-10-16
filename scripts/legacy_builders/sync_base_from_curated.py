"""curated (düzeltilmiş) içerikten base benchmark'ı yeniden üret + master'a kopyala."""
import json, sys, csv
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
ROOT = Path(r'C:\Users\Mustafa\OneDrive\Masaüstü\Akademik_yayın'); DATA = ROOT/'data'
cur = json.load(open(DATA/'appsec_benchmark_2000_curated.json', encoding='utf-8'))
FIELDS = ["id","text","label","language","source","attack_family","difficulty"]
base = [{k:x.get(k,"") for k in FIELDS} for x in cur]
for fn in ['appsec_benchmark_2000.json','benchmark_master_2000.json']:
    json.dump(base, open(DATA/fn,'w',encoding='utf-8'), ensure_ascii=False, indent=1)
for fn in ['appsec_benchmark_2000.csv','benchmark_master_2000.csv']:
    with open(DATA/fn,'w',newline='',encoding='utf-8') as fh:
        w=csv.DictWriter(fh, fieldnames=FIELDS); w.writeheader()
        for x in base: w.writerow(x)
print("base + master güncellendi. N=", len(base))
from collections import Counter
print("lang:", dict(Counter(x['language'] for x in base)), "| label:", dict(Counter(x['label'] for x in base)))
