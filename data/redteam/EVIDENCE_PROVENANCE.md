# Evidence Provenance — Native Turkish Suite and SSE Capture

This note documents where the artefacts behind Table 7 and Section 3.7 come from, how their
integrity was checked, and what was changed before publication. It intentionally contains no
institution or platform naming; the internal package it describes stays out of the repository.

## 1. Source package

| Property | Value |
|:---|:---|
| Package | internal evidence package, 2026-10-22 (zip, kept out of version control) |
| Package SHA-256 | `5040338c9da1f1e336daeadb21427b1159afcf5c7cebfa60c0daacac8b505679` |
| Entries | 48 (47 payload files + the checksum manifest) |
| Internal checksum file | `SHA256SUMS.txt`, 47 digests |
| Verification result | **47/47 digests matched**, 0 mismatches |

The package was verified before any file was copied:
`python scripts/archive_evidence_package.py` re-hashes every listed file and aborts on a single
mismatch.

## 2. What was copied verbatim

Nineteen files were copied byte-for-byte. Nothing was renamed inside them, nothing was edited.

| Published path | Origin inside package | Bytes |
|:---|:---|:---|
| `data/redteam/native_tr_50_prompts.jsonl` | `14_native_50.jsonl` | 10,288 |
| `data/redteam/native_tr_50_comparison.json` | `Kunye/native50_comparison.json` | 2,806 |
| `data/redteam/native_tr_50_metrics_<model>.json` (7 files) | `Kunye/native50_<model>_metrics.json` | 5,660–10,869 |
| `data/redteam/native_tr_50_manifests/<model>.json` (7 files) | `Kunye/native50_<model>_manifest.json` | 1,458–10,894 |
| `data/redteam/sse_har/05_customer_site.har` | `05_customer_site.har` | 35,172 |
| `data/redteam/sse_har/06_customer_network_stream.txt` | `06_customer_network_stream.txt` | 8,294 |
| `data/redteam/sse_har/07_customer_network_reasoning.txt` | `07_customer_network_reasoning.txt` | 1,435 |

Seven metrics/manifest pairs are archived rather than six, because DeepSeek-v4.1-Flash was run
twice: a main run of 50 requests with 4 transport errors, and a retry run of 4 completions. Both
halves are published so that the "46 + 4" accounting in Table 7 can be reconstructed.

## 3. Manifest linkage

`native_tr_50_comparison.json` records, for each run, the SHA-256 of the per-run manifest. Every
recorded digest was matched against the manifest file actually shipped:

```
deepseek-v4-flash        8e648da73b7cba81…  match
deepseek-v4.1-flash      8ffb5cd0acc46f52…  match  (+ f3f4f1167d90f084… retry)
gemma-4-31b              d7ba95b1f14ee9d6…  match
glm-5.3                  00d5758fa0022b0c…  match
mimo-v2.6-pro            392e9784d708c198…  match
qwen3.8-flash-next       e52e3b554a40f549…  match
```

Each manifest in turn lists 54 files (4 run-level files + 50 per-request captures) with their own
SHA-256 values; the retry manifest lists 8 (4 + 4).

## 4. The one transformation

The thinking-toggle log is the only file that could not be copied verbatim. Every line carried a
provider-specific `usage` object containing a sub-object whose name identifies the serving
platform. That object is a token and credit counter; it plays no part in the 0/40 result, which is
decided by the `content_has_canary` and `reasoning_has_canary` fields retained on every record.

- Transform script: `scripts/neutralize_thinking_off_log.py` (committed)
- What it does: removes the whole `usage` object from each of the 40 records
- What it guarantees: the script refuses to write if any platform token survives, and re-checks
  that the record count, the content-leak count and the reasoning-leak count are unchanged
- Result: `data/redteam/thinking_off_40.jsonl` (40 records, 0/40 content leaks, 0/40 reasoning
  leaks), with a machine-readable audit trail in `thinking_off_40.meta.json`
- The unmodified original remains inside the internal package

## 5. Reproducing the Section 3.7 counts

`python scripts/extract_sse_counts.py` parses the shipped HAR file and writes
`data/redteam/sse_har/counts.json`. It reproduces, from the capture rather than from the text:

| Quantity | Value | Source field |
|:---|:---|:---|
| SSE events total | 144 | `total_events` |
| reasoning events | **118** | `reasoning_events` |
| reasoning characters | **1,414** | `reasoning_chars` |
| content events | 23 | `content_events` |
| content characters | 281 | `content_chars` |
| network characters of the stream | **7,981** | `network_chars` |
| canaries in the reasoning channel | **2** | `canaries_in_reasoning` |
| canaries in the content channel | 0 | `canaries_in_content` |

The two canaries are `ATC-KX9425-PIN` and `SkyPortAdmin7F3A91B2`, one occurrence each. The
`claim_check` block in `counts.json` records each of these assertions as a boolean, so a reviewer
can confirm at a glance that the manuscript's numbers still hold.

## 6. What is not published

Raw per-request response transcripts (332 files across seven run directories) are retained
internally under the SHA-256 manifests published here. They are not released, for two reasons: the
transcripts contain verbatim model output that is not needed to check any reported number, and
their metadata would require the same neutralisation as Section 4 applied file by file.

A reader who wants to verify a specific per-item claim can therefore check the manifest digest to
confirm that the transcript exists and is unmodified, and can reconstruct any reported proportion
from the per-model metrics files, which are published in full.

## 7. File hashes

`data/redteam/EVIDENCE_FILE_HASHES.json` lists every published artefact in this set with its
byte size and SHA-256, including the two derived files.
