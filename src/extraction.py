from fastapi import UploadFile, HTTPException
from typing import Tuple
import pdfplumber
from docx import Document
from PIL import Image
import pytesseract

MAX_WORDS = 1000

# CORE HELPERS

def count_words(text: str) -> int:
    return len(text.split())

def enforce_word_limit(text: str) -> None:
    """
    Enforces the hard 1000-word post-extraction limit.
    """

    if count_words(text) > MAX_WORDS:
        raise HTTPException(
            status_code=400,
            detail="Document exceeds 1000-word limit after extraction",
        )

# TEXT EXTRACTION

def extract_from_txt(file: UploadFile) -> str:
    """
    Extracts text from .txt files.
    """

    content = file.file.read().decode("utf-8", errors="ignore")
    text = content.strip()

    if not text:
        raise HTTPException(
            status_code=400,
            detail="Text file is empty",
        )

    enforce_word_limit(text)
    return text

# DOCX EXTRACTION

def extract_from_docx(file: UploadFile) -> str:
    """
    Extracts text from .docx files.
    """

    document = Document(file.file)
    paragraphs = [p.text.strip() for p in document.paragraphs if p.text.strip()]

    if not paragraphs:
        raise HTTPException(
            status_code=400,
            detail="No readable text found in Word document",
        )

    text = "\n\n".join(paragraphs)
    enforce_word_limit(text)
    return text

# PDF EXTRACTION

def extract_from_pdf(file: UploadFile) -> str:
    """
    Extracts text from PDF.
    OCR is used ONLY if no extractable text layer exists.
    """

    extracted_pages = []

    with pdfplumber.open(file.file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text and page_text.strip():
                extracted_pages.append(page_text.strip())

    # If extractable text exists, OCR is NOT used
    if extracted_pages:
        text = "\n\n".join(extracted_pages)
        enforce_word_limit(text)
        return text

    # OCR fallback — allowed only when no text layer exists
    return extract_pdf_with_ocr(file)


def extract_pdf_with_ocr(file: UploadFile) -> str:
    """
    OCR fallback for scanned PDFs.
    """

    file.file.seek(0)

    images = []
    with pdfplumber.open(file.file) as pdf:
        for page in pdf.pages:
            images.append(page.to_image(resolution=300).original)

    text_blocks = []
    for image in images:
        text = pytesseract.image_to_string(image).strip()
        if text:
            text_blocks.append(text)

    if not text_blocks:
        raise HTTPException(
            status_code=400,
            detail="Unable to extract text from PDF",
        )

    text = "\n\n".join(text_blocks)
    enforce_word_limit(text)
    return text

# IMAGE OCR

def extract_from_image(file: UploadFile) -> str:
    """
    OCR extraction for JPG / JPEG images.
    """

    image = Image.open(file.file)
    text = pytesseract.image_to_string(image).strip()

    if not text:
        raise HTTPException(
            status_code=400,
            detail="No readable text found in image",
        )

    enforce_word_limit(text)
    return text

# MAIN DISPATCHER

def extract_text(file: UploadFile) -> Tuple[str, int]:
    """
    Central extraction dispatcher.
    Returns extracted text and word count.
    """

    filename = file.filename.lower()

    if filename.endswith(".txt"):
        text = extract_from_txt(file)

    elif filename.endswith(".docx"):
        text = extract_from_docx(file)

    elif filename.endswith(".pdf"):
        text = extract_from_pdf(file)

    elif filename.endswith((".jpg", ".jpeg")):
        text = extract_from_image(file)

    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format for extraction",
        )

    return text, count_words(text)
