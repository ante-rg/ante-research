"""Local-only assessment API for a prepared, permitted payment-event cohort.

This prototype returns relative review scores, never a diagnosis or an automatic
account decision. It has no authentication and must not be exposed publicly.
"""

import ipaddress
import json
import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from ante.config import MODELS_DIR
from ante.features import build_payment_features
from ante.modeling.core import score_from_artifact, validate_cohort


class AssessmentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    as_of: str
    events: list[dict[str, Any]] = Field(min_length=1)


def create_app(model_path: Path | None = None) -> FastAPI:
    """Create the single-endpoint prototype with an explicit local model path."""
    app = FastAPI(
        title="Ante review-score prototype",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    selected_model = model_path or Path(
        os.environ.get("ANTE_MODEL_PATH", str(MODELS_DIR / "payment_review_model.json"))
    )

    @app.middleware("http")
    async def loopback_only(request: Request, call_next: Any) -> Any:
        try:
            peer = ipaddress.ip_address(request.client.host) if request.client else None
        except ValueError:
            peer = None
        if peer is None or not peer.is_loopback:
            return JSONResponse(status_code=403, content={"detail": "Local access only"})
        return await call_next(request)

    @app.exception_handler(RequestValidationError)
    async def sanitized_validation_error(_request: Request, _error: RequestValidationError) -> Any:
        return JSONResponse(status_code=422, content={"detail": "Invalid assessment payload"})

    @app.post("/assess")
    def assess(request: AssessmentRequest) -> dict[str, Any]:
        try:
            with selected_model.open(encoding="utf-8") as stream:
                artifact = json.load(stream)
        except (OSError, json.JSONDecodeError) as exc:
            raise HTTPException(status_code=503, detail="Review model unavailable") from exc
        if not isinstance(artifact, dict):
            raise HTTPException(status_code=503, detail="Review model unavailable")

        try:
            events = pd.DataFrame(request.events)
            features = build_payment_features(events, request.as_of)
            cohort = validate_cohort(features, labeled=False)
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            raise HTTPException(status_code=422, detail="Invalid events or cutoff") from exc
        try:
            scores = score_from_artifact(cohort, artifact)
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            raise HTTPException(
                status_code=503, detail="Review model unavailable for cohort"
            ) from exc

        assessments = [
            {
                "player_id": str(player_id),
                "currency": str(currency),
                "review_score": float(score),
            }
            for player_id, currency, score in zip(
                cohort["player_id"], cohort["currency"], scores, strict=True
            )
        ]
        return {
            "as_of_utc": cohort["as_of_utc"].iloc[0].isoformat(),
            "assessments": assessments,
            "interpretation": "Relative score for human review; not a diagnosis or calibrated risk",
        }

    return app


app = create_app()
