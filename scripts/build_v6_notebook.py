"""NeuralShield-v6 notebook - P0/P1/P2 duzeltmeleriyle SAGLAM veri boru hatti."""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
P = Path(r'C:\Users\Mustafa\OneDrive\Masaüstü\Akademik_yayın\notebooks\Train_mmBERT_v6.ipynb')
def md(t): return {"cell_type":"markdown","metadata":{},"source":t}
def code(t): return {"cell_type":"code","metadata":{},"execution_count":None,"outputs":[],"source":t}
C=[]

C.append(md("""# 🧬 NeuralShield-v6 — mmBERT (çok dilli ModernBERT) Eğitimi
### P0/P1/P2 denetim düzeltmeleri uygulandı (label-aware extract, leakage purge, 12-dil denge, alpha-focal, ONNX eager+opset17)
**Taban:** `jhu-clsp/mmBERT-base` · **Kayıp:** CyberFocalLoss (γ=2.0, α=0.65) · **Kapsam:** AppSec-only.
Plan: `docs/V6_DATASET_PLAN.md` · Gerekçe: `docs/V6_RATIONALE_VE_KARSILASTIRMA.md`"""))

C.append(code("""# @title 1. Kurulum + HF token
import os
os.environ["TOKENIZERS_PARALLELISM"]="false"
!pip install -q -U transformers datasets accelerate scikit-learn seaborn onnx onnxruntime langdetect 2>/dev/null
HF_TOKEN=""
try:
    from google.colab import userdata; HF_TOKEN=userdata.get('HF_TOKEN') or ""
except Exception: pass
if not HF_TOKEN: HF_TOKEN=os.getenv("HF_TOKEN","")
if HF_TOKEN:
    os.environ["HF_TOKEN"]=HF_TOKEN
    from huggingface_hub import login; login(HF_TOKEN, add_to_git_credential=False)
print("✅ kurulum tamam")"""))

C.append(code("""# @title 2. Donanım + determinizm
import torch
print("CUDA:", torch.cuda.is_available(), "|", (torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"))
SEED=42
import random, numpy as np
random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)
if torch.cuda.is_available(): torch.cuda.manual_seed_all(SEED)"""))

C.append(code("""# @title 3. SEÇİCİ + LABEL-AWARE veri yükleme (etiket zehirlenmesi düzeltildi)
import re, pandas as pd
from datasets import load_dataset

ETHICS_PAT = re.compile(r"(suicide|self.?harm|intihar|genocide|soyk[ıi]r|organ mafya|ırkç|nefret söylemi|"
  r"11 eylül|9/11|terror|terör|nuke|bomb|bomba|meth|heroin|fentanyl|ricin|sarin|nerve agent|"
  r"chemical weapon|kimyasal silah|biyolojik silah|kendine zarar|cutting|eating disorder|bestiality|"
  r"molest|child porn|fidye|ransomware|money laundering|silah üret|uyuşturucu)", re.I)
INJECTION_MARKER = re.compile(r"(ignore|disregard|forget|override|overrid|bypass|system prompt|system message|"
  r"developer mode|do anything now|act as|you are now|pretend|roleplay|reveal|expose|leak|"
  r"print (?:your|the)|output (?:your|the)|instructions|previous|new (?:task|instruction|rule)|jailbreak|"
  r"base64|rot13|decode|execute|confidential|password|passwd|api[_ ]?key|credential|admin|token|config|"
  r"talimat|y[öo]nerge|şifre|sistem|unrestricted|verbatim|injection|<system|</?tool)", re.I)

KEEP_ATTACK = [
 "deepset/prompt-injections","reshabhs/SPML_Chatbot_Prompt_Injection","S-Labs/prompt-injection-dataset",
 "3nesdeniz/agentic-prompt-injection-5k","iamabhishekpanda/enterprise-prompt-injection-dataset",
 "imoxto/prompt_injection_hackaprompt_gpt35","prodnull/prompt-injection-repo-dataset","jayavibhav/prompt-injection",
 "3nesdeniz/turkish-conversation-prompt-injection","AltaySec/turkish-llm-injection","MAlmasabi/Indirect-Prompt-Injection-BIPIA-GPT",
 "cgoosen/prompt_injection_ctf_dataset_3","rikka-snow/prompt-injection-multilingual","dmtrdr/russian_prompt_injections",
 "halilneed/turkish-prompt-injection-benchmark","wambosec/prompt-injections","wambosec/prompt-injections-subtle",
 "zachz/prompt-injection-benchmark","masahiroid/japanese-indirect-prompt-injection-probes",
 "neuralchemy/Prompt-injection-dataset","hendzh/PromptShield","Lakera/gandalf_ignore_instructions",
 "Lakera/mosscap_prompt_injection","rgeada/tool-response-injections","microsoft/llmail-inject-challenge",
 "yanismiraoui/prompt_injections","TrustAIRLab/in-the-wild-jailbreak-prompts","JailbreakV-28K/JailBreakV-28k",
 "nvidia/Nemotron-RL-Agentic-Indirect-Prompt-Injection-v1" ]
KEEP_BENIGN = [
 "3nesdeniz/guardrail-hard-negatives","guychuk/benign-malicious-prompt-classification",
 "rogue-security/real-world-benign-use-cases","3nesdeniz/turkish-daily-dialogues-5k",
 "TFLai/Turkish-Dialog-Dataset","cisimcik/turkish-decisions-max-19k",
 "emreseyhan/Turkish-customer-service-conversations","kilicai/turkish-sft-multi-turn-dialogue-10k",
 "merve/turkish_instructions","CohereLabs/aya_collection_language_split",
 "dev-hussein/saudi-arabic-cs-conversations","halilneed/turkish-prompt-injection-false-alarm-benchmark",
 "OpenAssistant/oasst2","HuggingFaceH4/ultrachat_200k","fka/prompts.chat",
 "glaiveai/glaive-function-calling-v2","natolambert/xstest-v2-copy" ]
MARKER_REQUIRED = {"TrustAIRLab/in-the-wild-jailbreak-prompts","JailbreakV-28K/JailBreakV-28k"}

SPEC = {
 "CohereLabs/aya_collection_language_split": {"config":"standard_arabic","text":"inputs"},
 "CohereLabs/aya_dataset": {"text":"inputs"},
 "HuggingFaceH4/ultrachat_200k": {"split":"train_sft","text":"messages"},
 "dev-hussein/saudi-arabic-cs-conversations": {"text":"conversation"},
 "kilicai/turkish-sft-multi-turn-dialogue-10k": {"text":"conversation"},
 "merve/turkish_instructions": {"text":"talimat"},
 "MAlmasabi/Indirect-Prompt-Injection-BIPIA-GPT": {"text":"context"},
 "TrustAIRLab/in-the-wild-jailbreak-prompts": {"config":"jailbreak_2023_12_25","text":"prompt"},
 "reshabhs/SPML_Chatbot_Prompt_Injection": {"text":"User Prompt","label":"Prompt injection"},
 "wambosec/prompt-injections": {"text":"prompt","label":"label"},
 "halilneed/turkish-prompt-injection-false-alarm-benchmark": {"text":"text","label":"label"},
}
TEXT_COLS = ["text","prompt","instruction","user_prompt","goal","question","inputs","talimat","conversation","input","context"]
LABEL_COLS = ["label","Prompt injection","is_attack","is_malicious","injection","output","type","class"]
POSITIVE = {"1","injection","attack","malicious","jailbreak","unsafe","yes","true"}

def pick(df, cols, override=None):
    if override and override in df.columns: return override
    for c in cols:
        if c in df.columns: return c
    return None

def load_source(cid, fallback):
    spec = SPEC.get(cid, {})
    kw = {"split": spec.get("split","train")}
    if spec.get("config"): kw["config"]=spec["config"]
    try: ds = load_dataset(cid, **kw)
    except Exception:
        try: ds = load_dataset(cid, split=spec.get("split","train"))
        except Exception as e:
            print(f"  UYARI {cid}: {str(e)[:50]}"); return [],[]
    df = ds.to_pandas() if ds.num_rows < 300000 else ds.select(range(80000)).to_pandas()
    tcol = pick(df, TEXT_COLS, spec.get("text"))
    if not tcol:
        print(f"  UYARI {cid}: metin sutunu yok ({list(df.columns)[:6]})"); return [],[]
    lcol = pick(df, LABEL_COLS, spec.get("label"))
    atk=[]; ben=[]
    for _,row in df.iterrows():
        t=str(row[tcol]).strip()
        if not (12<=len(t)<=2000) or ETHICS_PAT.search(t): continue
        if cid in MARKER_REQUIRED and not INJECTION_MARKER.search(t): continue
        if lcol is not None and str(row[lcol]).strip().lower() in POSITIVE:
            atk.append(t)
        elif lcol is not None:
            ben.append(t)
        elif fallback=="attack":
            atk.append(t)
        else:
            ben.append(t)
    return atk, ben

ATTACKS=[]; BENIGN=[]
for cid in KEEP_ATTACK:
    a,b=load_source(cid,"attack"); ATTACKS+=a; BENIGN+=b
    print(f"  OK {cid}: atk={len(a)} ben={len(b)}")
for cid in KEEP_BENIGN:
    a,b=load_source(cid,"benign"); ATTACKS+=a; BENIGN+=b
    print(f"  OK {cid}: atk={len(a)} ben={len(b)}")
ATTACKS=list(dict.fromkeys(ATTACKS)); BENIGN=list(dict.fromkeys(BENIGN))
print(f"[i] Ham: attack={len(ATTACKS)} benign={len(BENIGN)}")"""))

C.append(code("""# @title 4. SIZINTI ÖNLEME (leakage purge) - eval setleri kara liste
import unicodedata, json, os
def norm(s): return re.sub(r"\\s+"," ",unicodedata.normalize("NFKC", s or "").lower().strip())
EVAL_TEXT_FILES = ["data/appsec_benchmark_2000.json","data/stress_boundary_mosscap_notinject.json",
                   "data/colab_e2e_suite_stratified.json","data/rivals_english_set.json","data/rivals_full_set.json"]
BLACKLIST=set()
for f in EVAL_TEXT_FILES:
    if os.path.exists(f):
        try:
            for x in json.load(open(f,encoding="utf-8")):
                if isinstance(x,dict) and x.get("text"): BLACKLIST.add(norm(x["text"]))
        except Exception: pass
print(f"[i] Kara liste (eval metinleri): {len(BLACKLIST)}")
ATTACKS=[t for t in ATTACKS if norm(t) not in BLACKLIST]
BENIGN=[t for t in BENIGN if norm(t) not in BLACKLIST]
print(f"[i] Purge sonrasi: attack={len(ATTACKS)} benign={len(BENIGN)}")"""))

C.append(code("""# @title 5. Çok dilli denge (12 dil, 50/50) + Tier atama
import random
from langdetect import detect, DetectorFactory
DetectorFactory.seed = SEED
LANGS = ["en","tr","de","fr","es","it","pt","ru","ar","ja","ko","zh"]
TGT_ATK = {"en":15000,"tr":15000, **{l:2000 for l in ["de","fr","es","it","pt","ru","ar","ja","ko","zh"]}}
TGT_BEN = {"en":15000,"tr":15000, **{l:2000 for l in ["de","fr","es","it","pt","ru","ar","ja","ko","zh"]}}
def lang_of(t):
    try:
        lg = detect(t[:400]);  return lg if lg in LANGS else "en"
    except Exception: return "en"
def tier_of(t):
    tl=t.lower()
    if any(k in tl for k in ("base64","rot13","in reverse","tersten","\\u200b","zero-width","unicode tag")): return 4
    if any(k in tl for k in ("dan","stan","developer mode","unrestricted","roleplay","pretend","act as","persona")): return 2
    if any(k in tl for k in ("story","scenario","novel","academic","thesis","hypothetical","imagine","document")): return 3
    if any(k in tl for k in ("<system","tool_call","function_call","agent","mcp")): return 5
    return 1
def bucket(texts):
    by={}
    for t in texts: by.setdefault(lang_of(t),[]).append(t)
    return by
A_by=bucket(ATTACKS); B_by=bucket(BENIGN)
arec=[]; brec=[]
for lg in LANGS:
    random.shuffle(A_by.get(lg,[])); random.shuffle(B_by.get(lg,[]))
    for t in A_by.get(lg,[])[:int(TGT_ATK[lg]*1.5)]:
        arec.append({"text":t,"label":1,"language":lg,"tier":tier_of(t)})
    for t in B_by.get(lg,[])[:int(TGT_BEN[lg]*1.5)]:
        brec.append({"text":t,"label":0,"language":lg,"tier":0})
def cap_to(recs, tgt):
    out=[]; have={}
    for r in recs:
        lg=r['language']
        if have.get(lg,0) >= tgt[lg]: continue
        have[lg]=have.get(lg,0)+1; out.append(r)
    return out
arec=cap_to(arec, TGT_ATK); brec=cap_to(brec, TGT_BEN)
print("attack dil:", pd.Series([x['language'] for x in arec]).value_counts().to_dict())
print("benign dil:", pd.Series([x['language'] for x in brec]).value_counts().to_dict())
print(f"[i] Dengeli: attack={len(arec)} benign={len(brec)}")
# NOT: eksik diller için MT/sentetik ayri uretilen data/ dosyasindan eklenir (MT Colab disinda onceden yapilmali)"""))

C.append(code("""# @title 6. Dedup + Stratified split (dil x etiket x tier)
import pandas as pd
from sklearn.model_selection import train_test_split
ALL=arec+brec
seen=set(); full=[]
for x in ALL:
    k=norm(x['text'])
    if k in seen or k in BLACKLIST: continue
    seen.add(k); full.append(x)
df=pd.DataFrame(full)
strat = df['label'].astype(str)+"_"+df['language'].astype(str)+"_"+df['tier'].astype(str)
if strat.value_counts().min()<2:
    strat = df['label'].astype(str)+"_"+df['language'].astype(str)
tv, test = train_test_split(df, test_size=0.15, stratify=strat, random_state=SEED)
strat2 = tv['label'].astype(str)+"_"+tv['language'].astype(str)
train, val = train_test_split(tv, test_size=0.1765, stratify=strat2, random_state=SEED)
print(f"train={len(train)} val={len(val)} test={len(test)} | toplam={len(df)} | denge={df['label'].value_counts().to_dict()}")"""))

C.append(code("""# @title 7. Tokenizasyon + mmBERT (eager attention)
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from datasets import Dataset
MODEL="jhu-clsp/mmBERT-base"
tok=AutoTokenizer.from_pretrained(MODEL)
def tk(batch): return tok(batch["text"], truncation=True, max_length=512, padding=False)
ds_tr=Dataset.from_pandas(train[['text','label']]).map(tk, batched=True)
ds_va=Dataset.from_pandas(val[['text','label']]).map(tk, batched=True)
ds_te=Dataset.from_pandas(test[['text','label']]).map(tk, batched=True)
model=AutoModelForSequenceClassification.from_pretrained(MODEL, num_labels=2, attn_implementation="eager")
print("mmBERT params:", round(sum(p.numel() for p in model.parameters())/1e6,1), "M")"""))

C.append(code("""# @title 8. CyberFocalLoss (gamma=2.0, alpha=0.65) + Trainer
import torch, torch.nn as nn
from transformers import Trainer, TrainingArguments, EarlyStoppingCallback
class FocalTrainer(Trainer):
    gamma=2.0; alpha=0.65
    def compute_loss(self, model, inputs, return_outputs=False, **kw):
        labels=inputs.get("labels")
        out=model(**inputs)
        ce=nn.functional.cross_entropy(out.logits, labels, reduction="none")
        p=torch.softmax(out.logits,-1).gather(1,labels.unsqueeze(1)).squeeze(1)
        pt = torch.where(labels==1, p, 1-p)
        alpha_t = torch.where(labels==1, torch.full_like(pt, self.alpha), torch.full_like(pt, 1-self.alpha))
        loss=(alpha_t*((1-pt)**self.gamma)*ce).mean()
        return (loss,out) if return_outputs else loss
def metrics(p):
    from sklearn.metrics import f1_score,accuracy_score,roc_auc_score
    import numpy as np
    pr=np.argmax(p.predictions,-1)
    try: auc=roc_auc_score(p.label_ids, torch.softmax(torch.tensor(p.predictions),-1)[:,1].numpy())
    except Exception: auc=0.0
    return {"accuracy":accuracy_score(p.label_ids,pr),"f1":f1_score(p.label_ids,pr,average="macro"),"auc":round(auc,4)}"""))

C.append(code("""# @title 9. EĞİTİM (bf16 + grad_accum)
use_bf16 = torch.cuda.is_available() and torch.cuda.is_bf16_supported()
EFF_BS=16*2
steps=len(ds_tr)//EFF_BS
args=TrainingArguments(output_dir="./v6_out", learning_rate=2e-5, weight_decay=0.01,
    num_train_epochs=3, per_device_train_batch_size=16, per_device_eval_batch_size=64,
    gradient_accumulation_steps=2, warmup_steps=int(steps*3*0.10), eval_strategy="epoch",
    save_strategy="epoch", load_best_model_at_end=True, metric_for_best_model="f1",
    bf16=use_bf16, fp16=(torch.cuda.is_available() and not use_bf16), report_to="none", logging_steps=100)
trainer=FocalTrainer(model=model, args=args, train_dataset=ds_tr, eval_dataset=ds_va,
    compute_metrics=metrics, callbacks=[EarlyStoppingCallback(early_stopping_patience=2)])
trainer.train()"""))

C.append(code("""# @title 10. Hold-out değerlendirme + confusion matrix
import numpy as np, seaborn as sns, matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report
pred=trainer.predict(ds_te); pr=np.argmax(pred.predictions,-1)
print(classification_report(pred.label_ids, pr, target_names=["Benign","Malicious"], digits=4))
cm=confusion_matrix(pred.label_ids, pr)
plt.figure(figsize=(5,4),dpi=150); sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
  xticklabels=["Benign","Malicious"], yticklabels=["Benign","Malicious"])
plt.title("v6 mmBERT - Hold-out Confusion Matrix"); plt.tight_layout(); plt.savefig("v6_confusion.png",dpi=300); plt.show()"""))

C.append(code("""# @title 11. Kalibrasyon (temperature scaling) - val
import numpy as np, scipy.optimize as opt, json
vp=trainer.predict(ds_va); logits=vp.predictions; labels=vp.label_ids
def nll(T):
    z=logits/T; z=z-z.max(1,keepdims=True); p=np.exp(z)/np.exp(z).sum(1,keepdims=True)
    return -np.mean(np.log(p[np.arange(len(labels)),labels]+1e-12))
res=opt.minimize_scalar(nll, bounds=(0.5,5.0), method="bounded")
T_OPT=float(round(res.x,4)); print("Optimal T* =", T_OPT, "| NLL", round(res.fun,5))
json.dump({"temperature":T_OPT}, open("v6_temperature.json","w"))"""))

C.append(code("""# @title 12. Bağımsız OOD (12-dil 2000) + DİL BAZINDA Recall/FP tablosu
import os, json, numpy as np, pandas as pd
from sklearn.metrics import accuracy_score, f1_score
OOD="data/appsec_benchmark_2000.json"
if os.path.exists(OOD):
    ood=pd.DataFrame(json.load(open(OOD,encoding="utf-8")))
    ods=Dataset.from_pandas(ood[['text','label']]).map(tk, batched=True)
    op=trainer.predict(ods); opr=np.argmax(op.predictions,-1)
    print("OOD genel acc:", round(accuracy_score(op.label_ids,opr)*100,2), "| macro-F1:", round(f1_score(op.label_ids,opr,average='macro')*100,2))
    recs=ood.to_dict('records'); rows=[]
    for lg in ["en","tr","de","fr","es","it","pt","ru","ar","ja","ko","zh"]:
        idx=[i for i,x in enumerate(recs) if x.get('language')==lg]
        la=[i for i in idx if recs[i]['label']==1]; lb=[i for i in idx if recs[i]['label']==0]
        rec=100*sum(1 for i in la if opr[i]==1)/len(la) if la else None
        fp=100*sum(1 for i in lb if opr[i]==1)/len(lb) if lb else None
        rows.append({"dil":lg,"recall%":round(rec,1) if rec is not None else None,"fp%":round(fp,1) if fp is not None else None})
    display(pd.DataFrame(rows).set_index("dil"))
else:
    print("OOD seti yok - repo klonlayinca gelir")"""))

C.append(code("""# @title 13. Grafikler (loss / F1 / ROC)
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
hist=trainer.state.log_history
tr_loss=[h['loss'] for h in hist if 'loss' in h]; ev_f1=[h.get('eval_f1') for h in hist if h.get('eval_f1') is not None]
fig,ax=plt.subplots(1,3,figsize=(16,4),dpi=150)
ax[0].plot(tr_loss); ax[0].set_title("Egitim Kaybi (Focal)"); ax[0].set_xlabel("adim")
ax[1].plot(ev_f1, marker='o', color='#2ca02c'); ax[1].set_title("Val Macro-F1"); ax[1].set_xlabel("epoch")
probs=torch.softmax(torch.tensor(pred.predictions),-1)[:,1].numpy()
fpr,tpr,_=roc_curve(pred.label_ids, probs); ax[2].plot(fpr,tpr,label=f"AUC={auc(fpr,tpr):.4f}")
ax[2].plot([0,1],[0,1],'--',color='gray'); ax[2].set_title("ROC (Hold-out)"); ax[2].legend()
plt.tight_layout(); plt.savefig("v6_curves.png",dpi=300); plt.show()"""))

C.append(md("""---
## 🔬 14. XLM-R (v5) KARŞILAŞTIRMA — adil ablasyon (2 hücre, sonra silinebilir)
Hiperparametreler mmBERT ile eşitlendi (512 token, 3 epoch, grad_accum). İş bitince silin."""))
C.append(code("""# @title 14A. (GEÇİCİ) XLM-RoBERTa - adil eğitim
from transformers import AutoTokenizer as T2, AutoModelForSequenceClassification as M2
mx=T2.from_pretrained("xlm-roberta-base")
def tkx(b): return mx(b["text"], truncation=True, max_length=512, padding=False)
x_tr=Dataset.from_pandas(train[['text','label']]).map(tkx, batched=True)
x_va=Dataset.from_pandas(val[['text','label']]).map(tkx, batched=True)
x_te=Dataset.from_pandas(test[['text','label']]).map(tkx, batched=True)
xmdl=M2.from_pretrained("xlm-roberta-base", num_labels=2)
args_x=TrainingArguments(output_dir="./xlm_tmp", learning_rate=2e-5, weight_decay=0.01, num_train_epochs=3,
  per_device_train_batch_size=16, gradient_accumulation_steps=2, eval_strategy="epoch",
  report_to="none", bf16=(torch.cuda.is_available() and torch.cuda.is_bf16_supported()))
trainer_x=FocalTrainer(model=xmdl, args=args_x, train_dataset=x_tr, eval_dataset=x_va, compute_metrics=metrics)
trainer_x.train()"""))
C.append(code("""# @title 14B. (GEÇİCİ) XLM-R vs v6 mmBERT kiyasi
import numpy as np
def ev(t, ds):
    p=t.predict(ds); pr=np.argmax(p.predictions,-1)
    from sklearn.metrics import f1_score, accuracy_score
    return round(accuracy_score(p.label_ids,pr)*100,2), round(f1_score(p.label_ids,pr,average='macro')*100,2)
a6,f6=ev(trainer, ds_te); ax,fx=ev(trainer_x, x_te)
print(f"{'Model':<22} {'Acc%':>8} {'F1%':>8}")
print(f"{'v6 mmBERT':<22} {a6:>8} {f6:>8}")
print(f"{'v5 XLM-R (adil)':<22} {ax:>8} {fx:>8}")"""))

C.append(code("""# @title 15. ONNX INT8 export (eager + opset 17) + bundle (T* dahil)
import torch, os, shutil, json
from onnxruntime.quantization import quantize_dynamic, QuantType
os.makedirs("./v6_bundle", exist_ok=True)
model.to("cpu").eval(); trainer.save_model("./v6_bundle"); tok.save_pretrained("./v6_bundle")
dummy=tok("test metni", return_tensors="pt")
torch.onnx.export(model, (dummy["input_ids"], dummy["attention_mask"]), "./v6_bundle/model.onnx",
  input_names=["input_ids","attention_mask"], output_names=["logits"],
  dynamic_axes={"input_ids":{0:"b",1:"s"},"attention_mask":{0:"b",1:"s"}}, opset_version=17)
quantize_dynamic("./v6_bundle/model.onnx","./v6_bundle/model_quantized_int8.onnx",weight_type=QuantType.QInt8)
for f in ["v6_temperature.json","v6_curves.png","v6_confusion.png"]:
    if os.path.exists(f): shutil.copy(f,"./v6_bundle/")
shutil.make_archive("neuralshield_v6_bundle","zip","./v6_bundle")
from google.colab import files; files.download("neuralshield_v6_bundle.zip")
print("v6 bundle (T* dahil) indirildi")"""))

nb={"cells":C,"metadata":{"kernelspec":{"display_name":"Python 3","name":"python3"},"accelerator":"GPU","colab":{"provenance":[]}},"nbformat":4,"nbformat_minor":0}
json.dump(nb, open(P,'w',encoding='utf-8'), ensure_ascii=False, indent=1)
print("-> notebooks/Train_mmBERT_v6.ipynb yazildi (hucre:", len(C), ")")
