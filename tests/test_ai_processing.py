import pytest
from fastapi import HTTPException
from src.schema import FeatureType
from src.ai_processing import build_prompt, process_with_ai

# BASIC SUCCESS CASES

def test_summarize_prompt_builds_successfully():
    text = "This is a sample paragraph for testing summarization."
    
    prompt = build_prompt(
        text=text,
        feature=FeatureType.summarize
    )
    assert "COMPRESSION-ONLY SUMMARIZATION" in prompt
    assert text in prompt

def test_grammar_prompt_builds_successfully():
    text = "This are bad grammar sentence."
    
    prompt = build_prompt(
        text=text,
        feature=FeatureType.grammar_correct
    )
    assert "GRAMMAR CORRECTION ONLY" in prompt
    assert text in prompt

def test_translate_requires_target_language():
    text = "Bonjour tout le monde"
    with pytest.raises(HTTPException) as exc:
        build_prompt(
            text=text,
            feature=FeatureType.translate
        )
    assert exc.value.status_code == 400
    assert "Target language required" in exc.value.detail

def test_translate_with_target_language():
    text = "Bonjour tout le monde"

    prompt = build_prompt(
        text=text,
        feature=FeatureType.translate,
        target_language="English"
    )
    assert "TARGET LANGUAGE:" in prompt
    assert "English" in prompt

# QUESTION GENERATION TESTS

def test_generate_questions_requires_word_count():
    text = "Short text."
    with pytest.raises(HTTPException) as exc:
        build_prompt(
            text=text,
            feature=FeatureType.generate_questions
        )
    assert exc.value.status_code == 400
    assert "Word count required" in exc.value.detail

def test_generate_questions_includes_scaling_rule():
    text = "word " * 200  # 200 words → small scale (1–300)
    prompt = build_prompt(
        text=text,
        feature=FeatureType.generate_questions,
        word_count=200
    )
    assert "DETERMINISTIC SCALING RULE" in prompt
    assert "Generate between" in prompt

# ANSWER GENERATION TESTS

def test_generate_answers_requires_questions():
    text = "Some content."
    with pytest.raises(HTTPException) as exc:
        build_prompt(
            text=text,
            feature=FeatureType.generate_answers
        )
    assert exc.value.status_code == 400
    assert "Questions required" in exc.value.detail

def test_generate_answers_includes_questions():
    text = "Some content."
    questions = [
        "1. What is the topic?",
        "2. Why is it important?"
    ]
    prompt = build_prompt(
        text=text,
        feature=FeatureType.generate_answers,
        questions=questions
    )
    assert "QUESTIONS TO ANSWER:" in prompt
    assert questions[0] in prompt
    assert questions[1] in prompt

# EMPTY TEXT VALIDATION

def test_empty_text_raises_error():
    with pytest.raises(HTTPException) as exc:
        build_prompt(
            text="   ",
            feature=FeatureType.summarize
        )
    assert exc.value.status_code == 400
    assert "Empty content cannot be processed" in exc.value.detail

# PROCESS ENTRY POINT

def test_process_with_ai_returns_prompt():
    text = "This is a valid test document."
    result = process_with_ai(
        text=text,
        feature=FeatureType.summarize
    )
    assert isinstance(result, str)
    assert text in result
