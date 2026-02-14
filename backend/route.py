from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, field_validator
from backend.rate_limit import rate_limit_ai
from src.ai_processing import process_with_ai, FeatureType
from src.ai_client import AIClient
from src.ai_validation import validate_text_input  # <-- import here

router = APIRouter()
ai_client = AIClient()

# Request / Response Schemas
class AIProcessRequest(BaseModel):
    text: str
    feature: FeatureType

    @field_validator("text")
    @classmethod
    def strip_text(cls, v: str) -> str:
        return v.strip()

class AIProcessResponse(BaseModel):
    result: str

@router.post(
    "/process",
    response_model=AIProcessResponse
)
def process_document(request: AIProcessRequest):

    # Step 0: validate & sanitize input using ai_validation.py
    text = validate_text_input(request.text)

    try:
        # Step 1: build prompt
        prompt = process_with_ai(
            text=text,
            feature=request.feature
        )

        # Step 2: execute AI call
        output = ai_client.generate(prompt)

        return AIProcessResponse(result=output)

    except HTTPException:
        # Preserve rate limit and other explicit HTTP errors
        raise

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_request",
                "message": str(e)
            }
        )

    except Exception:
        # Do not leak internal error details
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": "Unexpected processing error."
            }
        )
