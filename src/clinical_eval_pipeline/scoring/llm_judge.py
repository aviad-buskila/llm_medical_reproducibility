from __future__ import annotations

import json
import re

import pandas as pd

from clinical_eval_pipeline.config import JudgeConfig, PipelineConfig
from clinical_eval_pipeline.ollama_client import OllamaClient


def _extract_score(text: str) -> float | None:
    match = re.search(r"score\s*=\s*([0-9]*\.?[0-9]+)", text.lower())
    if match:
        score = float(match.group(1))
        return max(0.0, min(1.0, score))

    # Fallback: take first standalone float between 0 and 1 from the judge output.
    fallback = re.search(r"\b(0(?:\.\d+)?|1(?:\.0+)?)\b", text.lower())
    if fallback:
        score = float(fallback.group(1))
        return max(0.0, min(1.0, score))
    return None


def score_response(
    client: OllamaClient,
    judge_cfg: JudgeConfig,
    question: str,
    gold_answer: str,
    model_answer: str,
) -> tuple[float | None, str]:
    """Run the judge once on a single response and return (parsed_score, text).

    Shared by the main scoring pass and the judge-reliability sub-study so both
    use an identical prompt, fallback and parsing path.
    """
    judge_payload = {
        "instructions": judge_cfg.rubric_prompt,
        "question": question,
        "gold_answer": gold_answer,
        "model_answer": model_answer,
        "output_format": {"score": "float_0_to_1", "rationale": "short_string"},
    }
    judge_prompt = (
        "You are a strict evaluator. Return JSON only with keys: score, rationale.\n"
        f"{json.dumps(judge_payload, ensure_ascii=False)}"
    )

    if judge_cfg.use_chat_api:
        result = client.chat(model=judge_cfg.model, user_message=judge_prompt)
    else:
        result = client.generate(model=judge_cfg.model, prompt=judge_prompt)
    judge_text = str(result.get("response", "")).strip()
    if not judge_text:
        # One fallback attempt with a plain text format in case model struggles with JSON.
        fallback_prompt = (
            f"{judge_cfg.rubric_prompt}\n\n"
            "Return exactly in one line: score=<float> rationale=<short reason>\n\n"
            f"QUESTION: {question}\n"
            f"GOLD_ANSWER: {gold_answer}\n"
            f"MODEL_ANSWER: {model_answer}\n"
        )
        if judge_cfg.use_chat_api:
            result = client.chat(model=judge_cfg.model, user_message=fallback_prompt)
        else:
            result = client.generate(model=judge_cfg.model, prompt=fallback_prompt)
        judge_text = str(result.get("response", "")).strip()

    return _extract_score(judge_text), judge_text


def apply_llm_judge(scored_df: pd.DataFrame, config: PipelineConfig) -> pd.DataFrame:
    if not config.judge.enabled:
        out = scored_df.copy()
        out["judge_score"] = None
        out["judge_rationale"] = ""
        return out

    judge_cfg: JudgeConfig = config.judge
    if not judge_cfg.model:
        raise ValueError("Judge is enabled but no judge model is configured.")

    client = OllamaClient(config.ollama_base_url, config.generation)
    out = scored_df.copy()
    judge_scores: list[float | None] = []
    judge_rationales: list[str] = []
    parse_failures = 0

    for _, row in out.iterrows():
        if config.verbose:
            print(
                f"[judge] evaluating target_model={row['model']} question_id={row['question_id']} "
                f"judge_model={judge_cfg.model} mode={'chat' if judge_cfg.use_chat_api else 'generate'}",
                flush=True,
            )
        parsed, judge_text = score_response(
            client,
            judge_cfg,
            question=str(row["question"]),
            gold_answer=str(row["gold_answer"]),
            model_answer=str(row["response_text"]),
        )
        if not judge_text:
            print(
                f"[judge][warn] empty response after fallback judge_model={judge_cfg.model} "
                f"target_model={row['model']} question_id={row['question_id']}",
                flush=True,
            )
        if parsed is None:
            parse_failures += 1
            snippet = judge_text.replace("\n", " ")[:220]
            print(
                f"[judge][warn] could not parse score judge_model={judge_cfg.model} "
                f"target_model={row['model']} question_id={row['question_id']} output='{snippet}'",
                flush=True,
            )
        elif config.verbose:
            snippet = judge_text.replace("\n", " ")[:160]
            print(
                f"[judge] parsed score={parsed:.3f} target_model={row['model']} "
                f"question_id={row['question_id']} output_preview='{snippet}'",
                flush=True,
            )
        judge_scores.append(parsed)
        judge_rationales.append(judge_text)

    out["judge_score"] = judge_scores
    out["judge_rationale"] = judge_rationales
    print(
        f"[judge] completed rows={len(out)} judge_model={judge_cfg.model} "
        f"parsed_scores={len(out) - parse_failures} parse_failures={parse_failures}",
        flush=True,
    )
    if parse_failures == len(out):
        raise RuntimeError(
            "LLM judge produced no parseable scores for all rows. "
            "Check judge model output format, prompt, or model compatibility."
        )
    return out
