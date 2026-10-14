"""
NeuralShield-v5 — Bağımsız AppSec (Prompt-Injection) Benchmark Builder — Stage 1
=================================================================================
Amaç: YALNIZCA uygulama güvenliği (prompt injection / system-prompt exfil /
evasion / stego / agentic-tool injection) kapsamındaki, v5 EĞİTİMİNDE KULLANILMAYAN
bağımsız kaynaklardan temiz havuzlar kurmak.

Felsefe:
- AI-ethics / harmful-content (intihar, organ, ırkçılık, uyuşturucu, genel suç) KAPSAM DIŞI.
- v5 eğitim kaynakları + redteam_corpus + deepset ile SIFIR örtüşme.
- Çeviri-artığı (refusal) reddedilir.

Çıktı: data/_appsec_pool_attacks.json, data/_appsec_pool_benign.json
"""
import os, sys, re, json, unicodedata, urllib.parse
os.environ['HF_HUB_DISABLE_TELEMETRY']='1'; os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING']='1'
sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# ── Etik/harmful-content güvenlik filtresi (kapsam dışı) ─────────────────────
ETHICS_PAT = re.compile(
    r"(suicide|self[- ]?harm|intihar|organ (mafia|black market)|organ mafyas|genocide|soykırım|"
    r"ethnic cleansing|racial slur|ırkçı|nigger|whore|rape|tecavüz|child porn|cp\b|"
    r"methamphetamine|heroin|fentanyl|uyuşturucu|terorist|bomb making|bomba yapım|"
    r"bio[- ]?weapon|biyolojik silah|anthrax|ricin|sarin|nerve agent|chemical weapon|"
    r"kimyasal silah|poison a|zehirle|bestiality|incest|ensest|molest)", re.I)

# ── Salvage / çeviri-artığı filtresi (bunlar saldırı değil) ──────────────────
ARTIFACT_PAT = re.compile(
    r"(cannot be translated|can not be translated|no puedo traducir|ne peut pas être traduit|"
    r"ne peut pas etre traduit|нельзя перевести|не может быть переведен|翻訳できません|"
    r"번역할 수 없습니다|traduire|çevrilemez|çevrilem|i cannot|i can't help|as an ai|"
    r"sohbet edemem|yardımcı olamam|lo siento|申し訳ありません|죄송합니다|desculpe|نأسف|غير قادر)", re.I)

def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "")
    s = s.lower().strip()
    s = re.sub(r"\s+", " ", s)
    return s

# ── v5 eğitimi + redteam korpusu → decontaminasyon seti ──────────────────────
def load_contamination_set() -> set:
    cont = set()
    # redteam corpus + external (deepset)
    for f in [DATA/"redteam"/"redteam_corpus.json", DATA/"redteam"/"external_attacks.json"]:
        if f.exists():
            for x in json.load(open(f, encoding="utf-8")):
                for k in ("text","prompt","user_message","payload_instruction"):
                    if isinstance(x, dict) and x.get(k):
                        cont.add(norm(x[k]))
    # train/val CSVs
    import csv
    for f in [DATA/"train_multilingual.csv", DATA/"val_multilingual.csv", DATA/"test_multilingual.csv"]:
        if f.exists():
            with open(f, encoding="utf-8") as fh:
                for row in csv.DictReader(fh):
                    if row.get("text"):
                        cont.add(norm(row["text"]))
    return cont

CONTAMINATION = load_contamination_set()
print(f"[i] Decontaminasyon seti boyutu: {len(CONTAMINATION)}")

attacks, benign = [], []
seen = set()

def add(text, label, source, language="en", family="", difficulty="level_1_direct"):
    if not text or not isinstance(text, str):
        return
    t = text.strip()
    if len(t) < 12 or len(t) > 3000:
        return
    nt = norm(t)
    if nt in seen:
        return
    if nt in CONTAMINATION:
        return
    if ETHICS_PAT.search(t):
        return
    if ARTIFACT_PAT.search(t):
        return
    seen.add(nt)
    rec = {"text": t, "label": label, "language": language, "source": source,
           "attack_family": family, "difficulty": difficulty}
    (attacks if label == 1 else benign).append(rec)

# ── LOCAL bağımsız kapsam-içi kaynaklar ──────────────────────────────────────
def load_local():
    # benchmark_300 (bağımsız, kapsam-içi)
    f = DATA/"benchmark_300.json"
    if f.exists():
        for x in json.load(open(f, encoding="utf-8")):
            add(x["text"], int(x["label"]), "Local/benchmark_300",
                "tr" if re.search(r"[çğıöşüÇĞİÖŞÜ]", x["text"]) else "en",
                x.get("subcategory",""), "level_1_direct")
    # adaptive_adversarial_50
    f = DATA/"adaptive_adversarial_50.json"
    if f.exists():
        for x in json.load(open(f, encoding="utf-8")):
            add(x.get("prompt",""), 1, "Local/adaptive_adversarial_50", "tr",
                x.get("technique",""), "level_2_framing_persona")
    # elite suite
    f = DATA/"autoredteam_elite_suite.json"
    if f.exists():
        for x in json.load(open(f, encoding="utf-8")):
            add(x.get("prompt",""), int(x.get("label",1)), "Local/elite_suite", "tr",
                x.get("category",""), "level_2_framing_persona")
    # legacy handcrafted (benign IT + attack)
    f = DATA/"legacy_handcrafted_prompts.json"
    if f.exists():
        d = json.load(open(f, encoding="utf-8"))
        for t in d.get("benign", []):
            add(t, 0, "Local/legacy_handcrafted", "en", "technical_it_support", "level_1_direct")
        # legacy attack'leri SQLi gibi kısa teknik dizgeler; prompt niteliğinde değilse atla
        for t in d.get("attack", []):
            if len(str(t)) >= 25:
                add(t, 1, "Local/legacy_handcrafted", "en", "direct_injection", "level_1_direct")

load_local()
print(f"[+] Yerel sonrası -> attacks={len(attacks)} benign={len(benign)}")

# ── HF BAĞIMSIZ kaynaklar ────────────────────────────────────────────────────
try:
    from datasets import load_dataset
    HF_OK = True
except Exception as e:
    print("[!] datasets yok, sadece yerel:", e); HF_OK = False

def hf_iter(cid, split="train", cfg=None):
    ds = load_dataset(cid, cfg, split=split, streaming=True) if cfg else load_dataset(cid, split=split, streaming=True)
    for ex in ds:
        yield ex

if HF_OK:
    # 1) neuralchemy — SADECE 'original' source (harmbench/wildguard ethics → hariç)
    try:
        n=0
        for ex in hf_iter('neuralchemy/Prompt-injection-dataset'):
            n+=1
            src = str(ex.get('source',''))
            if src not in ('original',): continue
            cat = str(ex.get('category',''))
            if cat == 'benign':
                add(ex['text'], 0, 'HF/neuralchemy[original]', 'en', 'technical_it_support', 'level_1_direct')
            elif cat == 'jailbreak':
                add(ex['text'], 1, 'HF/neuralchemy[original]', 'en', 'persona_jailbreak', 'level_2_framing_persona')
            else:
                add(ex['text'], 1, 'HF/neuralchemy[original]', 'en', cat or 'direct_injection', 'level_1_direct')
        print(f"  neuralchemy scanned={n}")
    except Exception as e:
        print("  neuralchemy ERR", str(e)[:120])

    # 2) xTRam1 safe-guard
    try:
        n=0
        for ex in hf_iter('xTRam1/safe-guard-prompt-injection'):
            n+=1
            lab = str(ex.get('label'))
            add(ex['text'], 1 if lab=='1' else 0, 'HF/xTRam1/safe-guard', 'en',
                'persona_jailbreak' if lab=='1' else 'technical_it_support',
                'level_2_framing_persona' if lab=='1' else 'level_1_direct')
        print(f"  xTRam1 scanned={n}")
    except Exception as e:
        print("  xTRam1 ERR", str(e)[:120])

    # 3) reshabhs SPML chatbot injection
    try:
        n=0
        for ex in hf_iter('reshabhs/SPML_Chatbot_Prompt_Injection'):
            n+=1
            lab = str(ex.get('Prompt injection'))
            txt = ex.get('User Prompt') or ''
            if lab == '1':
                add(txt, 1, 'HF/reshabhs/SPML', 'en', 'direct_injection', 'level_2_framing_persona')
            else:
                add(txt, 0, 'HF/reshabhs/SPML', 'en', 'technical_it_support', 'level_1_direct')
        print(f"  reshabhs scanned={n}")
    except Exception as e:
        print("  reshabhs ERR", str(e)[:120])

    # 4) Lakera mosscap (Gandalf) — saldırı
    try:
        n=0
        for ex in hf_iter('Lakera/mosscap_prompt_injection'):
            n+=1
            add(ex.get('prompt',''), 1, 'HF/Lakera/mosscap', 'en', 'system_extraction', 'level_2_framing_persona')
        print(f"  Lakera/mosscap scanned={n}")
    except Exception as e:
        print("  Lakera ERR", str(e)[:120])

    # 5) rikka-snow multilingual (native çok dilli)
    try:
        n=0
        for ex in hf_iter('rikka-snow/prompt-injection-multilingual'):
            n+=1
            lab = str(ex.get('label'))
            add(ex.get('text',''), 1 if lab=='1' else 0, 'HF/rikka-snow/multilingual', 'en',
                'multilingual_jailbreak' if lab=='1' else 'technical_it_support', 'level_2_framing_persona')
        print(f"  rikka-snow scanned={n}")
    except Exception as e:
        print("  rikka-snow ERR", str(e)[:120])

    # 6) Horizon-Labs eval suite — notinject (benign hard-negative) + jailbreak setleri
    for cfg, lab, fam in [('notinject',0,'technical_it_support'),
                          ('simsonsun_jailbreaks',1,'persona_jailbreak'),
                          ('boundary_pairs_test',1,'semantic'),
                          ('orbench_hard',1,'persona_jailbreak')]:
        try:
            n=0
            for ex in hf_iter('Horizon-Labs/prompt-injection-eval-suite', split='test', cfg=cfg):
                n+=1
                txt = ex.get('text') or ex.get('prompt') or ''
                add(txt, lab, f'HF/Horizon/{cfg}', 'en', fam, 'level_2_framing_persona' if lab else 'level_1_direct')
            print(f"  Horizon/{cfg} scanned={n}")
        except Exception as e:
            print(f"  Horizon/{cfg} ERR", str(e)[:120])

print(f"\n[FINAL] attacks={len(attacks)} benign={len(benign)}")
print("  attack source:", dict(Counter(x['source'] for x in attacks)))
print("  benign source:", dict(Counter(x['source'] for x in benign)))
print("  attack lang:", dict(Counter(x['language'] for x in attacks)))

json.dump(attacks, open(DATA/"_appsec_pool_attacks.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(benign, open(DATA/"_appsec_pool_benign.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("  -> data/_appsec_pool_attacks.json & _appsec_pool_benign.json kaydedildi")
