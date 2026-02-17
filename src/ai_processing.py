from fastapi import HTTPException
from src.schema import (
    FeatureType,
    QuestionScale,
)
from src.validation import (
    classify_question_scale,
    get_question_range,
)
"""
API VERSION v1 CONTRACT
This behavior is frozen.
Breaking changes require:
#new prompt rules
#new constraints
#new endpoint version (/v2)
DO NOT MODIFY WITHOUT VERSION-v1
Changes here affect AI behavior and output guarantees.
"""

# Global AI Constraints (Aligned With Schema + Validation Contracts)

BASE_CONSTRAINTS = """
You are a professional document processing AI.
NON-NEGOTIABLE RULES:
- Preserve the original tone, formality, and voice
- Preserve original document structure and paragraph order
- Do NOT reorder headings, paragraphs, or bullet points
- Do NOT paraphrase creatively
- Do NOT embellish, expand, or add ideas
- Do NOT simplify beyond the author's intent
- Avoid generic or "AI-style" phrasing
- Maintain original sentence rhythm
- Act as a neutral, invisible processor
- Output must strictly comply with formatting constraints
"""

# Feature-Specific Rules (Fully Aligned With FeatureType Enum)

FEATURE_RULES = {

    FeatureType.summarize: """
TASK: COMPRESSION-ONLY SUMMARIZATION
RULES:
- Reduce length only
- Preserve argument flow
- Preserve paragraph structure
- Remove redundancy, not meaning
- No stylistic paraphrasing
- No rewording unless required for compression
""",

    FeatureType.grammar_correct: """
TASK: GRAMMAR CORRECTION ONLY
RULES:
- Fix grammatical and syntactic errors only
- Do NOT change tone or voice
- Do NOT upgrade vocabulary
- Do NOT rewrite sentences
- Sentence meaning must remain identical
""",

    FeatureType.translate: """
TASK: LANGUAGE TRANSLATION
RULES:
- Automatically detect source language
- Preserve voice, tone, and structure
- Maintain paragraph-to-paragraph alignment
- No localization or cultural adaptation
- Output must mirror original structure
""",

    FeatureType.explain: """
TASK: CONTENT EXPLANATION
RULES:
- Explain the document clearly
- Match explanation difficulty to source complexity
- Do NOT oversimplify
- Output explanation separately from original content
- Do NOT reinterpret intent
""",

    FeatureType.convert: """
TASK: DOCUMENT CONVERSION
RULES:
- Convert format only
- Do NOT modify wording
- Do NOT alter structure
- Do NOT introduce or remove content
""",

    FeatureType.generate_questions: """
TASK: QUESTION GENERATION
RULES:
- Generate questions strictly from document content
- Questions must be sequentially numbered starting at 1
- Follow deterministic question count limits provided
- Do NOT include answers
- Do NOT include commentary
- Output must be a numbered list only
""",

    FeatureType.generate_answers: """
TASK: ANSWER GENERATION
RULES:
- Answer each provided question
- Preserve sequential numbering exactly
- Do NOT add commentary
- Do NOT introduce new questions
- Output must be a numbered list only
"""
}

# Prompt Builder

def build_prompt(
    text: str,
    feature: FeatureType,
    *,
    word_count: int | None = None,
    questions: list[str] | None = None,
    target_language: str | None = None,
) -> str:
    """
    Builds a contract-enforced AI prompt fully aligned
    with schema + validation deterministic constraints.
    """

    if feature not in FEATURE_RULES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported feature requested"
        )

    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="Empty content cannot be processed"
        )

    extra_constraints = ""

    # Deterministic scaling enforcement for question generation
    
    if feature == FeatureType.generate_questions:
        if word_count is None:
            raise HTTPException(
                status_code=400,
                detail="Word count required for question generation"
            )

        scale: QuestionScale = classify_question_scale(word_count)
        min_q, max_q = get_question_range(word_count)

        extra_constraints = f"""
DETERMINISTIC SCALING RULE:
- Document classification: {scale.value}
- Generate between {min_q} and {max_q} questions
- Strictly respect this range
"""

    # Strict answer alignment
   
    if feature == FeatureType.generate_answers:
        if not questions:
            raise HTTPException(
                status_code=400,
                detail="Questions required for answer generation"
            )

        formatted_questions = "\n".join(questions)

        extra_constraints = f"""
QUESTIONS TO ANSWER:
{formatted_questions}
RULE:
- Preserve numbering exactly as provided
"""

    # Translation constraint
   
    if feature == FeatureType.translate:
        if not target_language:
            raise HTTPException(
                status_code=400,
                detail="Target language required for translation"
            )

        extra_constraints = f"""
TARGET LANGUAGE:
{target_language}
"""
    prompt = f"""
{BASE_CONSTRAINTS}
{FEATURE_RULES[feature]}
{extra_constraints}

DOCUMENT CONTENT:
{text}
"""
    return prompt.strip()

# AI Processing Entry Point

def process_with_ai(
    text: str,
    feature: FeatureType,
    *,
    word_count: int | None = None,
    questions: list[str] | None = None,
    target_language: str | None = None,
) -> str:
    """
    Contract-compliant AI processing entry point.

    This function prepares AI behavior only.
    Actual AI model invocation is handled elsewhere.
    """
    prompt = build_prompt(
        text=text,
        feature=feature,
        word_count=word_count,
        questions=questions,
        target_language=target_language,
    )
    return prompt
