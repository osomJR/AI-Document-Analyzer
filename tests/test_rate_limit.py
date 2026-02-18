import pytest
from fastapi import HTTPException
from types import SimpleNamespace
from backend import rate_limit
from backend.rate_limit import (
    rate_limit_ai,
    AI_RATE_LIMIT,
    HEAVY_FEATURE_LIMIT,
    AI_WINDOW_SECONDS,
)
from src.schema import FeatureType

# Helper: mock FastAPI Request

def mock_request(ip: str):
    return SimpleNamespace(client=SimpleNamespace(host=ip))

# Auto-reset in-memory store

@pytest.fixture(autouse=True)
def reset_requests():
    rate_limit._requests.clear()
    yield
    rate_limit._requests.clear()

# Tests

def test_normal_feature_rate_limit():
    ip = "1.2.3.4"
    request = mock_request(ip)
    feature = FeatureType.summarize
    for _ in range(AI_RATE_LIMIT):
        rate_limit_ai(request, feature)
    with pytest.raises(HTTPException) as exc:
        rate_limit_ai(request, feature)
    assert exc.value.status_code == 429
    assert "retry_after_seconds" in exc.value.detail

def test_heavy_feature_rate_limit():
    ip = "5.6.7.8"
    request = mock_request(ip)
    feature = FeatureType.generate_questions
    for _ in range(HEAVY_FEATURE_LIMIT):
        rate_limit_ai(request, feature)
    with pytest.raises(HTTPException) as exc:
        rate_limit_ai(request, feature)
    assert exc.value.status_code == 429
    assert "retry_after_seconds" in exc.value.detail

def test_expired_window_allows_new_request(monkeypatch):
    ip = "9.10.11.12"
    request = mock_request(ip)
    feature = FeatureType.summarize
    fake_time = [1000.0]
    def fake_now():
        return fake_time[0]

    # Monkeypatch time.time inside rate_limit module
    
    monkeypatch.setattr(rate_limit.time, "time", fake_now)

    # Fill window
    
    for _ in range(AI_RATE_LIMIT):
        rate_limit_ai(request, feature)

    # Move time forward beyond window
   
    fake_time[0] += AI_WINDOW_SECONDS + 1

    # Should now succeed immediately (no sleep)
    
    rate_limit_ai(request, feature)

def test_multiple_ips_are_independent():
    ip1 = "1.1.1.1"
    ip2 = "2.2.2.2"
    request1 = mock_request(ip1)
    request2 = mock_request(ip2)
    feature = FeatureType.summarize
    for _ in range(AI_RATE_LIMIT):
        rate_limit_ai(request1, feature)
    with pytest.raises(HTTPException):
        rate_limit_ai(request1, feature)

    # IP2 unaffected
   
    for _ in range(AI_RATE_LIMIT):
        rate_limit_ai(request2, feature)

def test_heavy_vs_normal_limits():
    ip = "3.3.3.3"
    request = mock_request(ip)
    normal_feature = FeatureType.summarize
    heavy_feature = FeatureType.generate_answers

    # Normal limit
    
    for _ in range(AI_RATE_LIMIT):
        rate_limit_ai(request, normal_feature)
    with pytest.raises(HTTPException):
        rate_limit_ai(request, normal_feature)

    # Reset only this IP so heavy test is isolated
    
    rate_limit._requests[ip] = []

    # Heavy limit
    
    for _ in range(HEAVY_FEATURE_LIMIT):
        rate_limit_ai(request, heavy_feature)
    with pytest.raises(HTTPException):
        rate_limit_ai(request, heavy_feature)
