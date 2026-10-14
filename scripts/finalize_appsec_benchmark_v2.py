"""
NeuralShield-v5 AppSec Benchmark — FINALIZE v2
===============================================
Mevcut appsec_benchmark_2000.json'u temizler ve tam 2.000'e (1000/1000, 12 dil) kilitler.
- legacy_handcrafted (print/log/f-string çöpü) KALDIRILIR
- junk / ethics / çeviri-artığı / tekrar temizlenir
- Benign açığı temiz EN IT/DevOps + notinject havuzundan EVREN MT ile kapatılır
- Çıktı: appsec_benchmark_2000.{json,csv,_metadata.json} VE benchmark_master_2000.* (uyumluluk)
"""
import os, sys, re, json, time, threading, unicodedata
sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
from pathlib import Path
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, r'C:\Users\Mustafa\OneDrive\Masaüstü\Akademik_yayın\backend')

ROOT = Path(r'C:\Users\Mustafa\OneDrive\Masaüstü\Akademik_yayın')
DATA = ROOT / "data"
LANG_NAME = {"ja":"Japanese","ko":"Korean","ar":"Arabic","ru":"Russian","de":"German",
             "fr":"French","es":"Spanish","it":"Italian","zh":"Chinese","pt":"Portuguese",
             "tr":"Turkish"}
TARGET = {"en":500,"tr":500, **{l:100 for l in ["ja","ko","ar","ru","de","fr","es","it","zh","pt"]}}

JUNK = re.compile(r"(\{[^}]*\}|\\033\[|\\n[🎉📊🏆🚀💡🔴🔥]|📊|🧪|print\(|TEBRİK|CONGRAT|FÉLICIT|恭喜|"
                  r"保存|SKOR:|STRESS TEST|GENİŞ KAPSAMLI|\bHATA\]|Tahmin:.*Gerçek:|v\d+\s*\(Ultimate\)|"
                  r"Raporu|test report|kelime ezberi|debug log|traceback)", re.I)
ETHICS = re.compile(r"(suicide|genocide|soykırım|organ mafya|racial slur|ırkçı|rape|tecavüz|heroin|"
                    r"fentanyl|bomb making|biyolojik silah|ricin|sarin|chemical weapon|kimyasal silah)", re.I)
ARTIFACT = re.compile(r"(cannot be translated|çevrilemez|翻訳できません|번역할 수 없습니다|no puedo traducir|"
                      r"ne peut pas être traduit|нельзя перевести|as an ai|i cannot help|here is the translation)", re.I)
TRW = re.compile(r"\b(nas[ıi]l|nedir|merhaba|u[çc]u[şs]|bilet|talimat|y[öo]nerge|i[çc]in|gizli|unuttum|"
                 r"ucret|ücret|saatlik|otopark|[çğıöşüÇĞİÖŞÜ])\b")
norm = lambda s: re.sub(r"\s+"," ", unicodedata.normalize("NFKC", s).lower().strip())

def clean(records):
    out=[]
    for r in records:
        t=r["text"].strip()
        if r["source"].startswith("Local/legacy_handcrafted"):
            continue
        if JUNK.search(t) or ETHICS.search(t) or ARTIFACT.search(t):
            continue
        if len(t) < 15 or len(t) > 1200:
            continue
        # TR-in-EN düzelt
        if r["language"]=="en" and TRW.search(t) and len(re.findall(r"[a-zA-Z]", t)) < len(t)*0.5:
            r=dict(r); r["language"]="tr"
        out.append(r)
    # global dedup
    seen=set(); ded=[]
    for r in out:
        k=norm(r["text"])
        if k in seen: continue
        seen.add(k); ded.append(r)
    return ded

def translate_batch(texts, lang, workers=6):
    from evren_client import EvrenClient
    c=EvrenClient()
    if not c.is_configured: return [None]*len(texts)
    name=LANG_NAME[lang]; B=5
    batches=[(i,texts[i:i+B]) for i in range(0,len(texts),B)]
    res=[None]*len(texts)
    def do(item):
        start,chunk=item
        sysm=(f"You are a professional translator for a cybersecurity benchmark. Translate each user text "
              f"into {name}. Preserve technical meaning. Return ONLY a JSON array of {len(chunk)} strings, same order.")
        for _ in range(3):
            r=c.generate_chat(json.dumps(chunk,ensure_ascii=False), system_instruction=sysm,
                              model="gemma-4-31b", max_tokens=2500, temperature=0.0)
            ct=(r.get("content") or "").strip()
            m=re.search(r"\[.*\]", ct, re.DOTALL)
            if m:
                try:
                    arr=json.loads(m.group(0))
                    if isinstance(arr,list) and len(arr)==len(chunk): return start,[str(x) for x in arr]
                except Exception: pass
            time.sleep(1.0)
        singles=[]
        for t in chunk:
            rr=c.generate_chat(f"Translate into {name}. Output only the translation:\n\n{t}",
                               model="gemma-4-31b", max_tokens=2500, temperature=0.0)
            singles.append((rr.get("content") or "").strip() or None)
        return start,singles
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for f in as_completed([ex.submit(do,it) for it in batches]):
            s,arr=f.result()
            for j,v in enumerate(arr):
                if s+j<len(res): res[s+j]=v
    return res

def main():
    d = json.load(open(DATA/"appsec_benchmark_2000.json", encoding="utf-8"))
    print("once N=",len(d))
    d = clean(d)
    print("temizlik sonrasi N=",len(d), dict(Counter(x['language'] for x in d)))

    # temiz EN havuzlar (legacy hariç)
    pool_b = json.load(open(DATA/"_appsec_pool_benign.json", encoding="utf-8"))
    pool_a = json.load(open(DATA/"_appsec_pool_attacks.json", encoding="utf-8"))
    def ok(r):
        t=r["text"]
        return (not r["source"].startswith("Local/legacy_handcrafted")
                and not JUNK.search(t) and not ETHICS.search(t) and not ARTIFACT.search(t)
                and 15<=len(t)<=1200 and not re.fullmatch(r"[\w./:@\-]+", t))
    used = set(norm(x["text"]) for x in d)
    # benign: IT/notinject/neuralchemy önce, sonra reshabhs/rikka
    pref_b = [r for r in pool_b if ok(r) and r["source"] in ("HF/Horizon/notinject","HF/neuralchemy[original]")]
    rest_b = [r for r in pool_b if ok(r) and r["source"] not in ("HF/Horizon/notinject","HF/neuralchemy[original]")]
    clean_ben = [r for r in pref_b+rest_b if norm(r["text"]) not in used]
    # attack: güvenilir injection kaynakları + marker
    INJ = re.compile(r"(ignore|disregard|override|system prompt|developer mode|do anything now|\bDAN\b|"
                     r"act as|you are now|reveal|expose|print (your|the)|verbi|instructions|previous|"
                     r"jailbreak|base64|secret|password|api[_ ]?key|credential|admin|talimat|şifre|gizli)", re.I)
    clean_atk = [r for r in pool_a if ok(r) and r["label"]==1 and r["language"]=="en" and INJ.search(r["text"])
                 and norm(r["text"]) not in used]
    print("temiz havuz: benign=%d attack=%d" % (len(clean_ben), len(clean_atk)))

    by=defaultdict(lambda:[0,0])  # lang -> [benign, attack]
    for r in d: by[r["language"]][r["label"]]+=1

    add=[]
    ben_cursor=0; atk_cursor=0
    for lang,tot in TARGET.items():
        half=tot//2
        for label,pool,cursor_name in [(0,clean_ben,'ben'),(1,clean_atk,'atk')]:
            need = half - by[lang][label]
            if need <= 0: continue
            if cursor_name=='ben':
                cand = pool[ben_cursor: ben_cursor+need*3]; ben_cursor += need*3
            else:
                cand = pool[atk_cursor: atk_cursor+need*3]; atk_cursor += need*3
            if lang=="en":
                picks=[dict(text=r["text"], label=label, language="en", source=r["source"]+"[clean]",
                            attack_family="technical_it_support" if label==0 else "direct_injection",
                            difficulty="level_1_direct" if label==0 else "level_2_framing_persona")
                       for r in cand[:need]]
            else:
                texts=[r["text"] for r in cand[:need]]
                tr=translate_batch(texts, lang, workers=6) if texts else []
                picks=[]
                for r,t in zip(cand, tr):
                    if t and len(t)>=12 and not JUNK.search(t) and not ARTIFACT.search(t) and not ETHICS.search(t):
                        picks.append(dict(text=t.strip(), label=label, language=lang,
                                          source=r["source"]+f"[MT->{lang}]",
                                          attack_family="technical_it_support" if label==0 else "direct_injection",
                                          difficulty="level_1_direct" if label==0 else "level_2_framing_persona"))
                    if len(picks)>=need: break
            add += picks
            print(f"  {lang} l{label}: +{len(picks)} (gereken {need})")

    d += add
    # yeniden değerlendir
    by=defaultdict(lambda:[0,0])
    for r in d: by[r["language"]][r["label"]]+=1
    # tam kırp
    final=[]
    import random; random.seed(42)
    for lang,tot in TARGET.items():
        half=tot//2
        a=[r for r in d if r["language"]==lang and r["label"]==1][:half]
        b=[r for r in d if r["language"]==lang and r["label"]==0][:half]
        final+=a+b
    random.shuffle(final)
    # dedup final
    seen=set(); f2=[]
    for r in final:
        k=norm(r["text"])
        if k in seen: continue
        seen.add(k); f2.append(r)
    final=f2
    for i,r in enumerate(final,1):
        r["id"]=f"APPSEC_{i:04d}"; r.setdefault("difficulty","level_2_framing_persona" if r["label"]==1 else "level_1_direct")

    json.dump(final, open(DATA/"appsec_benchmark_2000.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
    import csv
    with open(DATA/"appsec_benchmark_2000.csv","w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh, fieldnames=["id","text","label","language","source","attack_family","difficulty"])
        w.writeheader()
        for r in final: w.writerow({k:r.get(k,"") for k in w.fieldnames})
    meta={"dataset_name":"NeuralShield-v5 AppSec Independent Benchmark","version":"3.1.0-appsec",
          "total_samples":len(final),"classes":dict(Counter("Attack" if r["label"]==1 else "Benign" for r in final)),
          "language_breakdown":dict(Counter(r["language"] for r in final)),
          "note":"AppSec/prompt-injection kapsamı. Ethics/harmful-content kapsam dışı. legacy print/log çöpü temizlendi. v5 eğitim setleriyle sıfır örtüşme. MT dilleri [MT->xx] işaretli."}
    json.dump(meta, open(DATA/"appsec_benchmark_2000_metadata.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
    # uyumluluk kopyası
    json.dump(final, open(DATA/"benchmark_master_2000.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(DATA/"benchmark_master_2000.csv","w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh, fieldnames=["id","text","label","language","source","attack_family","difficulty"])
        w.writeheader()
        for r in final: w.writerow({k:r.get(k,"") for k in w.fieldnames})

    print(f"\nFINAL N={len(final)} | {meta['classes']}")
    print("lang:", meta["language_breakdown"])
    print("lang 50/50:")
    for lg in TARGET:
        a=sum(1 for x in final if x['language']==lg and x['label']==1)
        b=sum(1 for x in final if x['language']==lg and x['label']==0)
        print(f"  {lg}: atk={a} ben={b}")

if __name__ == "__main__":
    main()
