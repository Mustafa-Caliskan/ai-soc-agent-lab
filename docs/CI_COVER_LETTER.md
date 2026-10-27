# Cover Letter to the Editorial Board of Computers and Informatics (C&I)

**Date:** 26 October 2026  
**To:** The Editorial Board and Editor-in-Chief  
*Computers and Informatics* (C&I), DergiPark Academic Publishing  
ISSN: 2757-8259 | https://dergipark.org.tr/en/pub/ci  

**SUBJECT: Submission of Original Research Article — "NeuralShield: A Multilingual Multi-Layer Application Security Gateway for Large Language Models and Source-Disjoint Fair Evaluation"**

Dear Editor-in-Chief and Esteemed Members of the Editorial Board,

On behalf of my co-author Prof. Dr. Ali Hakan IŞIK and myself, I am pleased to submit our original research manuscript entitled **"NeuralShield: A Multilingual Multi-Layer Application Security Gateway for Large Language Models and Source-Disjoint Fair Evaluation"** for consideration for publication as a Research Article in *Computers and Informatics* (C&I).

In this paper we show that locally deployed and API-served LLMs disclose secrets embedded in their system prompts, that a non-trivial share of this disclosure occurs only in the reasoning channel and is therefore invisible to output-only inspection, and that a four-layer peripheral gateway removes the leak without touching the model. This is significant because enterprises increasingly delegate operational credentials to LLM assistants while measuring safety on the final response alone.

### Research Motivation and Novelty
As Large Language Models (LLMs) are rapidly integrated into production environments—such as autonomous workflow agents and retrieval-augmented generation (RAG)—securing natural language interfaces against prompt injection, jailbreaking, and confidential data exfiltration has become a pressing software engineering challenge. Existing commercial and academic guardrails remain predominantly English-centric, fail to address sophisticated non-Latin and steganographic evasion vectors, and exhibit significant performance collapse on non-translated low-resource queries. Furthermore, our audit of conventional out-of-distribution (OOD) benchmarks revealed a pervasive 76.9% source-level overlap with training corpora, artificially inflating reported safety figures.

### Key Contributions and Findings
In this work, we propose NeuralShield, a four-layer application security gateway (L0 Structural Normalizer, L1 Sub-millisecond Deterministic Regex, L2 12-Language mmBERT-base Transformer Classifier, and L3 Egress DLP Masker governed by an adaptive OR-Gate). NeuralShield runs entirely on commodity dual-thread CPU hardware with a median latency of ~50.6 ms (FP32 ONNX runtime), delivering high throughput without requiring expensive GPU infrastructure. Key scientific highlights include:
- **Source-Disjoint Fair Parity:** On a rigorously source-disjoint fair 12-language benchmark ($N=2,849$), NeuralShield demonstrates statistical parity in Macro-F1 with a commercial guardrail (Patronus Wolf Defender: 84.86% vs. 84.23%, overlapping 95% cluster-bootstrap confidence intervals), while achieving higher recall on native non-translated corpora (+34.4 pp on native Turkish; AUC 0.890 vs. 0.631 on native Cyrillic Russian).
- **14-Model Empirical Red-Teaming:** Empirical red-teaming across 14 diverse LLMs (from 1.5B edge models to Tier-2 enterprise models and Tier-3 flagship models evaluated on TÜBİTAK ULAKBİM EVREN H200 supercomputing infrastructure) blocked all 101 curated in-domain attacks, driving attack success rates (ASR) from up to 40.59% (Mistral-7B-v0.3) to flat 0.00%.
- **Discovery of Silent CoT Exfiltration:** We document the phenomenon of "Silent Chain-of-Thought Exfiltration", showing that flagship reasoning models (Gemma-4-31B and Qwen3.8-Flash-Next) achieve 0.00% user-facing ASR but verbalize confidential system canary secrets verbatim in 66.34% and 14.85% of internal reasoning traces—creating a critical exfiltration vector for SSE streaming architectures that is completely neutralized by NeuralShield's dual-stream egress DLP.
- **Reviewer-Proof Full-Pool Ablations:** Full-sample ($N=101$) paired McNemar tests prove the absence of a statistically significant quantization effect (4-bit NF4 vs. uncompressed FP16 exhibit overlapping CIs, $p=0.804$ on Llama-3.1-8B), while demonstrating that aggressive system prompt hardening leaves 16.83% residual leakage and also produces 1.67% benign canary leakage on legitimate user traffic.

### Relevance to Computers and Informatics
We believe this manuscript is ideally suited for *Computers and Informatics*, as it addresses core intersections of computer science, applied machine learning, software security, and robust computational engineering. The work presents both rigorous theoretical evaluation (cluster-bootstrap resampling, exact McNemar tests, Wilson score intervals) and practical systems engineering validated under real-world operational constraints.

### Author Declarations
In submitting this manuscript, we formally declare that:
1. The manuscript represents original work that has not been published previously and is not under consideration for publication elsewhere in any language.
2. The submission has been reviewed and approved by all authors, and permission has been obtained from the responsible authorities at Burdur Mehmet Akif Ersoy University.
3. The authors declare no competing financial interests or personal relationships that could have influenced the work.
4. All code artifacts, trained ONNX models, benchmark datasets, evaluation harnesses, and full per-item JSON outputs have been open-sourced and archived on GitHub (`https://github.com/Mustafa-Caliskan/ai-soc-agent-lab`) to guarantee absolute reproducibility.
5. Blind review requirements have been fully respected: author names and affiliations have been strictly omitted from the main manuscript (`docs/NeuralShield_CI_Manuscript.docx`) and provided separately in the Title Page (`docs/Title_Page.docx`).

Please address all correspondence concerning this manuscript to me at 2211404051@ogr.mehmetakif.edu.tr.

Thank you very much for your time, consideration, and management of the peer-review process.

Sincerely yours,

**Mustafa ÇALIŞKAN** (Corresponding Author)  
Department of Computer Engineering, Faculty of Engineering  
Burdur Mehmet Akif Ersoy University, 15030 Burdur, Türkiye  
Email: 2211404051@ogr.mehmetakif.edu.tr | ORCID: 0009-0004-3861-7628  

*On behalf of:*  
**Prof. Dr. Ali Hakan IŞIK** (Co-Author & Academic Advisor)  
Email: ahkan@mehmetakif.edu.tr | ORCID: 0000-0003-3561-9375  
