from fastapi import HTTPException
from typing import Literal

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

# Contract-Locked Feature Set

FeatureType = Literal[
    "summarize",
    "grammar",
    "translate",
    "explain",
    "convert"
]

# Global AI Constraints

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
"""

# Feature-Specific Constraints

FEATURE_RULES = {

    "summarize": """
TASK: COMPRESSION-ONLY SUMMARIZATION

RULES:
- Reduce length only
- Preserve argument flow
- Preserve paragraph structure
- Remove redundancy, not meaning
- No stylistic paraphrasing
- No rewording unless required for compression
""",

    "grammar": """
TASK: GRAMMAR CORRECTION ONLY

RULES:
- Fix grammatical and syntactic errors only
- Do NOT change tone or voice
- Do NOT upgrade vocabulary
- Do NOT rewrite sentences
- Sentence meaning must remain identical
""",

    "translate": """
TASK: LANGUAGE TRANSLATION

RULES:
- Automatically detect source language
- Preserve voice, tone, and structure
- Maintain paragraph-to-paragraph alignment
- No localization or cultural adaptation
- Output must mirror original structure
""",

    "explain": """
TASK: CONTENT EXPLANATION

RULES:
- Explain the document clearly
- Match explanation difficulty to source complexity
- Do NOT oversimplify
- Output explanation separately from original content
- Do NOT reinterpret intent
""",

    "convert": """
TASK: DOCUMENT CONVERSION

RULES:
- Convert format only
- Do NOT modify wording
- Do NOT alter structure
- Do NOT introduce or remove content
"""
}

# Prompt Builder

def build_prompt(
    text: str,
    feature: FeatureType
) -> str:
    """
    Builds a contract-enforced AI prompt.
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

    prompt = f"""
{BASE_CONSTRAINTS}

{FEATURE_RULES[feature]}

DOCUMENT CONTENT:
{text}
"""

    return prompt.strip()

# AI Processing Entry Point

def process_with_ai(
    text: str,
    feature: FeatureType
) -> str:
    """
    Contract-compliant AI processing entry point.

    NOTE:
    - This function prepares AI behavior only
    - Actual AI model invocation is handled elsewhere
    """

    prompt = build_prompt(text, feature)

    # Placeholder for AI provider integration
    # Example (later):
    # response = ai_provider.generate(prompt)
    # return response

    return prompt
