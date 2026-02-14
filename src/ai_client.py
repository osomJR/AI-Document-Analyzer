from fastapi import HTTPException
from openai import OpenAI
import concurrent.futures

# Configuration

AI_MODEL ="gpt-4o-mini"
AI_TIMEOUT_SECONDS =12       
PROVIDER_TIMEOUT_SECONDS =25 

# OpenAI client with provider-level timeout
client = OpenAI(timeout=PROVIDER_TIMEOUT_SECONDS)


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

        # Execute provider call in controlled thread
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self._call_provider, prompt)

            try:
                return future.result(timeout=AI_TIMEOUT_SECONDS)

            except concurrent.futures.TimeoutError:
                raise HTTPException(
                    status_code=504,
                    detail={
                        "error": "ai_timeout",
                        "message": "AI provider did not respond in time"
                    }
                )

            except HTTPException:
                raise

            except Exception as e:
                raise HTTPException(
                    status_code=502,
                    detail=f"AI provider error: {str(e)}"
                )

    def _call_provider(self, prompt: str) -> str:
        """
        Isolated provider call.
        This keeps timeout logic clean and testable.
        """

        response = client.chat.completions.create(
            model=AI_MODEL,
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
            temperature=0.0,
            max_tokens=1000,
            request_timeout_seconds=30
        )
        return response.choices[0].message.content.strip()
