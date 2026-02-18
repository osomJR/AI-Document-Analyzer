import pytest
from pathlib import Path
from PIL import Image, ImageDraw
from src.extraction import (
    build_document_payload,
    count_words,
    enforce_word_limit,
)
from src.schema import InputFormat, DocumentPayload, MAX_WORD_COUNT

# HELPERS TO CREATE TEMP FILES

def create_txt_file(tmp_path: Path, content: str) -> Path:
    file_path = tmp_path / "test.txt"
    file_path.write_text(content, encoding="utf-8")
    return file_path

def create_docx_file(tmp_path: Path, content: str) -> Path:
    import docx
    file_path = tmp_path / "test.docx"
    doc = docx.Document()
    doc.add_paragraph(content)
    doc.save(file_path)
    return file_path

def create_pdf_file(tmp_path: Path, content: str) -> Path:
    import fitz  # PyMuPDF
    file_path = tmp_path / "test.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), content)
    doc.save(file_path)
    doc.close()
    return file_path

def create_image_file(tmp_path: Path, content: str) -> Path:
    file_path = tmp_path / "test.jpg"
    image = Image.new("RGB", (200, 50), color="white")
    draw = ImageDraw.Draw(image)
    draw.text((10, 10), content, fill="black")
    image.save(file_path)
    return file_path

# BASIC EXTRACTION TESTS

def test_txt_extraction(tmp_path):
    content = "Hello world!"
    file_path = create_txt_file(tmp_path, content)
    payload: DocumentPayload = build_document_payload(file_path)
    assert payload.text.strip() == content
    assert payload.metadata.input_format == InputFormat.txt
    assert payload.metadata.ocr_used is False
    assert payload.metadata.extracted_word_count == count_words(content)

def test_docx_extraction(tmp_path):
    content = "This is a DOCX test."
    file_path = create_docx_file(tmp_path, content)
    payload: DocumentPayload = build_document_payload(file_path)
    assert content in payload.text
    assert payload.metadata.input_format == InputFormat.docx
    assert payload.metadata.ocr_used is False

def test_pdf_extraction(tmp_path):
    content = "PDF extraction works!"
    file_path = create_pdf_file(tmp_path, content)
    payload: DocumentPayload = build_document_payload(file_path)
    assert content in payload.text
    assert payload.metadata.input_format == InputFormat.pdf
    assert payload.metadata.ocr_used is False

def test_image_ocr_extraction(tmp_path):
    content = "OCR Test"
    file_path = create_image_file(tmp_path, content)
    payload: DocumentPayload = build_document_payload(file_path)

    # Validate OCR pipeline executed
    
    assert payload.metadata.input_format in (InputFormat.jpg, InputFormat.jpeg)
    assert payload.metadata.ocr_used is True

    # Validate text was extracted
    
    assert payload.text is not None
    assert payload.text.strip() != ""

    # Validate word count logic works
    
    assert payload.metadata.extracted_word_count >= 1

# WORD COUNT VALIDATION

def test_count_words():
    text = "One two three"
    assert count_words(text) == 3

def test_enforce_word_limit_valid():
    enforce_word_limit(10)  # Should not raise

def test_enforce_word_limit_zero():
    with pytest.raises(ValueError):
        enforce_word_limit(0)

def test_enforce_word_limit_too_many():
    with pytest.raises(ValueError):
        enforce_word_limit(MAX_WORD_COUNT + 1)

# EMPTY FILE / TEXT CHECKS

def test_empty_txt_file(tmp_path):
    file_path = create_txt_file(tmp_path, "")
    with pytest.raises(ValueError, match="File is empty"):
        build_document_payload(file_path)

# UNSUPPORTED FORMAT

def test_unsupported_format(tmp_path):
    file_path = tmp_path / "file.xyz"
    file_path.write_text("data")
    with pytest.raises(ValueError, match="Unsupported file format"):
        build_document_payload(file_path)
