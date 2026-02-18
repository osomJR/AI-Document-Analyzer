import pytest
from fastapi import HTTPException
from src.ai_validation import validate_text_input, MAX_INPUT_CHARS
from src.schema import MAX_WORD_COUNT

# SUCCESS CASE

def test_valid_text_returns_trimmed_text():
    text = "   Hello world   "
    result = validate_text_input(text)
    assert result == "Hello world"

def test_valid_minimum_letters_passes():
    text = "Hi"
    result = validate_text_input(text)
    assert result == "Hi"

# NULL + EMPTY INPUT

def test_null_input_raises_exception():
    with pytest.raises(HTTPException) as exc:
        validate_text_input(None)
    assert exc.value.status_code == 400
    assert exc.value.detail["error"] == "null_input"

def test_empty_string_raises_exception():
    with pytest.raises(HTTPException) as exc:
        validate_text_input("")
    assert exc.value.status_code == 400
    assert exc.value.detail["error"] == "empty_input"

def test_whitespace_only_raises_exception():
    with pytest.raises(HTTPException) as exc:
        validate_text_input("     ")
    assert exc.value.status_code == 400
    assert exc.value.detail["error"] == "empty_input"

# CHARACTER LIMIT

def test_input_exceeds_max_char_length_raises_exception():
    text = "a" * (MAX_INPUT_CHARS + 1)
    with pytest.raises(HTTPException) as exc:
        validate_text_input(text)
    assert exc.value.status_code == 400
    assert exc.value.detail["error"] == "input_too_long"

def test_input_exactly_max_char_length_passes():
    text = "a" * MAX_INPUT_CHARS
    result = validate_text_input(text)
    assert result == text

# PRINTABLE + CONTENT VALIDATION

def test_non_printable_characters_raise_exception():
    text = "Hello\x00World"  # Null byte
    with pytest.raises(HTTPException) as exc:
        validate_text_input(text)
    assert exc.value.status_code == 400
    assert exc.value.detail["error"] == "invalid_input"

def test_insufficient_letters_raise_exception():
    text = "1!"  # No alphabetic characters
    with pytest.raises(HTTPException) as exc:
        validate_text_input(text)
    assert exc.value.status_code == 400
    assert exc.value.detail["error"] == "invalid_input"

# WORD COUNT LIMITS

def test_no_words_raises_exception():
    text = "!!! ### $$$"
    with pytest.raises(HTTPException) as exc:
        validate_text_input(text)
    assert exc.value.status_code == 400
    assert exc.value.detail["error"] == "invalid_input"

def test_word_limit_exceeded_raises_exception():
    text = "word " * (MAX_WORD_COUNT + 1)
    with pytest.raises(HTTPException) as exc:
        validate_text_input(text)
    assert exc.value.status_code == 400
    assert exc.value.detail["error"] == "word_limit_exceeded"

def test_word_limit_exact_boundary_passes():
    text = "word " * MAX_WORD_COUNT
    result = validate_text_input(text)
    assert result.strip() == text.strip()
