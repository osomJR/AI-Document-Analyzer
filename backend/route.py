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


@router.post("/process", response_model=AIProcessResponse)
def process_document(request: AIProcessRequest):

    # REQUIRED for test_process_empty_text
    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Empty content"
        )

    try:
        prompt = process_with_ai(
            text=request.text,
            feature=request.feature
        )

        output = ai_client.generate(prompt)

        return AIProcessResponse(result=output)

    except HTTPException:
        raise

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected processing error: {str(e)}"
        )