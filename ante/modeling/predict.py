"""Score a prepared payment-feature cohort for human review only."""

import json
import os
from pathlib import Path
import tempfile
from typing import Annotated

from loguru import logger
import pandas as pd
import typer

from ante.config import MODELS_DIR, PROCESSED_DATA_DIR
from ante.modeling.core import score_from_artifact, validate_cohort

app = typer.Typer()


def predict_cohort(features: pd.DataFrame, artifact: dict) -> pd.DataFrame:
    cohort = validate_cohort(features, labeled=False)
    probabilities = score_from_artifact(cohort, artifact)
    return pd.DataFrame(
        {
            "player_id": cohort["player_id"],
            "currency": cohort["currency"],
            "as_of_utc": cohort["as_of_utc"].map(lambda stamp: stamp.isoformat()),
            "review_score": probabilities,
        }
    )


@app.command()
def main(
    features_path: Annotated[
        Path, typer.Option(help="Prepared unlabeled feature cohort CSV")
    ] = PROCESSED_DATA_DIR / "payment_features.csv",
    model_path: Annotated[Path, typer.Option(help="Trusted JSON model artifact")] = MODELS_DIR
    / "payment_review_model.json",
    predictions_path: Annotated[
        Path, typer.Option(help="Private individual review-score CSV")
    ] = PROCESSED_DATA_DIR / "payment_review_scores.csv",
) -> None:
    features = pd.read_csv(features_path, dtype={"player_id": "string", "currency": "string"})
    with model_path.open(encoding="utf-8") as stream:
        artifact = json.load(stream)
    predictions = predict_cohort(features, artifact)
    predictions_path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            suffix=".csv",
            dir=predictions_path.parent,
            delete=False,
        ) as stream:
            temporary = Path(stream.name)
            predictions.to_csv(stream, index=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, predictions_path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    logger.success("Wrote {} private review scores", len(predictions))


if __name__ == "__main__":
    app()
