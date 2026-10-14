"""AppSec benchmark'i tam 2.000'e (1000/1000, 12 dil 50/50) kilitle."""
import os, sys, re, json, time, unicodedata
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from collections import Counter, defaultdict
sys.path.insert(0, r'C:\Users\Mustafa\OneDrive\Masaüstü\Akademik_yayın\backend')
ROOT = Path(r'C:\Users\Mustafa\OneDrive\Masaüstü\Akademik_yayın'); DATA = ROOT/"data"
TARGET = {"en":500,"tr":500, **{l:100 for l in ["ja","ko","ar","ru","de","fr","es","it","zh","pt"]}}
LANG_NAME={"zh":"Chinese","ja":"Japanese","ko":"Korean","ar":"Arabic","ru":"Russian","de":"German",
           "fr":"French","es":"Spanish","it":"Italian","pt":"Portuguese","tr":"Turkish"}
norm=lambda s: re.sub(r"\s+"," ",unicodedata.normalize("NFKC",s).lower().strip())
JUNK=re.compile(r"(\{[^}]*\}|\\033\[|📊|🧪|print\(|Raporu|\bHATA\])")

d=json.load(open(DATA/"appsec_benchmark_2000.json",encoding="utf-8"))
pool=json.load(open(DATA/"_appsec_pool_benign.json",encoding="utf-8"))
used=set(norm(x["text"]) for x in d)
clean=[r for r in pool if not r["source"].startswith("Local/legacy_handcrafted")
       and not JUNK.search(r["text"]) and 15<=len(r["text"])<=1200
       and norm(r["text"]) not in used and not re.fullmatch(r"[\w./:@\-]+",r["text"])]

from evren_client import EvrenClient
c=EvrenClient()
by=defaultdict(lambda:[0,0])
for r in d: by[r["language"]][r["label"]]+=1
add=[]; ci=0
for lang,tot in TARGET.items():
    need=tot//2 - by[lang][0]
    if need<=0: continue
    picks=[]
    for r in clean[ci:]:
        if len(picks)>=need: break
        t=r["text"]
        if lang!="en":
            rr=c.generate_chat(f"Translate into {LANG_NAME[lang]}. Output only the translation:\n\n{t}",
                               model="gemma-4-31b",max_tokens=2500,temperature=0.0)
            t=(rr.get("content") or "").strip()
        if t and len(t)>=10 and not JUNK.search(t):
            picks.append(dict(text=t,label=0,language=lang,source=r["source"]+f"[MT->{lang}]",
                              attack_family="technical_it_support",difficulty="level_1_direct"))
        ci+=1
    add+=picks
    print(f"  {lang}: +{len(picks)} (gereken {need})")
d+=add

# kilitle: 12 dil 50/50, tam 2000
final=[]
import random; random.seed(7)
for lang,tot in TARGET.items():
    half=tot//2
    a=[r for r in d if r["language"]==lang and r["label"]==1][:half]
    b=[r for r in d if r["language"]==lang and r["label"]==0][:half]
    final+=a+b
random.shuffle(final)
seen=set(); f2=[]
for r in final:
    k=norm(r["text"])
    if k in seen: continue
    seen.add(k); f2.append(r)
final=f2
for i,r in enumerate(final,1):
    r["id"]=f"APPSEC_{i:04d}"; r.setdefault("difficulty","level_2_framing_persona" if r["label"]==1 else "level_1_direct")

json.dump(final,open(DATA/"appsec_benchmark_2000.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
import csv
with open(DATA/"appsec_benchmark_2000.csv","w",newline="",encoding="utf-8") as fh:
    w=csv.DictWriter(fh,fieldnames=["id","text","label","language","source","attack_family","difficulty"]); w.writeheader()
    for r in final: w.writerow({k:r.get(k,"") for k in w.fieldnames})
meta={"dataset_name":"NeuralShield-v5 AppSec Independent Benchmark","version":"3.2.0-appsec",
      "total_samples":len(final),"classes":dict(Counter("Attack" if r["label"]==1 else "Benign" for r in final)),
      "language_breakdown":dict(Counter(r["language"] for r in final)),
      "note":"AppSec/prompt-injection kapsamı. Ethics kapsam dışı. legacy çöp temiz. v5 eğitimle sıfır örtüşme. MT [MT->xx]."}
json.dump(meta,open(DATA/"appsec_benchmark_2000_metadata.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
json.dump(final,open(DATA/"benchmark_master_2000.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
with open(DATA/"benchmark_master_2000.csv","w",newline="",encoding="utf-8") as fh:
    w=csv.DictWriter(fh,fieldnames=["id","text","label","language","source","attack_family","difficulty"]); w.writeheader()
    for r in final: w.writerow({k:r.get(k,"") for k in w.fieldnames})

print(f"\n=== FINAL N={len(final)} | {meta['classes']} ===")
for lg in TARGET:
    a=sum(1 for x in final if x['language']==lg and x['label']==1)
    b=sum(1 for x in final if x['language']==lg and x['label']==0)
    print(f"  {lg}: atk={a} ben={b}")
# overflow kontrol
short=[lg for lg in TARGET if sum(1 for x in final if x['language']==lg) < TARGET[lg]]
print("eksik dil:", short if short else "YOK (tam 2000)")
