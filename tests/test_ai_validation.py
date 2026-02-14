import pytest
from fastapi import HTTPException
from src.ai_validation import validate_text_input, MAX_INPUT_CHARS

# Trim
def test_valid_text_returns_trimmed_text():
    result = validate_text_input("  Hello world  ")
    assert result == "Hello world"


def test_valid_minimum_letters_passes():
    # Exactly 2 alphabetic characters (minimum allowed)
    result = validate_text_input("Hi")
    assert result == "Hi"

# Empty / Whitespace

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

# Max Length

def test_input_exceeds_max_length_raises_exception():
    too_long = "a" * (MAX_INPUT_CHARS + 1)

    with pytest.raises(HTTPException) as exc:
        validate_text_input(too_long)

    assert exc.value.status_code == 400
    assert exc.value.detail["error"] == "input_too_long"

def test_input_exactly_max_length_passes():
    valid = "a" * MAX_INPUT_CHARS
    result = validate_text_input(valid)
    assert result == valid

# Non-printable Characters

def test_non_printable_characters_raise_exception():
    bad_input = "Hello\x00World"

    with pytest.raises(HTTPException) as exc:
        validate_text_input(bad_input)

    assert exc.value.status_code == 400
    assert exc.value.detail["error"] == "invalid_input"

# Insufficient Alphabetic Characters

def test_insufficient_letters_raise_exception():
    # Only 1 alphabetic character (minimum is 2)
    with pytest.raises(HTTPException) as exc:
        validate_text_input("A12345!!!")

    assert exc.value.status_code == 400
    assert exc.value.detail["error"] == "invalid_input"
