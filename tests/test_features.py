import pandas as pd
import pytest

from ante.features import build_payment_features


def sample_events():
    return pd.DataFrame(
        [
            ("a", "p1", "2026-10-08T00:00:00Z", "deposit", 20, "EUR"),
            ("b", "p1", "2026-10-14T23:59:59Z", "withdrawal", 5, "EUR"),
            ("c", "p1", "2026-10-15T00:00:00Z", "deposit", 999, "EUR"),
            ("d", "p1", "2026-10-01T00:00:00Z", "deposit", 10, "EUR"),
            ("e", "p1", "2026-10-14T12:00:00+02:00", "deposit", 7, "USD"),
            ("f", "p2", "2026-10-15T00:00:00Z", "deposit", 100, "EUR"),
        ],
        columns=["event_id", "player_id", "event_time", "event_type", "amount", "currency"],
    )


def test_window_boundaries_no_future_leakage_and_currency_separation():
    result = build_payment_features(sample_events(), "2026-10-15T00:00:00Z")
    eur = result.loc[result.currency == "EUR"].iloc[0]
    usd = result.loc[result.currency == "USD"].iloc[0]
    assert set(result.player_id) == {"p1"}  # Future-only players are not exposed.

    assert eur.deposit_count_7d == 1  # Inclusive lower bound.
    assert eur.deposit_amount_7d == 20
    assert eur.withdrawal_amount_7d == 5
    assert eur.net_deposit_7d == 15
    assert eur.deposit_amount_30d == 30  # Future event is excluded.
    assert usd.deposit_amount_7d == 7
    assert usd.net_deposit_7d == 7


def test_as_of_requires_timezone():
    with pytest.raises(ValueError, match="timezone"):
        build_payment_features(sample_events(), "2026-10-15T00:00:00")
