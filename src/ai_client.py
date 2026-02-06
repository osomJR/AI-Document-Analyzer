# src/ai_client.py

from fastapi import HTTPException
from openai import OpenAI

# OpenAI client initialization
client = OpenAI()


class AIClient:
    """
    Low-level AI execution layer.

    Responsibilities:
    - Send prompts to the AI model
    - Return raw model output
    - Handle provider-level failures

    This layer MUST NOT:
    - Modify prompts
    - Add business rules
    - Decide tone or structure
    """

    def generate(self, prompt: str) -> str:
        if not prompt.strip():
            raise HTTPException(
                status_code=500,
                detail="Empty prompt passed to AI client"
            )

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a strict document processing AI."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.0,     # CRITICAL: prevents creativity
                max_tokens=1200     # Safety cap (1000-word contract)
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            raise HTTPException(
                status_code=502,
                detail=f"AI provider error: {str(e)}"
            )
