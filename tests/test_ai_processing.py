import pytest
from fastapi import HTTPException
from src.ai_processing import build_prompt, process_with_ai, FeatureType, BASE_CONSTRAINTS

# Sample text for testing
sample_text = "This is a test document."

# Test that prompt is built correctly for each feature
@pytest.mark.parametrize("feature", ["summarize", "grammar", "translate", "explain", "convert"])
def test_build_prompt_contains_all_rules(feature: FeatureType):
    prompt = build_prompt(sample_text, feature)
    
    # 1. Contract rules (BASE_CONSTRAINTS) must be included
    assert BASE_CONSTRAINTS.strip() in prompt, "BASE_CONSTRAINTS missing from prompt!"
    
    # 2. Document content must be included
    assert sample_text in prompt, "Document content missing from prompt!"
    
    # 3. Feature-specific rules must be included
    from src.ai_processing import FEATURE_RULES
    assert FEATURE_RULES[feature].strip() in prompt, f"Feature rules for {feature} missing from prompt!"

# Test empty content raises HTTPException
def test_build_prompt_empty_text():
    with pytest.raises(HTTPException):
        build_prompt("", "summarize")

# Test unsupported feature raises HTTPException
def test_build_prompt_invalid_feature():
    with pytest.raises(HTTPException):
        build_prompt(sample_text, "invalid_feature")  # type: ignore
