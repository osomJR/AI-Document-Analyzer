from pydantic import BaseModel, Field
from typing import Optional, Literal

# INPUT SCHEMAS

class TextInput(BaseModel):
    """
    Schema for copy-paste text input.
    """
    feature: Literal['summarize', 'grammar', 'translate', 'explain', 'convert'] = Field(
        ..., description="AI feature to apply to input")
    text: str = Field(..., description="Copy-paste text input, max 1000 words")
    output_format: Optional[Literal['pdf', 'docx', 'txt']] = Field(
        'txt', description="Desired output format (for conversion or AI services)")

class FileInput(BaseModel):
    """
    Schema for metadata of file uploads.
    Actual file handled separately as UploadFile in FastAPI endpoint.
    """
    feature: Literal['summarize', 'grammar', 'translate', 'explain', 'convert'] = Field(
        ..., description="AI feature to apply to uploaded file")
    output_format: Optional[Literal['pdf', 'docx', 'txt']] = Field(
        'txt', description="Desired output format")
    max_words: Optional[int] = Field(1000, description="Maximum allowed words after extraction")
    max_file_size_mb: Optional[int] = Field(10, description="Maximum file size in MB")

# OUTPUT SCHEMAS

class ProcessedTextOutput(BaseModel):
    """
    Schema for AI-processed text output.
    """
    filename: Optional[str] = Field(None, description="Original filename if uploaded")
    words: int = Field(..., description="Word count of processed content")
    content_preview: str = Field(..., description="Preview of first ~500 characters of processed content")
    feature_applied: str = Field(..., description="AI feature applied")
    output_format: str = Field(..., description="Format of the output returned")

class ErrorResponse(BaseModel):
    """
    Standard error response schema
    """
    detail: str = Field(..., description="Error message")
