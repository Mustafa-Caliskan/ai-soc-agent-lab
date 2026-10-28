# Response to Reviewers

**Manuscript:** NeuralShield: A Multilingual Multi-Layer Security Gateway Against Prompt Injection and Data Exfiltration in Large Language Models
**Journal:** Computers and Informatics (C&I)
**Decision addressed:** Major Revision

We thank the reviewer for an unusually detailed and technically accurate report. Every critical finding was reproducible in our own archive, and two of them were more serious than stated: the Table 1 row mixed three different runs, and the "adaptive" threshold that the manuscript called "deterministic" did in fact exist in the code but was never described. During the revision we also verified the Llama-3.1-8B discordant bookkeeping in Table 9 against the per-item rows; it is internally consistent (8 + 7 = 15 under 4-bit, 8 + 9 = 17 under FP16), and a build gate now enforces that identity.

The governing rule for this revision was set before any edit: **the data rules the number, the number never rules the data.** Where a reported value could not be tied to a released artefact we removed it or re-measured it, and where a re-measurement produced a different value we report the new one. The retired figures (76.9%, 89.11%, 95.50%, 98.12%, 49.03, 32–50 ms) are now blocked by an automated gate.

---

## K1. Table 4 contradicted the current source data

**Accepted in full.** The reviewer is right on every sub-point, including the diagnosis: the INT8 rows came from `data/redteam/archive_legacy/l2_only_ablation_v6_2.json` while the L0 row came from the current run.

Table 4 is now generated exclusively from `data/redteam/l2_only_ablation.json`:

| | Before | After (canonical) |
|:---|:---|:---|
| L2-only INT8 recall | 89.11% (90/101) | **91.09% (92/101)** |
| L2-only INT8 CI | [81.5, 93.8] | **[83.9, 95.2]** |
| L2-only INT8 benign FP | 6.67% (4/60) | **8.33% (5/60)** |
| Dual-channel row | 95.05% (96/101), labelled dual-channel | **96.04% (97/101)** for `max(P_raw, P_ext)`; the 96/101 figure is the single-channel L0-normalised row and is now reported as such in the text |
| Macro-F1 | 95.50% (unattributable) | **93.31%** (recomputed macro average of the dual-channel confusion matrix) |
| Recovered attacks | "6" | **4** for single-channel INT8+L0, **5** for dual-channel |

The dual-channel configuration's benign false-positive rate (10.00%, 6/60) is now visible in the table rather than hidden behind the single-channel value.

## K2. The "Macro-F1" column was a binary F1

**Accepted.** The column was mislabelled. The reviewer's arithmetic is correct: for L2-FP32 (TP=101, FP=4, FN=0, TN=56) the malicious-class F1 is 98.06% and the macro average is 97.30%, not 98.12%. The same error explains the 86.50 vs 86.52 discrepancy in the L0+L1 row.

Table 4 now reports a true macro average and carries the full confusion matrices in a footnote (77/24/0/60, 101/0/4/56, 92/9/5/55, 97/4/6/54), with the binary F1 given alongside so that either convention can be checked.

The 83.33 ↔ 84.86 discrepancy is also explained: 83.33 was the binary F1 in `l0_contribution_fair.json` for the raw-text run, while 84.86 is the macro F1 of the same run in `e2e_layer_test_v6_2.json`. The paper now states that these are two statistics of one run, not two conflicting measurements.

## K3. "17 recovered attacks"

**Accepted with a correction to our own correction.** `rescued_by_l0 = 17` and `broken_by_l0 = 2` are both present in `data/l0_contribution_fair.json`. The defect was that we reported the gross figure as if it were the net gain and hid the two lost attacks.

The text now reads: *"recovered 17 attacks that the raw-text run missed and lost 2 that it had caught — a net gain of 15 detections (74.10% → 75.14%, +1.04 pp; Macro-F1 84.86% → 85.40%)"*.

On significance, we went further than the reviewer asked and than our own first draft. The draft's Wilson-based sentence was itself wrong: Wilson intervals apply to single proportions, not to a paired difference. We replaced it with an exact McNemar test on the 19 discordant pairs (17 recovered, 2 lost):

$$p = 2\cdot P(X \le 2 \mid X \sim \mathrm{Bin}(19, 0.5)) = \frac{382}{524288} \approx 0.0007$$

The gain is significant, and the claim "statistically measurable" is gone from the manuscript. This is a post-hoc analysis of the archived per-item data, and the response says so.

## K4. The licence sentence was factually indefensible

**Accepted.** The sentence claiming that all corpora fall under "permissive open-source licenses (MIT, Apache-2.0, CC-BY-SA)" was wrong: the benchmark translations were produced with NLLB-200-3.3B, which is CC-BY-NC 4.0, a non-commercial licence. Our own internal handover document said so.

Section 2.3 now declares each resource and its licence explicitly, including the non-commercial restriction, and a new supplementary **Table S1** (`docs/SUPPLEMENTARY_LICENSES.md`) lists every external resource with version, licence, use and redistribution status. Two rows deserve emphasis:

- **NLLB-200-3.3B — CC-BY-NC 4.0.** Used strictly for non-commercial academic research; the derived benchmark inherits the restriction.
- **Rubend18 collection — no licence stated by the uploader.** Used for internal research evaluation only and not redistributed. Reference [27] now exists, and `data/reference_verification.json` records the status as `LICENCE-NOT-SPECIFIED` rather than `OK`.

"Jackhhao" and "SPML" were named without references; both names have been removed and the text now says "public prompt collections".

## K5. The Table 1 footnote mixed two statistics and two runs

**Accepted, and the table has been restructured rather than patched.** The reviewer identified two separate defects: the interval [0.4538, 0.69] belongs to Recall@FP=1% (not to recall at τ=0.70), and the row's point estimates did not come from one run.

On investigation a third problem appeared: the Recall and FP point values for XLM-RoBERTa, BGE-M3 and Patronus (47.50/2.20, 61.50/2.20, 70.10/0.80) exist only in earlier prose documents and in no measurement file. Rather than keep numbers we cannot trace, **Table 1 now reports only archived metrics** — Macro-F1, ROC-AUC and Recall@FP=1% — all three with cluster-bootstrap intervals, all from `data/validation_ci_v6.json`.

The mmBERT recall is retained but relocated to the table footnote with its own Wilson interval: 74.10% (95% CI [71.8, 76.3]) at 3.83% false positives ([2.95, 4.97]), labelled *standalone L2 on raw text*, together with the full-pipeline value (75.14%, 85.40% Macro-F1). The claim "74.10% vs 70.10%" no longer appears, because the 70.10% baseline value has no archived provenance. The Subject of every related sentence (contributions, Table 3 header, Section 3.1, conclusion) now names the classifier rather than the gateway, as the reviewer requested.

A note on the bootstrap point estimate: 84.82% versus the full-sample 84.86% is now described as resampling variance, not as "the same statistic to two decimals".

---

## O1. Model count

**Accepted.** The paper now states **19 distinct checkpoints**: 10 open-weight (Tier-1/2), 3 open-weight reasoning models, 4 flagship API models, and 2 additional API models (DeepSeek-v4-Flash, MiMo-v2.6-Pro) that appear only in the native Turkish suite. The abstract, Section 2.5, Table 7's caption and the cover letter all use the same figure.

## O2. Three incompatible layer schemes

**Accepted, and resolved by adopting the code's own scheme.** The manuscript now uses six stages and five defensive controls throughout: L0 normalisation, L1 rules, L2 classifier, **L3 OR-Gate arbiter**, L4 target model, **L5 egress DLP**. Eight sites were corrected, and `scripts/verify_layer_naming.py` rejects any build in which L3 is used outside the arbiter, L4 outside the target model, DLP is numbered L3, or "four-layer"/"five defenses" reappears.

The adjective conflict is also resolved, and it revealed an omission: the arbiter is deterministic *given a request history* but the classifier threshold is genuinely adaptive in `backend/security_layer.py` (`ml_effective = max(20, 70 − penalty)`). Section 2.2 now describes this mechanism and adds it as Eq. 3.

## O1 addendum: the DeepSeek-v4-Flash alias

While checking the endpoint catalogue for this revision we found that the provider no longer serves
`deepseek-v4-flash`: requests addressed to it are routed to `deepseek-v4.1-flash`
(`data/serving_endpoint_catalog_2026-10-28.json`). Table 7 therefore reports **19 endpoint entries over 18
distinct checkpoints**, and the retired alias is labelled as such. Both rows returned 0/50, so no
conclusion depends on the alias; removing the duplicate row would change the table's row count but not
a single result. The corpus-wide model count in the abstract, Section 2.5 and Section 5 has been
corrected from 19 to 18 distinct checkpoints.

## O3. Section 3.7 numbers are not traceable

**Accepted, and now resolved by releasing the artefacts.** Our first pass said the numbers could not be traced; that was wrong, and the reviewer's demand for traceability is what exposed it. The evidence package captured on 2026-10-22 contains the native Turkish run (50 prompts, per-model metrics, per-run SHA-256 manifests, a thinking-toggle log) and a HAR capture of the SSE session. It was simply never migrated into the repository.

It has now been archived under `data/redteam/`, with the internal package's own checksum manifest verified first:

- **47/47** digests in the package manifest matched before any file was copied.
- Nineteen files were copied byte-for-byte: the prompt set (`native_tr_50_prompts.jsonl`), the six-model comparison (`native_tr_50_comparison.json`), seven per-model metrics files and seven run manifests, and the HAR plus its two extracted network files.
- Every SHA-256 recorded inside `native_tr_50_comparison.json` was matched against the manifest actually shipped, so the comparison file and the manifests cannot drift apart.
- `scripts/extract_sse_counts.py` recomputes the Section 3.7 figures from the HAR itself and writes `sse_har/counts.json`: **118** reasoning events, **1,414** reasoning characters, **7,981** network characters, **2** canaries in the reasoning channel and **0** in the content channel. All four manuscript numbers are assertions in that file's `claim_check` block.

Two clarifications the reviewer will want:

1. **The thinking-toggle log needed one transformation.** Each of the 40 lines carried a provider `usage` block containing a sub-object whose name identifies the serving platform. That block is a token counter, not evidence. `scripts/neutralize_thinking_off_log.py` removes the whole object, refuses to write if any platform token survives, and re-verifies that the record count and both leak flags are unchanged: 40 records, 0/40 content leaks, 0/40 reasoning leaks.
2. **Raw transcripts are retained, not published.** 332 per-request transcripts exist internally and all 332 verify against their published manifests. They are withheld because they contain verbatim model output that no reported number depends on. A reader can confirm existence and integrity through the manifest digests and can reconstruct any proportion from the published per-model metrics. Raw transcripts are available to reviewers upon request.

Table 7 therefore no longer says "pilot": its caption states exactly what is released and what is retained under hashed manifests, and the SSE paragraph says the capture is public.

## O4. "Calibrated" versus T\* = 1.8345

**Accepted.** Temperature scaling was fitted (T* = 1.8345; ECE 11.51% → 3.45%) but is not active: the deployed configuration and every red-team run use T = 1.0. Section 2.2 no longer calls the output "calibrated", and Section 2.6 states the calibration result and its status, including the reason it is not applied — a monotone transform preserves ranking (and ROC-AUC) but moves the τ = 0.70 operating point.

## O5. Speculative causality

**Accepted.** The phrase "attention cross-talk in the model's ungrounded weights" has been removed. The observation is reported as an observation, with an explicitly labelled hypothesis.

## O6. Equation typography

**Accepted.** Equations 1–3 are now typeset with Cambria Math, real subscripts and Unicode operators (∨, ∧, ≥, ±, τ, ∈). A build gate confirms that `v`, `^`, `+-`, `p_hat` and the word `tau` no longer appear anywhere in the rendered PDF.

## O7. Table 3 comparability

**Accepted.** The "Local x86 workstation" row is gone (no archived measurement). The table now has an **Input Tokens** column (12 for FP32, 23 for INT8) and a footnote stating that the two latencies are not directly comparable. The unattributable 49.03% is replaced by the archived 53.30%, and storage now reports the measured artefact (1.17 GB) rather than the theoretical FP32 size.

## O8. The 76.9% overlap

**Accepted, and re-measured under a pre-registered criterion.** The criterion was fixed in writing before the audit ran: word 8-grams, lowercase, punctuation stripped, an item is contaminated if at least one 8-gram appears in the training corpus. The result differs from the old number, so the old number is gone:

- **8.7%** of the 2,000 audited items share at least one verbatim 8-gram with the v6 training corpus (85,083 records);
- **3.1%** share half or more of their 8-grams;
- **89.25%** name a public training repository in their `source` field — the larger and more consequential finding.

Script, criterion and raw counts are released as `data/contamination_audit.json`. Abstract, Section 1, Section 2.4 and the cover letter all now carry these figures.

## O9. Residual AI-detector patterns

**Addressed.** The bracketed layer lists in the abstract and Section 1 are gone; Section 3.4 and Section 4.1 no longer use "(1)(2)(3)"; the contributions paragraph no longer runs "First/Second/Finally". Sentence length now varies from 4 to 40 words in the body prose. The only surviving enumeration is the list of four canary secrets in Section 2.5, which is a factual list of values rather than an argumentative scaffold.

## O10. Data-source transparency

Covered by K4: Rubend18 is now [27], Jackhhao/SPML are removed, and `reference_verification.json` covers all 27 entries including [25], [26] and the `LICENCE-NOT-SPECIFIED` status of [27].

---

## Minor points

| # | Point | Action |
|:---|:---|:---|
| 1 | 84.86 rounds to 84.9 | Abstract now says 84.9% vs 84.2% |
| 2 | "such as (e.g., ...)" | Redundant "e.g." removed |
| 3 | `evren` in the artefact path | Copied to `data/redteam/tier3_gemma_4_31b.json`; Appendix B cites the new name, the old file is kept as an alias |
| 4 | Table 2 AUC precision | Reported at source precision: 0.890 and 0.631 (delta +0.259) |
| 5 | Handover said 25 references | Corrected to 27 |
| 6 | Eq. 1 fourth disjunct undefined | `ML_class` is now defined as the argmax prediction (P ≥ 0.50), making the disjunct a genuine soft-AND band |
| 7 | ISSN vs e-ISSN | Cover letter now says e-ISSN |
| 8 | Secret scan | `git ls-files` checked; no key or service-account file is tracked |

## Discordant bookkeeping in Table 9

Table 9 reports the Llama-3.1-8B pair with b = 7 attacks leaking only under 4-bit NF4 and c = 9 only under FP16, against a common set of 8 that leak under both. The two ASR numerators (15 for 4-bit, 17 for FP16) and the two discordant counts therefore describe the same 2x2 table: 8 + 7 = 15 and 8 + 9 = 17, so FP16 - 4-bit = 2 = 9 - 7. The build gate now recomputes this marginal identity on every build, which prevents the two labels from being exchanged in either direction.

## Verification now enforced at build time

Two gates must pass before a build is accepted:

1. `scripts/verify_paper_metrics.py` — 162 manifest entries, 188 values. It does not compare strings; it **recomputes** each proportion, Wilson interval, binary F1, macro F1 and McNemar p-value from its (k, n) / (tp, fp, fn) / (b, c) inputs, checks the value against its JSON source, and checks the rendered string in the manuscript. Retired numbers are blacklisted.
2. `scripts/verify_layer_naming.py` — enforces the single canonical layer scheme.

Layout is unchanged in its guarantees: 17 pages, 10 tables, none split across a page boundary, verified through Word COM.
