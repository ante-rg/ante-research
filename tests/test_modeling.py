"""Model checks use synthetic, explicitly supplied labels only."""

import json

import pandas as pd
import pytest
from typer.testing import CliRunner

from ante.modeling.core import FEATURE_COLUMNS, train_and_evaluate
from ante.modeling.predict import app as predict_app
from ante.modeling.predict import predict_cohort
from ante.modeling.train import app as train_app


def row(player_id: str, as_of: str, deposit: float, label: int, label_available: str) -> dict:
    return {
        "player_id": player_id,
        "currency": "EUR",
        "as_of_utc": as_of,
        "deposit_count_7d": 1,
        "deposit_amount_7d": deposit,
        "withdrawal_count_7d": 0,
        "withdrawal_amount_7d": 0,
        "net_deposit_7d": deposit,
        "deposit_count_30d": 1,
        "deposit_amount_30d": deposit,
        "withdrawal_count_30d": 0,
        "withdrawal_amount_30d": 0,
        "net_deposit_30d": deposit,
        "label": label,
        "label_available_at_utc": label_available,
    }


def cohorts() -> tuple[pd.DataFrame, pd.DataFrame]:
    train = pd.DataFrame(
        [
            row("t-1", "2026-01-01T00:00:00Z", 1, 0, "2026-01-08T00:00:00Z"),
            row("t-2", "2026-01-01T00:00:00Z", 10, 1, "2026-01-08T00:00:00Z"),
            row("t-3", "2026-01-01T00:00:00Z", 2, 0, "2026-01-08T00:00:00Z"),
            row("t-4", "2026-01-01T00:00:00Z", 9, 1, "2026-01-08T00:00:00Z"),
        ]
    )
    holdout = pd.DataFrame(
        [
            row("h-1", "2026-02-01T00:00:00Z", 3, 0, "2026-02-08T00:00:00Z"),
            row("h-2", "2026-02-01T00:00:00Z", 8, 1, "2026-02-08T00:00:00Z"),
            row("h-3", "2026-02-01T00:00:00Z", 6, 1, "2026-02-08T00:00:00Z"),
        ]
    )
    return train, holdout


def test_train_evaluate_and_predict_without_inventing_labels():
    train, holdout = cohorts()
    artifact, report = train_and_evaluate(train, holdout, capacity=2)
    assert artifact["feature_columns"] == list(FEATURE_COLUMNS)
    assert artifact["eligible_from_utc"] == "2026-01-08T00:00:00+00:00"
    assert report["review_capacity"] == 2
    assert report["logistic_regression"]["reviewed"] == 2
    assert report["fixed_rule_net_deposit_30d"]["reviewed"] == 2
    assert "player_id" not in json.dumps(report)
    assert "h-1" not in json.dumps(report)

    unlabeled = holdout.drop(columns=["label", "label_available_at_utc"])
    predictions = predict_cohort(unlabeled, artifact)
    assert len(predictions) == 3
    assert predictions["review_score"].between(0, 1).all()

    historical = unlabeled.assign(as_of_utc="2026-01-07T23:59:59Z")
    with pytest.raises(ValueError, match="label-availability boundary"):
        predict_cohort(historical, artifact)
    at_boundary = unlabeled.assign(as_of_utc="2026-01-08T00:00:00Z")
    with pytest.raises(ValueError, match="label-availability boundary"):
        predict_cohort(at_boundary, artifact)


@pytest.mark.parametrize(
    "mutate, message",
    [
        (
            lambda train, holdout: (train, holdout.assign(player_id=["t-1", "h-2", "h-3"])),
            "overlap",
        ),
        (
            lambda train, holdout: (train, holdout.assign(as_of_utc="2025-12-01T00:00:00Z")),
            "precede",
        ),
        (lambda train, holdout: (train.assign(label=[0, 0, 0, 0]), holdout), "both binary"),
        (lambda train, holdout: (train.assign(label=[0, 1, 2, 1]), holdout), "binary 0 or 1"),
        (lambda train, holdout: (train.drop(columns="deposit_count_7d"), holdout), "columns"),
        (lambda train, holdout: (train, holdout.assign(currency="USD")), "currencies differ"),
        (
            lambda train, holdout: (train, holdout.assign(currency=["EUR", "USD", "EUR"])),
            "one currency",
        ),
        (
            lambda train, holdout: (train.drop(columns="label_available_at_utc"), holdout),
            "columns",
        ),
        (
            lambda train, holdout: (
                train.assign(label_available_at_utc="2026-02-01T00:00:00Z"),
                holdout,
            ),
            "training labels must be available",
        ),
        (
            lambda train, holdout: (
                train.assign(label_available_at_utc="2025-12-31T00:00:00Z"),
                holdout,
            ),
            "before their prediction instant",
        ),
        (
            lambda train, holdout: (
                train.assign(label_available_at_utc="2026-01-08T00:00:00"),
                holdout,
            ),
            "include a timezone",
        ),
    ],
)
def test_fail_closed_invalid_cohort_or_split(mutate, message):
    train, holdout = mutate(*cohorts())
    with pytest.raises(ValueError, match=message):
        train_and_evaluate(train, holdout, capacity=2)


def test_training_cli_writes_only_aggregate_report(tmp_path):
    train, holdout = cohorts()
    train_path = tmp_path / "train.csv"
    holdout_path = tmp_path / "holdout.csv"
    model_path = tmp_path / "model.json"
    report_path = tmp_path / "report.json"
    train.to_csv(train_path, index=False)
    holdout.to_csv(holdout_path, index=False)
    result = CliRunner().invoke(
        train_app,
        [
            "--train-path",
            str(train_path),
            "--holdout-path",
            str(holdout_path),
            "--model-path",
            str(model_path),
            "--report-path",
            str(report_path),
            "--review-capacity",
            "2",
        ],
    )
    assert result.exit_code == 0, result.output
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["holdout_rows"] == 3
    assert "h-2" not in report_path.read_text(encoding="utf-8")
    assert "t-2" not in model_path.read_text(encoding="utf-8")

    unlabeled_path = tmp_path / "unlabeled.csv"
    predictions_path = tmp_path / "private_scores.csv"
    holdout.drop(columns=["label", "label_available_at_utc"]).to_csv(unlabeled_path, index=False)
    predicted = CliRunner().invoke(
        predict_app,
        [
            "--features-path",
            str(unlabeled_path),
            "--model-path",
            str(model_path),
            "--predictions-path",
            str(predictions_path),
        ],
    )
    assert predicted.exit_code == 0, predicted.output
    scores = pd.read_csv(predictions_path)
    assert len(scores) == 3
    assert scores["review_score"].between(0, 1).all()
