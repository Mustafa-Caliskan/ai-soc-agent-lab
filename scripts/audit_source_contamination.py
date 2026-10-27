"""
Pre-registered source-contamination audit for the NeuralShield manuscript.

Criterion (fixed in docs/HAKEM_DUZELTME_PLANI.md, section E.3, before execution):

  normalisation : lowercase, strip punctuation, collapse whitespace
  unit          : word 8-gram
  primary rule  : an evaluation item is contaminated if AT LEAST ONE of its
                  8-grams also occurs in the training corpus
  strict rule   : an evaluation item is contaminated if AT LEAST 50% of its
                  8-grams occur in the training corpus
  evaluation set: data/appsec_benchmark_2000.json (all 2000 items)
  training set  : data/train_multilingual.csv + data/v6_multilingual_supplement.json
  lineage stat  : share of evaluation items whose `source` field names a public
                  training split at all

The criterion must not be tuned to reproduce any previously quoted figure. The
number produced here is the number reported in the manuscript.

Output: data/contamination_audit.json
"""

import csv
import io
import json
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")

NGRAM = 8
STRICT_FRACTION = 0.5
EVAL_PATH = "data/appsec_benchmark_2000.json"
TRAIN_CSV = "data/train_multilingual.csv"
TRAIN_JSON = "data/v6_multilingual_supplement.json"
OUT_PATH = "data/contamination_audit.json"

_PUNCT = re.compile(r"[^\w\s]", re.UNICODE)
_WS = re.compile(r"\s+", re.UNICODE)


def normalize(text):
    text = (text or "").lower()
    text = _PUNCT.sub(" ", text)
    return _WS.sub(" ", text).strip()


def ngrams(text, n=NGRAM):
    tokens = text.split()
    if len(tokens) < n:
        return set()
    return {" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)}


def load_training_ngrams():
    corpus = set()
    n_rows = 0

    with io.open(TRAIN_CSV, encoding="utf-8", errors="ignore") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            corpus |= ngrams(normalize(row.get("text", "")))
            n_rows += 1

    with io.open(TRAIN_JSON, encoding="utf-8", errors="ignore") as handle:
        for rec in json.load(handle):
            corpus |= ngrams(normalize(rec.get("text", "")))
            n_rows += 1

    return corpus, n_rows


def main():
    eval_items = json.load(io.open(EVAL_PATH, encoding="utf-8"))
    corpus, n_train = load_training_ngrams()

    primary_hits = 0
    strict_hits = 0
    lineage_hits = 0
    per_source = Counter()
    contaminated_by_source = Counter()
    empty = 0

    for item in eval_items:
        source = str(item.get("source") or "")
        if source:
            per_source[source] += 1
            if "HF/" in source or "huggingface" in source.lower():
                lineage_hits += 1

        grams = ngrams(normalize(item.get("text", "")))
        if not grams:
            empty += 1
            continue

        matched = len(grams & corpus)
        if matched:
            primary_hits += 1
            contaminated_by_source[source] += 1
        if matched / len(grams) >= STRICT_FRACTION:
            strict_hits += 1

    n = len(eval_items)
    result = {
        "criterion": {
            "pre_registered_in": "docs/HAKEM_DUZELTME_PLANI.md#E.3",
            "normalisation": "lowercase, punctuation stripped, whitespace collapsed",
            "unit": f"word {NGRAM}-gram",
            "primary_rule": "at least one 8-gram shared with the training corpus",
            "strict_rule": f"at least {int(STRICT_FRACTION * 100)}% of 8-grams shared",
            "evaluation_set": EVAL_PATH,
            "training_set": [TRAIN_CSV, TRAIN_JSON],
        },
        "counts": {
            "evaluation_items": n,
            "training_records": n_train,
            "training_distinct_ngrams": len(corpus),
            "items_too_short_for_ngram": empty,
            "primary_contaminated": primary_hits,
            "strict_contaminated": strict_hits,
            "items_with_public_source_field": lineage_hits,
        },
        "rates_pct": {
            "primary_contamination": round(100.0 * primary_hits / n, 2),
            "strict_contamination": round(100.0 * strict_hits / n, 2),
            "public_source_lineage": round(100.0 * lineage_hits / n, 2),
        },
        "per_source": {
            "top_sources": per_source.most_common(10),
            "top_contaminated_sources": contaminated_by_source.most_common(10),
        },
    }

    with io.open(OUT_PATH, "w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)

    print(f"evaluation items          : {n}")
    print(f"training records          : {n_train}")
    print(f"distinct training 8-grams : {len(corpus)}")
    print(f"primary contamination     : {result['rates_pct']['primary_contamination']}%")
    print(f"strict contamination      : {result['rates_pct']['strict_contamination']}%")
    print(f"public-source lineage     : {result['rates_pct']['public_source_lineage']}%")
    print(f"written: {OUT_PATH}")


if __name__ == "__main__":
    main()
