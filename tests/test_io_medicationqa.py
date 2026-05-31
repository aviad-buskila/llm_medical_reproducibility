import pandas as pd

from clinical_eval_pipeline.io_gold_csv import load_gold_csv
from clinical_eval_pipeline.io_medicationqa import convert_medicationqa


def test_convert_medicationqa_normalizes_and_drops_blanks(tmp_path) -> None:
    # MedicationQA-style raw file: capitalized columns, an extra focus column,
    # and a blank-answer row that must be dropped.
    raw = pd.DataFrame(
        {
            "Question": ["What is metformin?", "Side effects of aspirin?", "Blank one?"],
            "Answer": ["Metformin treats type 2 diabetes.", "Aspirin may cause bleeding.", ""],
            "Focus (Drug)": ["metformin", "aspirin", "x"],
            "Question Type": ["Information", "SideEffects", "Other"],
        }
    )
    src = tmp_path / "medqa_raw.csv"
    raw.to_csv(src, index=False)

    dst = convert_medicationqa(src, tmp_path / "medicationqa.csv")
    converted = pd.read_csv(dst)
    assert list(converted.columns)[:2] == ["question", "answer"]
    assert len(converted) == 2  # blank-answer row dropped
    assert converted["source"].unique().tolist() == ["MedicationQA"]

    # Output is directly loadable by the existing gold-CSV loader.
    gold = load_gold_csv(dst)
    assert set(["id", "question", "gold_answer", "category"]).issubset(gold.columns)
    assert len(gold) == 2


def test_convert_medicationqa_missing_columns_raises(tmp_path) -> None:
    src = tmp_path / "bad.csv"
    pd.DataFrame({"foo": [1], "bar": [2]}).to_csv(src, index=False)
    try:
        convert_medicationqa(src, tmp_path / "out.csv")
    except ValueError as exc:
        assert "question/answer columns" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("expected ValueError for missing columns")
