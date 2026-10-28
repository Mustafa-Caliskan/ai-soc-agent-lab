"""
Accuracy gate for the manuscript.

Unlike a string-equality check, this script *recomputes* every derived statistic
from its (k, n) / (tp, fp, fn) / (b, c) inputs and compares the result with both
the manifest and the rendered manuscript. A manifest that encodes a wrong number
therefore fails, it does not lock the error in.

Checks
  1. derivation   : recompute pct / wilson / f1_binary / f1_macro / mcnemar / difference
  2. source       : the value still equals the value at its JSON path
  3. presence     : every `renders` string appears in docs/CI_MANUSCRIPT_EN.md
  4. forbidden    : retired numbers and retired terminology are absent

Exit code 1 on any failure.
"""

import io
import json
import math
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

MANIFEST = "data/paper_metrics_manifest.json"
MANUSCRIPT = "docs/CI_MANUSCRIPT_EN.md"
TOL = 0.051

# Retired figures and retired framing.
#
# Bare "pilot" is deliberately NOT forbidden: Section 3.9.1 is titled "The
# Fallacy of Small-Sample Pilots", which is the correct scientific term for the
# n=25 study compared in Table 10. What must never return is the *framing* that
# was applied to the native Turkish suite and the SSE capture before their
# artefacts were released.
FORBIDDEN = [
    # retired numbers
    "76.9", "89.11", "95.50", "98.12", "86.50", "92.30", "49.03",
    "74.10% to 53.30% even when paired with L0",
    # retired layer terminology
    "four-layer", "five defenses",
    # retired claims
    "32–50 ms", "32-50 ms", "attention cross-talk",
    "same statistic to two decimals", "statistically measurable",
    # unreferenced source names
    "Jackhhao", "SPML",
    # retired framing of the native suite / SSE capture
    "red-team pilot", "pilot observation", "observational case study",
    "artefacts are not released", "artifacts are not released",
]

FAIL = []
WARN = []


def read_source(source):
    """Loads a source payload described by a manifest `source` entry.

    Supports plain JSON with a dotted/bracketed path, and JSONL with an
    aggregate (`records`, `count_true` on a field).
    """
    path = source["file"]
    if source.get("format") == "jsonl":
        rows = []
        with io.open(path, encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        agg = source.get("aggregate")
        if agg == "records":
            return len(rows)
        if agg == "count_true":
            return sum(1 for r in rows if r.get(source["field"]))
        if agg == "count_false":
            return sum(1 for r in rows if not r.get(source["field"]))
        raise ValueError(f"unknown jsonl aggregate {agg}")

    with io.open(path, encoding="utf-8") as handle:
        doc = json.load(handle)
    return resolve(doc, source["path"])


def resolve(doc, path):
    """Resolve a dotted path that may contain bracketed indices and dots in keys."""
    if path in ("", None):
        return doc
    parts = path.split(".")
    node = doc
    i = 0
    while i < len(parts):
        part = parts[i]
        # fold trailing numeric fragments back into the key when lookup fails
        candidates = [part]
        j = i + 1
        while j < len(parts):
            candidates.append(".".join(parts[i:j + 1]))
            j += 1
        matched = False
        for cand in candidates:
            key, _, idx = cand.partition("[")
            try:
                nxt = node[key] if key else node
            except (KeyError, TypeError, IndexError):
                continue
            if idx:
                nxt = nxt[int(idx.rstrip("]"))]
            node = nxt
            i += cand.count(".") + 1
            matched = True
            break
        if not matched:
            raise KeyError(f"cannot resolve '{path}' at '{part}'")
    return node


def wilson(k, n, z=1.96):
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return [round((centre - half) * 100, 2), round((centre + half) * 100, 2)]


def mcnemar_exact(b, c):
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(min(b, c) + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def check_derivation(entry):
    d = entry["derive"]
    stat = d["statistic"]
    if stat == "pct":
        return 100.0 * d["k"] / d["n"]
    if stat == "wilson":
        return wilson(d["k"], d["n"])
    if stat == "f1_binary":
        return 100.0 * 2 * d["tp"] / (2 * d["tp"] + d["fp"] + d["fn"])
    if stat == "f1_macro":
        f_mal = 2 * d["tp"] / (2 * d["tp"] + d["fp"] + d["fn"])
        f_ben = 2 * d["tn"] / (2 * d["tn"] + d["fp"] + d["fn"])
        return 100.0 * (f_mal + f_ben) / 2
    if stat == "mcnemar":
        return mcnemar_exact(d["b"], d["c"])
    if stat == "difference":
        return d["a"] - d["b"]
    if stat == "discordant":
        return [d["b"], d["c"]]
    raise ValueError(f"unknown statistic {stat}")


def close(actual, expected, tol=TOL):
    if isinstance(expected, (list, tuple)):
        if not isinstance(actual, (list, tuple)) or len(actual) != len(expected):
            return False
        return all(abs(a - e) <= tol for a, e in zip(actual, expected))
    return abs(actual - expected) <= tol


def check_marginals(entry):
    """McNemar bookkeeping must close against the two ASR numerators.

    The 2x2 table is leak/no-leak under each configuration:
        total_base      = both + c          (e.g. FP16 = 8 + 9 = 17)
        total_candidate = both + b          (e.g. 4-bit = 8 + 7 = 15)
        both            = total_candidate - b = total_base - c
        total_base - total_candidate == c - b           (17-15 == 9-7)
        both + b + c <= n                               (8+7+9 <= 101)

    Swapping the two discordant labels breaks the difference identity and the
    `both` agreement, which is exactly the error this gate exists to catch.
    """
    d = entry["derive"]
    n, b, c = d["n"], d["b"], d["c"]
    tot_base, tot_cand = d["tot_base"], d["tot_candidate"]
    problems = []

    both_from_cand = tot_cand - b
    both_from_base = tot_base - c
    if both_from_cand < 0 or both_from_base < 0:
        problems.append(f"negative agreement cell ({both_from_cand}, {both_from_base})")
    if both_from_cand != both_from_base:
        problems.append(
            f"agreement cell disagrees: total_candidate-b={both_from_cand} "
            f"vs total_base-c={both_from_base}")
    if (tot_base - tot_cand) != (c - b):
        problems.append(
            f"marginal identity broken: totals differ by {tot_base - tot_cand} "
            f"but discordant counts differ by {c - b}")
    if both_from_cand + b + c > n:
        problems.append(f"cells exceed n ({both_from_cand}+{b}+{c} > {n})")
    return problems, both_from_cand


def main():
    manifest = json.load(io.open(MANIFEST, encoding="utf-8"))
    text = io.open(MANUSCRIPT, encoding="utf-8").read()

    n_checked = 0
    for entry in manifest["entries"]:
        mid = entry["id"]
        status = entry.get("status", "measured")
        value = entry["value"]

        # 1. recompute
        if entry.get("derive"):
            try:
                recomputed = check_derivation(entry)
            except Exception as exc:  # noqa: BLE001
                FAIL.append(f"{mid}: derivation error {exc}")
                continue
            if not close(recomputed, value, entry.get("tol") or TOL):
                FAIL.append(f"{mid}: recomputed {recomputed} != manifest {value}")
            if entry["derive"].get("statistic") == "discordant":
                problems, common = check_marginals(entry)
                for problem in problems:
                    FAIL.append(f"{mid}: {problem}")
                print(f"marginals {mid}: n={entry['derive']['n']} both={common} "
                      f"b(4-bit only)={entry['derive']['b']} c(FP16 only)={entry['derive']['c']} "
                      f"totals(FP16/4-bit)={entry['derive']['tot_base']}/{entry['derive']['tot_candidate']} -> "
                      f"{'OK' if not problems else 'FAIL'}")
            n_checked += 1

        # 2. source agreement
        if entry.get("source"):
            try:
                src = read_source(entry["source"])
            except Exception as exc:  # noqa: BLE001
                FAIL.append(f"{mid}: source path error {exc}")
                src = None
            if src is not None:
                scale = entry.get("source_scale", 1.0)
                tol = entry.get("tol") or TOL
                try:
                    if isinstance(src, list) and all(isinstance(x, (int, float)) for x in src):
                        scaled = [float(x) * scale for x in src]
                        if isinstance(value, list) and not close(scaled, value, tol):
                            FAIL.append(f"{mid}: source {src} != manifest {value}")
                    elif isinstance(src, (int, float)) and not isinstance(src, bool):
                        if not close(float(src) * scale, value, tol):
                            FAIL.append(f"{mid}: source {src} (x{scale}) != manifest {value}")
                except (TypeError, ValueError):
                    FAIL.append(f"{mid}: non-numeric source value {src!r}")
                n_checked += 1

        # 3. presence in the manuscript
        if status != "pilot-observation":
            for rendered in entry.get("renders", []):
                if not rendered:
                    continue
                pattern = r"(?<![\d.,])" + re.escape(rendered) + r"(?![\d])"
                if not re.search(pattern, text):
                    FAIL.append(f"{mid}: '{rendered}' missing from manuscript")

        if status == "pilot-observation":
            WARN.append(f"{mid}: pilot observation, not backed by a released artefact")

    for token in FORBIDDEN:
        pattern = r"(?<![\d.,])" + re.escape(token) + r"(?![\d])" if token[0].isdigit() else re.escape(token)
        if re.search(pattern, text):
            FAIL.append(f"forbidden token still present: '{token}'")

    print(f"entries          : {manifest['entry_count']}")
    print(f"values verified  : {n_checked}")
    for warn in WARN:
        print(f"WARN: {warn}")
    if FAIL:
        print(f"\n=== {len(FAIL)} FAILURE(S) ===")
        for failure in FAIL:
            print(f"FAIL: {failure}")
        return 1
    print("\nPASS: all metrics recompute, match their sources, and appear as rendered.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
