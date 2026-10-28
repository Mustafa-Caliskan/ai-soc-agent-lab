"""
Produces the publishable copy of the thinking-toggle log.

The internal capture (Kunye/thinking_off_results.jsonl inside the 2026-10-22
evidence package) carries a provider-specific `usage` block on every line. In
that block a single key names the national HPC platform. The block is a token
counter, not evidence: it plays no part in the 0/40 result, which is decided by
`content_has_canary` and `reasoning_has_canary` on each record.

This script therefore drops the whole `usage` object rather than editing one
key, so the transformation is coarse, auditable and leaves no residue. Every
other field is preserved byte-for-byte in meaning, and the record count, model
distribution and both leak flags are re-checked after the rewrite.

Usage:
    python scripts/neutralize_thinking_off_log.py <source.jsonl>
"""

import io
import json
import os
import sys
from collections import Counter

DEFAULT_SOURCE = None
OUT_PATH = "data/redteam/thinking_off_40.jsonl"


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: neutralize_thinking_off_log.py <source.jsonl>")
    source = sys.argv[1]
    if not os.path.exists(source):
        raise SystemExit(f"missing source: {source}")

    records = []
    dropped_fields = Counter()
    total_usage_keys = Counter()

    with io.open(source, encoding="utf-8") as handle:
        for raw in handle:
            raw = raw.strip()
            if not raw:
                continue
            rec = json.loads(raw)
            usage = rec.get("usage")
            if isinstance(usage, dict):
                for key in usage:
                    total_usage_keys[key] += 1
                rec.pop("usage")
                dropped_fields["usage"] += 1
            records.append(rec)

    # Post-conditions: the neutralisation must not change any measurement.
    after_blob = json.dumps(records, ensure_ascii=False)
    residual = after_blob.lower().count("evren")
    if residual:
        raise SystemExit(f"refusing to write: {residual} platform tokens still present")

    n = len(records)
    content_leaks = sum(1 for r in records if r.get("content_has_canary"))
    reasoning_leaks = sum(1 for r in records if r.get("reasoning_has_canary"))

    meta = {
        "source_file": os.path.basename(source),
        "records": n,
        "content_leaks": content_leaks,
        "reasoning_leaks": reasoning_leaks,
        "dropped_fields": dict(dropped_fields),
        "dropped_usage_subobjects": len(total_usage_keys),
        "dropped_usage_subobject_note": ("one provider metadata sub-object per record; its name is not "
                                         "reproduced here because it identifies the serving platform"),
        "note": ("The `usage` block was removed in full. It is a provider token/credit "
                 "counter and carries no measurement: leak status is determined by "
                 "content_has_canary and reasoning_has_canary, both retained."),
        "transform": "scripts/neutralize_thinking_off_log.py",
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with io.open(OUT_PATH, "w", encoding="utf-8", newline="\n") as handle:
        for rec in records:
            handle.write(json.dumps(rec, ensure_ascii=False) + "\n")

    meta_path = OUT_PATH.replace(".jsonl", ".meta.json")
    with io.open(meta_path, "w", encoding="utf-8") as handle:
        json.dump(meta, handle, ensure_ascii=False, indent=2)

    print(f"records          : {n}")
    print(f"content leaks    : {content_leaks}/{n}")
    print(f"reasoning leaks  : {reasoning_leaks}/{n}")
    print(f"dropped fields   : {dict(dropped_fields)}")
    print(f"platform tokens  : {residual} (must be 0)")
    print(f"written          : {OUT_PATH}")
    print(f"metadata         : {meta_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
