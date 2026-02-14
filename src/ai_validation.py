from fastapi import HTTPException
import string

MAX_INPUT_CHARS = 10000 

# Helper: printable characters check
def is_printable(text: str) -> bool:
    return all(c in string.printable for c in text)

# Helper: minimum alphabetic letters
def has_sufficient_text(text: str, min_letters: int = 2) -> bool:
    letters = [c for c in text if c.isalpha()]
    return len(letters) >= min_letters

# Main validation function
def validate_text_input(text: str) -> str:
    trimmed = text.strip()

    # Empty input check
    if not trimmed:
        raise HTTPException(
            status_code=400,
            detail={"error": "empty_input", "message": "Input text cannot be empty."}
        )

    # Max character length check
    if len(trimmed) > MAX_INPUT_CHARS:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "input_too_long",
                "message": f"Input exceeds maximum allowed length of {MAX_INPUT_CHARS} characters."
            }
        )

    # Binary / junk content check
    if not is_printable(trimmed) or not has_sufficient_text(trimmed):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_input",
                "message": "Input contains non-text or unreadable content."
            }
        )
    return trimmed
