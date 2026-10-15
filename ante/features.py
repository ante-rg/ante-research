"""Point-in-time summaries of canonical payment events.

These are descriptive payment features. Net deposits are not gambling losses, and
these features alone cannot establish risk of harm or a clinical diagnosis.
"""

import os
from pathlib import Path
import tempfile

from loguru import logger
import pandas as pd
import typer

from ante.config import PROCESSED_DATA_DIR
from ante.payment_schema import validate_payment_events

app = typer.Typer()
WINDOW_DAYS = (7, 30)
KEYS = ["player_id", "currency"]


def build_payment_features(events: pd.DataFrame, as_of: str | pd.Timestamp) -> pd.DataFrame:
    """Summarise events strictly before a timezone-aware prediction instant.

    The lower bound of each lookback window is inclusive and the prediction
    instant is exclusive. Separate rows are kept for separate currencies.
    """
    cutoff = pd.Timestamp(as_of)
    if cutoff.tzinfo is None:
        raise ValueError("as_of must include a timezone")
    cutoff = cutoff.tz_convert("UTC")

    valid = validate_payment_events(events)
    history = valid.loc[valid["event_time"] < cutoff]
    keys = history[KEYS].drop_duplicates().sort_values(KEYS).reset_index(drop=True)
    result = keys.copy()
    result["as_of_utc"] = cutoff.isoformat()

    for days in WINDOW_DAYS:
        start = cutoff - pd.Timedelta(days=days)
        window = history.loc[history["event_time"] >= start]
        for event_type in ("deposit", "withdrawal"):
            subset = window.loc[window["event_type"] == event_type]
            counts = subset.groupby(KEYS, sort=False)["event_id"].count()
            amounts = subset.groupby(KEYS, sort=False)["amount"].sum()
            index = pd.MultiIndex.from_frame(keys[KEYS])
            result[f"{event_type}_count_{days}d"] = counts.reindex(index, fill_value=0).to_numpy()
            result[f"{event_type}_amount_{days}d"] = amounts.reindex(
                index, fill_value=0
            ).to_numpy()

        result[f"net_deposit_{days}d"] = (
            result[f"deposit_amount_{days}d"] - result[f"withdrawal_amount_{days}d"]
        )

    return result


@app.command()
def main(
    input_path: Path = PROCESSED_DATA_DIR / "payment_events.csv",
    output_path: Path = PROCESSED_DATA_DIR / "payment_features.csv",
    as_of: str = typer.Option(..., help="Timezone-aware ISO 8601 prediction instant"),
) -> None:
    """Generate local player-level payment features for controlled analysis."""
    events = pd.read_csv(input_path, dtype={"event_id": "string", "player_id": "string"})
    features = build_payment_features(events, as_of)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Keep the destination intact if validation or writing fails.
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".csv", dir=output_path.parent, delete=False
        ) as tmp:
            tmp_path = Path(tmp.name)
            features.to_csv(tmp, index=False)
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(tmp_path, output_path)
    finally:
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)
    logger.info("Wrote {} aggregate player-currency feature rows", len(features))


if __name__ == "__main__":
    app()
