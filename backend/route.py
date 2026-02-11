from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal

from src.ai_processing import process_with_ai, FeatureType
from src.ai_client import AIClient

router = APIRouter()
ai_client = AIClient()

# Request / Response Schemas

class AIProcessRequest(BaseModel):
    text: str
    feature: FeatureType

class AIProcessResponse(BaseModel):
    result: str

# Routes

@router.post("/process", response_model=AIProcessResponse)
def process_document(request: AIProcessRequest):
    """
    Main AI processing endpoint.

    Flow:
    1. Validate request
    2. Build contract-enforced prompt (ai_processor)
    3. Execute AI call (ai_client)
    4. Return raw, policy-compliant output
    """

    try:
        # Step 1: Build prompt via contract logic
        prompt = process_with_ai(
            text=request.text,
            feature=request.feature
        )

        # Step 2: Execute AI call
        output = ai_client.generate(prompt)

        return AIProcessResponse(result=output)

    except HTTPException:
        # Pass through known, intentional errors
        raise

    except Exception as e:
        # Catch-all safety net
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected processing error: {str(e)}"
        )
