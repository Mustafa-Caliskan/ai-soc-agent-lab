"""
NeuralShield-v5 â€” AppSec Benchmark Builder â€” Stage 2
=====================================================
Havuzlardan (Stage 1) temiz, dengeli, 12-dilli 2.000 Ã¶rnekli benchmark kurar.

TasarÄ±m: en=500 (250/250), tr=500 (250/250), 10 dil x100 (50/50)
MT: EVREN API (reasoning modeller), batched + concurrent, artifact filtreli.

KullanÄ±m:
  python scripts/build_appsec_benchmark_v2_stage2.py --test      # 8 Ã¶rnekle MT testi
  python scripts/build_appsec_benchmark_v2_stage2.py             # tam kurulum
  python scripts/build_appsec_benchmark_v2_stage2.py --no-mt     # sadece EN/TR native
"""
import os, sys, re, json, time, argparse, unicodedata, threading
os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
from pathlib import Path
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT / "backend"))

SEED = 42
import random; random.seed(SEED)

LANGS_10 = ["ja","ko","ar","ru","de","fr","es","it","zh","pt"]
LANG_NAME = {"ja":"Japanese","ko":"Korean","ar":"Arabic","ru":"Russian","de":"German",
             "fr":"French","es":"Spanish","it":"Italian","zh":"Chinese","pt":"Portuguese",
             "tr":"Turkish","en":"English"}
TARGET = {"en":500,"tr":500, **{l:100 for l in LANGS_10}}  # her dil toplam, 50/50

ARTIFACT_PAT = re.compile(
    r"(cannot be translated|can not be translated|no puedo traducir|ne peut pas Ãªtre traduit|"
    r"Ğ½ĞµĞ»ÑŒĞ·Ñ Ğ¿ĞµÑ€ĞµĞ²ĞµÑÑ‚Ğ¸|ç¿»è¨³ã§ãã¾ã›ã‚“|ë²ˆì—­í•  ìˆ˜ ì—†ìŠµë‹ˆë‹¤|Ã§evrilemez|i cannot|i can't help|"
    r"as an ai|lo siento|ç”³ã—è¨³ã‚ã‚Šã¾ã›ã‚“|ì£„ì†¡í•©ë‹ˆë‹¤|desculpe|here is the translation|"
    r"translation:|Ã§evirisi:|ç¿»è¨³ï¼š|ë²ˆì—­:)", re.I)
ETHICS_PAT = re.compile(
    r"(suicide|self[- ]?harm|intihar|organ mafya|organ black market|genocide|soykÄ±rÄ±m|"
    r"racial slur|Ä±rkÃ§Ä±|rape|tecavÃ¼z|heroin|fentanyl|methamphetamine|bomb making|bomba yapÄ±m|"
    r"bio[- ]?weapon|biyolojik silah|ricin|sarin|nerve agent|chemical weapon|kimyasal silah)", re.I)

JUNK_PAT = re.compile(r"(test raporu|test report|ğŸ“Š|ğŸ§ª|kelime ezberi|\bv\d+\.\d+\b|debug log|traceback)", re.I)

ATTACK_OK_SOURCES = {
 "HF/reshabhs/SPML","HF/Lakera/mosscap","HF/xTRam1/safe-guard",
 "HF/Horizon/simsonsun_jailbreaks","HF/Horizon/orbench_hard","HF/neuralchemy[original]",
 "HF/rikka-snow/multilingual","Local/benchmark_300","Local/adaptive_adversarial_50","Local/elite_suite",
}

INJECTION_MARKER = re.compile(
    r"(ignore|disregard|forget|override|overrid|bypass|system prompt|system message|"
    r"developer mode|do anything now|\bDAN\b|act as|you are now|pretend|roleplay|role-play|"
    r"reveal|expose|leak|print (?:your|the|all)|output (?:your|the|all)|list (?:all|the)|"
    r"instructions|previous|new (?:task|instruction|prompt|rule)|jailbreak|"
    r"base64|rot13|hex|decode|execute|internal|confidential|secret|password|passwd|"
    r"api[_ ]?key|credential|admin|sudo|token|config|talimat|y[Ã¶o]nerge|ÅŸifre|sistem prompt|"
    r"unrestricted|no restrictions|without restrictions|hidden|verbatim)", re.I)

def norm(s):
    s = unicodedata.normalize("NFKC", s or "").lower().strip()
    return re.sub(r"\s+", " ", s)

def has_cyrillic_or_cjk(s):
    return any(0x0400<=ord(c)<=0x04FF or 0x3040<=ord(c)<=0x30FF or 0x4E00<=ord(c)<=0x9FFF
               or 0xAC00<=ord(c)<=0xD7A3 or 0x0600<=ord(c)<=0x06FF for c in s)

# â”€â”€ Curation â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def curate(pool, n, *, prefer_sources=None, source_cap=None, min_len=20, max_len=900,
           require_latin_only=False, require_pattern=None, forbid_pattern=None):
    """Kaynak-Ã§eÅŸitliliÄŸi ve kalite gÃ¶zeterek n Ã¶rnek seÃ§er."""
    random.shuffle(pool)
    out, cnt = [], Counter()
    for rec in pool:
        t = rec["text"].strip()
        if not (min_len <= len(t) <= max_len):
            continue
        if ETHICS_PAT.search(t) or ARTIFACT_PAT.search(t) or JUNK_PAT.search(t):
            continue
        # tek-token / URL / paket-adÄ± artÄ±klarÄ± (Ã¶r. 'protectai/deberta-v3-...')
        if re.fullmatch(r"[\w./:@\-]+", t):
            continue
        if require_latin_only and has_cyrillic_or_cjk(t):
            continue
        if require_pattern and not require_pattern.search(t):
            continue
        if forbid_pattern and forbid_pattern.search(t):
            continue
        src = rec["source"]
        if source_cap and cnt[src] >= source_cap:
            continue
        if prefer_sources and src not in prefer_sources:
            continue
        out.append(rec); cnt[src] += 1
        if len(out) >= n:
            break
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true")
    ap.add_argument("--no-mt", action="store_true")
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()

    attacks = json.load(open(DATA/"_appsec_pool_attacks.json", encoding="utf-8"))
    benign  = json.load(open(DATA/"_appsec_pool_benign.json", encoding="utf-8"))
    # Dil netliÄŸi: Ã§ift-dilli yerel benchmark_300'Ã¼ (etiket belirsizliÄŸi) ve legacy attack'i Ã§Ä±kar.
    # Yerel TÃ¼rkÃ§e kaynaklarÄ± 'tr' olarak sabitle.
    attacks = [r for r in attacks if not r["source"].startswith("Local/benchmark_300")]
    benign  = [r for r in benign  if not r["source"].startswith("Local/benchmark_300")]
    for r in attacks + benign:
        if r["source"].startswith(("Local/adaptive_adversarial_50","Local/elite_suite")):
            r["language"] = "tr"
        elif r["source"].startswith("Local/legacy_handcrafted"):
            r["language"] = "en"
    en_pool_a = [r for r in attacks if r["language"] == "en"]
    en_pool_b = [r for r in benign  if r["language"] == "en"]
    print(f"[i] Havuz (dil-nette): attacks={len(attacks)} benign={len(benign)} | EN attack={len(en_pool_a)} EN benign={len(en_pool_b)}")

    need_atk_en = TARGET["en"]//2      # 250
    need_ben_en = TARGET["en"]//2
    need_atk_per = {l: TARGET[l]//2 for l in ["tr"]+LANGS_10}   # tr:250, diger:50
    need_ben_per = dict(need_atk_per)

    # EN attack core: gÃ¼venilir injection kaynaklarÄ± + marker zorunlu + kaynak cap
    en_attacks = curate(en_pool_a, need_atk_en, source_cap=40, require_pattern=INJECTION_MARKER,
                        prefer_sources=ATTACK_OK_SOURCES)
    # EN benign core: IT/notinject Ã¶ncelikli, injection-marker YASAK
    prefer = {"Local/legacy_handcrafted",
              "HF/Horizon/notinject","HF/neuralchemy[original]"}
    en_benign_a = curate(en_pool_b, need_ben_en, prefer_sources=prefer, source_cap=120,
                         forbid_pattern=INJECTION_MARKER)
    if len(en_benign_a) < need_ben_en:
        extra = curate([b for b in en_pool_b if b not in en_benign_a],
                       need_ben_en-len(en_benign_a), source_cap=80, forbid_pattern=INJECTION_MARKER)
        en_benign = en_benign_a + extra
    else:
        en_benign = en_benign_a
    print(f"[+] EN core: attacks={len(en_attacks)} benign={len(en_benign)}")
    print("    EN attack src:", dict(Counter(x['source'] for x in en_attacks)))
    print("    EN benign src:", dict(Counter(x['source'] for x in en_benign)))

    if args.test:
        print("[TEST MODU] 3 attack + 3 benign -> fr MT denemesi")
        sample = en_attacks[:3] + en_benign[:3]
        translated = translate_batch(sample, "fr", workers=args.workers, test=True)
        for s, t in zip(sample, translated):
            print(f"   EN: {s['text'][:80]!r}\n   FR: {(t or 'FAIL')[:80]!r}")
        return

    # â”€â”€ Ã‡ok dilli Ã¼retim â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    records = []
    for r in en_attacks: r2=dict(r); r2["language"]="en"; records.append(r2)
    for r in en_benign:  r2=dict(r); r2["language"]="en"; records.append(r2)

    if not args.no_mt:
        # TR: native mÃ¼mkÃ¼n olduÄŸunca kullan, kalanÄ± MT
        tr_native_atk = [a for a in attacks if a["language"]=="tr"]
        tr_native_ben = [b for b in benign if b["language"]=="tr"]
        tr_native_atk = curate(tr_native_atk, need_atk_per["tr"], source_cap=999)
        tr_native_ben = curate(tr_native_ben, need_ben_per["tr"], source_cap=999)
        print(f"    TR native: attacks={len(tr_native_atk)} benign={len(tr_native_ben)}")
        for r in tr_native_atk: r2=dict(r); r2["language"]="tr"; records.append(r2)
        for r in tr_native_ben: r2=dict(r); r2["language"]="tr"; records.append(r2)
        # TR MT-fill
        tr_atk_src = en_attacks[len(tr_native_atk): need_atk_per["tr"]]
        tr_ben_src = en_benign[len(tr_native_ben): need_ben_per["tr"]]
        fill_mt(records, tr_atk_src, tr_ben_src, "tr", args.workers)
        # 10 langs
        for lang in LANGS_10:
            a_src = en_attacks[:need_atk_per[lang]]
            b_src = en_benign[:need_ben_per[lang]]
            fill_mt(records, a_src, b_src, lang, args.workers)
    else:
        # native TR yoksa EN kopyala (uyarÄ±)
        for r in en_attacks[:need_atk_per["tr"]]:
            r2=dict(r); r2["language"]="tr"; r2["source"]+="[TR-copy]"; records.append(r2)

    assemble_and_save(records)

def fill_mt(records, atk_src, ben_src, lang, workers):
    print(f"    [{lang}] MT: {len(atk_src)} attack + {len(ben_src)} benign ...", flush=True)
    src = atk_src + ben_src
    translated = translate_batch(src, lang, workers=workers)
    n_ok = 0
    for rec, tr in zip(src, translated):
        if not tr: continue
        t = tr.strip().strip('"').strip()
        if len(t) < 8 or ARTIFACT_PAT.search(t): continue
        if ETHICS_PAT.search(t): continue
        r2 = dict(rec); r2["text"] = t; r2["language"] = lang; r2["source"] += f"[MT->{lang}]"
        records.append(r2); n_ok += 1
    print(f"        -> {n_ok}/{len(src)} Ã§eviri baÅŸarÄ±lÄ±")

def translate_batch(records, lang, workers=6, test=False):
    from evren_client import EvrenClient
    client = EvrenClient()
    if not client.is_configured:
        print("[!] EVREN yapÄ±landÄ±rÄ±lmamÄ±ÅŸ"); return [None]*len(records)
    name = LANG_NAME[lang]
    B = 5
    batches = [(i, records[i:i+B]) for i in range(0, len(records), B)]
    results = [None]*len(records)
    lock = threading.Lock()

    def do_batch(item):
        start, chunk = item
        texts = [c["text"] for c in chunk]
        sysmsg = (f"You are a professional translator for a cybersecurity benchmark. Translate each user "
                  f"text into {name}. Preserve technical meaning exactly (prompt-injection terms). "
                  f"Return ONLY a JSON array of {len(texts)} translated strings in the same order. No markdown.")
        user = json.dumps(texts, ensure_ascii=False)
        for attempt in range(3):
            r = client.generate_chat(user, system_instruction=sysmsg, model="gemma-4-31b",
                                     max_tokens=2500, temperature=0.0)
            content = (r.get("content") or "").strip()
            if not content:
                time.sleep(1.5); continue
            m = re.search(r"\[.*\]", content, re.DOTALL)
            if not m:
                time.sleep(1.0); continue
            try:
                arr = json.loads(m.group(0))
                if isinstance(arr, list) and len(arr) == len(texts):
                    return start, [str(x) for x in arr]
            except Exception:
                pass
            time.sleep(1.0)
        # fallback: tekil Ã§eviri
        singles = []
        for t in texts:
            rr = client.generate_chat(f"Translate into {name}. Output only the translation:\n\n{t}",
                                      model="gemma-4-31b", max_tokens=2500, temperature=0.0)
            singles.append((rr.get("content") or "").strip() or None)
        return start, singles

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(do_batch, it): it for it in batches}
        done = 0
        for f in as_completed(futs):
            start, arr = f.result()
            with lock:
                for j, v in enumerate(arr):
                    if start+j < len(results):
                        results[start+j] = v
                done += 1
                if done % 5 == 0 or test:
                    print(f"        ... {done}/{len(batches)} batch", flush=True)
    return results

def assemble_and_save(records):
    # global dedup (normalize) â€” dil-etiket kaymalarÄ±ndan kalan kopyalarÄ± temizle
    seen = set(); deduped = []
    for r in records:
        k = norm(r["text"])
        if k in seen:
            continue
        seen.add(k); deduped.append(r)
    records = deduped
    # etiket/language sayÄ±larÄ±
    by = defaultdict(lambda: [0,0])  # lang -> [benign, attack]
    for r in records:
        by[r["language"]][r["label"]] += 1
    # hedefe gÃ¶re kÄ±rp
    final = []
    for lang, tot in TARGET.items():
        half = tot//2
        atk = [r for r in records if r["language"]==lang and r["label"]==1][:half]
        ben = [r for r in records if r["language"]==lang and r["label"]==0][:half]
        final += atk + ben
        print(f"   {lang}: attack={len(atk)}/{half}  benign={len(ben)}/{half}")
    random.shuffle(final)
    for i, r in enumerate(final, 1):
        r["id"] = f"APPSEC_{i:04d}"
        r.setdefault("difficulty","level_2_framing_persona" if r["label"]==1 else "level_1_direct")
    DATA.joinpath("appsec_benchmark_2000.json").write_text(json.dumps(final, ensure_ascii=False, indent=1), encoding="utf-8")
    # CSV
    import csv
    with open(DATA/"appsec_benchmark_2000.csv","w",newline="",encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["id","text","label","language","source","attack_family","difficulty"])
        w.writeheader()
        for r in final: w.writerow({k:r.get(k,"") for k in w.fieldnames})
    # metadata
    meta = {
      "dataset_name":"NeuralShield-v5 AppSec (Prompt-Injection) Independent Benchmark",
      "version":"3.0.0-appsec","total_samples":len(final),
      "classes":{"Attack(1)":sum(1 for r in final if r["label"]==1),"Benign(0)":sum(1 for r in final if r["label"]==0)},
      "language_breakdown":dict(Counter(r["language"] for r in final)),
      "attack_source_breakdown":dict(Counter(r["source"] for r in final if r["label"]==1).most_common()),
      "benign_source_breakdown":dict(Counter(r["source"] for r in final if r["label"]==0).most_common()),
      "note":"Yalnizca AppSec/prompt-injection kapsami. Ethics/harmful-content kapsam disi. v5 egitim setleriyle sifir ortusme. MT ile uretilen diller [MT->xx] ile isaretli."
    }
    DATA.joinpath("appsec_benchmark_2000_metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n[FINAL] N={len(final)} | classes={meta['classes']}")
    print("  lang:", meta["language_breakdown"])
    print("  -> data/appsec_benchmark_2000.{json,csv,_metadata.json}")

if __name__ == "__main__":
    main()
