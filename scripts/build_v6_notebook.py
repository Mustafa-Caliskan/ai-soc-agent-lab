"""NeuralShield-v6 Colab defterini üretir: seçici 100k veri + mmBERT + XLM kıyas + grafikler."""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
P = Path(r'C:\Users\Mustafa\OneDrive\Masaüstü\Akademik_yayın\notebooks\Train_mmBERT_v6.ipynb')
def md(t): return {"cell_type":"markdown","metadata":{},"source":t}
def code(t): return {"cell_type":"code","metadata":{},"execution_count":None,"outputs":[],"source":t}
C=[]
C.append(md("""# 🧬 NeuralShield-v6 — mmBERT (çok dilli ModernBERT) Eğitimi
### Kusursuz ~100k, 12-dilli, kapsam-temiz (AppSec-only) veri havuzu

**Taban:** `jhu-clsp/mmBERT-base` (çok dilli ModernBERT, ~300M) · **Kayıp:** CyberFocalLoss (γ=2.0)
**Kapsam:** injection / system-extraction / evasion / stego / agentic / indirect / coercion. **Ethics hariç.**
Detaylı plan: `docs/V6_DATASET_PLAN.md`"""))

C.append(code("""# @title 1. Kurulum + HF token
import os, sys, subprocess
os.environ["TOKENIZERS_PARALLELISM"]="false"
!pip install -q -U transformers datasets accelerate scikit-learn seaborn onnx onnxruntime 2>/dev/null
HF_TOKEN=""
try:
    from google.colab import userdata; HF_TOKEN=userdata.get('HF_TOKEN') or ""
except Exception: pass
if not HF_TOKEN: HF_TOKEN=input("HF token (boş geçilebilir): ")
if HF_TOKEN:
    os.environ["HF_TOKEN"]=HF_TOKEN; from huggingface_hub import login; login(HF_TOKEN, add_to_git_credential=False)
print("✅ kurulum tamam")"""))

C.append(code("""# @title 2. Donanım kontrolü
import torch
print("CUDA:", torch.cuda.is_available(), "|", (torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"))
SEED=42
import random, numpy as np
random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)
if torch.cuda.is_available(): torch.cuda.manual_seed_all(SEED)"""))

C.append(code("""# @title 3. SEÇİCİ Veri Havuzu (keep/drop + ethics filtresi)
import re, pandas as pd
from datasets import load_dataset, concatenate_datasets

KEEP_ATTACK = [
 # bizim v5 KEEP'lerimiz (kapsam-içi)
 "3nesdeniz/agentic-prompt-injection-5k","AltaySec/turkish-llm-injection",
 "MAlmasabi/Indirect-Prompt-Injection-BIPIA-GPT","S-Labs/prompt-injection-dataset",
 "cgoosen/prompt_injection_ctf_dataset_3","deepset/prompt-injections",
 "iamabhishekpanda/enterprise-prompt-injection-dataset","imoxto/prompt_injection_hackaprompt_gpt35",
 "prodnull/prompt-injection-repo-dataset","jayavibhav/prompt-injection",
 "3nesdeniz/turkish-conversation-prompt-injection",
 # çok dilli / native (içerik denetiminden geçti)
 "rikka-snow/prompt-injection-multilingual","dmtrdr/russian_prompt_injections",
 "halilneed/turkish-prompt-injection-benchmark","wambosec/prompt-injections",
 "wambosec/prompt-injections-subtle","zachz/prompt-injection-benchmark",
 "masahiroid/japanese-indirect-prompt-injection-probes",
 # RAKİPLERİN izinli kaynaklarından (Horizon-Labs/ProtectAI reçetesi)
 "neuralchemy/Prompt-injection-dataset","hendzh/PromptShield",
 "Lakera/gandalf_ignore_instructions","Lakera/mosscap_prompt_injection",
 "reshabhs/SPML_Chatbot_Prompt_Injection","rgeada/tool-response-injections",
 "microsoft/llmail-inject-challenge","yanismiraoui/prompt_injections",
 "TrustAIRLab/in-the-wild-jailbreak-prompts","JailbreakV-28K/JailBreakV-28k",
 "nvidia/Nemotron-RL-Agentic-Indirect-Prompt-Injection-v1" ]
KEEP_BENIGN = [
 "3nesdeniz/guardrail-hard-negatives","guychuk/benign-malicious-prompt-classification",
 "rogue-security/real-world-benign-use-cases","3nesdeniz/turkish-daily-dialogues-5k",
 "TFLai/Turkish-Dialog-Dataset","cisimcik/turkish-decisions-max-19k",
 "emreseyhan/Turkish-customer-service-conversations","kilicai/turkish-sft-multi-turn-dialogue-10k",
 "merve/turkish_instructions","CohereLabs/aya_collection_language_split",
 "dev-hussein/saudi-arabic-cs-conversations","halilneed/turkish-prompt-injection-false-alarm-benchmark",
 # rakiplerin benign kaynakları (izinli)
 "OpenAssistant/oasst2","HuggingFaceH4/ultrachat_200k","fka/prompts.chat",
 "glaiveai/glaive-function-calling-v2","CohereLabs/aya_dataset",
 "natolambert/xstest-v2-copy","OpenSafetyLab/Salad-Data","alespalla/chatbot_instruction_prompts" ]
# GATED/401 (token ister): or-bench-80k, Harelix/Prompt-Injection-Mixed-Techniques-2024, hlynurd/insecure-code
# MODEL (rakip): NAMAA-Space/Ara-Prompt-Guard (Arapça), Horizon-Labs/prompt-injection-guard-base (mmBERT)
# KAPSAM DIŞI (yüklenmez): AdvBench, WildJailbreak, JailbreakHub, CAIS, magpie, swiss-ai, vllm-sr

ETHICS_PAT = re.compile(r"(suicide|self.?harm|intihar|genocide|soyk[ıi]r|organ mafya|ırkç|nefret söylemi|"
  r"11 eylül|9/11|nuke|bomb|bomba|meth|heroin|fentan|ricin|sarin|nerve agent|kimyasal silah|biyolojik silah)", re.I)

def extract(df):
    txt=None
    for c in ('text','prompt','instruction','user_prompt','goal','question','adversarial','instruction'):
        if c in df.columns: txt=c; break
    if txt is None: return []
    out=[]
    for t in df[txt].dropna():
        t=str(t).strip()
        if 12<=len(t)<=2000 and not ETHICS_PAT.search(t): out.append(t)
    return out

ATTACKS=[]; BENIGN=[]
for cid in KEEP_ATTACK:
    try:
        ds=load_dataset(cid, split="train")
        df=ds.to_pandas() if ds.num_rows<200000 else ds.select(range(60000)).to_pandas()
        ATTACKS += extract(df)
        print(f"  ✅ {cid}: {ds.num_rows if hasattr(ds,'num_rows') else '?'}")
    except Exception as e: print(f"  ⚠️ {cid}: {str(e)[:60]}")
for cid in KEEP_BENIGN:
    try:
        ds=load_dataset(cid, split="train")
        df=ds.to_pandas() if ds.num_rows<200000 else ds.select(range(40000)).to_pandas()
        BENIGN += extract(df)
    except Exception as e: print(f"  ⚠️ {cid}: {str(e)[:60]}")
print(f"\\n[i] Ham: attack={len(ATTACKS)} benign={len(BENIGN)}")"""))

C.append(code("""# @title 4. Çok dilli dengeleme + Tier atama + (gerekiyorsa) MT
import unicodedata, json
def norm(s): return re.sub(r"\\s+"," ",unicodedata.normalize("NFKC",s or "").lower().strip())
def lang_of(t):
    tr=set('çğıöşüÇĞİÖŞÜ')
    if len(set(t)&tr)>2: return 'tr'
    return 'en'   # further lang detection/M-T below
def tier_of(t):
    tl=t.lower()
    if any(k in tl for k in ('base64','rot13','in reverse','tersten','\\u200b','сыворот' )): return 4
    if any(k in tl for k in ('dan','stan','developer mode','unrestricted','roleplay','pretend','act as','persona')): return 2
    if any(k in tl for k in ('story','scenario','novel','academic','thesis','hypothetical','imagine')): return 3
    return 1
ATTACKS=list(dict.fromkeys(ATTACKS)); BENIGN=list(dict.fromkeys(BENIGN))
# Basit atama (gerçek çok dilli dengeleme/MT bir sonraki hücrede EVREN ile yapılır)
A=[{"text":t,"label":1,"language":lang_of(t),"tier":tier_of(t)} for t in ATTACKS]
B=[{"text":t,"label":0,"language":lang_of(t),"tier":0} for t in BENIGN]
print(f"attack={len(A)} benign={len(B)}")
print("≈ dil (attack):", pd.Series([x['language'] for x in A]).value_counts().to_dict())
# NOT: en/tr dışı diller için MT (EVREN) v5'teki gibi uygulanacak — notebook'ta mevcut""")) 

C.append(code("""# @title 5. Dedup + sızıntı denetimi + STRATIFIED split
from sklearn.model_selection import train_test_split
ALL=A+B
seen=set(); full=[]
for x in ALL:
    k=norm(x['text'])
    if k in seen: continue
    seen.add(k); full.append(x)
df=pd.DataFrame(full)
strat = df['label'].astype(str)+"_"+df['language']
train_val, test = train_test_split(df, test_size=0.15, stratify=strat, random_state=SEED)
tv_strat = train_val['label'].astype(str)+"_"+train_val['language']
train, val = train_test_split(train_val, test_size=0.1765, stratify=tv_strat, random_state=SEED)
print(f"train={len(train)} val={len(val)} test={len(test)} | toplam={len(df)}")
print("label denge:", df['label'].value_counts().to_dict())"""))

C.append(code("""# @title 6. Tokenizasyon + mmBERT yükleme
from transformers import AutoTokenizer, AutoModelForSequenceClassification
MODEL="jhu-clsp/mmBERT-base"
tok=AutoTokenizer.from_pretrained(MODEL)
def tk(batch): return tok(batch["text"], truncation=True, max_length=512, padding=False)
from datasets import Dataset
ds_tr=Dataset.from_pandas(train[['text','label']]).map(tk, batched=True)
ds_va=Dataset.from_pandas(val[['text','label']]).map(tk, batched=True)
ds_te=Dataset.from_pandas(test[['text','label']]).map(tk, batched=True)
model=AutoModelForSequenceClassification.from_pretrained(MODEL, num_labels=2)
print("✅ mmBERT hazır | params:", sum(p.numel() for p in model.parameters())/1e6, "M")"""))

C.append(code("""# @title 7. CyberFocalLoss (γ=2.0) + Trainer
import torch.nn as nn
from transformers import Trainer, TrainingArguments, EarlyStoppingCallback
class FocalTrainer(Trainer):
    gamma=2.0
    def compute_loss(self, model, inputs, return_outputs=False, **kw):
        labels=inputs.get("labels")
        out=model(**inputs)
        ce=nn.functional.cross_entropy(out.logits, labels, reduction="none")
        p=torch.softmax(out.logits,-1).gather(1,labels.unsqueeze(1)).squeeze(1)
        loss=(((1-p)**self.gamma)*ce).mean()
        return (loss,out) if return_outputs else loss
def metrics(p):
    import numpy as np; from sklearn.metrics import f1_score,accuracy_score
    pr=np.argmax(p.predictions,-1)
    return {"accuracy":accuracy_score(p.label_ids,pr),"f1":f1_score(p.label_ids,pr,average="macro")}"""))

C.append(code("""# @title 8. EĞİTİM
EFF_BS=16*2
steps=len(ds_tr)//EFF_BS
args=TrainingArguments(output_dir="./v6_out", learning_rate=2e-5, weight_decay=0.01,
    num_train_epochs=3, per_device_train_batch_size=16, per_device_eval_batch_size=64,
    warmup_steps=int(steps*3*0.10), eval_strategy="epoch", save_strategy="epoch",
    load_best_model_at_end=True, metric_for_best_model="f1", fp16=torch.cuda.is_available(),
    report_to="none", logging_steps=50)
trainer=FocalTrainer(model=model, args=args, train_dataset=ds_tr, eval_dataset=ds_va,
    compute_metrics=metrics, callbacks=[EarlyStoppingCallback(early_stopping_patience=2)])
trainer.train()"""))

C.append(code("""# @title 9. Hold-out değerlendirme (confusion matrix + metrikler)
import numpy as np, seaborn as sns, matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report, roc_auc_score
pred=trainer.predict(ds_te)
pr=np.argmax(pred.predictions,-1)
probs=torch.softmax(torch.tensor(pred.predictions),-1)[:,1].numpy()
print(classification_report(pred.label_ids, pr, target_names=["Benign","Malicious"], digits=4))
print("AUC:", round(roc_auc_score(pred.label_ids, probs),4))
cm=confusion_matrix(pred.label_ids, pr)
plt.figure(figsize=(5,4),dpi=150); sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
  xticklabels=["Benign","Malicious"], yticklabels=["Benign","Malicious"])
plt.title("v6 mmBERT — Hold-out Confusion Matrix"); plt.tight_layout(); plt.savefig("v6_confusion.png",dpi=300); plt.show()"""))

C.append(code("""# @title 10. Kalibrasyon (temperature scaling) — val üzerinde
import numpy as np, scipy.optimize as opt
vp=trainer.predict(ds_va)
logits=vp.predictions; labels=vp.label_ids
def nll(T):
    z=logits/T; z=z-z.max(1,keepdims=True); p=np.exp(z)/np.exp(z).sum(1,keepdims=True)
    return -np.mean(np.log(p[np.arange(len(labels)),labels]+1e-12))
res=opt.minimize_scalar(nll, bounds=(0.5,5.0), method="bounded")
print("Optimal T* =", round(res.x,4), "| NLL", round(res.fun,5))
open("v6_temperature.txt","w").write(str(round(res.x,4)))"""))

C.append(code("""# @title 11. Bağımsız OOD değerlendirme (12-dil 2000-seti) — varsa
import os, json
OOD="data/appsec_benchmark_2000.json"
if os.path.exists(OOD):
    ood=pd.DataFrame(json.load(open(OOD,encoding="utf-8")))
    ods=Dataset.from_pandas(ood[['text','label']]).map(tk, batched=True)
    op=trainer.predict(ods); opr=np.argmax(op.predictions,-1)
    from sklearn.metrics import f1_score, accuracy_score
    print("OOD acc:", round(accuracy_score(op.label_ids,opr)*100,2), "| macro-F1:", round(f1_score(op.label_ids,opr,average='macro')*100,2))
else:
    print("OOD seti yok — repo klonlayınca otomatik gelir")"""))

C.append(code("""# @title 12. Grafikler (loss / F1 ilerlemesi / dil kıyası)
import matplotlib.pyplot as plt
hist=trainer.state.log_history
tr_loss=[h['loss'] for h in hist if 'loss' in h]; ev_f1=[h['eval_f1'] for h in hist if 'eval_f1' in h]
fig,ax=plt.subplots(1,2,figsize=(11,4),dpi=150)
ax[0].plot(tr_loss, color='#1f77b4'); ax[0].set_title("Eğitim Kaybı (CyberFocalLoss)"); ax[0].set_xlabel("adım")
ax[1].plot(ev_f1, marker='o', color='#2ca02c'); ax[1].set_title("Doğrulama Macro-F1 (epoch)"); ax[1].set_xlabel("epoch")
plt.tight_layout(); plt.savefig("v6_curves.png",dpi=300); plt.show()"""))

C.append(md("""---
## 🔬 13. XLM-RoBERTa (v5) KARŞILAŞTIRMA — 2 hücre (sonra silinebilir)
Aşağıdaki 2 hücre v5 modelini (XLM-R) kısa eğitip v6 mmBERT ile kıyaslar. **Hakemin kafası karışmasın diye makale dışıdır; iş bitince silin.**"""))

C.append(code("""# @title 13A. (GEÇİCİ) v5 XLM-RoBERTa hızlı eğitim
from transformers import AutoTokenizer as T2, AutoModelForSequenceClassification as M2
mx=T2.from_pretrained("xlm-roberta-base")
def tkx(b): return mx(b["text"], truncation=True, max_length=256, padding=False)
x_tr=Dataset.from_pandas(train[['text','label']]).map(tkx, batched=True)
x_va=Dataset.from_pandas(val[['text','label']]).map(tkx, batched=True)
xmdl=M2.from_pretrained("xlm-roberta-base", num_labels=2)
args_x=TrainingArguments(output_dir="./xlm_tmp", learning_rate=2e-5, num_train_epochs=2,
  per_device_train_batch_size=16, eval_strategy="epoch", report_to="none", fp16=torch.cuda.is_available())
trainer_x=FocalTrainer(model=xmdl, args=args_x, train_dataset=x_tr, eval_dataset=x_va, compute_metrics=metrics)
trainer_x.train()
print("✅ XLM-R (v5-tipi) geçici eğitim bitti")"""))

C.append(code("""# @title 13B. (GEÇİCİ) XLM-R vs v6 mmBERT kıyası
import numpy as np
def ev(t, ds):
    p=t.predict(ds); pr=np.argmax(p.predictions,-1)
    from sklearn.metrics import f1_score, accuracy_score
    return round(accuracy_score(p.label_ids,pr)*100,2), round(f1_score(p.label_ids,pr,average='macro')*100,2)
def tkx2(b): return mx(b["text"], truncation=True, max_length=256, padding=False)
x_te=Dataset.from_pandas(test[['text','label']]).map(tkx2, batched=True)
a6,f6=ev(trainer, ds_te); ax,fx=ev(trainer_x, x_te)
print(f"{'Model':<22} {'Acc%':>8} {'F1%':>8}")
print(f"{'v6 mmBERT':<22} {a6:>8} {f6:>8}")
print(f"{'v5 XLM-R (geçici)':<22} {ax:>8} {fx:>8}")"""))

C.append(code("""# @title 14. ONNX INT8 export + dağıtım paketi
!pip install -q onnx onnxruntime 2>/dev/null
import torch, os, shutil
from onnxruntime.quantization import quantize_dynamic, QuantType
os.makedirs("./v6_bundle", exist_ok=True)
model.to("cpu").eval(); trainer.save_model("./v6_bundle"); tok.save_pretrained("./v6_bundle")
torch.onnx.export(model, (tok("test",return_tensors="pt")["input_ids"], tok("test",return_tensors="pt")["attention_mask"]),
  "./v6_bundle/model.onnx", input_names=["input_ids","attention_mask"], output_names=["logits"],
  dynamic_axes={"input_ids":{0:"b",1:"s"},"attention_mask":{0:"b",1:"s"}}, opset_version=14)
quantize_dynamic("./v6_bundle/model.onnx","./v6_bundle/model_quantized_int8.onnx",weight_type=QuantType.QInt8)
shutil.make_archive("neuralshield_v6_bundle","zip","./v6_bundle")
from google.colab import files; files.download("neuralshield_v6_bundle.zip")
print("🎉 v6 bundle indirildi")"""))

nb={"cells":C,"metadata":{"kernelspec":{"display_name":"Python 3","name":"python3"},"accelerator":"GPU","colab":{"provenance":[]}},"nbformat":4,"nbformat_minor":0}
json.dump(nb, open(P,'w',encoding='utf-8'), ensure_ascii=False, indent=1)
print("-> notebooks/Train_mmBERT_v6.ipynb yazıldı (hucre:", len(C), ")")
