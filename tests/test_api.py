from fastapi.testclient import TestClient
from backend.api import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "AI Document Analyzer"
    }

def test_docs_available():
    response = client.get("/docs")
    assert response.status_code == 200

def test_openapi_schema():
    response = client.get("/openapi.json")
    assert response.status_code == 200

def test_process_route_registered():
    response = client.post(
        "/api/process",
        json={
            "text": "Test",
            "feature": "summarize"
        }
    )

    # Either success (mocked) or provider error is acceptable
    assert response.status_code in (200, 502)
