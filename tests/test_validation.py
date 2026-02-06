import pytest
from fastapi import UploadFile
from io import BytesIO
from src.schema import TextInput, FileInput
from src.validation import (
    validate_text_input,
    validate_file_input,
    validate_input_mode,
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE_MB,
    MAX_WORDS,
)

# TEXT INPUT TESTS

def test_valid_text_input():
    payload = TextInput(
        feature="summarize",
        text="This is a valid text input under the 1000-word limit."
    )
    word_count = validate_text_input(payload)
    assert word_count == len(payload.text.split())

def test_empty_text_input():
    payload = TextInput(feature="grammar", text="   ")
    with pytest.raises(Exception) as e:
        validate_text_input(payload)
    assert "Text input is empty" in str(e.value)

def test_text_over_word_limit():
    long_text = "word " * (MAX_WORDS + 1)
    payload = TextInput(feature="summarize", text=long_text)
    with pytest.raises(Exception) as e:
        validate_text_input(payload)
    assert "Text exceeds 1000-word limit" in str(e.value)

# FILE INPUT TESTS

def create_fake_file(filename: str, size_mb: float) -> UploadFile:
    """
    Helper to create a mock UploadFile object with specific size.
    """
    size_bytes = int(size_mb * 1024 * 1024)
    content = BytesIO(b"a" * size_bytes)
    return UploadFile(filename=filename, file=content)

def test_valid_file_input():
    payload = FileInput(feature="convert")
    file = create_fake_file("sample.txt", 1)
    # Should not raise any exception
    validate_file_input(file, payload)

def test_unsupported_file_extension():
    payload = FileInput(feature="convert")
    file = create_fake_file("sample.exe", 1)
    with pytest.raises(Exception) as e:
        validate_file_input(file, payload)
    assert "Unsupported file format" in str(e.value)

def test_file_over_size_limit():
    payload = FileInput(feature="convert")
    file = create_fake_file("sample.pdf", MAX_FILE_SIZE_MB + 1)
    with pytest.raises(Exception) as e:
        validate_file_input(file, payload)
    assert "File exceeds 10MB size limit" in str(e.value)

def test_no_file_uploaded():
    payload = FileInput(feature="convert")
    with pytest.raises(Exception) as e:
        validate_file_input(None, payload)
    assert "No file uploaded" in str(e.value)

# INPUT MODE VALIDATION TESTS

def test_both_text_and_file_provided():
    text_payload = TextInput(feature="summarize", text="Valid text")
    file = create_fake_file("sample.txt", 1)
    with pytest.raises(Exception) as e:
        validate_input_mode(text_payload, file)
    assert "Provide either text input or file upload, not both" in str(e.value)

def test_neither_text_nor_file_provided():
    with pytest.raises(Exception) as e:
        validate_input_mode(None, None)
    assert "No input provided" in str(e.value)

def test_only_text_provided():
    text_payload = TextInput(feature="summarize", text="Valid text")
    # Should not raise
    validate_input_mode(text_payload, None)

def test_only_file_provided():
    file = create_fake_file("sample.txt", 1)
    # Should not raise
    validate_input_mode(None, file)
