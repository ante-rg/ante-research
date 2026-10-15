"""Conservative, labeled-cohort prototype for review ranking.

Labels must be supplied independently. Payment features never create labels.
Scores are exploratory and do not diagnose a person or prove harm reduction.
"""

import json
import math
import os
from pathlib import Path
import tempfile

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

FEATURE_COLUMNS = (
    "deposit_count_7d",
    "deposit_amount_7d",
    "withdrawal_count_7d",
    "withdrawal_amount_7d",
    "net_deposit_7d",
    "deposit_count_30d",
    "deposit_amount_30d",
    "withdrawal_count_30d",
    "withdrawal_amount_30d",
    "net_deposit_30d",
)
COUNT_COLUMNS = tuple(name for name in FEATURE_COLUMNS if "count" in name)
AMOUNT_COLUMNS = tuple(name for name in FEATURE_COLUMNS if "amount" in name)
BASE_COLUMNS = ("player_id", "currency", "as_of_utc", *FEATURE_COLUMNS)


def validate_cohort(frame: pd.DataFrame, *, labeled: bool) -> pd.DataFrame:
    """Validate one single-currency, one-row-per-player feature cohort."""
    required = (*BASE_COLUMNS, "label", "label_available_at_utc") if labeled else BASE_COLUMNS
    if not frame.columns.is_unique or set(frame.columns) != set(required):
        raise ValueError("Cohort has missing or unexpected columns")
    if frame.empty:
        raise ValueError("Cohort must not be empty")
    result = frame.loc[:, list(required)].copy()
    ids = result["player_id"]
    if (
        ids.isna().any()
        or not ids.map(lambda value: isinstance(value, str) and bool(value.strip())).all()
    ):
        raise ValueError("player_id must contain nonempty strings")
    if ids.duplicated().any():
        raise ValueError("Cohort contains duplicate player_id values")
    currencies = result["currency"]
    if not currencies.map(
        lambda value: (
            isinstance(value, str)
            and len(value) == 3
            and value.isascii()
            and value.isalpha()
            and value.isupper()
        )
    ).all():
        raise ValueError("currency must use three uppercase letters")
    if currencies.nunique() != 1:
        raise ValueError("Each evaluation cohort must contain one currency")

    def parse_aware(value: object, column: str) -> pd.Timestamp:
        if not isinstance(value, str) or "T" not in value:
            raise ValueError(f"{column} must use timezone-aware ISO 8601 text")
        try:
            stamp = pd.Timestamp(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{column} must use timezone-aware ISO 8601 text") from exc
        if stamp.tzinfo is None:
            raise ValueError(f"{column} must include a timezone")
        return stamp.tz_convert("UTC")

    result["as_of_utc"] = pd.to_datetime(
        result["as_of_utc"].map(lambda value: parse_aware(value, "as_of_utc")), utc=True
    )
    for column in FEATURE_COLUMNS:
        raw = result[column]
        if raw.map(lambda value: isinstance(value, (bool, np.bool_))).any():
            raise ValueError("Feature columns must contain finite numbers")
        parsed = pd.to_numeric(raw, errors="coerce")
        if parsed.isna().any() or not np.isfinite(parsed.to_numpy(dtype=float)).all():
            raise ValueError("Feature columns must contain finite numbers")
        if column in COUNT_COLUMNS and ((parsed < 0).any() or (parsed % 1 != 0).any()):
            raise ValueError("Count features must be nonnegative integers")
        if column in AMOUNT_COLUMNS and (parsed < 0).any():
            raise ValueError("Amount features must be nonnegative")
        result[column] = parsed.astype(float)
    for days in (7, 30):
        expected = result[f"deposit_amount_{days}d"] - result[f"withdrawal_amount_{days}d"]
        if not np.allclose(result[f"net_deposit_{days}d"], expected):
            raise ValueError("Net deposit feature does not match payment amounts")
    if labeled:
        result["label_available_at_utc"] = pd.to_datetime(
            result["label_available_at_utc"].map(
                lambda value: parse_aware(value, "label_available_at_utc")
            ),
            utc=True,
        )
        if (result["label_available_at_utc"] < result["as_of_utc"]).any():
            raise ValueError("Labels cannot be available before their prediction instant")
        labels = result["label"]
        if labels.map(lambda value: isinstance(value, (bool, np.bool_))).any():
            raise ValueError("label must be binary 0 or 1")
        parsed = pd.to_numeric(labels, errors="coerce")
        if parsed.isna().any() or not parsed.isin([0, 1]).all():
            raise ValueError("label must be binary 0 or 1")
        result["label"] = parsed.astype(int)
    return result


def validate_split(train: pd.DataFrame, holdout: pd.DataFrame) -> None:
    """Disallow shared players, currency mixing and nonchronological evaluation."""
    if set(train["player_id"]) & set(holdout["player_id"]):
        raise ValueError("Train and holdout player IDs overlap")
    if train["currency"].iloc[0] != holdout["currency"].iloc[0]:
        raise ValueError("Train and holdout currencies differ")
    if train["as_of_utc"].max() >= holdout["as_of_utc"].min():
        raise ValueError("Train prediction times must precede holdout prediction times")
    if train["label_available_at_utc"].max() >= holdout["as_of_utc"].min():
        raise ValueError("All training labels must be available before holdout prediction times")
    if train["label"].nunique() != 2:
        raise ValueError("Training cohort must contain both binary label classes")


def score_from_artifact(cohort: pd.DataFrame, artifact: dict) -> np.ndarray:
    """Apply a trusted JSON model artifact to a validated cohort."""
    if artifact.get("version") != 1 or artifact.get("feature_columns") != list(FEATURE_COLUMNS):
        raise ValueError("Unsupported model artifact")
    if artifact.get("currency") != cohort["currency"].iloc[0]:
        raise ValueError("Model currency and cohort currency differ")
    try:
        eligible_from = pd.Timestamp(artifact["eligible_from_utc"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("Model artifact lacks valid label-availability boundary") from exc
    if eligible_from.tzinfo is None:
        raise ValueError("Model artifact lacks valid label-availability boundary")
    if (cohort["as_of_utc"] <= eligible_from.tz_convert("UTC")).any():
        raise ValueError("Prediction precedes model label-availability boundary")
    try:
        mean = np.asarray(artifact["scaler_mean"], dtype=float)
        scale = np.asarray(artifact["scaler_scale"], dtype=float)
        coef = np.asarray(artifact["coefficient"], dtype=float)
        intercept = float(artifact["intercept"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("Invalid model artifact") from exc
    if any(vector.shape != (len(FEATURE_COLUMNS),) for vector in (mean, scale, coef)):
        raise ValueError("Invalid model artifact dimensions")
    if (
        not all(np.isfinite(vector).all() for vector in (mean, scale, coef))
        or not math.isfinite(intercept)
        or (scale <= 0).any()
    ):
        raise ValueError("Invalid model artifact values")
    scaled = (cohort[list(FEATURE_COLUMNS)].to_numpy(dtype=float) - mean) / scale
    logit = np.clip(scaled @ coef + intercept, -700, 700)
    return 1 / (1 + np.exp(-logit))


def precision_at_capacity(labels: pd.Series, scores: np.ndarray, capacity: int) -> dict:
    if capacity < 1 or capacity > len(labels):
        raise ValueError("Review capacity must be within cohort size")
    selected = np.argsort(-scores, kind="stable")[:capacity]
    positives = int(labels.iloc[selected].sum())
    return {
        "reviewed": capacity,
        "proxy_positives_reviewed": positives,
        "proxy_precision_at_capacity": positives / capacity,
    }


def train_and_evaluate(
    train: pd.DataFrame, holdout: pd.DataFrame, capacity: int
) -> tuple[dict, dict]:
    """Train on an independently labeled cohort and compare a fixed rule at K."""
    train = validate_cohort(train, labeled=True)
    holdout = validate_cohort(holdout, labeled=True)
    validate_split(train, holdout)
    if capacity < 1 or capacity > len(holdout):
        raise ValueError("Review capacity must be within holdout cohort size")
    scaler = StandardScaler().fit(train[list(FEATURE_COLUMNS)])
    x_train = scaler.transform(train[list(FEATURE_COLUMNS)])
    model = LogisticRegression(random_state=0, max_iter=1000, class_weight="balanced").fit(
        x_train, train["label"]
    )
    artifact = {
        "version": 1,
        "currency": train["currency"].iloc[0],
        "eligible_from_utc": train["label_available_at_utc"].max().isoformat(),
        "feature_columns": list(FEATURE_COLUMNS),
        "scaler_mean": scaler.mean_.tolist(),
        "scaler_scale": scaler.scale_.tolist(),
        "coefficient": model.coef_[0].tolist(),
        "intercept": float(model.intercept_[0]),
    }
    model_scores = score_from_artifact(holdout, artifact)
    baseline_scores = holdout["net_deposit_30d"].to_numpy(dtype=float)
    report = {
        "evaluation_scope": "labeled holdout proxy only; not population performance",
        "train_rows": len(train),
        "holdout_rows": len(holdout),
        "currency": artifact["currency"],
        "review_capacity": capacity,
        "holdout_proxy_positives": int(holdout["label"].sum()),
        "logistic_regression": precision_at_capacity(holdout["label"], model_scores, capacity),
        "fixed_rule_net_deposit_30d": precision_at_capacity(
            holdout["label"], baseline_scores, capacity
        ),
    }
    return artifact, report


def write_json_atomic(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".json", dir=path.parent, delete=False
        ) as stream:
            temporary = Path(stream.name)
            json.dump(payload, stream, indent=2, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
