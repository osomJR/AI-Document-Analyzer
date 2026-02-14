from fastapi import HTTPException, Request
import time

AI_RATE_LIMIT = 3
AI_WINDOW = 60

_requests: dict[str, list[float]] = {}


def rate_limit_ai(request: Request):
    ip = request.client.host
    now = time.time()

    window = _requests.get(ip, [])

    # Remove expired timestamps
    window = [t for t in window if now - t < AI_WINDOW]

    if len(window) >= AI_RATE_LIMIT:
        retry_after = int(AI_WINDOW - (now - window[0]))

        raise HTTPException(
            status_code=429,
            detail={
                "error": "rate_limit_exceeded",
                "message": "Too many requests. Please retry later.",
                "retry_after_seconds": retry_after
            },
            headers={
                "Retry-After": str(retry_after)
            }
        )

    window.append(now)
    _requests[ip] = window
