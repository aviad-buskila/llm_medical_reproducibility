"""Convert the MedicationQA dataset into the pipeline's gold CSV schema.

MedicationQA (Ben Abacha et al., 2019, "Bridging the Gap between Consumers'
Medication Questions and Trusted Answers") is a free-form consumer medical QA
dataset with reference answers, in the same spirit as MedQuAD. This module
normalizes its column names (which vary across releases, e.g. ``Question`` /
``Answer`` in the original XLSX) into the ``question,answer`` columns consumed
by :func:`clinical_eval_pipeline.io_gold_csv.load_gold_csv`, and drops rows
with an empty question or answer. The converted CSV can then be used as the
pipeline ``prompt_file`` (Reviewer #1: a second evaluation dataset).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

_QUESTION_ALIASES = ("question", "questions", "consumer question")
_ANSWER_ALIASES = ("answer", "answers", "trusted answer", "response")
_FOCUS_ALIASES = ("focus", "focus (drug)", "drug", "focus_area")
_TYPE_ALIASES = ("question type", "qtype", "category")


def _read_any(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    if suffix in {".tsv", ".tab"}:
        return pd.read_csv(path, sep="\t")
    return pd.read_csv(path)


def _find_column(columns: list[str], aliases: tuple[str, ...]) -> str | None:
    lowered = {c.strip().lower(): c for c in columns}
    for alias in aliases:
        if alias in lowered:
            return lowered[alias]
    return None


def convert_medicationqa(
    src: str | Path,
    dst: str | Path = "data/medicationqa.csv",
    *,
    question_col: str | None = None,
    answer_col: str | None = None,
) -> Path:
    """Convert a raw MedicationQA file (CSV/TSV/XLSX) to the gold CSV schema.

    Writes ``dst`` with columns ``question,answer,source,focus_area`` and
    returns its path. Raises if the question/answer columns cannot be located.
    """
    src_path = Path(src)
    if not src_path.exists():
        raise FileNotFoundError(f"MedicationQA source file not found: {src_path}")

    raw = _read_any(src_path)
    columns = list(raw.columns)
    q_col = question_col or _find_column(columns, _QUESTION_ALIASES)
    a_col = answer_col or _find_column(columns, _ANSWER_ALIASES)
    if q_col is None or a_col is None:
        raise ValueError(
            "Could not locate question/answer columns in MedicationQA file. "
            f"Found columns: {columns}. Pass question_col/answer_col explicitly."
        )
    focus_col = _find_column(columns, _FOCUS_ALIASES)
    type_col = _find_column(columns, _TYPE_ALIASES)

    out = pd.DataFrame(
        {
            "question": raw[q_col].astype("string").str.strip(),
            "answer": raw[a_col].astype("string").str.strip(),
            "source": "MedicationQA",
            "focus_area": (
                raw[focus_col].astype("string") if focus_col else pd.Series([""] * len(raw))
            ),
        }
    )
    if type_col:
        out["focus_area"] = out["focus_area"].fillna("") + " | " + raw[type_col].astype("string").fillna("")

    # Drop rows lacking a usable question or answer (MedicationQA has some blanks).
    out = out[(out["question"].fillna("") != "") & (out["answer"].fillna("") != "")]
    out = out.reset_index(drop=True)

    dst_path = Path(dst)
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(dst_path, index=False)
    return dst_path
