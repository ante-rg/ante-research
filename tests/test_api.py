"""The API test uses synthetic events and a synthetic, unvalidated model."""

import json

from fastapi.testclient import TestClient

from ante.api import create_app
from ante.modeling.core import FEATURE_COLUMNS


def fake_artifact() -> dict:
    return {
        "version": 1,
        "currency": "EUR",
        "eligible_from_utc": "2026-01-08T00:00:00+00:00",
        "feature_columns": list(FEATURE_COLUMNS),
        "scaler_mean": [0] * len(FEATURE_COLUMNS),
        "scaler_scale": [1] * len(FEATURE_COLUMNS),
        "coefficient": [0] * len(FEATURE_COLUMNS),
        "intercept": 0,
    }


def payload() -> dict:
    return {
        "as_of": "2026-03-01T00:00:00Z",
        "events": [
            {
                "event_id": "synthetic-1",
                "player_id": "synthetic-player",
                "event_time": "2026-02-28T00:00:00Z",
                "event_type": "deposit",
                "amount": 10,
                "currency": "EUR",
            }
        ],
    }


def test_assess_returns_relative_score_and_no_automatic_diagnosis(tmp_path):
    model_path = tmp_path / "synthetic-model.json"
    model_path.write_text(json.dumps(fake_artifact()), encoding="utf-8")
    client = TestClient(create_app(model_path), client=("127.0.0.1", 12345))

    response = client.post("/assess", json=payload())
    assert response.status_code == 200
    body = response.json()
    assert body["assessments"] == [
        {"player_id": "synthetic-player", "currency": "EUR", "review_score": 0.5}
    ]
    assert "diagnosis" in body["interpretation"]
    assert "label" not in body
    assert client.get("/docs").status_code == 404


def test_assess_rejects_invalid_input_without_echoing_player_data(tmp_path):
    model_path = tmp_path / "synthetic-model.json"
    model_path.write_text(json.dumps(fake_artifact()), encoding="utf-8")
    client = TestClient(create_app(model_path), client=("127.0.0.1", 12345))
    bad = payload()
    bad["events"][0]["amount"] = -10
    response = client.post("/assess", json=bad)
    assert response.status_code == 422
    assert "synthetic-player" not in response.text


def test_assess_requires_local_model(tmp_path):
    client = TestClient(create_app(tmp_path / "missing.json"), client=("127.0.0.1", 12345))
    response = client.post("/assess", json=payload())
    assert response.status_code == 503


def test_request_schema_error_does_not_echo_extra_player_data(tmp_path):
    model_path = tmp_path / "synthetic-model.json"
    model_path.write_text(json.dumps(fake_artifact()), encoding="utf-8")
    client = TestClient(create_app(model_path), client=("127.0.0.1", 12345))
    bad = payload()
    bad["private_player_note"] = "sensitive player detail"
    response = client.post("/assess", json=bad)
    assert response.status_code == 422
    assert "sensitive player detail" not in response.text


def test_api_rejects_nonlocal_clients(tmp_path):
    client = TestClient(create_app(tmp_path / "missing.json"), client=("203.0.113.7", 12345))
    response = client.post("/assess", json=payload())
    assert response.status_code == 403


def test_invalid_model_artifact_is_server_error(tmp_path):
    model_path = tmp_path / "bad-model.json"
    broken = fake_artifact()
    del broken["coefficient"]
    model_path.write_text(json.dumps(broken), encoding="utf-8")
    client = TestClient(create_app(model_path), client=("127.0.0.1", 12345))
    response = client.post("/assess", json=payload())
    assert response.status_code == 503

    model_path.write_text("[]", encoding="utf-8")
    response = client.post("/assess", json=payload())
    assert response.status_code == 503
