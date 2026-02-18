import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.schema import FeatureType
from backend.route import router
from backend.rate_limit import _requests  # <-- important

# Test App Setup

app = FastAPI()
app.include_router(router)
client = TestClient(app)

# TEST ISOLATION FIX

@pytest.fixture(autouse=True)
def clear_rate_limit_store():
    """
    Ensures each test starts with a clean in-memory rate limit store.
    Prevents cross-test contamination.
    """
    _requests.clear()

# SUCCESS CASE

@patch("backend.route.ai_client.generate")
@patch("backend.route.rate_limit_ai")
def test_process_success(mock_rate_limit, mock_generate):
    mock_generate.return_value = "Processed result"
    response = client.post(
        "/process",
        json={
            "text": "Hello world",
            "feature": FeatureType.summarize.value
        }
    )
    assert response.status_code == 200
    assert response.json()["result"] == "Processed result"
    mock_rate_limit.assert_called_once()

# INPUT VALIDATION FAILURE

def test_empty_input_fails():
    response = client.post(
        "/process",
        json={
            "text": " ",
            "feature": FeatureType.summarize.value
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "empty_input"

# FEATURE CONTRACT FAILURE

def test_generate_questions_requires_word_count():
    response = client.post(
        "/process",
        json={
            "text": "Valid text here",
            "feature": FeatureType.generate_questions.value
        }
    )
    assert response.status_code == 400
    assert "Word count required" in str(response.json()["detail"])
def test_generate_answers_requires_questions():
    response = client.post(
        "/process",
        json={
            "text": "Valid text here",
            "feature": FeatureType.generate_answers.value
        }
    )
    assert response.status_code == 400
    assert "Questions required" in str(response.json()["detail"])
def test_translate_requires_target_language():
    response = client.post(
        "/process",
        json={
            "text": "Valid text here",
            "feature": FeatureType.translate.value
        }
    )
    assert response.status_code == 400
    assert "Target language required" in str(response.json()["detail"])

# RATE LIMIT PASSTHROUGH

@patch("backend.route.rate_limit_ai")
def test_rate_limit_error_propagates(mock_rate_limit):
    mock_rate_limit.side_effect = HTTPException(
        status_code=429,
        detail={"error": "rate_limit_exceeded"}
    )
    response = client.post(
        "/process",
        json={
            "text": "Hello world",
            "feature": FeatureType.summarize.value
        }
    )
    assert response.status_code == 429
    assert response.json()["detail"]["error"] == "rate_limit_exceeded"

# INTERNAL ERROR PROTECTION

@patch("backend.route.ai_client.generate")
@patch("backend.route.rate_limit_ai")
def test_internal_error_returns_500(mock_rate_limit, mock_generate):
    mock_generate.side_effect = Exception("Unexpected failure")
    response = client.post(
        "/process",
        json={
            "text": "Hello world",
            "feature": FeatureType.summarize.value
        }
    )
    assert response.status_code == 500
    assert response.json()["detail"]["error"] == "internal_error"
