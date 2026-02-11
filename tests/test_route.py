from fastapi.testclient import TestClient
from fastapi import FastAPI
import pytest
from backend.route import router
from src.ai_client import AIClient

# Create a test app and register router
app = FastAPI()
app.include_router(router, prefix="/api")

client = TestClient(app)

# ---- Mock AIClient.generate ----
@pytest.fixture(autouse=True)
def mock_ai_generate(monkeypatch):
    def fake_generate(self, prompt: str) -> str:
        return "MOCK_AI_RESPONSE"

    monkeypatch.setattr(AIClient, "generate", fake_generate)

def test_process_success():
    response = client.post(
        "/api/process",
        json={
            "text": "This is a test document.",
            "feature": "summarize"
        }
    )

    assert response.status_code == 200
    assert response.json() == {
        "result": "MOCK_AI_RESPONSE"
    }

def test_process_empty_text():
    response = client.post(
        "/api/process",
        json={
            "text": "",
            "feature": "summarize"
        }
    )

    assert response.status_code == 400
    assert "Empty content" in response.text

def test_process_invalid_feature():
    response = client.post(
        "/api/process",
        json={
            "text": "Hello",
            "feature": "invalid_feature"
        }
    )

    assert response.status_code == 422

def test_process_missing_field():
    response = client.post(
        "/api/process",
        json={
            "text": "Hello"
        }
    )

    assert response.status_code == 422
