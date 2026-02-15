from pydantic import BaseModel, Field, validator
from typing import List, Literal, Optional, Annotated

# CONSTANTS (HARD LIMITS — NON-CONFIGURABLE)

MAX_WORDS = 1000
MAX_FILE_SIZE_MB = 10

# ENUMS

FeatureType = Literal[
    "convert",
    "summarize",
    "grammar",
    "translate",
    "explain",
    "generate_questions",
    "generate_answers",
]

InputFormat = Literal["pdf", "docx", "txt", "jpg", "jpeg"]
OutputFormat = Literal["pdf", "docx", "txt"]

# INPUT SCHEMAS

class TextInput(BaseModel):
    """
    Copy-paste text input.
    Used for all features except file-based OCR.
    """

    feature: FeatureType = Field(..., description="Requested AI feature")
    text: str = Field(..., description="Raw input text (max 1000 words)")
    output_format: OutputFormat = Field(
        "txt", description="Desired output format"
    )

    @validator("text")
    def enforce_word_limit(cls, v: str):
        if len(v.split()) > MAX_WORDS:
            raise ValueError("Text exceeds 1000-word limit")
        return v

class FileInput(BaseModel):
    """
    File metadata input.
    Actual file is handled separately via UploadFile.
    """

    feature: FeatureType = Field(..., description="Requested AI feature")
    input_format: InputFormat = Field(..., description="Uploaded file format")
    output_format: OutputFormat = Field(..., description="Desired output format")

    file_size_mb: Annotated[int, Field(le=MAX_FILE_SIZE_MB)] = Field(
    ..., description="Uploaded file size in MB (must be ≤ 10)"
    )

class QuestionGenerationInput(BaseModel):
    """
    Stateless request for question generation.
    """

    feature: Literal["generate_questions"] = Field(
        ..., description="Question generation feature"
    )
    source_text: str = Field(..., description="Original document text")

    @validator("source_text")
    def enforce_word_limit(cls, v: str):
        if len(v.split()) > MAX_WORDS:
            raise ValueError("Text exceeds 1000-word limit")
        return v

class AnswerGenerationInput(BaseModel):
    """
    Stateless request for answer generation.
    Frontend must resend original document + generated questions.
    """

    feature: Literal["generate_answers"] = Field(
        ..., description="Answer generation feature"
    )
    source_text: str = Field(..., description="Original document text")
    questions: List[str] = Field(
        ..., description="Previously generated numbered questions"
    )

    @validator("source_text")
    def enforce_word_limit(cls, v: str):
        if len(v.split()) > MAX_WORDS:
            raise ValueError("Text exceeds 1000-word limit")
        return v

# OUTPUT SCHEMAS

class ConvertedDocumentOutput(BaseModel):
    """
    Output for conversion, summarization, grammar correction, and translation.
    """

    output_format: OutputFormat = Field(..., description="Returned file format")
    word_count: int = Field(..., description="Final word count")
    content: str = Field(..., description="Full processed content")

class ExplanationOutput(BaseModel):
    """
    Output for explanation feature.
    """

    explanation: str = Field(..., description="Clear explanation of document content")

class QuestionOutput(BaseModel):
    """
    Deterministic question output.
    """

    classification: Literal["small", "medium", "large"] = Field(
        ..., description="Document size classification"
    )
    questions: List[str] = Field(
        ..., description="Numbered questions ordered by increasing difficulty"
    )

class AnswerOutput(BaseModel):
    """
    Deterministic answer output aligned with questions.
    """

    answers: List[str] = Field(
        ..., description="Numbered answers aligned exactly with questions"
    )

class ErrorResponse(BaseModel):
    """
    Standard error response.
    """

    detail: str = Field(..., description="Error message")
