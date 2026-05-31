# Ollama Medical Reproducibility Pipeline

Run repeated medical prompt evaluations across multiple Ollama models, compare against gold answers, measure reproducibility, and generate structured reports/figures.

## Intro (Plain Language)

This project helps answer a simple question:

- If we ask several medical LLMs the same medical questions many times, do they give:
  - accurate answers, and
  - consistent answers?

You can think of this as a "lab test" for model reliability:

- **Accuracy**: how close the answer is to a trusted reference ("gold answer").
- **Reproducibility**: how stable the model is when you repeat the same test.

The pipeline is designed so clinicians, researchers, and product teams can run repeatable experiments locally (via Ollama), then review clear summary tables and visuals without needing to write analysis code.

## Methodology (What the pipeline does step by step)

1. **Load gold dataset**
   - Reads `data/gold_data.csv` (`question`, `answer`).
   - `answer` is treated as the gold reference.
2. **Run repeated generation**
   - For each configured model, each question is asked multiple times (`runs_per_prompt`).
   - Optional shared instruction is applied to all models.
3. **Store raw evidence**
   - Saves every generated response with run metadata (model, run index, latency, token counts, etc.).
4. **Score against gold**
   - Computes lexical + semantic metrics (exact match, token overlap, BLEU/ROUGE, BERTScore).
   - Optional LLM-as-judge adds rubric-based scoring.
5. **Measure reproducibility**
   - Quantifies how much each model varies across repeated runs.
   - Includes agreement and uniqueness-based stability indicators.
6. **Aggregate + report**
   - Produces model-level summaries, per-question stability views, pairwise model similarity, and performance tables.

## How to use this if you are not a data scientist

- Start with `clinical-eval all --sample-random 5` to run a small pilot.
- Open `outputs/report.md` and read sections in order:
  1. **Quality vs gold** - "Which model is most correct?"
  2. **Within-model reproducibility** - "Which model is most stable?"
  3. **By model + question** - "Which questions cause instability?"
  4. **Global comparison** - "How variable is each model overall?"
  5. **Pairwise similarity** - "Which models behave similarly?"
  6. **Performance** - "Which model is fastest / most efficient?"
- Use figures in `outputs/figures/` for presentations.

Practical interpretation:

- A "good" model in this framework usually has:
  - high quality metrics (Part 1),
  - high agreement + low uniqueness (Parts 2-4),
  - acceptable latency/tokens-per-second (Part 6).

## What this repository does

- Runs a grid of `models x prompts x runs_per_prompt`.
- Persists all raw outputs with metadata.
- Scores model outputs against gold answers using:
  - exact/normalized exact match,
  - token-level and string-level overlap,
  - BLEU, ROUGE-L, BERTScore (RoBERTa),
  - optional LLM-as-judge score/rationale.
- Computes reproducibility/stability metrics across repeated runs.
- Produces machine-readable outputs plus a multi-part Markdown report and plots.

## Repository structure

- `configs/pipeline.yaml` - primary pipeline config.
- `data/gold_data.csv` - editable CSV of prompts + gold answers.
- `src/clinical_eval_pipeline/` - CLI and pipeline modules.
- `outputs/` - generated artifacts (ignored by git).

## Requirements

- Python 3.10+
- Local Ollama server running on `http://localhost:11434`
- Pulled model tags that exactly match config values:

```bash
ollama list
```

Use exact tags from that output in `configs/pipeline.yaml`.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

For the revision config closed-source model (`gpt-4.1-mini` in `configs/pipeline_revision.yaml`):

```bash
cp .env.example .env
# edit .env and set OPENAI_API_KEY=sk-...
pip install -e ".[openai]"
```

The CLI loads `.env` from the project root (or current working directory) on startup. Existing shell environment variables take precedence over `.env`.

Note: first BERTScore run downloads transformer weights and may be slower.

## Input data format

Edit `data/gold_data.csv`.

Required columns:

- `question`
- `answer`

Notes:

- The pipeline auto-generates internal IDs (`q1`, `q2`, ...).
- `answer` is mapped internally to `gold_answer`.
- Current gold dataset source: **MedQuAD** (medical question-answer pairs).
- Reference: [A question entailment approach to question answering](https://link.springer.com/article/10.1186/s12859-019-3119-4).

## Dataset provenance (MedQuAD)

This repository currently uses `data/gold_data.csv` derived from MedQuAD-style medical Q/A content.

When publishing results, cite:

- Ben Abacha A, Demner-Fushman D. *A Question Entailment Approach to Question Answering*. BMC Bioinformatics. 2019. [https://link.springer.com/article/10.1186/s12859-019-3119-4](https://link.springer.com/article/10.1186/s12859-019-3119-4)

## Prompting behavior

- User prompt sent to model is exactly the `question` value.
- Shared instruction is sent separately via config (`shared_instruction`) as system guidance.

## Configuration reference

All configured in `configs/pipeline.yaml`:

- `ollama_base_url` - Ollama server URL.
- `prompt_file` - gold CSV path (expects `question,answer` columns).
- `shared_instruction` - common instruction for all model calls.
- `models` - list of model tags, with optional per-model `runs_per_prompt`.
- `runs_per_prompt` - global default repeats.
- `generation` - `temperature`, `top_p`, `max_tokens`, `timeout_seconds`, `retries`.
- `judge`:
  - `enabled` - toggle LLM judge.
  - `model` - judge model tag.
  - `use_chat_api` - use `/api/chat` for judge calls (recommended).
  - `rubric_prompt` - judge rubric text.
- `resume` - skip completed stages when artifacts already exist.
- `verbose` - detailed terminal/log progress.
- `bertscore_model` - default `roberta-base`.
- `bertscore_batch_size` - BERTScore batching.
- `output` - output directory and file formats.

## Commands

Defaults to `configs/pipeline.yaml`, so `--config-path` is optional.

Run full pipeline:

```bash
clinical-eval all
```

Run phases separately:

```bash
clinical-eval run
clinical-eval score
clinical-eval report
```

Useful flags:

- `--resume/--no-resume` on `run`, `score`, `report`, `all`
- `--sample N` on `run` and `all` (use first N questions only)
- `--sample-random N` on `run` and `all` (sample N random questions)
- `--sample-seed <int>` with `--sample-random` for reproducible random sampling

Examples:

```bash
clinical-eval all --sample 2 --no-resume
clinical-eval all --resume
clinical-eval all --sample-random 50 --sample-seed 42 --no-resume
```

## Logging

- Terminal output is mirrored to timestamped logs:
  - `outputs/logs/pipeline_YYYYMMDD_HHMMSS.log`
- Log includes command line and start/end timestamps.
- Verbose lines are timestamp-prefixed.
- Retry failures and judge parse failures are explicitly logged.
- If judge API responses are empty, pipeline attempts an `ollama run` CLI fallback automatically.

## Output artifacts

Under `outputs/`:

- `raw_responses.jsonl`, `raw_responses.csv`, `raw_responses.parquet`
- `scored_responses.csv`, `scored_responses.parquet`
  - includes per-run performance fields: `latency_ms`, `output_tokens`, `tokens_per_second`
- `aggregates.csv`
- `report.md`
- `figures/`:
  - `model_token_f1_bar.png`
  - `string_similarity_boxplot.png`
  - `token_f1_heatmap.png`
  - `pairwise_model_similarity_heatmap.png`

Quick link:

- [Open latest generated report](outputs/report.md)
  - Note: this file is generated/overwritten by the pipeline (`clinical-eval report` or `clinical-eval all`).

## Report sections

`outputs/report.md` includes:

1. Model-vs-gold quality (average + median)
2. Within-model reproducibility (ignoring gold)
3. Reproducibility by model + question
4. Global model comparison (ignoring question id)
5. Pairwise model similarity matrix
6. Performance summary (model-level latency/token stats)

### Part 1 metrics explained (Model-vs-Gold)

- `exact_match`: strict string equality against gold (`1` exact match, `0` otherwise).
- `token_f1`: token overlap score after normalization (higher = better content overlap).
- `string_similarity`: character-level similarity ratio on normalized text (higher = closer wording).
- `bleu`: n-gram precision-oriented overlap (higher = closer phrasing to gold).
- `rouge_l`: longest-common-subsequence F1-style overlap (higher = better structural/content overlap).
- `bertscore_f1`: semantic similarity using contextual embeddings (higher = better semantic alignment).
- `judge_score` (optional): LLM-judge rubric score from `0..1` (higher = better judged medical quality).
- Why both `avg` and `median`:
  - `avg` captures overall trend,
  - `median` is more robust to outlier generations.

### Part 2 metrics explained (Within-model reproducibility, gold-independent)

- `normalized_self_agreement_rate`:
  - fraction of runs matching the modal normalized output for that model/question.
  - higher = more stable/reproducible.
- `normalized_response_uniqueness_rate`:
  - number of unique normalized outputs divided by run count.
  - lower = more stable/reproducible.
- Interpretation:
  - high agreement + low uniqueness implies deterministic/consistent behavior.
  - low agreement + high uniqueness implies variable behavior across runs.

### Part 3 metrics explained (Reproducibility by model and question)

- Same reproducibility metrics as Part 2, but broken down per `question_id`.
- Use this to identify unstable prompts for specific models.
- Rows with low agreement/high uniqueness are instability hotspots.

### Part 4 metrics explained (Global model comparison, no question grouping)

- `total_outputs`: total generations produced by a model.
- `unique_outputs`: distinct raw responses across all runs/questions.
- `unique_normalized_outputs`: distinct responses after normalization.
- `global_response_uniqueness_rate`: `unique_outputs / total_outputs`.
- `global_normalized_uniqueness_rate`: `unique_normalized_outputs / total_outputs`.
- Lower global uniqueness typically indicates higher overall consistency.

### Part 5 metrics explained (Pairwise model similarity matrix)

- Cell `(A, B)` is the fraction of aligned `(question_id, run_index)` pairs where models A and B produced the same normalized output.
- Range is `0..1`:
  - `1.0` means the two models always matched (after normalization),
  - `0.0` means they never matched.
- Diagonal values are `1.0` by definition (model compared with itself).

### Part 6 metrics explained (Performance, model level)

- `latency_ms_avg` / `latency_ms_median`:
  - response latency per run in milliseconds, aggregated by model.
- `output_tokens_avg` / `output_tokens_median`:
  - generated output token count per run (from Ollama `eval_count`).
- `tokens_per_second_avg` / `tokens_per_second_median`:
  - throughput computed as `output_tokens / latency_seconds`.
- Interpretation:
  - lower latency is faster,
  - higher tokens/sec indicates better generation throughput.

## Reproducibility metrics

Core reproducibility indicators:

- `normalized_self_agreement_rate` (higher is better)
- `normalized_response_uniqueness_rate` (lower is better)
- metric spread (`*_std`) across repeated runs

## Troubleshooting

- Judge returns empty/NaN:
  - verify `judge.enabled: true`
  - verify exact `judge.model` tag exists in `ollama list`
  - keep `judge.use_chat_api: true`
  - judge path includes automatic `ollama run` fallback when API response is empty
  - run with `--no-resume` to force re-scoring
- HTTP 404 model not found:
  - config tag does not match installed tag exactly
- BERTScore errors:
  - rerun `pip install -e .`
  - ensure internet access for first model download
- Partial/stale outputs:
  - rerun with `--no-resume`
