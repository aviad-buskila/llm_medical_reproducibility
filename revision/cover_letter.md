# Cover Letter — Revised Submission, PONE-D-26-19748

Dear Dr. Mohammadzadeh and the PLOS ONE Editorial Office,

Please find enclosed our revised manuscript, *"Evaluating Small Open LLMs for Medical Question Answering: A Practical Framework"* (PONE-D-26-19748), together with a point-by-point Response to Reviewers and a tracked-changes version.

We are grateful for the constructive reviews. In this revision we strengthened the statistical reporting (95% bootstrap confidence intervals and an explicit aggregation procedure), added a semantic reproducibility metric, and substantially expanded the evaluation: it now spans **five models** — adding a same-size general-purpose control (Gemma 3 4B) and a closed-source reference (GPT-4.1-nano) — across **two datasets** (MedQuAD and MedicationQA; 5,000 responses in total). These additions yield two strengthened findings: run-to-run divergence is overwhelmingly *paraphrastic* (semantic self-similarity 0.94–0.97 despite lexical self-agreement of only 0.11–0.26), a pattern that holds on both datasets and even for the closed reference model; and, with the same-size control included, *model scale* rather than clinical fine-tuning drives quality. We also quantified the LLM judge's reliability (ICC(1) = 0.94 on MedQuAD, 0.69 on MedicationQA), reframed several claims more conservatively, and added a Discussion of how the framework could be extended (including a type-3 ANFIS uncertainty-aware aggregation layer) and how it relates to other methods, as the editor requested.

We address the journal requirements below.

**Prior posting / dual publication.** An earlier version of this work was posted as a **preprint on arXiv**. This is a non-peer-reviewed preprint of the present manuscript, not a separate, formally published, peer-reviewed article, and therefore does not constitute dual publication. No part of this work has been published in, or is under consideration at, any peer-reviewed venue.

**PLOS LaTeX template & style.** The manuscript has been reformatted using the official PLOS LaTeX template and conforms to PLOS ONE style and file-naming requirements.

**Abstract consistency.** The abstract in the manuscript and the abstract entered in the online submission form have been made identical.

**Financial disclosure.** [PLACEHOLDER — confirm/keep current statement, e.g.: "The author received no specific funding for this work."]

**Data availability.** All code, data-processing pipelines, configurations, and the exact sampled evaluation set (Supplementary S1) are publicly released at https://github.com/aviad-buskila/llm_medical_reproducibility to ensure full reproducibility.

**Peer-review history.** [PLACEHOLDER — state your choice: do you opt in to publishing the peer-review history?]

**ORCID.** The corresponding (and sole) author's ORCID iD is verified in the submission system.

We believe the revised manuscript fully addresses the reviewers' and editor's comments and hope it is now suitable for publication in PLOS ONE.

Sincerely,
Avi-ad Avraam Buskila
Department of Information Science and Applied Artificial Intelligence, Bar-Ilan University, Ramat-Gan, Israel
aviad-avraam.buskila@biu.ac.il
