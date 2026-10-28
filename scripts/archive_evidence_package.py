"""
Archives the publishable subset of the internal evidence package.

Source   : SSB_Musteri_Kanit_Paketi_20261022.zip in the repository root
           (internal package, never committed; listed in .gitignore)
Target   : data/redteam/

Only files that carry no institution or platform naming are copied verbatim.
The one file that does carry such naming (the thinking-toggle log, in its
`usage` block) is passed through scripts/neutralize_thinking_off_log.py, and the
original stays in the zip.

The script verifies the package before copying:
  * SHA256SUMS.txt covers 47 of 48 entries and all 47 hashes must match;
  * the six run manifests referenced by native50_comparison.json must hash to
    the digests recorded inside that comparison file.

Usage: python scripts/archive_evidence_package.py
"""

import glob
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import zipfile

ZIP = "SSB_Musteri_Kanit_Paketi_20261022.zip"
PREFIX = "SSB_Musteri_Kanit_Paketi_20261022/"
DEST = "data/redteam"

# model -> published file stem. The retry run is a separate endpoint entry and
# is archived alongside the main run so that 46 + 4 is auditable.
MODELS = [
    "gemma-4-31b",
    "qwen3.8-flash-next",
    "deepseek-v4-flash",
    "deepseek-v4.1-flash",
    "deepseek-v4.1-flash_retry",
    "glm-5.3",
    "mimo-v2.6-pro",
]

VERBATIM = [
    ("14_native_50.jsonl", "native_tr_50_prompts.jsonl"),
    ("Kunye/native50_comparison.json", "native_tr_50_comparison.json"),
    ("05_customer_site.har", "sse_har/05_customer_site.har"),
    ("06_customer_network_stream.txt", "sse_har/06_customer_network_stream.txt"),
    ("07_customer_network_reasoning.txt", "sse_har/07_customer_network_reasoning.txt"),
]


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def verify_package(z):
    sums = z.read(PREFIX + "SHA256SUMS.txt").decode("utf-8", "ignore")
    lines = [l.strip() for l in sums.splitlines() if l.strip()]
    ok = bad = 0
    for line in lines:
        parts = line.split()
        if len(parts) < 2:
            continue
        digest, name = parts[0], parts[-1].lstrip("*")
        cands = [n for n in z.namelist() if n.endswith("/" + name) or n.endswith(name)]
        if not cands:
            bad += 1
            continue
        if sha256(z.read(cands[0])).lower() == digest.lower():
            ok += 1
        else:
            bad += 1
    print(f"SHA256SUMS: {ok}/{len(lines)} verified, {bad} problems")
    if bad or ok != len(lines):
        raise SystemExit("package integrity check failed")

    comparison = json.loads(z.read(PREFIX + "Kunye/native50_comparison.json").decode("utf-8"))
    for run in comparison["runs"]:
        model = run["model"]
        manifest_name = f"Kunye/native50_{model}_manifest.json"
        if PREFIX + manifest_name not in z.namelist():
            raise SystemExit(f"missing manifest for {model}")
        digest = sha256(z.read(PREFIX + manifest_name))
        if digest not in run["manifest_sha256"]:
            raise SystemExit(f"{model}: manifest hash not listed in comparison.json")
    print(f"manifest linkage: {len(comparison['runs'])} runs consistent with comparison.json")
    return ok


def main():
    if not os.path.exists(ZIP):
        raise SystemExit(f"missing {ZIP}")

    os.makedirs(os.path.join(DEST, "sse_har"), exist_ok=True)
    os.makedirs(os.path.join(DEST, "native_tr_50_manifests"), exist_ok=True)

    z = zipfile.ZipFile(ZIP)
    verified = verify_package(z)

    written = []
    for src, dst in VERBATIM:
        data = z.read(PREFIX + src)
        out = os.path.join(DEST, dst.replace("/", os.sep))
        with open(out, "wb") as handle:
            handle.write(data)
        written.append((src, out, sha256(data), len(data)))

    for model in MODELS:
        for kind, pattern, target_dir in (
            ("metrics", f"Kunye/native50_{model}_metrics.json", None),
            ("manifest", f"Kunye/native50_{model}_manifest.json", "native_tr_50_manifests"),
        ):
            if PREFIX + pattern not in z.namelist():
                raise SystemExit(f"missing {pattern}")
            data = z.read(PREFIX + pattern)
            name = (f"native_tr_50_metrics_{model}.json" if kind == "metrics"
                    else f"{model}.json")
            out = (os.path.join(DEST, name) if target_dir is None
                   else os.path.join(DEST, target_dir, name))
            with open(out, "wb") as handle:
                handle.write(data)
            written.append((pattern, out, sha256(data), len(data)))

    tmp = os.path.join(DEST, "_thinking_off_source.jsonl")
    with open(tmp, "wb") as handle:
        handle.write(z.read(PREFIX + "Kunye/thinking_off_results.jsonl"))
    rc = subprocess.call([sys.executable, "scripts/neutralize_thinking_off_log.py", tmp])
    os.remove(tmp)
    if rc != 0:
        raise SystemExit("neutralisation failed")

    rc = subprocess.call([sys.executable, "scripts/extract_sse_counts.py"])
    if rc != 0:
        raise SystemExit("SSE count reproduction failed")

    print(f"\nSHA256SUMS entries verified : {verified}")
    print(f"files archived              : {len(written)} verbatim + 2 derived")
    for src, out, digest, size in written:
        print(f"  {src:<48s} -> {out}  ({size} B)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
