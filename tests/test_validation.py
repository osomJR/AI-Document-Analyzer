import pytest
from src.schema import (
    AnalyzerRequest,
    DocumentPayload,
    DocumentMetadata,
    InputFormat,
    FeatureType,
    UserTier,
    UsageSnapshot,
    ConversionRequest,
    SummarizationRequest,
    QuestionGenerationRequest,
    AnswerGenerationRequest,
)
from src.validation import (
    validate_usage,
    validate_action_payload_consistency,
    validate_word_count_bounds,
    classify_question_scale,
    get_question_range,
    validate_structured_text_response,
    validate_numbered_list_response,
    validate_analyzer_request,
)

# FIXTURE HELPERS

def make_valid_metadata(word_count: int = 100):
    return DocumentMetadata(
        input_format=InputFormat.txt,
        file_size_mb=1,
        extracted_word_count=word_count,
        ocr_used=False,
    )

def make_valid_document(word_count: int = 100):
    return DocumentPayload(
        text="Valid text content",
        metadata=make_valid_metadata(word_count),
    )

def make_valid_snapshot(actions_used=0):
    return UsageSnapshot(
        user_tier=UserTier.free,
        actions_used_today=actions_used,
    )

# USAGE VALIDATION

def test_validate_usage_within_limit():
    snapshot = make_valid_snapshot(actions_used=3)
    validate_usage(snapshot)  # Should not raise

def test_validate_usage_exceeds_limit():
    snapshot = make_valid_snapshot(actions_used=5)
    with pytest.raises(ValueError):
        validate_usage(snapshot)

# ACTION–PAYLOAD CONSISTENCY

def test_valid_action_payload_match():
    request = AnalyzerRequest(
        user_tier=UserTier.free,
        action=FeatureType.summarize,
        document=make_valid_document(),
        payload=SummarizationRequest(feature=FeatureType.summarize),
    )
    validate_action_payload_consistency(request)

def test_invalid_action_payload_mismatch():
    request = AnalyzerRequest(
        user_tier=UserTier.free,
        action=FeatureType.convert,
        document=make_valid_document(),
        payload=SummarizationRequest(feature=FeatureType.summarize),
    )
    with pytest.raises(ValueError):
        validate_action_payload_consistency(request)

# WORD COUNT VALIDATION

def test_valid_word_count():
    request = AnalyzerRequest(
        user_tier=UserTier.free,
        action=FeatureType.summarize,
        document=make_valid_document(100),
        payload=SummarizationRequest(feature=FeatureType.summarize),
    )
    validate_word_count_bounds(request)

# QUESTION SCALING

def test_classify_small_scale():
    scale = classify_question_scale(200)
    assert scale.value == "small"

def test_classify_medium_scale():
    scale = classify_question_scale(500)
    assert scale.value == "medium"

def test_classify_large_scale():
    scale = classify_question_scale(900)
    assert scale.value == "large"

def test_question_range_small():
    min_q, max_q = get_question_range(200)
    assert min_q == 4
    assert max_q == 6

# RESPONSE VALIDATION

def test_validate_structured_text_response():
    response = validate_structured_text_response("Valid output")
    assert response.content == "Valid output"

def test_structured_text_empty():
    with pytest.raises(ValueError):
        validate_structured_text_response("   ")

def test_validate_numbered_list_response_valid():
    items = [
        "1. First item",
        "2. Second item",
    ]
    response = validate_numbered_list_response(items)
    assert len(response.items) == 2

def test_validate_numbered_list_response_invalid_numbering():
    items = [
        "1. First item",
        "3. Wrong numbering",
    ]
    with pytest.raises(ValueError):
        validate_numbered_list_response(items)

# FULL ANALYZER PIPELINE

def test_validate_analyzer_request_full_success():
    request = AnalyzerRequest(
        user_tier=UserTier.free,
        action=FeatureType.generate_questions,
        document=make_valid_document(200),
        payload=QuestionGenerationRequest(
            feature=FeatureType.generate_questions
        ),
    )
    snapshot = make_valid_snapshot(0)
    validate_analyzer_request(request, snapshot)

