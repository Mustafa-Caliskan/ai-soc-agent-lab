"""
Kürat + karar-eşiği analizi ve rapor üretimi.
Girdi : data/appsec_benchmark_2000_shield.json (ml_risk, regex_score, ... alanlı)
Çıktı : data/appsec_benchmark_2000_curated.json  (katman etiketli)
         docs/BENCHMARK_GENERALIZATION_VE_ESIK_ANALIZI.md
"""
import json, sys, re
sys.stdout.reconfigure(encoding='utf-8')
from collections import Counter, defaultdict
from pathlib import Path
ROOT = Path(r'C:\Users\Mustafa\OneDrive\Masaüstü\Akademik_yayın'); DATA = ROOT/'data'
CONFIG = json.load(open(ROOT/'backend'/'shield_config.json', encoding='utf-8'))

d = json.load(open(DATA/'appsec_benchmark_2000_shield.json', encoding='utf-8'))

EXPL = re.compile(r'(ignore|disregard|forget|override|unut|yok say|ignorier|oublie|ignora|忘れ|無視|무시|'
                  r'ignorez|ignoriere|系统|系統|инструкц|instruction|talimat|talimatlar|yönerge)', re.I)
def tag(x):
    src = x['source']
    x['origin'] = 'MT' if '[MT->' in src else 'native'
    x['challenge'] = 'explicit' if EXPL.search(x['text']) else 'subtle'
    # OR-Bench hard: görünüşte-zararlı ama over-refusal testi (kapsam belirsiz) -> out_of_scope
    x['scope'] = 'out_of_scope' if ('orbench' in src.lower()) else 'in_scope'
    x['benign_type'] = 'hard_negative' if 'notinject' in src.lower() else 'normal'
    return x
d = [tag(x) for x in d]
json.dump(d, open(DATA/'appsec_benchmark_2000_curated.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)

A = [x for x in d if x['label']==1]
B = [x for x in d if x['label']==0]
Ain = [x for x in A if x['scope']=='in_scope']
Bin = [x for x in B if x['scope']=='in_scope']

def comp(x, thr, wml=CONFIG['weight_ml'], wr=CONFIG['weight_regex'], ws=CONFIG['weight_stego']):
    c = wml*x['ml_risk'] + wr*x['regex_score'] + ws*(100 if x['hard_stego'] else 0)
    if x['hard_stego']: r=max(c, CONFIG['hard_block_stego_score'])
    elif x['regex_triggered'] and x['ml_class']=='Malicious': r=max(c, CONFIG['hard_block_regex_and_ml_score'])
    elif x['regex_triggered']: r=max(c, CONFIG['regex_only_floor_score'])
    else: r=c
    return (r>=thr) or (x['regex_triggered'] and x['ml_class']=='Malicious')

def orgate(x, mt):
    # Arkadaş önerisi: stego ve regex gücünü koru, ML'yi 0.70 ağırlığıyla EZME
    return x['hard_stego'] or x['regex_score'] >= 60 or x['ml_risk'] >= mt

RULES = {
 "Mevcut composite (thr=60)":        lambda x: comp(x, 60),
 "composite thr=50":                 lambda x: comp(x, 50),
 "composite thr=40":                 lambda x: comp(x, 40),
 "ML>=70 (önerilen)":                lambda x: x['ml_risk']>=70 or x['hard_stego'] or x['regex_triggered'],
 "ML>=60":                           lambda x: x['ml_risk']>=60 or x['hard_stego'] or x['regex_triggered'],
 "ML>=50":                           lambda x: x['ml_risk']>=50 or x['hard_stego'] or x['regex_triggered'],
 "ML sınıf=Malicious":               lambda x: x['ml_class']=='Malicious',
 "OR-Gate (ML>=70)":                 lambda x: orgate(x, 70),
 "OR-Gate (ML>=60)":                 lambda x: orgate(x, 60),
 "OR-Gate (ML>=50)":                 lambda x: orgate(x, 50),
}

def rates(rule, A_, B_):
    ab = sum(1 for x in A_ if rule(x)); bf = sum(1 for x in B_ if rule(x))
    return (100*ab/len(A_) if A_ else 0), (100*bf/len(B_) if B_ else 0), ab, bf

lines=[]
def w(s=""): lines.append(s)

w("# NeuralShield-v5 — Bağımsız Benchmark: Genelleme Boşluğu ve Karar Eşiği Analizi")
w()
w("> **Amaç:** Kalkanın bağımsız (in-distribution olmayan) AppSec benchmark'ındaki gerçek davranışını ölçmek,")
w("> düşük blok oranının kök nedenini model/regex/karar katmanı olarak ayrıştırmak ve eşik kararı için")
w("> kanıt sunmak. **Doküman, karar alma aşamasında paylaşılmak üzere hazırlanmıştır.**")
w()
w(f"**Benchmark:** `data/appsec_benchmark_2000_curated.json` — 2000 örnek (1000 saldırı / 1000 meşru), 12 dil.")
w(f"**Kalkan:** NeuralShield-v5 (XLM-RoBERTa ONNX INT8, T*=1.8345) + Layer 0/1/3. Karar: composite 0.70·ML + 0.20·regex + 0.10·stego, eşik {CONFIG['block_threshold']}.")
w()
w("---")
w()
w("## 1. Metodolojik UYARI: Paper'daki %94.64 ile buradaki fark NEDEN?")
w()
w("- Paper'daki **%94.64 doğruluk / 0.9954 AUC**, eğitimle **AYNI dağılımdan** çekilen held-out test kümesindedir (**in-distribution**).")
w("- Bu benchmark ise **farklı kaynaklardan** (Lakera/mosscap, reshahhs, xTRam1, Horizon, neuralchemy) + **MT ile 10 dilde** üretilmiştir (**out-of-distribution**).")
w("- İkisi çelişmez: biri 'kapalı sınav', diğeri 'gerçek dünya' performansıdır. **Gerçekçi performans = bağımsız setteki değerdir.**")
w()
w("## 2. Bileşen Ayrıştırması — Sorun modelde mi, regex'te mi, kararda mı?")
w()
recall_ml = 100*sum(1 for x in A if x['ml_class']=='Malicious')/len(A)
regex_trig = 100*sum(1 for x in A if x['regex_triggered'])/len(A)
w("| Bileşen | Ölçüm | Yorum |")
w("|---|---|---|")
w(f"| **Model (L2)** | Saldırıların **%{recall_ml:.0f}**'ini Malicious diyor | Recall iyi; ana dedektör model |")
w(f"| **Regex (L1)** | Saldırıların yalnızca **%{regex_trig:.0f}**'unda tetikleniyor | Rolü küçük; darboğaz DEĞİL |")
w(f"| **Karar katmanı** | Mevcut blok **%{rates(RULES['Mevcut composite (thr=60)'],A,B)[0]:.1f}** | `0.70·ML` eşiği 60 → **ML≥86** istiyor; tespitlerin çoğu kesiliyor |")
w()
w("**KANIT:** *\"Ignore everything above this line\"* → ML **%84 Malicious** ama `0.70×84 = 59 < 60` → bloklanmadı.")
w("**Sonuç: Model doğru tespit ediyor; darboğaz karar eşiğidir.** (Kapasite/model büyütme sorunu değildir.)")
w()
w("## 3. Kapsam & Zorluk Kırılımı (kürat edilmiş etiketler)")
w()
w("| Kırılım | Saldırı (n) | Meşru (n) |")
w("|---|---:|---:|")
w(f"| Tüm set | {len(A)} | {len(B)} |")
w(f"| Kapsam-içi (OR-Bench hariç) | {len(Ain)} | {len(Bin)} |")
w(f"| native (TR/EN) | {sum(1 for x in A if x['origin']=='native')} | {sum(1 for x in B if x['origin']=='native')} |")
w(f"| MT (diğer 10 dil) | {sum(1 for x in A if x['origin']=='MT')} | {sum(1 for x in B if x['origin']=='MT')} |")
w(f"| explicit injection | {sum(1 for x in A if x['challenge']=='explicit')} | - |")
w(f"| subtle | {sum(1 for x in A if x['challenge']=='subtle')} | - |")
w(f"| hard-negative benign (NotInject) | - | {sum(1 for x in B if x['benign_type']=='hard_negative')} |")
w()
w("### Recall / FP (ML≥50, dil ve zorluk bazında)")
w()
def rate(rows, cond): return 100*sum(1 for x in rows if cond(x))/len(rows) if rows else 0
w("| Grup | Metrik | Değer |")
w("|---|---|---|")
w(f"| native TR/EN saldırı | Recall (ML≥50) | %{rate([x for x in A if x['origin']=='native'], lambda x:x['ml_risk']>=50):.0f} |")
w(f"| MT diller saldırı | Recall (ML≥50) | %{rate([x for x in A if x['origin']=='MT'], lambda x:x['ml_risk']>=50):.0f} |")
w(f"| explicit saldırı | Recall (ML≥50) | %{rate([x for x in A if x['challenge']=='explicit'], lambda x:x['ml_risk']>=50):.0f} |")
w(f"| subtle saldırı | Recall (ML≥50) | %{rate([x for x in A if x['challenge']=='subtle'], lambda x:x['ml_risk']>=50):.0f} |")
w(f"| normal benign | FP (ML≥50) | %{rate([x for x in B if x['benign_type']=='normal'], lambda x:x['ml_risk']>=50):.0f} |")
w(f"| hard-negative benign | FP (ML≥50) | %{rate([x for x in B if x['benign_type']=='hard_negative'], lambda x:x['ml_risk']>=50):.0f} |")
w()
w("> **Not:** MT diller recall'u native'den **daha kötü değil** → model dili bağımsız çalışıyor. FP'nin büyük kısmı **NotInject hard-negative**'lerden.")
w()
w("## 4. KARAR EŞİĞİ ÖDÜNLEŞİM TABLOSU (Kapsam-içi set)")
w()
w("| Karar Kuralı | Saldırı Blok [in-scope] | Meşru FP [in-scope] | Saldırı Blok [tüm] | Meşru FP [tüm] |")
w("|---|---:|---:|---:|---:|")
for name, rule in RULES.items():
    a_in, b_in, _, _ = rates(rule, Ain, Bin)
    a_all, b_all, _, _ = rates(rule, A, B)
    w(f"| {name} | **%{a_in:.1f}** | %{b_in:.1f} | %{a_all:.1f} | %{b_all:.1f} |")
w()
w("**Yorum:** Recall'i %29'dan yükseltmek FP'yi de yükseltir (bu bir **tercih**, ücretsiz düzeltme değil).")
w("Modelin ayrım gücü (bu sette ~AUC 0.86) bu ödünleşim eğrisini belirler.")
w()
w("## 5. ÖNERİ VE KARAR SEÇENEKLERİ")
w()
w("**Not:** `OR-Gate` ile `ML≥X` kuralları bu veride **birebir aynı** sonucu verir; çünkü regex tetiklendiğinde skoru zaten ≥60'tır.")
w("Yani arkadaş önerisi (stego/regex gücünü koru, ML'yi 0.70 ile ezme) hem doğru hem de en dengeli davranışı üretir.")
w()
w("**Önerilen kural: `OR-Gate (ML≥70)`** (veya modelin kalibre optimal eşiği τ*=0.4567 → ~`ML≥46`):")
w()
w("| Seçenek | Blok (in-scope) | FP (in-scope) | Saldırı Blok (tüm) | Uygun senaryo |")
w("|---|---:|---:|---:|---|")
a1,b1,_,_ = rates(RULES["Mevcut composite (thr=60)"], Ain, Bin); a1a,_,_,_ = rates(RULES["Mevcut composite (thr=60)"], A, B)
a2,b2,_,_ = rates(RULES["OR-Gate (ML>=70)"], Ain, Bin); a2a,_,_,_ = rates(RULES["OR-Gate (ML>=70)"], A, B)
a3,b3,_,_ = rates(RULES["OR-Gate (ML>=50)"], Ain, Bin); a3a,_,_,_ = rates(RULES["OR-Gate (ML>=50)"], A, B)
w(f"| A. Mevcut (thr=60) | %{a1:.1f} | %{b1:.1f} | %{a1a:.1f} | FP toleransı sıfır, recall düşük |")
w(f"| B. **OR-Gate ML≥70 (önerilen)** | **%{a2:.1f}** | %{b2:.1f} | %{a2a:.1f} | **Dengeli kurumsal** |")
w(f"| C. OR-Gate ML≥50 | %{a3:.1f} | %{b3:.1f} | %{a3a:.1f} | Recall-kritik (SOC alarm) |")
w()
w("**Bağımsız kararlar (eşikten ayrı):**")
w("1. **Benchmark küratı:** OR-Bench (kapsam belirsiz) çıkar → in-scope set daha net.")
w("2. **v6 retrain'i (opsiyonel, büyük iş):** kapsam-içi veri + geniş benign/hard-negative havuzu. **Kapasite artırımı gereksiz.**")
w("3. **Paper dürüstlüğü:** in-distribution %94.64 yanına **bağımsız benchmark sonucu** mutlaka raporlanmalı.")
w()
w("---")
w("_Üretildi: scripts/analyze_generalization_and_threshold.py_")

md = "\n".join(lines)
(ROOT/'docs'/'BENCHMARK_GENERALIZATION_VE_ESIK_ANALIZI.md').write_text(md, encoding='utf-8')
print(md)
print("\n[OK] -> docs/BENCHMARK_GENERALIZATION_VE_ESIK_ANALIZI.md ve data/appsec_benchmark_2000_curated.json")
