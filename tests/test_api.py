import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from unittest.mock import patch
from backend.api import app

client = TestClient(app)

# HEALTH CHECK

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "AI Document Analyzer"
    assert body["version"] == "1.0.0"

# ROUTER REGISTRATION

@patch("backend.route.ai_client.generate")
@patch("backend.route.rate_limit_ai")
def test_v1_route_registered(mock_rate_limit, mock_generate):
    mock_generate.return_value = "OK"
    response = client.post(
        "/api/v1/process",
        json={
            "text": "Hello world",
            "feature": "summarize"
        }
    )
    assert response.status_code == 200
    assert response.json()["result"] == "OK"

# GLOBAL REQUEST VALIDATION HANDLER

def test_request_validation_error_handler():
    # Missing required "text"
    response = client.post(
        "/api/v1/process",
        json={
            "feature": "summarize"
        }
    )
    assert response.status_code == 422
    body = response.json()
    assert body["error"] == "request_validation_error"
    assert "details" in body

# GLOBAL HTTP EXCEPTION HANDLER

@patch("backend.route.rate_limit_ai")
def test_http_exception_passthrough(mock_rate_limit):
    mock_rate_limit.side_effect = HTTPException(
        status_code=429,
        detail={"error": "rate_limit_exceeded"},
        headers={"Retry-After": "10"}
    )
    response = client.post(
        "/api/v1/process",
        json={
            "text": "Hello world",
            "feature": "summarize"
        }
    )
    assert response.status_code == 429
    assert response.json()["detail"]["error"] == "rate_limit_exceeded"
    assert response.headers["Retry-After"] == "10"

# OPENAPI + DOCS EXISTENCE

def test_openapi_available():
    response = client.get("/openapi.json")
    assert response.status_code == 200

def test_docs_available():
    response = client.get("/docs")
    assert response.status_code == 200

def test_redoc_available():
    response = client.get("/redoc")
    assert response.status_code == 200
