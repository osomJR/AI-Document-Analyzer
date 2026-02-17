from pathlib import Path
from typing import Tuple
from src.schema import (
    DocumentMetadata,
    DocumentPayload,
    InputFormat,
    MAX_FILE_SIZE_MB,
    MAX_WORD_COUNT,
)

# Real extraction libraries

import fitz  # PyMuPDF for PDFs
import docx  # python-docx for DOCX
import pytesseract
from PIL import Image

# FILE SIZE VALIDATION

def get_file_size_mb(file_path: Path) -> float:
    size_bytes = file_path.stat().st_size
    size_mb = size_bytes / (1024 * 1024)

    if size_mb > MAX_FILE_SIZE_MB:
        raise ValueError("File exceeds maximum allowed size")
    if size_mb <= 0:
        raise ValueError("File is empty")

    return round(size_mb, 4)

# TEXT EXTRACTION FUNCTIONS

def extract_text_from_txt(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8")

def extract_text_from_pdf(file_path: Path) -> str:
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()

def extract_text_from_docx(file_path: Path) -> str:
    doc = docx.Document(file_path)
    return "\n".join(p.text for p in doc.paragraphs).strip()

def extract_text_from_image(file_path: Path) -> str:
    image = Image.open(file_path)
    text = pytesseract.image_to_string(image)
    return text.strip()

# WORD COUNT

def count_words(text: str) -> int:
    return len(text.split())

def enforce_word_limit(word_count: int) -> None:
    if word_count < 1:
        raise ValueError("Document contains no words")
    if word_count > MAX_WORD_COUNT:
        raise ValueError("Document exceeds maximum allowed word count")

# FORMAT ROUTER

def detect_format(file_path: Path) -> InputFormat:
    suffix = file_path.suffix.lower().replace(".", "")
    try:
        return InputFormat(suffix)
    except ValueError:
        raise ValueError(f"Unsupported file format: {suffix}")

def extract_text_by_format(file_path: Path, fmt: InputFormat) -> Tuple[str, bool]:
    """
    Returns:
        text (str)
        ocr_used (bool)
    """
    if fmt == InputFormat.txt:
        return extract_text_from_txt(file_path), False
    if fmt == InputFormat.pdf:
        return extract_text_from_pdf(file_path), False
    if fmt == InputFormat.docx:
        return extract_text_from_docx(file_path), False
    if fmt in (InputFormat.jpg, InputFormat.jpeg):
        return extract_text_from_image(file_path), True

    raise ValueError(f"Unsupported file format: {fmt}")

# PUBLIC ENTRYPOINT

def build_document_payload(file_path: str) -> DocumentPayload:
    """
    Deterministic document extraction pipeline.

    1. Detect format
    2. Validate file size
    3. Extract text
    4. Enforce word count limits
    5. Build schema-compliant payload
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError("File not found")

    input_format = detect_format(path)
    file_size_mb = get_file_size_mb(path)
    text, ocr_used = extract_text_by_format(path, input_format)

    if not text.strip():
        raise ValueError("File is empty")

    word_count = count_words(text)
    enforce_word_limit(word_count)
    metadata = DocumentMetadata(
        input_format=input_format,
        file_size_mb=file_size_mb,
        extracted_word_count=word_count,
        ocr_used=ocr_used,
    )
    return DocumentPayload(
        text=text,
        metadata=metadata,
    )
