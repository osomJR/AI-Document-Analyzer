import pytest
from fastapi import HTTPException
from unittest.mock import patch, MagicMock
from src.ai_client import AIClient

def test_generate_returns_text():
    client = AIClient()

    fake_response = MagicMock()
    fake_response.choices = [
        MagicMock(
            message=MagicMock(
                content="Processed document output"
            )
        )
    ]

    with patch("src.ai_client.client.chat.completions.create", return_value=fake_response):
        result = client.generate("Valid prompt text")

        assert isinstance(result, str)
        assert result == "Processed document output"

def test_generate_rejects_empty_prompt():
    client = AIClient()

    with pytest.raises(HTTPException) as exc:
        client.generate("   ")

    assert exc.value.status_code == 500
    assert "Empty prompt" in exc.value.detail

def test_generate_handles_provider_error():
    client = AIClient()

    with patch(
        "src.ai_client.client.chat.completions.create",
        side_effect=Exception("OpenAI outage")
    ):
        with pytest.raises(HTTPException) as exc:
            client.generate("Valid prompt")

    assert exc.value.status_code == 502
    assert "AI provider error" in exc.value.detail
