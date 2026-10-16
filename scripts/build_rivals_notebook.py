"""Tam kapsamlı Rakip Guardrail Kıyaslama Colab defteri (A100 odaklı)."""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
P = Path(r'C:\Users\Mustafa\OneDrive\Masaüstü\Akademik_yayın\notebooks\Guardrail_Rivals_Colab.ipynb')

def md(t): return {"cell_type":"markdown","metadata":{},"source":t}
def code(t): return {"cell_type":"code","metadata":{},"execution_count":None,"outputs":[],"source":t}

C=[]
C.append(md("""# 🥊 Kapsamlı Guardrail Rakip Kıyaslaması (A100)

**Amaç:** NeuralShield-v5'i SOTA açık guardrail modelleriyle kıyaslamak.
**Ana odak: İngilizce (adil).** Ek: çok dilli (2000-set) → rakiplerin çok dilli zayıflığını gösterir.

**Rakipler:** ProtectAI DeBERTa-v3 · Patronus Wolf Defender · (ops.) Meta Llama-Guard-3-8B
**Metrikler:** Recall (saldırı yakalama), FP (yanlış alarm), Precision, Gecikme — ayrıca **dil bazında**.

**Donanım:** A100 (40/80GB) önerilir; T4'te de çoğu çalışır.
"""))
C.append(code("""# @title 1. Hugging Face Token (gated modeller için) 🔑
import os
HF_TOKEN = ""  #@param {type:"string"}
if not HF_TOKEN:
    try:
        from google.colab import userdata
        HF_TOKEN = userdata.get('HF_TOKEN') or ""
    except Exception:
        HF_TOKEN = ""
if HF_TOKEN:
    os.environ["HF_TOKEN"] = HF_TOKEN
    os.environ["HUGGING_FACE_HUB_TOKEN"] = HF_TOKEN
    print("✅ HF token ayarlandı (gated modeller açılır).")
else:
    print("ℹ️ Token yok → ProtectAI/Patronus çalışır; Llama-Guard gated olduğu için gerekir.")"""))
C.append(code("""# @title 2. GPU / VRAM kontrolü
import torch
print("CUDA:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))
    print("VRAM: %.1f GB" % (torch.cuda.get_device_properties(0).total_memory/1e9))
else:
    print("⚠️ GPU yok — Runtime > Change runtime type > A100/T4"))"""))
C.append(code("""# @title 3. Kütüphaneler
!pip install -q transformers accelerate bitsandbytes pandas matplotlib 2>/dev/null
print("✅ kurulum tamam")"""))
C.append(code("""# @title 4. Repo klonla + veri setlerini yükle
import os, json
if not os.path.exists('ai-soc-agent-lab'):
    !git clone -q https://github.com/Mustafa-Caliskan/ai-soc-agent-lab.git
%cd ai-soc-agent-lab
!git pull -q

EN_SET   = json.load(open('data/rivals_english_set.json', encoding='utf-8'))
FULL_SET = json.load(open('data/rivals_full_set.json', encoding='utf-8'))
print(f"İngilizce set: N={len(EN_SET)} (250 saldırı / 250 meşru)")
print(f"Çok dilli set: N={len(FULL_SET)}")"""))
C.append(code("""# @title 5. Değerlendirme çerçevesi (metrik + dil kırılımı)
import time, gc
import pandas as pd
import torch

def hf_blocked(model_id, texts, max_len=512, positive=('INJECTION','LABEL_1','ATTACK','UNSAFE','JAILBREAK'), bs=16):
    from transformers import pipeline
    clf = pipeline("text-classification", model=model_id, truncation=True,
                   max_length=max_len, device=0 if torch.cuda.is_available() else -1)
    t0=time.perf_counter()
    preds = clf(texts, batch_size=bs)
    lat=(time.perf_counter()-t0)/len(texts)*1000
    blocked=[any(p in str(r['label']).upper() for p in positive) for r in preds]
    del clf; gc.collect()
    if torch.cuda.is_available(): torch.cuda.empty_cache()
    return blocked, lat

def summarize(name, dataset, blocked, lat):
    a=[i for i,x in enumerate(dataset) if x['label']==1]
    b=[i for i,x in enumerate(dataset) if x['label']==0]
    tp=sum(1 for i in a if blocked[i]); fp=sum(1 for i in b if blocked[i])
    recall=100*tp/len(a) if a else 0; fpr=100*fp/len(b) if b else 0
    prec=100*tp/(tp+fp) if (tp+fp) else 0
    per_lang={}
    for lg in sorted(set(x['language'] for x in dataset)) if dataset and 'language' in dataset[0] else ['en']:
        la=[i for i,x in enumerate(dataset) if x['label']==1 and x.get('language','en')==lg]
        lb=[i for i,x in enumerate(dataset) if x['label']==0 and x.get('language','en')==lg]
        per_lang[lg]=(round(100*sum(1 for i in la if blocked[i])/len(la),1) if la else None,
                      round(100*sum(1 for i in lb if blocked[i])/len(lb),1) if lb else None)
    return {"Model":name,"Recall%":round(recall,1),"FP%":round(fpr,1),"Prec%":round(prec,1),
            "ms":round(lat,1),"TP":tp,"FP":fp,"per_language":per_lang}

def show_table(results):
    df = pd.DataFrame([{k:r[k] for k in ("Model","Recall%","FP%","Prec%","ms","TP","FP")} for r in results])
    return df.sort_values("Recall%", ascending=False).reset_index(drop=True)

EN_RESULTS = {}"""))
C.append(code("""# @title 6. İngilizce test: ProtectAI + Patronus + Llama-Guard + NeuralShield
RUN_LLAMA_GUARD = True  #@param {type:"boolean"}

en_texts=[x['text'] for x in EN_SET]

# Bizim kalkan (sette gömülü karar)
EN_RESULTS["NeuralShield-v5 (bizim)"] = summarize("NeuralShield-v5 (bizim)", EN_SET,
                                                 [x['neural_shield_blocked'] for x in EN_SET], 9.8)

# ProtectAI
bl, lat = hf_blocked("protectai/deberta-v3-base-prompt-injection-v2", en_texts, 512)
EN_RESULTS["ProtectAI DeBERTa-v3"] = summarize("ProtectAI DeBERTa-v3", EN_SET, bl, lat)

# Patronus Wolf Defender
bl, lat = hf_blocked("patronus-studio/wolf-defender-prompt-injection", en_texts, 2048)
EN_RESULTS["Patronus Wolf Defender"] = summarize("Patronus Wolf Defender", EN_SET, bl, lat)

# Llama-Guard-3-8B
if RUN_LLAMA_GUARD:
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        mid="meta-llama/Llama-Guard-3-8B"
        tok=AutoTokenizer.from_pretrained(mid)
        bnb=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.float16)
        m=AutoModelForCausalLM.from_pretrained(mid, quantization_config=bnb, device_map="auto")
        def lg_blocked(t):
            inp=tok.apply_chat_template([{"role":"user","content":t}], return_tensors="pt", add_generation_prompt=True).to(m.device)
            out=m.generate(inp, max_new_tokens=12, do_sample=False, pad_token_id=tok.eos_token_id)
            return "unsafe" in tok.decode(out[0][inp.shape[1]:], skip_special_tokens=True).lower()
        t0=time.perf_counter(); bl=[lg_blocked(t) for t in en_texts]; lat=(time.perf_counter()-t0)/len(en_texts)*1000
        EN_RESULTS["Llama-Guard-3-8B"] = summarize("Llama-Guard-3-8B", EN_SET, bl, lat)
        del m; gc.collect(); torch.cuda.empty_cache()
    except Exception as e:
        print("Llama-Guard atlandı:", str(e)[:120])

print("\\n===== İNGİLİZCE (ADİL) KIYASLAMA =====")
display(show_table(list(EN_RESULTS.values())))"""))
C.append(code("""# @title 7. İngilizce: dil/tier detayı yok (hepsi EN) — karşılaştırma grafiği
import matplotlib.pyplot as plt, numpy as np
names=list(EN_RESULTS.keys()); rec=[EN_RESULTS[n]['Recall%'] for n in names]; fp=[EN_RESULTS[n]['FP%'] for n in names]
x=np.arange(len(names)); w=0.38
plt.figure(figsize=(10,5),dpi=200)
b1=plt.bar(x-w/2, rec, w, label='Recall %', color='#2ca02c')
b2=plt.bar(x+w/2, fp, w, label='FP %', color='#d62728')
plt.xticks(x,[n.replace(' ','\\n') for n in names], fontsize=9)
plt.ylim(0,110); plt.title('Guardrail Kıyaslaması — İngilizce (Adil)'); plt.legend(); plt.grid(axis='y',alpha=.3)
for b in list(b1)+list(b2):
    plt.text(b.get_x()+b.get_width()/2, b.get_height()+1, f"{b.get_height():.0f}", ha='center', fontsize=8)
plt.tight_layout(); plt.savefig('rivals_english.png',dpi=300); plt.show()"""))
C.append(code("""# @title 8. Çok dilli test (2000-set) — rakiplerin çok dilli zafiyeti
MULTI_LIMIT = 0   #@param {type:"integer"}  # 0 = tamamı (2000). Küçültmek için ör. 600
full = FULL_SET[:MULTI_LIMIT] if MULTI_LIMIT else FULL_SET
full_texts=[x['text'] for x in full]
print(f"Çok dilli test seti: N={len(full)}")

MULTI_RESULTS={}
MULTI_RESULTS["NeuralShield-v5 (bizim)"] = summarize("NeuralShield-v5 (bizim)", full,
    [x['neural_shield_blocked'] for x in full], 9.8)
bl, lat = hf_blocked("protectai/deberta-v3-base-prompt-injection-v2", full_texts, 512)
MULTI_RESULTS["ProtectAI DeBERTa-v3"] = summarize("ProtectAI DeBERTa-v3", full, bl, lat)
bl, lat = hf_blocked("patronus-studio/wolf-defender-prompt-injection", full_texts, 2048)
MULTI_RESULTS["Patronus Wolf Defender"] = summarize("Patronus Wolf Defender", full, bl, lat)
print("\\n===== ÇOK DİLLİ (2000) KIYASLAMA =====")
display(show_table(list(MULTI_RESULTS.values())))"""))
C.append(code("""# @title 9. Çok dilli: DİL BAZINDA karşılaştırma (rakiplerin çöküşü)
import pandas as pd
langs=['en','tr','de','fr','es','it','pt','ru','ar','ja','ko','zh']
rows=[]
for lg in langs:
    row={"lang":lg}
    for name,r in MULTI_RESULTS.items():
        row[name]=r['per_language'].get(lg,(None,None))[0]  # attack recall per lang
    rows.append(row)
df=pd.DataFrame(rows).set_index('lang')
print("Saldırı Yakalama (Recall %) — DİL BAZINDA:")
display(df)
print("\\n(None = o dilde örnek yok; rakiplerin İngilizce-dışı dillerde çöküşü görülür)")"""))
C.append(code("""# @title 10. Grafikler + Sonuçları indir
import json, zipfile, matplotlib.pyplot as plt
# Çok dilli bar
names=list(MULTI_RESULTS.keys()); rec=[MULTI_RESULTS[n]['Recall%'] for n in names]; fp=[MULTI_RESULTS[n]['FP%'] for n in names]
import numpy as np
x=np.arange(len(names)); w=0.38
plt.figure(figsize=(10,5),dpi=200)
plt.bar(x-w/2,rec,w,label='Recall %',color='#2ca02c'); plt.bar(x+w/2,fp,w,label='FP %',color='#d62728')
plt.xticks(x,[n.replace(' ','\\n') for n in names],fontsize=9); plt.ylim(0,110)
plt.title('Guardrail Kıyaslaması — Çok Dilli (2000)'); plt.legend(); plt.grid(axis='y',alpha=.3)
plt.tight_layout(); plt.savefig('rivals_multilingual.png',dpi=300); plt.show()

json.dump({"english":list(EN_RESULTS.values()),"multilingual":list(MULTI_RESULTS.values())},
          open('rivals_full_results.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
with zipfile.ZipFile('rivals_full_bundle.zip','w') as z:
    z.write('rivals_full_results.json')
    import os
    for f in ['rivals_english.png','rivals_multilingual.png']:
        if os.path.exists(f): z.write(f)
from google.colab import files
files.download('rivals_full_bundle.zip')
print("🎉 İndirme tetiklendi.")"""))

nb={"cells":C,"metadata":{"kernelspec":{"display_name":"Python 3","name":"python3"},"colab":{"provenance":[]}},"nbformat":4,"nbformat_minor":0}
json.dump(nb, open(P,'w',encoding='utf-8'), ensure_ascii=False, indent=1)
print("-> notebooks/Guardrail_Rivals_Colab.ipynb yazıldı (hucre:", len(C), ")")
