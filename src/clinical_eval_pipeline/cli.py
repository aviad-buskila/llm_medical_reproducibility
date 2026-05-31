from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import typer

from clinical_eval_pipeline.env import load_env

load_env()

from clinical_eval_pipeline.aggregate import compute_aggregates, save_aggregates
from clinical_eval_pipeline.config import load_config
from clinical_eval_pipeline.io_gold_csv import load_gold_csv
from clinical_eval_pipeline.logging_utils import tee_terminal_to_log
from clinical_eval_pipeline.reporting import generate_figures, write_markdown_report
from clinical_eval_pipeline.runner import run_evaluations
from clinical_eval_pipeline.scoring.deterministic import score_deterministic
from clinical_eval_pipeline.scoring.judge_reliability import run_judge_reliability
from clinical_eval_pipeline.scoring.llm_judge import apply_llm_judge
from clinical_eval_pipeline.scoring.semantic import compute_semantic_reproducibility

app = typer.Typer(help="Clinical reproducibility evaluation pipeline (Ollama).")


def _build_report(scored_df: pd.DataFrame, config, out_dir: Path) -> tuple[Path, Path]:
    """Compute aggregates (incl. semantic reproducibility), figures and report."""
    semantic_repro_df = None
    if config.semantic_reproducibility:
        semantic_repro_df = compute_semantic_reproducibility(
            scored_df,
            model_type=config.bertscore_model,
            batch_size=config.bertscore_batch_size,
            max_pairs_per_group=config.semantic_max_pairs_per_group,
            seed=config.random_seed or 42,
        )
    aggregate_df = compute_aggregates(scored_df, semantic_repro_df)
    agg_path = save_aggregates(aggregate_df, out_dir)
    generate_figures(
        scored_df,
        aggregate_df,
        out_dir,
        n_boot=config.bootstrap_resamples,
        ci=config.bootstrap_ci,
        seed=config.random_seed or 42,
    )
    report_path = write_markdown_report(
        scored_df,
        aggregate_df,
        out_dir,
        n_boot=config.bootstrap_resamples,
        ci=config.bootstrap_ci,
        seed=config.random_seed or 42,
    )
    return agg_path, report_path


def _read_raw(config_path: str) -> tuple[pd.DataFrame, str]:
    config = load_config(config_path)
    out_dir = Path(config.output.output_dir)
    parquet_path = out_dir / "raw_responses.parquet"
    csv_path = out_dir / "raw_responses.csv"
    if parquet_path.exists():
        return pd.read_parquet(parquet_path), str(out_dir)
    if csv_path.exists():
        return pd.read_csv(csv_path), str(out_dir)
    raise FileNotFoundError("No raw responses found. Run `clinical-eval run` first.")


def _resolve_resume(cli_resume: bool | None, config_resume: bool) -> bool:
    if cli_resume is None:
        return config_resume
    return cli_resume


def _apply_overrides(config, prompt_file: str | None, output_dir: str | None):
    """Apply CLI overrides for dataset/output without editing the config file.

    Lets a single config drive multiple datasets (e.g. MedQuAD vs MedicationQA)
    and keep their outputs separate.
    """
    if prompt_file:
        config.prompt_file = prompt_file
    if output_dir:
        config.output.output_dir = output_dir
    return config


def _read_scored(out_dir: Path) -> pd.DataFrame:
    scored_parquet = out_dir / "scored_responses.parquet"
    scored_csv = out_dir / "scored_responses.csv"
    if scored_parquet.exists():
        return pd.read_parquet(scored_parquet)
    if scored_csv.exists():
        return pd.read_csv(scored_csv)
    raise FileNotFoundError("No scored responses found. Run `clinical-eval score` first.")


def _scored_exists(out_dir: Path) -> bool:
    return (out_dir / "scored_responses.parquet").exists() or (out_dir / "scored_responses.csv").exists()


def _report_exists(out_dir: Path) -> bool:
    return (out_dir / "report.md").exists() and (out_dir / "aggregates.csv").exists()


def _apply_sample(questions: pd.DataFrame, sample: int | None) -> pd.DataFrame:
    if sample is None:
        return questions
    if sample <= 0:
        raise ValueError("--sample must be a positive integer")
    return questions.head(sample).copy()


def _apply_sampling(
    questions: pd.DataFrame,
    sample: int | None,
    sample_random: int | None,
    sample_seed: int | None,
) -> pd.DataFrame:
    if sample is not None and sample_random is not None:
        raise ValueError("Use only one of --sample or --sample-random, not both.")
    if sample is not None:
        return _apply_sample(questions, sample)
    if sample_random is not None:
        if sample_random <= 0:
            raise ValueError("--sample-random must be a positive integer")
        n = min(sample_random, len(questions))
        return questions.sample(n=n, random_state=sample_seed).reset_index(drop=True)
    return questions


@app.command()
def run(
    config_path: str = "configs/pipeline.yaml",
    resume: bool | None = typer.Option(None, "--resume/--no-resume"),
    sample: int | None = typer.Option(None, "--sample", min=1),
    sample_random: int | None = typer.Option(None, "--sample-random", min=1),
    sample_seed: int | None = typer.Option(None, "--sample-seed"),
    prompt_file: str | None = typer.Option(None, "--prompt-file"),
    output_dir: str | None = typer.Option(None, "--output-dir"),
) -> None:
    """Run model inference loop and persist raw outputs (incrementally, resumable)."""
    config = _apply_overrides(load_config(config_path), prompt_file, output_dir)
    effective_resume = _resolve_resume(resume, config.resume)
    command_line = " ".join(sys.argv)
    with tee_terminal_to_log(config.output.output_dir, config.output.log_subdir, command_line) as log_path:
        typer.echo(f"[run] loading questions from {config.prompt_file}")
        questions = _apply_sampling(
            load_gold_csv(config.prompt_file),
            sample=sample,
            sample_random=sample_random,
            sample_seed=sample_seed,
        )
        typer.echo(f"[run] loaded {len(questions)} questions")
        # run_evaluations is resume-aware: with resume it skips already-completed
        # (model, question, run) triples recorded in the JSONL checkpoint.
        raw_df = run_evaluations(config, questions, resume=effective_resume)
        typer.echo(f"[run] saved raw outputs: {len(raw_df)} rows -> {config.output.output_dir}")
        typer.echo(f"[run] terminal output log -> {log_path}")


@app.command()
def score(
    config_path: str = "configs/pipeline.yaml",
    resume: bool | None = typer.Option(None, "--resume/--no-resume"),
) -> None:
    """Score raw outputs with deterministic metrics and optional judge."""
    config = load_config(config_path)
    effective_resume = _resolve_resume(resume, config.resume)
    command_line = " ".join(sys.argv)
    with tee_terminal_to_log(config.output.output_dir, config.output.log_subdir, command_line) as log_path:
        out_dir = Path(config.output.output_dir)
        if effective_resume and _scored_exists(out_dir):
            typer.echo("[score] resume enabled and scored outputs already exist; skipping score phase")
            typer.echo(f"[score] terminal output log -> {log_path}")
            return
        typer.echo("[score] loading raw outputs")
        raw_df, out_dir = _read_raw(config_path)
        typer.echo(f"[score] loaded {len(raw_df)} raw rows")
        deterministic_df = score_deterministic(
            raw_df,
            bertscore_model=config.bertscore_model,
            bertscore_batch_size=config.bertscore_batch_size,
        )
        typer.echo("[score] normalization + deterministic scoring complete")
        scored_df = apply_llm_judge(deterministic_df, config)
        typer.echo("[score] llm-judge pass complete")

        out_path_parquet = Path(out_dir) / "scored_responses.parquet"
        out_path_csv = Path(out_dir) / "scored_responses.csv"
        scored_df.to_parquet(out_path_parquet, index=False)
        scored_df.to_csv(out_path_csv, index=False)
        typer.echo(f"[score] saved scored outputs -> {out_path_parquet} and {out_path_csv}")
        typer.echo(f"[score] terminal output log -> {log_path}")


@app.command()
def report(
    config_path: str = "configs/pipeline.yaml",
    resume: bool | None = typer.Option(None, "--resume/--no-resume"),
    output_dir: str | None = typer.Option(None, "--output-dir"),
) -> None:
    """Aggregate scored outputs and generate report + figures."""
    config = _apply_overrides(load_config(config_path), None, output_dir)
    effective_resume = _resolve_resume(resume, config.resume)
    command_line = " ".join(sys.argv)
    with tee_terminal_to_log(config.output.output_dir, config.output.log_subdir, command_line) as log_path:
        out_dir = Path(config.output.output_dir)
        if effective_resume and _report_exists(out_dir):
            typer.echo("[report] resume enabled and report artifacts already exist; skipping report phase")
            typer.echo(f"[report] terminal output log -> {log_path}")
            return
        scored_df = _read_scored(out_dir)

        typer.echo(f"[report] loaded {len(scored_df)} scored rows")
        agg_path, report_path = _build_report(scored_df, config, out_dir)
        typer.echo("[report] aggregate metrics computed")
        typer.echo(f"[report] saved aggregates -> {agg_path}")
        typer.echo(f"[report] saved report -> {report_path}")
        typer.echo(f"[report] terminal output log -> {log_path}")


@app.command(name="export-sample")
def export_sample(
    config_path: str = "configs/pipeline.yaml",
    sample_random: int = typer.Option(50, "--sample-random", min=1),
    sample_seed: int = typer.Option(42, "--sample-seed"),
    out: str = typer.Option("outputs/sampled_questions.csv", "--out"),
    prompt_file: str | None = typer.Option(None, "--prompt-file"),
) -> None:
    """Export the exact deterministically sampled question set (supplementary S1).

    Reuses the same load + ``df.sample(random_state=...)`` path as the run
    commands, so the written file is precisely the evaluation set, making the
    sampling fully reproducible and documentable.
    """
    config = _apply_overrides(load_config(config_path), prompt_file, None)
    questions = load_gold_csv(config.prompt_file)
    sampled = _apply_sampling(
        questions, sample=None, sample_random=sample_random, sample_seed=sample_seed
    )
    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sampled.to_csv(out_path, index=False)
    typer.echo(
        f"[export-sample] wrote {len(sampled)} questions sampled from "
        f"{config.prompt_file} (n={sample_random}, seed={sample_seed}) -> {out_path}"
    )


@app.command(name="judge-reliability")
def judge_reliability(
    config_path: str = "configs/pipeline.yaml",
    output_dir: str | None = typer.Option(None, "--output-dir"),
) -> None:
    """Re-judge a stratified subset K times to quantify judge stochasticity."""
    config = _apply_overrides(load_config(config_path), None, output_dir)
    command_line = " ".join(sys.argv)
    with tee_terminal_to_log(config.output.output_dir, config.output.log_subdir, command_line) as log_path:
        out_dir = Path(config.output.output_dir)
        scored_df = _read_scored(out_dir)
        typer.echo(
            f"[judge-reliability] loaded {len(scored_df)} scored rows; "
            f"subset={config.judge.reliability_subset} passes={config.judge.reliability_passes}"
        )
        long_scores, summary = run_judge_reliability(scored_df, config)
        scores_path = out_dir / "judge_reliability_scores.csv"
        summary_path = out_dir / "judge_reliability_summary.csv"
        long_scores.to_csv(scores_path, index=False)
        pd.DataFrame([summary]).to_csv(summary_path, index=False)
        typer.echo(f"[judge-reliability] summary: {summary}")
        typer.echo(f"[judge-reliability] saved -> {scores_path} and {summary_path}")
        typer.echo(f"[judge-reliability] terminal output log -> {log_path}")


@app.command(name="all")
def run_all(
    config_path: str = "configs/pipeline.yaml",
    resume: bool | None = typer.Option(None, "--resume/--no-resume"),
    sample: int | None = typer.Option(None, "--sample", min=1),
    sample_random: int | None = typer.Option(None, "--sample-random", min=1),
    sample_seed: int | None = typer.Option(None, "--sample-seed"),
    prompt_file: str | None = typer.Option(None, "--prompt-file"),
    output_dir: str | None = typer.Option(None, "--output-dir"),
) -> None:
    """Run full pipeline: run -> score -> report."""
    config = _apply_overrides(load_config(config_path), prompt_file, output_dir)
    effective_resume = _resolve_resume(resume, config.resume)
    command_line = " ".join(sys.argv)
    with tee_terminal_to_log(config.output.output_dir, config.output.log_subdir, command_line) as log_path:
        typer.echo("[all] starting full pipeline")
        out_dir = Path(config.output.output_dir)

        if effective_resume and _scored_exists(out_dir):
            typer.echo("[all] resume enabled: found scored outputs, skipping run + score phases")
            scored_df = _read_scored(out_dir)
        else:
            questions = _apply_sampling(
                load_gold_csv(config.prompt_file),
                sample=sample,
                sample_random=sample_random,
                sample_seed=sample_seed,
            )
            typer.echo(f"[all] loaded {len(questions)} questions from {config.prompt_file}")
            # Resume-aware + incrementally checkpointed: a crash mid-run resumes
            # from the JSONL checkpoint instead of restarting from scratch.
            raw_df = run_evaluations(config, questions, resume=effective_resume)
            typer.echo(f"[all] run phase complete ({len(raw_df)} rows)")
            deterministic_df = score_deterministic(
                raw_df,
                bertscore_model=config.bertscore_model,
                bertscore_batch_size=config.bertscore_batch_size,
            )
            typer.echo("[all] normalization + deterministic scoring complete")
            scored_df = apply_llm_judge(deterministic_df, config)
            scored_df.to_parquet(out_dir / "scored_responses.parquet", index=False)
            scored_df.to_csv(out_dir / "scored_responses.csv", index=False)
            typer.echo("[all] score phase complete")

        if effective_resume and _report_exists(out_dir):
            typer.echo("[all] resume enabled: found report artifacts, skipping report phase")
        else:
            agg_path, report_path = _build_report(scored_df, config, out_dir)
            typer.echo(f"[all] report phase complete ({report_path})")
            typer.echo(f"[all] aggregates -> {agg_path}")
        typer.echo(f"[all] terminal output log -> {log_path}")


if __name__ == "__main__":
    app()
