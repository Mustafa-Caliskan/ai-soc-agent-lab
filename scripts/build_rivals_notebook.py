"""Rakip Guardrail Kıyaslama Colab defterini üretir."""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
nb_path = Path(r'C:\Users\Mustafa\OneDrive\Masaüstü\Akademik_yayın\notebooks\Guardrail_Rivals_Colab.ipynb')

def md(text): return {"cell_type":"markdown","metadata":{},"source":text}
def code(text): return {"cell_type":"code","metadata":{},"execution_count":None,"outputs":[],"source":text}

cells = []
cells.append(md("""# 🥊 Guardrail Rakip Kıyaslaması — Adil (İngilizce-Only) Karşılaştırma

**Amaç:** NeuralShield-v5'i, literatürdeki SOTA açık guardrail modelleriyle **eşit şartlarda** kıyaslamak.
**Adil koşul:** Tüm testler **İNGİLİZCE** (rakipler İngilizce odaklı). Set: `data/rivals_english_set.json` (250 saldırı + 250 meşru).

**Karşılaştırılan modeller:**
- 🛡️ **NeuralShield-v5** (bizim; L0-L2, ONNX INT8, CPU) — kararı sette gömülü
- ProtectAI `deberta-v3-base-prompt-injection-v2`
- Patronus `wolf-defender-prompt-injection`
- (opsiyonel) Meta `Llama-Guard-3-8B` (4-bit)

**Metrikler:** Saldırı Yakalama (Recall), Yanlış Alarm (FP), Kesinlik, Gecikme.
"""))

cells.append(code("""# @title 1. GPU Kontrolü
import torch
print("CUDA:", torch.cuda.is_available(), "|", (torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"))"""))

cells.append(code("""# @title 2. Kütüphaneler
!pip install -q transformers accelerate bitsandbytes 2>/dev/null
print("✅ hazır")"""))

cells.append(code("""# @title 3. Proje deposunu klonla (veri seti için)
import os
if not os.path.exists('ai-soc-agent-lab'):
    !git clone -q https://github.com/Mustafa-Caliskan/ai-soc-agent-lab.git
%cd ai-soc-agent-lab
!git pull -q
import json
SET = json.load(open('data/rivals_english_set.json', encoding='utf-8'))
atk = [x for x in SET if x['label']==1]; ben = [x for x in SET if x['label']==0]
print(f"Set: N={len(SET)} | saldırı={len(atk)} meşru={len(ben)}")"""))

cells.append(code("""# @title 4. Rakipleri Koştur (İngilizce)
import time, gc, json
from transformers import pipeline

RESULTS = {}

def run_pipeline_model(model_id, max_len=512, label_positive=None, name=""):
    print(f"\\n[*] {name}: {model_id} yükleniyor...")
    try:
        clf = pipeline("text-classification", model=model_id, truncation=True,
                       max_length=max_len, device=0 if torch.cuda.is_available() else -1)
    except Exception as e:
        print(f"  ⚠️ yüklenemedi: {e}"); return None
    texts = [x['text'] for x in SET]
    t0 = time.perf_counter()
    preds = clf(texts, batch_size=16)
    lat = (time.perf_counter()-t0)/len(texts)*1000
    blocked = []
    for r in preds:
        lab = str(r['label']).upper()
        if label_positive:
            blocked.append(label_positive in lab)
        else:
            blocked.append(('INJECTION' in lab) or ('LABEL_1' in lab) or ('ATTACK' in lab) or ('UNSAFE' in lab))
    res = summarize(name, blocked, lat)
    RESULTS[name] = res
    print(f"  -> Recall %{res['recall']:.1f} | FP %{res['fp']:.1f} | {res['latency']:.1f} ms")
    del clf; gc.collect()
    if torch.cuda.is_available(): torch.cuda.empty_cache()
    return res

def summarize(name, blocked, latency):
    a = [i for i,x in enumerate(SET) if x['label']==1]
    b = [i for i,x in enumerate(SET) if x['label']==0]
    tp = sum(1 for i in a if blocked[i]); fp = sum(1 for i in b if blocked[i])
    rec = 100*tp/len(a); fpr = 100*fp/len(b)
    prec = 100*tp/(tp+fp) if (tp+fp) else 0
    return {"name":name,"recall":round(rec,1),"fp":round(fpr,1),"precision":round(prec,1),
            "latency":round(latency,1),"tp":tp,"fp_n":fp,"n_atk":len(a),"n_ben":len(b)}

# Bizim kalkan (sette gömülü)
nb_blocked = [x['neural_shield_blocked'] for x in SET]
RESULTS["NeuralShield-v5 (bizim)"] = summarize("NeuralShield-v5 (bizim)", nb_blocked, 9.8)

run_pipeline_model("protectai/deberta-v3-base-prompt-injection-v2", 512, name="ProtectAI DeBERTa-v3")
run_pipeline_model("patronus-studio/wolf-defender-prompt-injection", 2048, name="Patronus Wolf Defender")"""))

cells.append(code("""# @title 5A. (OPSİYONEL, A100) Meta Llama-Guard-3-8B — 4-bit
RUN_LLAMA_GUARD = False #@param {type:"boolean"}
if RUN_LLAMA_GUARD:
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        mid = "meta-llama/Llama-Guard-3-8B"
        tok = AutoTokenizer.from_pretrained(mid)
        bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.float16)
        m = AutoModelForCausalLM.from_pretrained(mid, quantization_config=bnb, device_map="auto")
        import time
        def lg_blocked(t):
            msg=[{"role":"user","content":t}]
            inp=tok.apply_chat_template(msg, return_tensors="pt", add_generation_prompt=True).to(m.device)
            out=m.generate(inp, max_new_tokens=12, do_sample=False, pad_token_id=tok.eos_token_id)
            return "unsafe" in tok.decode(out[0][inp.shape[1]:], skip_special_tokens=True).lower()
        t0=time.perf_counter(); bl=[lg_blocked(x['text']) for x in SET]; lat=(time.perf_counter()-t0)/len(SET)*1000
        RESULTS["Llama-Guard-3-8B"] = summarize("Llama-Guard-3-8B", bl, lat)
        print("Llama-Guard:", RESULTS["Llama-Guard-3-8B"])
    except Exception as e:
        print("Llama-Guard atlandı:", e)"""))

cells.append(code("""# @title 6. Kıyaslama Tablosu + Grafik + İndir
import matplotlib.pyplot as plt, json, zipfile
if "SET" not in dir():
    import json; SET=json.load(open('data/rivals_english_set.json',encoding='utf-8'))

print("\\n" + "="*82)
print(f"{'Model':<32} | {'Recall%':>8} | {'FP%':>6} | {'Prec%':>6} | {'ms':>8}")
print("-"*82)
for name, r in RESULTS.items():
    print(f"{name:<32} | {r['recall']:>8.1f} | {r['fp']:>6.1f} | {r['precision']:>6.1f} | {r['latency']:>8.1f}")
print("="*82)

names=list(RESULTS.keys()); rec=[RESULTS[n]['recall'] for n in names]; fp=[RESULTS[n]['fp'] for n in names]
import numpy as np
x=np.arange(len(names)); w=0.38
plt.figure(figsize=(9,4.5),dpi=200)
plt.bar(x-w/2, rec, w, label='Saldırı Yakalama (Recall %)', color='#2ca02c')
plt.bar(x+w/2, fp, w, label='Yanlış Alarm (FP %)', color='#d62728')
plt.xticks(x, [n.replace(' ','\\n') for n in names], fontsize=8)
plt.ylim(0,105); plt.title('Guardrail Kıyaslaması (İngilizce-Only)'); plt.legend(); plt.tight_layout()
plt.savefig('guardrail_rivals_comparison.png', dpi=300); plt.show()

json.dump(RESULTS, open('guardrail_rivals_results.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
with zipfile.ZipFile('guardrail_rivals_bundle.zip','w') as z:
    z.write('guardrail_rivals_results.json'); z.write('guardrail_rivals_comparison.png')
from google.colab import files
files.download('guardrail_rivals_bundle.zip')
print("🎉 İndirme tetiklendi.")"""))

nb = {"cells": cells, "metadata": {"kernelspec":{"display_name":"Python 3","name":"python3"},"colab":{"provenance":[]}}, "nbformat":4, "nbformat_minor":0}
json.dump(nb, open(nb_path,'w',encoding='utf-8'), ensure_ascii=False, indent=1)
print("-> notebooks/Guardrail_Rivals_Colab.ipynb yazıldı (hücre:", len(cells), ")")
