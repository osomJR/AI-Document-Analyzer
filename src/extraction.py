from fastapi import UploadFile, HTTPException
from typing import Tuple
import io

# PDF
import pdfplumber

# DOCX
from docx import Document

# OCR
from PIL import Image
import pytesseract

# CONSTANTS

MAX_WORDS = 1000

# CORE HELPERS 

def count_words(text: str) -> int:
    return len(text.split())

def enforce_word_limit(text: str, max_words: int = MAX_WORDS) -> None:
    words = count_words(text)
    if words > max_words:
        raise HTTPException(
            status_code=400,
            detail="Document exceeds 1000-word limit after extraction"
        )

# TEXT EXTRACTION

def extract_from_txt(file: UploadFile) -> str:
    content = file.file.read().decode("utf-8", errors="ignore")
    text = content.strip()
    enforce_word_limit(text)
    return text

# DOCX EXTRACTION 

def extract_from_docx(file: UploadFile) -> str:
    document = Document(file.file)
    paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
    text = "\n\n".join(paragraphs)
    enforce_word_limit(text)
    return text

# PDF EXTRACTION

def extract_from_pdf(file: UploadFile) -> str:
    extracted_paragraphs = []

    with pdfplumber.open(file.file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                extracted_paragraphs.append(page_text.strip())

    # If text was extractable, OCR is NOT used
    if extracted_paragraphs:
        text = "\n\n".join(extracted_paragraphs)
        enforce_word_limit(text)
        return text

    # OCR fallback (only when needed)
    return extract_pdf_with_ocr(file)

def extract_pdf_with_ocr(file: UploadFile) -> str:
    images = []
    file.file.seek(0)

    with pdfplumber.open(file.file) as pdf:
        for page in pdf.pages:
            image = page.to_image(resolution=300).original
            images.append(image)

    text_blocks = []
    for img in images:
        text = pytesseract.image_to_string(img)
        if text.strip():
            text_blocks.append(text.strip())

    if not text_blocks:
        raise HTTPException(
            status_code=400,
            detail="Unable to extract text from PDF"
        )

    text = "\n\n".join(text_blocks)
    enforce_word_limit(text)
    return text

# IMAGE OCR

def extract_from_image(file: UploadFile) -> str:
    image = Image.open(file.file)
    text = pytesseract.image_to_string(image).strip()

    if not text:
        raise HTTPException(
            status_code=400,
            detail="No readable text found in image"
        )

    enforce_word_limit(text)
    return text

# MAIN DISPATCHER

def extract_text(file: UploadFile) -> Tuple[str, int]:
    """
    Central extraction dispatcher.
    Returns extracted text + word count.
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
            detail="Unsupported file format for extraction"
        )

    return text, count_words(text)
