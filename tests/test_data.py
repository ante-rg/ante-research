"""Canonical payment input checks use synthetic events only."""

import pandas as pd
import pytest

from ante.dataset import process_payment_csv
from ante.features import build_payment_features
from ante.payment_schema import validate_payment_events


def payment_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "event_id": "e-1",
                "player_id": "p-1",
                "event_time": "2026-01-01T12:00:00+02:00",
                "event_type": "deposit",
                "amount": 10.5,
                "currency": "EUR",
            },
            {
                "event_id": "e-2",
                "player_id": "p-1",
                "event_time": "2026-01-02T10:00:00Z",
                "event_type": "withdrawal",
                "amount": 2.0,
                "currency": "EUR",
            },
        ]
    )


def test_valid_input_is_normalized_and_written(tmp_path):
    source = tmp_path / "raw.csv"
    output = tmp_path / "processed" / "events.csv"
    payment_frame().to_csv(source, index=False)
    assert process_payment_csv(source, output) == 2
    result = pd.read_csv(output)
    assert result.columns.tolist() == [
        "event_id",
        "player_id",
        "event_time",
        "event_type",
        "amount",
        "currency",
    ]
    assert result.loc[0, "event_time"] == "2026-01-01T10:00:00+00:00"
    assert result.loc[0, "amount"] == 10.5

    features = build_payment_features(result, "2026-01-03T00:00:00Z")
    assert features.loc[0, "deposit_count_7d"] == 1
    assert features.loc[0, "withdrawal_count_7d"] == 1
    assert features.loc[0, "net_deposit_7d"] == 8.5


@pytest.mark.parametrize(
    ("change", "error"),
    [
        (lambda frame: frame.drop(columns="currency"), "canonical columns"),
        (
            lambda frame: frame.assign(event_time=["2026-01-01T12:00:00", "2026-01-02T10:00:00Z"]),
            "UTC offset",
        ),
        (lambda frame: frame.assign(amount=[0, 2]), "positive finite"),
        (lambda frame: frame.assign(event_id=["e-1", "e-1"]), "duplicate event_id"),
    ],
)
def test_invalid_input_is_rejected(change, error):
    with pytest.raises(ValueError, match=error):
        validate_payment_events(change(payment_frame()))


def test_failed_validation_does_not_replace_existing_output(tmp_path):
    source = tmp_path / "raw.csv"
    output = tmp_path / "processed.csv"
    output.write_text("existing", encoding="utf-8")
    payment_frame().assign(amount=[-1, 2]).to_csv(source, index=False)
    with pytest.raises(ValueError, match="positive finite"):
        process_payment_csv(source, output)
    assert output.read_text(encoding="utf-8") == "existing"
