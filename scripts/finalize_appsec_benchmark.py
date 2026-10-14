import os, sys, json, re, unicodedata
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\Mustafa\OneDrive\Masaüstü\Akademik_yayın\backend')
os.chdir(r'C:\Users\Mustafa\OneDrive\Masaüstü\Akademik_yayın')
from pathlib import Path
from collections import Counter
DATA = Path('data')
d = json.load(open(DATA/'appsec_benchmark_2000.json', encoding='utf-8'))

# Eksik 1 TR saldırıyı tamamla: kullanılmayan bir EN saldırıyı TR'ye çevir
norm = lambda s: re.sub(r'\s+',' ', unicodedata.normalize('NFKC', s).lower().strip())
existing = set(norm(x['text']) for x in d)
tr_attacks = [x for x in d if x['language']=='tr' and x['label']==1]
en_attacks = [x for x in d if x['language']=='en' and x['label']==1]
if len(tr_attacks) < 250:
    from evren_client import EvrenClient
    c = EvrenClient()
    src = en_attacks[0]['text']
    r = c.generate_chat(f"Translate into Turkish. Output ONLY the translation:\n\n{src}",
                        model='gemma-4-31b', max_tokens=2500, temperature=0.0)
    tr = (r.get('content') or '').strip()
    if tr and norm(tr) not in existing:
        new = dict(en_attacks[0]); new['text']=tr; new['language']='tr'; new['source']+='[MT->tr]'
        d.append(new); print("TR saldırı eklendi:", tr[:70])

# yeniden numarala
import random; random.seed(42); random.shuffle(d)
for i,x in enumerate(d,1): x['id']=f"APPSEC_{i:04d}"
json.dump(d, open(DATA/'appsec_benchmark_2000.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)

# ── FINAL AUDIT ──────────────────────────────────────────────────────────────
print("\n===== FINAL AUDIT =====")
print("N =", len(d), "| classes:", dict(Counter(x['label'] for x in d)))
print("lang:", dict(Counter(x['language'] for x in d)))
# ethics / artifact / dup kontrol
ETH = re.compile(r"(suicide|genocide|soykırım|organ mafya|racial slur|ırkçı|rape|tecavüz|heroin|"
                 r"fentanyl|bomb making|biyolojik silah|ricin|sarin|chemical weapon|kimyasal silah)", re.I)
ART = re.compile(r"(cannot be translated|çevrilemez|翻訳できません|번역할 수 없습니다|no puedo traducir|"
                 r"ne peut pas être traduit|нельзя перевести|as an ai|i cannot help)", re.I)
eth = [x for x in d if ETH.search(x['text'])]
art = [x for x in d if ART.search(x['text'])]
norms = [norm(x['text']) for x in d]
dups = [t for t,c in Counter(norms).items() if c>1]
print("ethics kalıntı:", len(eth), "| çeviri-artığı:", len(art), "| tekrar:", len(dups))
# contamination kontrol (redteam + train)
import csv
cont = set()
for f in ['redteam/redteam_corpus.json','redteam/external_attacks.json']:
    if (DATA/f).exists():
        for x in json.load(open(DATA/f,encoding='utf-8')):
            for k in ('text','prompt','user_message','payload_instruction'):
                if isinstance(x,dict) and x.get(k): cont.add(norm(x[k]))
for f in ['train_multilingual.csv','val_multilingual.csv']:
    if (DATA/f).exists():
        with open(DATA/f,encoding='utf-8') as fh:
            for row in csv.DictReader(fh):
                if row.get('text'): cont.add(norm(row['text']))
ov = [x for x in d if norm(x['text']) in cont]
print("v5 eğitim/redteam örtüşmesi:", len(ov))
# 50/50 per language
print("\nDil başına 50/50:")
for lg in ['en','tr','ja','ko','ar','ru','de','fr','es','it','zh','pt']:
    a=sum(1 for x in d if x['language']==lg and x['label']==1)
    b=sum(1 for x in d if x['language']==lg and x['label']==0)
    print(f"  {lg}: atk={a} ben={b}")
