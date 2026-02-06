import io
import pytest
from fastapi import UploadFile, HTTPException
from unittest.mock import patch
from src.extraction import (
    extract_from_txt,
    extract_from_docx,
    extract_from_pdf,
    extract_from_image,
    extract_text
)
from docx import Document
from PIL import Image

# Helper to create UploadFile

def create_upload_file(filename: str, content: bytes) -> UploadFile:
    return UploadFile(filename=filename, file=io.BytesIO(content))

# TXT Extraction Tests

def test_extract_from_txt():
    text_content = "Hello world\nThis is a test."
    file = create_upload_file("test.txt", text_content.encode("utf-8"))
    result = extract_from_txt(file)
    assert "Hello world" in result
    assert "This is a test." in result

# DOCX Extraction Tests

def test_extract_from_docx():
    # Create a simple in-memory DOCX
    doc = Document()
    doc.add_paragraph("First paragraph")
    doc.add_paragraph("Second paragraph")
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    
    file = UploadFile(filename="test.docx", file=bio)
    result = extract_from_docx(file)
    assert "First paragraph" in result
    assert "Second paragraph" in result

# PDF Extraction Tests (text only)

def test_extract_from_pdf_text_only(tmp_path):
    import pdfplumber
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    pdf_file = tmp_path / "test.pdf"
    c = canvas.Canvas(str(pdf_file), pagesize=letter)
    c.drawString(100, 750, "Hello PDF")
    c.save()

    with open(pdf_file, "rb") as f:
        file = UploadFile(filename="test.pdf", file=io.BytesIO(f.read()))
        text = extract_from_pdf(file)
        assert "Hello PDF" in text

# IMAGE OCR Extraction Test

def test_extract_from_image():
    # Create simple in-memory image
    image = Image.new("RGB", (100, 30), color=(255, 255, 255))
    bio = io.BytesIO()
    image.save(bio, format="PNG")
    bio.seek(0)

    file = UploadFile(filename="test.png", file=bio)

    # Mock OCR to return empty text (simulate blank image OCR result)
    with patch("src.extraction.pytesseract.image_to_string", return_value=""):
        with pytest.raises(HTTPException) as exc:
            extract_from_image(file)

        assert exc.value.status_code == 400
        assert "No readable text found" in exc.value.detail

# Dispatcher test

def test_extract_text_dispatch_txt():
    text_content = "Hello dispatcher"
    file = create_upload_file("file.txt", text_content.encode("utf-8"))
    text, word_count = extract_text(file)
    assert text == text_content
    assert word_count == 2

def test_extract_text_invalid_extension():
    file = create_upload_file("file.xyz", b"content")
    with pytest.raises(HTTPException):
        extract_text(file)
