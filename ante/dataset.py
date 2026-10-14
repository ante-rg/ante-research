"""Validate a prepared canonical payment-event CSV for the prototype."""

import os
from pathlib import Path
import tempfile
from typing import Annotated

from loguru import logger
import pandas as pd
import typer

from ante.config import PROCESSED_DATA_DIR, RAW_DATA_DIR
from ante.payment_schema import validate_payment_events

app = typer.Typer()


def process_payment_csv(input_path: Path, output_path: Path) -> int:
    """Validate and atomically write a canonical CSV; return event count."""
    frame = pd.read_csv(
        input_path,
        dtype={
            "event_id": "string",
            "player_id": "string",
            "event_type": "string",
            "currency": "string",
        },
    )
    validated = validate_payment_events(frame)
    # Keep the processed CSV inside the same ISO 8601 input contract.
    validated["event_time"] = validated["event_time"].map(lambda stamp: stamp.isoformat())
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            suffix=".csv",
            prefix=f".{output_path.name}.",
            dir=output_path.parent,
            delete=False,
        ) as stream:
            temp_path = Path(stream.name)
            validated.to_csv(stream, index=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_path, output_path)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
    return len(validated)


@app.command()
def main(
    input_path: Annotated[Path, typer.Option(help="Prepared canonical CSV")] = RAW_DATA_DIR
    / "payment_events.csv",
    output_path: Annotated[Path, typer.Option(help="Validated CSV")] = PROCESSED_DATA_DIR
    / "payment_events.csv",
) -> None:
    count = process_payment_csv(input_path, output_path)
    logger.success("Validated {} payment events and wrote processed CSV", count)


if __name__ == "__main__":
    app()
