from fastapi import UploadFile, HTTPException
from typing import Optional
from src.schema import TextInput, FileInput

# CONSTANTS

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "jpg", "jpeg"}
MAX_FILE_SIZE_MB = 10
MAX_WORDS = 1000

# TEXT VALIDATION

def validate_text_input(payload: TextInput) -> int:
    """
    Validates copy-paste text input.
    Returns word count if valid.
    """

    text = payload.text.strip()

    if not text:
        raise HTTPException(
            status_code=400,
            detail="Text input is empty"
        )

    word_count = len(text.split())

    if word_count > MAX_WORDS:
        raise HTTPException(
            status_code=400,
            detail="Text exceeds 1000-word limit"
        )

    return word_count

# FILE VALIDATION

def validate_file_input(
    file: UploadFile,
    payload: FileInput
) -> None:
    """
    Validates uploaded file metadata and size.
    """

    if not file or not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file uploaded"
        )

    extension = file.filename.split(".")[-1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format"
        )

    # File size check (in MB)
    file.file.seek(0, 2)  # Move cursor to end
    size_mb = file.file.tell() / (1024 * 1024)
    file.file.seek(0)     # Reset cursor

    if size_mb > payload.max_file_size_mb:
        raise HTTPException(
            status_code=400,
            detail="File exceeds 10MB size limit"
        )

# INPUT MODE VALIDATION

def validate_input_mode(
    text_payload: Optional[TextInput],
    file: Optional[UploadFile]
) -> None:
    """
    Ensures exactly ONE input type is provided: text OR file.
    """

    if text_payload and file:
        raise HTTPException(
            status_code=400,
            detail="Provide either text input or file upload, not both"
        )

    if not text_payload and not file:
        raise HTTPException(
            status_code=400,
            detail="No input provided"
        )
