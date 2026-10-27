# Supplementary Table S1 — Provenance and Licences of External Resources

Manuscript: *NeuralShield: A Multilingual Multi-Layer Security Gateway Against Prompt Injection and Data Exfiltration in Large Language Models*

This table answers the reviewer question "where did this data come from and is redistribution lawful?".
It is referenced from Section 2.3 of the manuscript.

| Resource | Type | Version / snapshot | Licence | Use in this study | Redistributed? |
|:---|:---|:---|:---|:---|:---|
| Simsonsun JailbreakPrompts [18] | dataset | Hugging Face snapshot, 2023 | MIT | Adversarial prompts for the source-disjoint benchmark (n = 1,440) | No; identifiers and derived splits only |
| Rubend18 ChatGPT-Jailbreak-Prompts [27] | dataset | GitHub repository, 2023 | Not specified by the uploader | Adversarial prompts for the source-disjoint benchmark | No; used for internal research evaluation only |
| Databricks Dolly-15k [19] | dataset | `databricks/databricks-dolly-15k` | CC-BY-SA 3.0 | Benign instructions for the source-disjoint benchmark (n = 1,409) | No; derived splits only |
| Deepset prompt-injections [26] | dataset | `deepset/prompt-injections` | Apache-2.0 | Quality-control ensemble member (Section 2.3) | No |
| ProtectAI DeBERTa-v3 [8] | model | `protectai/deberta-v3-base-prompt-injection` | Apache-2.0 | Quality-control ensemble member | No |
| Patronus Wolf Defender [9] | model | `patronus-studio/wolf-defender-prompt-injection` | See model card | Commercial baseline (Table 1) and QC ensemble | No |
| Meta Prompt Guard [7] | model | `meta-llama/Prompt-Guard-86M` | See model card | Discussed as a baseline guardrail | No |
| mmBERT-base [16] | model | `jhu-clsp/mmBERT-base` | Apache-2.0 | Encoder initialised and fine-tuned as L2 | No; weights released with the paper |
| NLLB-200-3.3B [20] | model | `facebook/nllb-200-3.3B` | **CC-BY-NC 4.0** | Machine translation of the benchmark across 12 languages | No; **non-commercial research use only** |
| Derived multilingual benchmark (`heldout_benchmark_v6_fair.json`) | derived dataset | This study, v6.2 | **CC-BY-NC 4.0** (inherits the NLLB restriction) | Evaluation set (N = 2,849) | Yes, for research use |
| Curated red-team suite (`curated_redteam_v6_2.json`) | derived dataset | This study, v6.2 | CC-BY-4.0 | Red-team evaluation (N = 161) | Yes |
| NeuralShield v6.2 corpus | derived dataset | This study, v6.2 | Research use; synthetic records generated with a hosted teacher model | Classifier training (98,606 records) | Per-item text not released; statistics released |

## Notes

1. **NLLB-200 is not a permissive licence.** It is CC-BY-NC 4.0 (Attribution-NonCommercial). The manuscript declares this explicitly and does not describe the corpus as permissively licensed.
2. **Rubend18 has no stated licence.** The collection is therefore used only for internal evaluation and is not redistributed. This is the conservative reading; if the uploader later adds a licence, this row must be updated.
3. **Derived benchmark licensing is inherited.** Because the evaluation set is an NLLB translation of Dolly-15k plus public jailbreak prompts, the most restrictive upstream term (CC-BY-NC 4.0) governs the derived set.
4. **Commercial baselines are evaluated, not redistributed.** Patronus Wolf Defender and Meta Prompt Guard are queried through their published interfaces/weights under their own terms.
5. **No personally identifiable information** is present in any released artefact; all canary secrets are synthetic values created for this study.
