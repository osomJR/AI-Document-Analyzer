import pytest
from fastapi import HTTPException
from unittest.mock import patch, MagicMock
import concurrent.futures
from src.ai_client import AIClient

# Helpers

def mock_openai_response(content: str):
    """
    Creates a mock OpenAI response object
    matching the structure used in ai_client.py
    """
    mock_choice = MagicMock()
    mock_choice.message.content = content
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    return mock_response

# Tests

def test_generate_success():
    client = AIClient()
    with patch("src.ai_client.client.chat.completions.create") as mock_create, \
         patch("src.ai_client.validate_structured_text_response") as mock_validate:
        mock_create.return_value = mock_openai_response("Valid response")
        result = client.generate("Valid prompt")
        assert result == "Valid response"
        mock_validate.assert_called_once_with("Valid response")

def test_empty_prompt_raises_500():
    client = AIClient()
    with pytest.raises(HTTPException) as exc:
        client.generate("")
    assert exc.value.status_code == 500
    assert "Empty prompt" in exc.value.detail

def test_ai_returns_empty_string():
    client = AIClient()
    with patch("src.ai_client.client.chat.completions.create") as mock_create:
        mock_create.return_value = mock_openai_response("")
        with pytest.raises(HTTPException) as exc:
            client.generate("Valid prompt")
        assert exc.value.status_code == 502
        assert "empty response" in exc.value.detail.lower()

def test_ai_returns_null_content():
    client = AIClient()
    mock_choice = MagicMock()
    mock_choice.message.content = None
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    with patch("src.ai_client.client.chat.completions.create") as mock_create:
        mock_create.return_value = mock_response
        with pytest.raises(HTTPException) as exc:
            client.generate("Valid prompt")
        assert exc.value.status_code == 502
        assert "null content" in exc.value.detail.lower()

def test_provider_timeout():
    client = AIClient()
    with patch(
        "src.ai_client.AIClient._call_provider",
        side_effect=concurrent.futures.TimeoutError
    ):
        with pytest.raises(HTTPException) as exc:
            client.generate("Valid prompt")
        assert exc.value.status_code == 504
        assert exc.value.detail["error"] == "ai_timeout"

def test_provider_exception():
    client = AIClient()
    with patch(
        "src.ai_client.AIClient._call_provider",
        side_effect=Exception("Provider crashed")
    ):
        with pytest.raises(HTTPException) as exc:
            client.generate("Valid prompt")
        assert exc.value.status_code == 502
        assert "Provider crashed" in exc.value.detail

def test_validation_failure_propagates():
    client = AIClient()
    with patch("src.ai_client.client.chat.completions.create") as mock_create, \
         patch(
             "src.ai_client.validate_structured_text_response",
             side_effect=HTTPException(status_code=422, detail="Invalid structure")
         ):
        mock_create.return_value = mock_openai_response("Bad structure")
        with pytest.raises(HTTPException) as exc:
            client.generate("Valid prompt")
        assert exc.value.status_code == 422
        assert exc.value.detail == "Invalid structure"
