"""Validation contract for prepared prototype payment events."""

from datetime import datetime

import numpy as np
import pandas as pd

PAYMENT_COLUMNS = (
    "event_id",
    "player_id",
    "event_time",
    "event_type",
    "amount",
    "currency",
)
EVENT_TYPES = frozenset({"deposit", "withdrawal"})


def validate_payment_events(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a validated copy with UTC times and numeric amounts.

    Exceptions include aggregate diagnostics only, never player records.
    """
    if not isinstance(frame, pd.DataFrame):
        raise TypeError("Payment events must be a pandas DataFrame")
    if not frame.columns.is_unique or set(frame.columns) != set(PAYMENT_COLUMNS):
        raise ValueError("Payment input must contain exactly the six canonical columns")
    result = frame.loc[:, list(PAYMENT_COLUMNS)].copy()
    if result.empty:
        raise ValueError("Payment input must contain at least one event")

    for column in ("event_id", "player_id"):
        values = result[column]
        if values.isna().any() or not values.map(lambda value: isinstance(value, str)).all():
            raise ValueError(f"{column} must contain nonempty strings")
        if not values.map(lambda value: bool(value.strip()) and value == value.strip()).all():
            raise ValueError(f"{column} must contain nonempty strings without outer whitespace")
    if result["event_id"].duplicated().any():
        raise ValueError("Payment input contains duplicate event_id values")
    if (
        not result["event_type"]
        .map(lambda value: isinstance(value, str) and value in EVENT_TYPES)
        .all()
    ):
        raise ValueError("event_type must be deposit or withdrawal")
    if (
        not result["currency"]
        .map(
            lambda value: (
                isinstance(value, str)
                and len(value) == 3
                and value.isascii()
                and value.isalpha()
                and value.isupper()
            )
        )
        .all()
    ):
        raise ValueError("currency must be a three-letter uppercase code")

    amount = pd.to_numeric(result["amount"], errors="coerce")
    if result["amount"].map(lambda value: isinstance(value, (bool, np.bool_))).any():
        raise ValueError("amount must be a positive finite number")
    if (
        amount.isna().any()
        or not np.isfinite(amount.to_numpy(dtype=float)).all()
        or (amount <= 0).any()
    ):
        raise ValueError("amount must be a positive finite number")
    result["amount"] = amount.astype(float)

    def parse_time(value: object) -> pd.Timestamp:
        if not isinstance(value, (str, datetime, pd.Timestamp)):
            raise TypeError("event_time must be an aware ISO timestamp")
        if isinstance(value, str):
            if not value.strip() or "T" not in value:
                raise ValueError("event_time must be an aware ISO timestamp")
            try:
                parsed = datetime.fromisoformat(value)
            except ValueError as exc:
                raise ValueError("event_time must be an aware ISO timestamp") from exc
        else:
            parsed = value
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError("event_time must include a UTC offset")
        return pd.Timestamp(parsed).tz_convert("UTC")

    result["event_time"] = pd.to_datetime(result["event_time"].map(parse_time), utc=True)
    return result
