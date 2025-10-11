import pytest
from unittest.mock import MagicMock
from scripts.utils.response_parser import parse_json_response, ParsingFailedAfterRepairError

# --- Group 1: Tests for successful parsing and repair ---
@pytest.mark.parametrize(
    "name, response_text, expected_count, expected_output",
    [
        # Standard success cases
        ("perfect_json", '["translation1", "translation2"]', 2, ["translation1", "translation2"]),
        ("markdown_wrapped", '```json\n["item1", "item2"]\n```', 2, ["item1", "item2"]),
        ("nested_response", '{"response": "[\\"nested1\\", \\"nested2\\"]"}', 2, ["nested1", "nested2"]),
        ("mixed_types", '[1, true, "text"]', 3, ["1", "True", "text"]),
        ("empty_list", '[]', 0, []),
        # Count adjustment cases
        ("count_mismatch_less", '["only_one"]', 2, ["only_one", ""]),
        ("count_mismatch_more", '["one", "two", "three"]', 2, ["one", "two"]),
        # New case to test the repair logic for missing commas, using a real newline
        ("repairable_json", '["item1"\n"item2"]', 2, ["item1", "item2"]),
    ],
)
def test_parse_json_response_success_scenarios(mocker, name, response_text, expected_count, expected_output):
    """
    Tests various scenarios where JSON parsing should succeed, including after repair.
    """
    mocker.patch("scripts.utils.i18n.t", side_effect=lambda key, **kwargs: f"i18n:{key} {kwargs}")
    mock_save_debug = mocker.patch("scripts.utils.response_parser._save_debug_file")

    result = parse_json_response(response_text, expected_count)

    assert result == expected_output, f"Test case '{name}' failed"
    assert not mock_save_debug.called, f"Debug file should not be saved on success for '{name}'"

# --- Group 2: Tests for unrecoverable parsing errors ---
@pytest.mark.parametrize(
    "name, response_text, expected_count",
    [
        ("malformed_unrepairable", '["missing_quote, "item2"]', 2),
        ("nested_malformed_unrepairable", '{"response": "[\\"invalid"}', 1),
    ],
)
def test_parse_json_response_raises_exception(mocker, name, response_text, expected_count):
    """
    Tests scenarios where parsing should fail even after repair attempts,
    raising a ParsingFailedAfterRepairError.
    """
    mocker.patch("scripts.utils.i18n.t", side_effect=lambda key, **kwargs: f"i18n:{key} {kwargs}")
    mock_save_debug = mocker.patch("scripts.utils.response_parser._save_debug_file")

    with pytest.raises(ParsingFailedAfterRepairError):
        parse_json_response(response_text, expected_count)

    assert mock_save_debug.called, f"Debug file should be saved on failure for '{name}'"

# --- Group 3: Tests for special return values ---
def test_parse_json_response_empty_string_returns_none(mocker):
    """
    Tests that providing an empty string to the parser correctly returns None.
    """
    mocker.patch("scripts.utils.i18n.t", side_effect=lambda key, **kwargs: f"i18n:{key} {kwargs}")
    mock_save_debug = mocker.patch("scripts.utils.response_parser._save_debug_file")

    result = parse_json_response("", 2)

    assert result is None
    assert not mock_save_debug.called

def test_parse_json_response_wrong_type_dict_returns_padded_list(mocker):
    """
    Tests that providing a JSON object (dict) instead of a list returns a
    list of empty strings padded to the expected count.
    """
    mocker.patch("scripts.utils.i18n.t", side_effect=lambda key, **kwargs: f"i18n:{key} {kwargs}")

    response_text = '{"key": "value"}'
    expected_count = 2
    result = parse_json_response(response_text, expected_count)

    assert result == ["", ""]
