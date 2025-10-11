# tests/utils/test_post_process_validator.py
import pytest
from scripts.utils.post_process_validator import PostProcessValidator, ValidationLevel

@pytest.fixture
def validator():
    """Provides a PostProcessValidator instance for testing."""
    return PostProcessValidator()

def test_residual_punctuation_check_finds_issue(validator):
    """
    Tests that the built-in residual punctuation check correctly identifies
    source language punctuation in a translated text.
    """
    game_id = "1"  # Victoria 3, which defaults to zh-CN as source
    test_text = "This is a translated sentence，but it still contains a Chinese comma。"

    results = validator.validate_game_text(game_id, test_text, line_number=1)

    assert len(results) > 0, "Validator should have found at least one issue."

    punctuation_result = None
    for result in results:
        if "punctuation" in result.message or "标点" in result.message:
            punctuation_result = result
            break

    assert punctuation_result is not None, "A specific punctuation validation result should be found."
    assert punctuation_result.is_valid is False
    assert punctuation_result.level == ValidationLevel.WARNING
    assert "，" in punctuation_result.details
    assert "。" in punctuation_result.details

def test_residual_punctuation_check_passes_clean_text(validator):
    """
    Tests that the residual punctuation check does not raise issues for a clean text.
    """
    game_id = "1"  # Victoria 3
    test_text = "This is a perfectly clean sentence."

    results = validator.validate_game_text(game_id, test_text, line_number=1)

    punctuation_result = None
    for result in results:
        # Check for the specific message keys or parts of the message
        if "validation_residual_punctuation_found" in result.message:
            punctuation_result = result
            break

    assert punctuation_result is None, "No punctuation issues should be found in clean text."
