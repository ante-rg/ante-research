"""Train and evaluate a provisional review-ranking model on labeled cohorts."""

from pathlib import Path
from typing import Annotated

from loguru import logger
import pandas as pd
import typer

from ante.config import MODELS_DIR, PROCESSED_DATA_DIR
from ante.modeling.core import train_and_evaluate, write_json_atomic

app = typer.Typer()


@app.command()
def main(
    train_path: Annotated[
        Path, typer.Option(help="Independently labeled training cohort CSV")
    ] = PROCESSED_DATA_DIR / "train_labeled.csv",
    holdout_path: Annotated[
        Path, typer.Option(help="Independently labeled holdout cohort CSV")
    ] = PROCESSED_DATA_DIR / "holdout_labeled.csv",
    model_path: Annotated[Path, typer.Option(help="Output JSON model artifact")] = MODELS_DIR
    / "payment_review_model.json",
    report_path: Annotated[
        Path, typer.Option(help="Output aggregate evaluation JSON")
    ] = MODELS_DIR / "payment_review_evaluation.json",
    review_capacity: Annotated[
        int, typer.Option(min=1, help="Fixed number of holdout players reviewed by each method")
    ] = 10,
) -> None:
    train = pd.read_csv(train_path, dtype={"player_id": "string", "currency": "string"})
    holdout = pd.read_csv(holdout_path, dtype={"player_id": "string", "currency": "string"})
    artifact, report = train_and_evaluate(train, holdout, review_capacity)
    write_json_atomic(model_path, artifact)
    write_json_atomic(report_path, report)
    logger.success("Trained prototype and wrote aggregate holdout evaluation")


if __name__ == "__main__":
    app()
