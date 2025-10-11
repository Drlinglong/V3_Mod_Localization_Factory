# tests/utils/test_json_repair.py
import pytest
from scripts.utils.response_parser import _attempt_to_repair_json

@pytest.mark.parametrize(
    "name, input_string, expected_output",
    [
        (
            "simple_missing_comma",
            '["item1" "item2"]',
            '["item1","item2"]'
        ),
        (
            "missing_comma_with_newline",
            '["item1"\n "item2"]',
            '["item1","item2"]'
        ),
        (
            "multiple_missing_commas",
            '["a" "b" "c"]',
            '["a","b","c"]'
        ),
        (
            "already_valid_json",
            '["valid", "json"]',
            '["valid", "json"]'
        ),
        (
            "no_repair_needed_with_spaces",
            '["item1", "item2"]',
            '["item1", "item2"]'
        ),
        (
            "unrepairable_malformed_json",
            '["missing_quote, "item2"]',
            '["missing_quote, "item2"]'
        ),
        (
            "empty_string",
            '',
            ''
        ),
        (
            "string_with_internal_quotes",
            '["a\\"b" "c\\"d"]',
            '["a\\"b","c\\"d"]'
        ),
    ]
)
def test_attempt_to_repair_json(name, input_string, expected_output):
    """
    Tests the _attempt_to_repair_json function with various inputs.
    """
    result = _attempt_to_repair_json(input_string)
    assert result == expected_output, f"Test case '{name}' failed"
