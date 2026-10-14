"""en kovasındaki yabancı-script (CJK/Kiril) örnekleri temiz İngilizce meşrulardan gelenlerle değiştir."""
import json, re, sys, unicodedata, csv
sys.stdout.reconfigure(encoding='utf-8')
from collections import Counter
from pathlib import Path
ROOT=Path(r'C:\Users\Mustafa\OneDrive\Masaüstü\Akademik_yayın'); DATA=ROOT/'data'
norm=lambda s: re.sub(r'\s+',' ',unicodedata.normalize('NFKC',s).lower().strip())
NONLAT=re.compile(r'[\u0400-\u04FF\u3040-\u30FF\u4E00-\u9FFF\uAC00-\uD7A3\u0600-\u06FF]')
JUNK=re.compile(r"(\{[^}]*\}|\\033\[|📊|🧪|print\(|Raporu|\bHATA\])")

d=json.load(open(DATA/'appsec_benchmark_2000.json',encoding='utf-8'))
bad=[x for x in d if x['language']=='en' and NONLAT.search(x['text'])]
print("değiştirilecek yabancı örnek:",len(bad))

pool=json.load(open(DATA/'_appsec_pool_benign.json',encoding='utf-8'))
used=set(norm(x['text']) for x in d)
cand=[r for r in pool if r['label']==0 and not NONLAT.search(r['text'])
      and not r['source'].startswith('Local/legacy_handcrafted')
      and not JUNK.search(r['text']) and 15<=len(r['text'])<=400
      and not re.fullmatch(r'[\w./:@\-]+',r['text']) and norm(r['text']) not in used]

# en kovasindan yabancilari cikar, yerine temiz ingilizce koy
keep=[x for x in d if not (x['language']=='en' and NONLAT.search(x['text']))]
need=len(bad)
adds=[]
for r in cand:
    if len(adds)>=need: break
    adds.append(dict(text=r['text'],label=0,language='en',source=r['source']+'[en-clean]',
                     attack_family='technical_it_support',difficulty='level_1_direct'))
keep+=adds
print(f"  +{len(adds)} temiz İngilizce benign eklendi")

# kilitle: 12 dil 50/50 tam 2000
TARGET={"en":500,"tr":500,**{l:100 for l in ["ja","ko","ar","ru","de","fr","es","it","zh","pt"]}}
import random; random.seed(11)
final=[]
for lg,tot in TARGET.items():
    half=tot//2
    final+= [x for x in keep if x['language']==lg and x['label']==1][:half]
    final+= [x for x in keep if x['language']==lg and x['label']==0][:half]
random.shuffle(final)
seen=set(); f2=[]
for x in final:
    k=norm(x['text'])
    if k in seen: continue
    seen.add(k); f2.append(x)
final=f2
for i,x in enumerate(final,1):
    x['id']=f"APPSEC_{i:04d}"; x.setdefault('difficulty','level_2_framing_persona' if x['label']==1 else 'level_1_direct')

for fn in ['appsec_benchmark_2000.json','benchmark_master_2000.json']:
    json.dump(final,open(DATA/fn,'w',encoding='utf-8'),ensure_ascii=False,indent=1)
for fn in ['appsec_benchmark_2000.csv','benchmark_master_2000.csv']:
    with open(DATA/fn,'w',newline='',encoding='utf-8') as fh:
        w=csv.DictWriter(fh,fieldnames=['id','text','label','language','source','attack_family','difficulty']); w.writeheader()
        for x in final: w.writerow({k:x.get(k,'') for k in w.fieldnames})

# dogrulama
print("\nN =",len(final),"| classes:",dict(Counter(x['label'] for x in final)))
print("en yabanci kalan:",sum(1 for x in final if x['language']=='en' and NONLAT.search(x['text'])))
print("tekrar:",sum(1 for v in Counter(norm(x['text']) for x in final).values() if v>1))
for lg in TARGET:
    a=sum(1 for x in final if x['language']==lg and x['label']==1); b=sum(1 for x in final if x['language']==lg and x['label']==0)
    print(f"  {lg}: {a}/{b}")
