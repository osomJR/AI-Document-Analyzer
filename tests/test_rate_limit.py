import time
import pytest
from fastapi import Request, HTTPException
from backend.rate_limit import rate_limit_ai, AI_RATE_LIMIT, AI_WINDOW, _requests

# Mock request object
class MockRequest:
    def __init__(self, ip):
        self.client = type("Client", (), {"host": ip})()

@pytest.fixture(autouse=True)
def clear_requests():
    """Clear the in-memory store before each test"""
    _requests.clear()
    yield
    _requests.clear()

def test_rate_limit_allows_under_limit():
    ip = "1.2.3.4"
    request = MockRequest(ip)

    # Send requests under the limit
    for _ in range(AI_RATE_LIMIT):
        rate_limit_ai(request)  # Should not raise

    # The _requests dict should contain exactly AI_RATE_LIMIT timestamps
    assert len(_requests[ip]) == AI_RATE_LIMIT

def test_rate_limit_blocks_over_limit():
    ip = "5.6.7.8"
    request = MockRequest(ip)

    # Fill up the limit
    for _ in range(AI_RATE_LIMIT):
        rate_limit_ai(request)

    # Next request should raise HTTPException with 429
    with pytest.raises(HTTPException) as exc:
        rate_limit_ai(request)

    assert exc.value.status_code == 429
    assert exc.value.detail["error"] == "rate_limit_exceeded"
    assert "retry_after_seconds" in exc.value.detail
    assert int(exc.value.headers["Retry-After"]) <= AI_WINDOW

def test_rate_limit_expires_after_window():
    ip = "9.10.11.12"
    request = MockRequest(ip)

    # Send maximum allowed requests
    for _ in range(AI_RATE_LIMIT):
        rate_limit_ai(request)

    # Simulate time passing beyond the window
    for i in range(AI_RATE_LIMIT):
        _requests[ip][i] -= (AI_WINDOW + 1)

    # Next request should be allowed now
    rate_limit_ai(request)
    assert len(_requests[ip]) == 1  # Old timestamps should be removed
