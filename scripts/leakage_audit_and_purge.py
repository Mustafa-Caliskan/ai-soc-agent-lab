"""
Sızıntı (leakage) re-audit: v5 eğitim kaynaklarındaki metinleri indirip benchmark
ile normalize-eşleşmeyi bulur. Gerçek eğitim havuzu (71.440) Colab'da olduğu için
bu bir ALT SINIRDır; yine de erişilebilen tüm v5 kaynaklarını tarar.
Çıktı: docs/LEAKAGE_AUDIT.md + data/appsec_benchmark_2000_purged.json (örtüşenler hariç)
"""
import os, sys, json, re, unicodedata
os.environ['HF_HUB_DISABLE_TELEMETRY']='1'; os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING']='1'
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from collections import Counter
ROOT = Path(r'C:\Users\Mustafa\OneDrive\Masaüstü\Akademik_yayın'); DATA = ROOT/'data'
norm = lambda s: re.sub(r'\s+',' ', unicodedata.normalize('NFKC', s or '').lower().strip())

d = json.load(open(DATA/'appsec_benchmark_2000_curated.json', encoding='utf-8'))
bm_norm = { norm(x['text']): x for x in d }

from datasets import load_dataset

SOURCES = [
 ("3nesdeniz/turkish-conversation-prompt-injection", None, "train"),
 ("3nesdeniz/turkish-daily-dialogues-5k", None, "train"),
 ("AltaySec/turkish-llm-injection", None, "train"),
 ("MAlmasabi/Indirect-Prompt-Injection-BIPIA-GPT", None, "train"),
 ("S-Labs/prompt-injection-dataset", None, "train"),
 ("deepset/prompt-injections", None, "train"),
 ("guychuk/benign-malicious-prompt-classification", None, "train"),
 ("iamabhishekpanda/enterprise-prompt-injection-dataset", None, "train"),
 ("imoxto/prompt_injection_hackaprompt_gpt35", None, "train"),
 ("jackhhao/jailbreak-classification", None, "train"),
 ("jayavibhav/prompt-injection", None, "train"),
 ("jayavibhav/prompt-injection-safety", None, "train"),
 ("prodnull/prompt-injection-repo-dataset", None, "train"),
 ("fevziegeyurtsevenler/turkish-prompt-injection", None, "train"),
 ("beratcmn/turkish-prompt-injections", None, "train"),
 ("Necent/llm-jailbreak-prompt-injection-dataset", None, "train"),
 ("walledai/JailbreakHub", None, "train"),
 ("cgoosen/prompt_injection_ctf_dataset_3", None, "train"),
 ("TrustAIRLab/in-the-wild-jailbreak-prompts", None, "train"),
]

overlap = {}   # bm_norm_key -> kaynak
per_src = {}
for cid, cfg, split in SOURCES:
    hit = 0; n = 0
    try:
        ds = load_dataset(cid, cfg, split=split, streaming=True) if cfg else load_dataset(cid, split=split, streaming=True)
        for ex in ds:
            n += 1
            txt = None
            for k in ('text','prompt','instruction','user_prompt','goal','question','input'):
                if isinstance(ex, dict) and ex.get(k):
                    txt = str(ex[k]); break
            if not txt:
                # bazi setlerde tum string alanlari birlestir
                txt = ' '.join(str(v) for v in ex.values() if isinstance(v,str))
            key = norm(txt)
            if key in bm_norm:
                if key not in overlap:
                    overlap[key] = cid
                    hit += 1
            if n >= 60000:  # guvenli ust sinir
                break
        per_src[cid] = (hit, n)
    except Exception as e:
        per_src[cid] = (f"ERR:{str(e)[:50]}", n)

print("=== Kaynak bazında birebir örtüşme ===")
total_keys = len(overlap)
for cid,(hit,n) in per_src.items():
    print(f"  {cid:52s} {hit}")
print(f"\nBirebir örtüşen benchmark kaydı: {total_keys} / {len(d)} ({total_keys/len(d)*100:.1f}%)")

# arındırılmış kopya
purged = [x for x in d if norm(x['text']) not in overlap]
json.dump(purged, open(DATA/'appsec_benchmark_2000_purged.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)

# rapor
L=[]
def w(s=""): L.append(s)
w("# Sızıntı (Leakage) Re-Audit — v5 Eğitim Kaynaklarına Karşı")
w()
w("> **Not:** Gerçek v5 eğitim havuzu (71.440) Colab'da üretildi ve yerelde yok;")
w("> bu denetim erişilebilen **v5 kaynaklarının** normalize birebir eşleşmesini arar → **ALT SINIR**.")
w("> Gated/kapalı ve ~20 diğer kaynak taranmadı; yakın-kopya (near-dup) ve çapraz-dil (MT) aranmadı.")
w()
w(f"**Benchmark:** `appsec_benchmark_2000_curated.json` (N={len(d)})")
w()
w("| v5 eğitim adayı kaynak | Birebir örtüşen benchmark kaydı |")
w("|---|---:|")
for cid,(hit,n) in per_src.items():
    w(f"| {cid} | {hit} |")
w()
w(f"**Toplam birebir örtüşen: {total_keys} / {len(d)} (%{total_keys/len(d)*100:.1f}).**")
w()
w(f"Arındırılmış kopya: `data/appsec_benchmark_2000_purged.json` → **N={len(purged)}** (örtüşenler çıkarıldı).")
w()
w("## Yorum")
w("- Örtüşme, benchmark'ın bağımsız olmadığını gösterir (özellikle agregatör setler).")
w("- Yayın için: ya arındırılmış kopyayı kullan, ya da örtüşen kayıtları 'eğitim-görülmüş' olarak ayrı raporla.")
w("- Gerçek havuzla tam denetim Colab çıktısı gerektirir (train/val/test export).")
w()
w("_Üretildi: scripts/leakage_audit_and_purge.py_")
(ROOT/'docs'/'LEAKAGE_AUDIT.md').write_text("\n".join(L), encoding='utf-8')
print("\n[OK] -> docs/LEAKAGE_AUDIT.md ve data/appsec_benchmark_2000_purged.json")
