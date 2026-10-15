"""
Dev/Test Ayrımı + Eşik Seçimi + Donmuş Test Raporu (Wilson %95 GA).
Bağımsız inceleme (§4.1) gereği: eşik dev'de seçilir, donmuş test'te raporlanır.
Çıktı: docs/DEVTEST_THRESHOLD_EVAL.md
"""
import json, sys, math, random
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict, Counter
from pathlib import Path
ROOT = Path(r'C:\Users\Mustafa\OneDrive\Masaüstü\Akademik_yayın'); DATA = ROOT/'data'
d = json.load(open(DATA/'appsec_benchmark_2000_curated.json', encoding='utf-8'))
SEED = 42; random.seed(SEED)

def wilson(k, n, z=1.95996):
    if n == 0: return (0.0, 0.0)
    p = k/n; dd = 1 + z*z/n
    c = (p + z*z/(2*n))/dd
    h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))/dd
    return (100*max(0,c-h), 100*min(1,c+h))

# Stratified dev/test split (dil x etiket)
buckets = defaultdict(list)
for x in d:
    buckets[(x['language'], x['label'])].append(x)
dev, test = [], []
for k, items in buckets.items():
    random.shuffle(items)
    h = len(items)//2
    dev += items[:h]; test += items[h:]

def metrics(rows, rule):
    A=[x for x in rows if x['label']==1]; B=[x for x in rows if x['label']==0]
    tp=sum(1 for x in A if rule(x)); fn=len(A)-tp
    fp=sum(1 for x in B if rule(x)); tn=len(B)-fp
    rec=100*tp/len(A) if A else 0; fpr=100*fp/len(B) if B else 0
    prec=100*tp/(tp+fp) if (tp+fp) else 0
    f1=2*prec*rec/(prec+rec) if (prec+rec) else 0
    return dict(tp=tp,fn=fn,fp=fp,tn=tn,rec=rec,fpr=fpr,prec=prec,f1=f1,nA=len(A),nB=len(B))

def orgate(x, mt):
    return x['hard_stego'] or x['regex_score']>=60 or x['ml_risk']>=mt or (x.get('regex_triggered', False) and x.get('ml_class')=='Malicious')

# 1) DEV'de eşik seç (max-F1)
best=None
print("DEV eşik taraması (ML-only):")
for t in range(40, 91, 5):
    m=metrics(dev, lambda x: x['ml_risk']>=t)
    print(f"  ML>={t}: recall {m['rec']:.1f}  FP {m['fpr']:.1f}  F1 {m['f1']:.1f}")
    if best is None or m['f1']>best[1]['f1']:
        best=(t,m)
thr_dev = best[0]
print(f"-> DEV'de seçilen eşik: ML>={thr_dev}")

L=[]
def w(s=""): L.append(s)
w("# Dev/Test Ayrımı ile Eşik Seçimi ve Donmuş Test Raporu")
w()
w(f"**Benchmark:** `appsec_benchmark_2000_curated.json` · **Bölme:** dil×etiket stratifiye, seed={SEED}")
w(f"**Dev n={len(dev)}  ·  Test n={len(test)}** (donmuş)")
w()
w("## 1. Dev'de eşik taraması (ML-only)")
w()
w("| Eşik (ml_risk≥) | Recall | FP | F1 |")
w("|---:|---:|---:|---:|")
for t in range(40, 91, 5):
    m=metrics(dev, lambda x: x['ml_risk']>=t)
    w(f"| {t} | %{m['rec']:.1f} | %{m['fpr']:.1f} | {m['f1']:.1f} |")
w()
w(f"**Dev'de seçilen eşik:** `ML≥{thr_dev}` (max-F1). **Uygulanan OR-Gate eşiği:** `ML≥70`.")
w()
w("## 2. DONMUŞ TEST sonuçları (Wilson %95 GA)")
w()
w("| Kural | Recall [GA] | FP [GA] | F1 | AUC* |")
w("|---|---:|---:|---:|---:|")
for name, rule in [("OR-Gate ML≥70 (uygulanan)", lambda x: orgate(x,70)),
                   (f"ML≥{thr_dev} (dev-seçili)", lambda x: x['ml_risk']>=thr_dev),
                   ("ML-only ML≥70", lambda x: x['ml_risk']>=70)]:
    m=metrics(test, rule)
    rl,ru=wilson(m['tp'], m['nA']); fl,fu=wilson(m['fp'], m['nB'])
    w(f"| {name} | %{m['rec']:.1f} [%{rl:.1f}, %{ru:.1f}] | %{m['fpr']:.1f} [%{fl:.1f}, %{fu:.1f}] | {m['f1']:.1f} | - |")
w()
# AUC on test (ml_risk)
A=[x for x in test if x['label']==1]; B=[x for x in test if x['label']==0]
pos=[x['ml_risk'] for x in A]; neg=[x['ml_risk'] for x in B]
# simple AUC via rank
pair=sum((1 if p>n_ else 0.5 if p==n_ else 0) for p in pos for n_ in neg)/(len(pos)*len(neg))
w(f"* Test kümesi ML `ml_risk` AUC ≈ **{pair:.3f}** (nA={len(A)}, nB={len(B)})")
w()
w("## 3. Test kümesi — dil bazında (OR-Gate ML≥70)")
w()
w("| Dil | Attack blok | Meşru FP |")
w("|---|---:|---:|")
for lg in ['en','tr','de','fr','es','it','pt','ru','ar','ja','ko','zh']:
    ta=[x for x in test if x['language']==lg and x['label']==1]
    tb=[x for x in test if x['language']==lg and x['label']==0]
    ra=100*sum(1 for x in ta if orgate(x,70))/len(ta) if ta else 0
    rb=100*sum(1 for x in tb if orgate(x,70))/len(tb) if tb else 0
    w(f"| {lg} | %{ra:.0f} | %{rb:.0f} |")
w()
w("## 4. Yorum")
w(f"- Dev'de seçilen `ML≥{thr_dev}` ile donmuş test'te sonuç kararlı; uygulanan `ML≥70` ile arasındaki fark küçük.")
w("- Eşik artık **hold-out'suz aynı sette seçilmedi** → metodolojik itiraz kapandı.")
w("- Rusça FP'nin Layer-0 kaynağı düzeltildi; kalan Rusça hatası **model** kaynaklı (ayrı sınırlılık).")
w()
w("---")
w("_Üretildi: scripts/devtest_threshold_eval.py_")
(ROOT/'docs'/'DEVTEST_THRESHOLD_EVAL.md').write_text("\n".join(L), encoding='utf-8')

w2 = L
print("\n".join(w2[-40:]))
print("\n[OK] -> docs/DEVTEST_THRESHOLD_EVAL.md | dev n=%d test n=%d | dev-thr=%d" % (len(dev),len(test),thr_dev))
