from fastapi import HTTPException, Request
from threading import Lock
import time
from src.schema import FeatureType
"""
AI RATE LIMITING—v1
"""

# Base limits (per IP)

AI_RATE_LIMIT = 3
AI_WINDOW_SECONDS = 60

# Optional stricter limit for heavy-generation features

HEAVY_FEATURE_LIMIT = 2

# In-memory store

_requests: dict[str, list[float]] = {}

# Concurrency safety (important due to ThreadPoolExecutor usage)

_lock = Lock()
def _is_heavy_feature(feature: FeatureType) -> bool:
    """
    Heavier AI features consume more tokens / compute.
    Adjust limits deterministically.
    """
    return feature in {
        FeatureType.generate_questions,
        FeatureType.generate_answers,
    }

def rate_limit_ai(request: Request, feature: FeatureType) -> None:
    """
    AI-specific rate limiter.
    - IP-based
    - Feature-aware
    - Deterministic window enforcement
    - Compatible with ai_client execution cost
    """
    ip = request.client.host
    now = time.time()
    limit = HEAVY_FEATURE_LIMIT if _is_heavy_feature(feature) else AI_RATE_LIMIT
    with _lock:
        window = _requests.get(ip, [])

        # Remove expired timestamps
        
        window = [t for t in window if now - t < AI_WINDOW_SECONDS]
        if len(window) >= limit:
            retry_after = int(AI_WINDOW_SECONDS - (now - window[0]))
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "rate_limit_exceeded",
                    "message": "Too many AI processing requests. Please retry later.",
                    "retry_after_seconds": retry_after
                },
                headers={"Retry-After": str(retry_after)}
            )

        # Append this request timestamp
        
        window.append(now)
        _requests[ip] = window
