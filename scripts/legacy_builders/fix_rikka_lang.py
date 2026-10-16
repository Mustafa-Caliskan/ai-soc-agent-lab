"""rikka-snow kaynaklı yanlış-dil (en bucket FR/PT) kayıtlarını temizle + dengeyi koru."""
import json, sys, re, unicodedata
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from collections import Counter
ROOT = Path(r'C:\Users\Mustafa\OneDrive\Masaüstü\Akademik_yayın'); DATA = ROOT/'data'
norm = lambda s: re.sub(r'\s+',' ', unicodedata.normalize('NFKC', s or '').lower().strip())
TARGET = {"en":500,"tr":500, **{l:100 for l in ["ja","ko","ar","ru","de","fr","es","it","zh","pt"]}}

d = json.load(open(DATA/'appsec_benchmark_2000_curated.json', encoding='utf-8'))
# en bucket rikka-snow yanlış dil tespiti (İngilizce stopword yok + PT/FR var)
EN = re.compile(r'\b(the|is|are|you|your|ignore|above|previous|instructions|and|to|of|with|what)\b', re.I)
bad = [x for x in d if x['language']=='en' and 'rikka-snow' in x['source'] and not EN.search(x['text'])]
print("çıkarılacak yanlış-dil (en/rikka-snow):", len(bad))
for x in bad: print("   ", repr(x['text'][:70]))

keep = [x for x in d if x not in bad]

# eksik en attack'ları temiz havuzdan doldur
pool = json.load(open(DATA/'_appsec_pool_attacks.json', encoding='utf-8'))
used = set(norm(x['text']) for x in keep)
INJ = re.compile(r"(ignore|disregard|override|system prompt|developer mode|do anything now|\bDAN\b|"
                 r"act as|you are now|reveal|expose|print (your|the)|instructions|previous|jailbreak|"
                 r"base64|secret|password|api[_ ]?key|credential|admin)", re.I)
need = 250 - sum(1 for x in keep if x['language']=='en' and x['label']==1)
cand=[r for r in pool if r['label']==1 and r['language']=='en' and INJ.search(r['text'])
      and norm(r['text']) not in used and not re.search(r'[\u0400-\u04FF\u0600-\u06FF\u4E00-\u9FFF\u3040-\u30FF\uAC00-\uD7A3]', r['text'])
      and 'rikka-snow' not in r['source']]
adds=[]
for r in cand:
    if len(adds)>=need: break
    adds.append(dict(text=r['text'], label=1, language='en', source=r['source']+'[lang-fix]',
                     attack_family='direct_injection', difficulty='level_2_framing_persona'))
keep += adds
print(f"+{len(adds)} temiz İngilizce saldırı eklendi (gereken {need})")

# kilitle
import random; random.seed(21)
final=[]
for lg,tot in TARGET.items():
    half=tot//2
    final += [x for x in keep if x['language']==lg and x['label']==1][:half]
    final += [x for x in keep if x['language']==lg and x['label']==0][:half]
random.shuffle(final)
seen=set(); f2=[]
for x in final:
    k=norm(x['text'])
    if k in seen: continue
    seen.add(k); f2.append(x)
final=f2
for i,x in enumerate(final,1):
    x['id']=f"APPSEC_{i:04d}"; x.setdefault('difficulty','level_2_framing_persona' if x['label']==1 else 'level_1_direct')
json.dump(final, open(DATA/'appsec_benchmark_2000_curated.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)

print(f"\nN={len(final)} | {dict(Counter(x['label'] for x in final))}")
# kalan yanlış dil kontrolü
bad2=[x for x in final if x['language']=='en' and 'rikka-snow' in x['source'] and not EN.search(x['text'])]
print("kalan yanlış-dil (en/rikka-snow):", len(bad2))
for lg in TARGET:
    a=sum(1 for x in final if x['language']==lg and x['label']==1); b=sum(1 for x in final if x['language']==lg and x['label']==0)
    print(f"  {lg}: {a}/{b}", "" if a==b else "<-- DENGESIZ")
