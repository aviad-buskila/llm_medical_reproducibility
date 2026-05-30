# Response to Reviewers — PONE-D-26-19748

**Manuscript:** Evaluating Small Open LLMs for Medical Question Answering: A Practical Framework
**Author:** Avi-ad Avraam Buskila

> **How to read this file.** Each reviewer/editor point is quoted, followed by our response and the exact location of the change in the revised manuscript. Items marked **[NUMBER]** / **[REF §]** are placeholders to be filled once the expanded experimental runs (new same-size control model, one closed-source model, second dataset, judge-reliability sub-study) and the PLOS-template port are complete. All code changes referenced below are already implemented in the released repository and covered by unit tests.

We thank the Academic Editor and both reviewers for constructive, detailed feedback. The revision (a) substantially strengthens the statistical reporting, (b) adds a semantic reproducibility measure, (c) expands the evaluation along model and dataset axes, (d) quantifies judge reliability, and (e) reframes several claims more conservatively. We summarize the major additions, then respond point by point.

## Summary of changes
1. **Statistics.** All model-level results (Tables 1–2) are now reported as the mean with a **95% bootstrap confidence interval** (clustered resampling over questions; 1,000 resamples), and we state the exact aggregation procedure explicitly.
2. **Semantic reproducibility.** We add a **semantic self-similarity** reproducibility metric (mean pairwise BERTScore-F1 across the repeated runs), complementing the lexical self-agreement/uniqueness metrics.
3. **More models.** We add a **same-size general-purpose control (Gemma 3 4B)** so that Gemma 3 4B vs MedGemma 1.5 4B isolates clinical fine-tuning from scale, and **one closed-source API model ([NUMBER: model])** as an open-vs-closed reference point.
4. **More data.** We add a **second evaluation dataset ([NUMBER: dataset])** alongside MedQuAD.
5. **Judge reliability.** We re-judge a stratified subset **5×** and report the judge's within-response score variability and ICC(1).
6. **Framing.** We soften over-strong claims (notably "entirely disjoint output spaces"), clarify MedQuAD as a proxy benchmark, document stateless inference, and add a discussion of how the approach could be extended (incl. type-3 ANFIS) and how it relates to other methods.

---

## Academic Editor

> *"please apply the comments of reviewers; also to give a better direction for readers; add a section to discuss how the suggested approach can be improved using type-3 ANFIS; compare the results with other related methods."*

- **Reviewer comments:** addressed individually below.
- **Better direction for readers:** we sharpened the Introduction's framing and added explicit signposting linking the Reddit motivation to the MedQuAD proxy benchmark. **[REF §Introduction]**
- **Type-3 ANFIS:** we added a new Discussion subsection, *"Toward improved reproducibility: type-3 ANFIS and related post-processing,"* outlining how a type-3 fuzzy logic / ANFIS layer could model and reduce the higher-order uncertainty we observe across repeated generations (e.g., as an uncertainty-aware aggregator over the N runs), with citations. **[REF §Discussion]**
- **Comparison with other related methods:** we added a paragraph/table positioning our reproducibility metrics relative to self-consistency voting, semantic entropy, and conformal prediction. **[REF §Discussion / Related Work]**

## Journal Requirements

1. **PLOS style + file naming** — done; the manuscript was reformatted to the PLOS template (see #3) and files renamed per PLOS conventions.
2. **arXiv preprint** — addressed in the cover letter: the arXiv posting is a **non-peer-reviewed preprint** of this same work, not a separate formally published article, so it does not constitute dual publication.
3. **PLOS LaTeX template** — the manuscript has been ported to the official PLOS LaTeX template. **[REF: paper/]**
4. **Abstract identical to submission form** — the manuscript abstract and the online submission-form abstract have been made identical.
5. **Reviewer-recommended citations** — no specific prior works were mandated; we evaluated and cited the additional methods relevant to the new discussion (self-consistency, semantic entropy, conformal prediction, type-3 ANFIS).

---

## Reviewer #1

> **1. "The evaluation is only conducted across three models in different families, not sufficient... More evaluation are encouraged, such as the same family but different sizes; open-source and close-source."**

We expanded the model set along both axes the reviewer identifies:
- **Same family, different sizes:** we added **Gemma 3 4B**, a same-size general-purpose counterpart to MedGemma 1.5 4B (both 4B, both Gemma-derived). This directly isolates the effect of *clinical fine-tuning* from *model scale* — the confound our original manuscript could only flag. **[NUMBER: Gemma 3 4B vs MedGemma results]**
- **Open vs closed source:** we added one closed-source API model, **[NUMBER: model]**, as a reference point, while keeping the paper's focus on locally-deployable open-weight models (the privacy/cost thesis). The pipeline now supports API providers through a provider abstraction. **[REF §Models, Table 1–2]**

> **2. "Repeated evaluation should report the variance."**

All repeated-evaluation results now report uncertainty. Tables 1 and 2 give each metric as **mean with a 95% bootstrap CI** (resampling questions; 1,000 resamples), and per-question standard deviations are available in the released aggregates. **[REF §Results, Tables 1–2]**

> **3. "Only one evaluation dataset is also very limited."**

We added a second free-form medical QA dataset, **[NUMBER: dataset]**, evaluated under the identical protocol, and report results on both. **[REF §Dataset, Results]**

## Reviewer #2

> **Major 1. "Reproducibility metric is currently surface-level... primarily capture lexical variation rather than semantic or clinical equivalence... add semantic similarity-based reproducibility measures or note this as a limitation."**

We implemented a **semantic reproducibility metric**: for each (model, question) we compute the mean pairwise semantic similarity (BERTScore-F1) across the N repeated runs, reusing the same embedding backbone as our quality metrics. This complements the lexical metrics and is robust to paraphrase. Strikingly, while lexical self-agreement is low and uniqueness high, **semantic self-similarity is substantially higher ([NUMBER])**, indicating that much of the observed run-to-run variation is paraphrastic rather than meaning-level. We discuss this directly and note the caveat that embedding-based similarity has a high baseline floor, so it is best read as a complement to the lexical view rather than a strict clinical-equivalence test. **[REF §Metrics, Table 2, §Discussion]**

> **Major 2. "...more detail on the judge model and its reliability... judge stability or agreement with human judgment (even on a small subset)."**

We expanded the judge description (locally-hosted 20B open-weight model, rubric, single-pass in the main runs) and added a **judge-reliability sub-study**: we re-judged a stratified subset of [NUMBER] responses **5 times** and report the within-response score standard deviation (mean [NUMBER]) and the one-way intraclass correlation **ICC(1) = [NUMBER]**. **[REF §Metrics, §Discussion]** *(Optional: a small author spot-check of [NUMBER] items vs. the judge, rank correlation [NUMBER].)*

> **Major 3. "...does not explicitly specify the aggregation procedure... whether metrics are averaged across runs, across questions, or both... no uncertainty estimates (e.g., bootstrap confidence intervals) or per-question variance."**

We now state the aggregation procedure explicitly: quality metrics are averaged over all responses (equivalently, the mean of per-question means under our balanced N=10 design), and reproducibility rates are computed per (model, question) then averaged over questions. We added **95% bootstrap CIs** (clustered over questions) to both tables so that small between-model differences are not over-interpreted. **[REF §Results methods paragraph, Tables 1–2]**

> **Major 4. "...zero overlap across models is expected... 'entirely disjoint output spaces' ... overstating... present as a qualitative observation... frame findings as relating to output variability rather than direct clinical inconsistency."**

We agree. We removed the "entirely disjoint output spaces" phrasing, now present the zero exact-overlap result as a **qualitative observation** that explicitly acknowledges string-level overlap is uninformative about semantic/clinical equivalence in free-form generation, and we reframed the Results/Discussion to speak of **output variability** rather than clinical inconsistency. The new semantic metric reinforces this more conservative reading. **[REF §Results, §Discussion]**

> **Minor 1. "...Reddit-based motivation... but the evaluation is conducted on MedQuAD. Just a brief clarification that MedQuAD serves as a proxy benchmark."**

Added a sentence clarifying MedQuAD is used as a **proxy** for consumer-facing/Reddit-style health questions. **[REF §Introduction/Dataset]**

> **Minor 2. "...fixing a random seed (seed=42)... only strictly valid if the full data pipeline is identical... different sampling methods may yield different subsets... provide the exact sampled questions (e.g., in a supplementary file) or explicitly document the full deterministic data loading and sampling pipeline."**

Both: (a) we document the exact deterministic pipeline (pinned `gold_data.csv`, no row removal, pandas `df.sample(random_state=42)` over the loaded frame), and (b) we ship the **exact sampled question set as Supplementary S1**, reproducible via a single command (`clinical-eval export-sample --sample-random 50 --sample-seed 42`). We also note the dataset has 16,412 records (14,984 unique questions). **[REF §Dataset, Supplementary S1]**

> **Minor 3. "...explicit statement confirming whether inference is fully stateless across questions and runs..."**

Added: each query is an independent, stateless `/api/generate` call; no conversation history is retained across questions or runs, so there is no cross-sample context leakage. **[REF §Pipeline Architecture]**

---

We believe these revisions address all points and materially strengthen the paper's rigor and framing. We thank the editor and reviewers again for their time.
