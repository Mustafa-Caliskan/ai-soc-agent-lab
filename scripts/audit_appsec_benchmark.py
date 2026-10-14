import json, csv, re, sys, unicodedata
sys.stdout.reconfigure(encoding='utf-8')
from collections import Counter, defaultdict
ROOT=r'C:\Users\Mustafa\OneDrive\Masaüstü\Akademik_yayın'
DATA=ROOT+r'\data'
d=json.load(open(DATA+r'\appsec_benchmark_2000.json',encoding='utf-8'))
norm=lambda s: re.sub(r'\s+',' ',unicodedata.normalize('NFKC',s).lower().strip())
print("N =",len(d),"| classes:",dict(Counter(x['label'] for x in d)))
print("lang:",dict(Counter(x['language'] for x in d)))

JUNK=re.compile(r"(\{[^}]*\}|\\033\[|📊|🧪|TEBRİK|SKOR:|print\(|Raporu|\bHATA\])")
ETH=re.compile(r"(suicide|genocide|soykırım|organ mafya|racial slur|ırkçı|rape|tecavüz|heroin|fentanyl|bomb making|kimyasal silah|biyolojik silah)",re.I)
ART=re.compile(r"(cannot be translated|çevrilemez|翻訳できません|번역할 수 없습니다|no puedo traducir|нельзя перевести|as an ai)",re.I)
PT_ES=re.compile(r"[¿¡]")
print("\n-- KALİTE --")
print("junk/print/log:",sum(1 for x in d if JUNK.search(x['text'])))
print("ethics kalıntı:",sum(1 for x in d if ETH.search(x['text'])))
print("çeviri-artığı:",sum(1 for x in d if ART.search(x['text'])))
print("pt'de İspanyolca ¿/¡:",sum(1 for x in d if x['language']=='pt' and PT_ES.search(x['text'])))
c=Counter(norm(x['text']) for x in d); print("tekrar metin:",sum(1 for v in c.values() if v>1))

# contamination
cont=set()
for f in ['redteam/redteam_corpus.json','redteam/external_attacks.json']:
    try:
        for x in json.load(open(DATA+'/'+f,encoding='utf-8')):
            for k in ('text','prompt','user_message','payload_instruction'):
                if isinstance(x,dict) and x.get(k): cont.add(norm(x[k]))
    except: pass
for f in ['train_multilingual.csv','val_multilingual.csv']:
    try:
        for row in csv.DictReader(open(DATA+'/'+f,encoding='utf-8')):
            if row.get('text'): cont.add(norm(row['text']))
    except: pass
print("v5 eğitim/redteam örtüşmesi:",sum(1 for x in d if norm(x['text']) in cont))
print("\n-- PER-DIL 50/50 --")
ok=True
for lg in ['en','tr','ja','ko','ar','ru','de','fr','es','it','zh','pt']:
    a=sum(1 for x in d if x['language']==lg and x['label']==1); b=sum(1 for x in d if x['language']==lg and x['label']==0)
    flag='' if a==b else '  <-- DENGESIZ'; ok=ok and (a==b)
    print(f"  {lg}: {a}/{b}{flag}")
print("\nAttack kaynak dagilimi:",dict(Counter(x['source'].split('[')[0] for x in d if x['label']==1).most_common(12)))
print("Benign kaynak dagilimi:",dict(Counter(x['source'].split('[')[0] for x in d if x['label']==0).most_common(12)))
print("\nSONUC:", "TEMIZ & DENGELI ✅" if ok else "SORUN VAR")
