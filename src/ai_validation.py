from fastapi import HTTPException
import string
from src.schema import MAX_WORD_COUNT
from src.extraction import count_words
"""
AI INPUT VALIDATION LAYER — v1 CONTRACT
Responsibilities:
- Validate raw text inputs before AI processing
- Enforce deterministic size + structure constraints
- Remain aligned with extraction + schema contracts
This module MUST NOT:
- Perform business logic decisions
- Modify AI prompts
- Perform AI output validation (handled elsewhere)
"""
MAX_INPUT_CHARS = 10000  # Hard safety ceiling (independent of word limit)

# Low-Level Helpers

def _is_printable(text: str) -> bool:
    return all(c in string.printable for c in text)

def _has_sufficient_text(text: str, min_letters: int = 2) -> bool:
    letters = [c for c in text if c.isalpha()]
    return len(letters) >= min_letters

# Core Validation

def validate_text_input(text: str) -> str:
    """
    Deterministic validation for raw AI text input.
    Enforces:
    - Non-empty input
    - Character ceiling
    - Printable content only
    - Minimum alphabetic density
    - Word count within system contract
    """
    if text is None:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "null_input",
                "message": "Input text cannot be null."
            }
        )
    trimmed = text.strip()

    # Empty input

    if not trimmed:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "empty_input",
                "message": "Input text cannot be empty."
            }
        )

    # Character length ceiling (transport-level safety)
    
    if len(trimmed) > MAX_INPUT_CHARS:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "input_too_long",
                "message": f"Input exceeds maximum allowed length of {MAX_INPUT_CHARS} characters."
            }
        )

    # Printable + alphabetic density validation
    
    if not _is_printable(trimmed) or not _has_sufficient_text(trimmed):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_input",
                "message": "Input contains non-text or unreadable content."
            }
        )

    # Word count alignment with extraction contract
    
    word_count = count_words(trimmed)
    if word_count < 1:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "no_words",
                "message": "Input contains no valid words."
            }
        )
    if word_count > MAX_WORD_COUNT:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "word_limit_exceeded",
                "message": f"Input exceeds maximum allowed word count of {MAX_WORD_COUNT}."
            }
        )
    return trimmed
