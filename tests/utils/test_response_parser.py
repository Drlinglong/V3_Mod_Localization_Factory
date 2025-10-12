# tests/utils/test_response_parser.py
import pytest
from scripts.utils.response_parser import parse_json_from_response

# 用于在回退测试中断言的常量
MOCK_ORIGINAL_INPUT_3 = ["source1", "source2", "source3"]
MOCK_ORIGINAL_INPUT_2 = ["source1", "source2"]

@pytest.mark.parametrize("test_name, response_text, original_input, expected_output", [
    # --- Standard Dirty String Tests ---
    ("perfectly_legal_json",
     '["A", "B", "C"]',
     MOCK_ORIGINAL_INPUT_3,
     ["A", "B", "C"]),
    ("markdown_wrapper",
     '```json\n["A", "B", "C"]\n```',
     MOCK_ORIGINAL_INPUT_3,
     ["A", "B", "C"]),
    ("trailing_notes",
     '["A", "B", "C"]\nHere is a summary.',
     MOCK_ORIGINAL_INPUT_3,
     ["A", "B", "C"]),
    ("missing_comma_with_space",
     '["A" "B"]',
     MOCK_ORIGINAL_INPUT_2,
     ["A", "B"]),
    ("missing_comma_no_space",
     '["A""B"]',
     MOCK_ORIGINAL_INPUT_2,
     ["A", "B"]),
    ("unescaped_internal_quote",
     '["This is a \\"quote\\"", "This is an "illegal" quote"]',
     MOCK_ORIGINAL_INPUT_2,
     ['This is a "quote"', 'This is an "illegal" quote']), # Corrected expected output
    ("illegal_warning_message",
     '["A", WARNING: Source localization entry is incomplete, "C"]',
     MOCK_ORIGINAL_INPUT_3,
     ["A", "WARNING: Source localization entry is incomplete", "C"]),
    ("unrecoverable_damage_fallback",
     '["A", "B", "C"', # 括号不匹配
     MOCK_ORIGINAL_INPUT_3,
     MOCK_ORIGINAL_INPUT_3), # 期望回退到原文
    ("no_json_array_at_all_fallback",
     'Just some random text from a confused AI.',
     MOCK_ORIGINAL_INPUT_3,
     MOCK_ORIGINAL_INPUT_3), # 期望回退到原文
    ("mixed_poisoning_attack",
     '```json\\n["A""B", "Another "illegal" quote"]\\n```\\nAnd that is all.',
     MOCK_ORIGINAL_INPUT_2,
     ["A", "B", 'Another "illegal" quote']),

    # --- Nested JSON (Triage Step) Tests ---
    ("gemini_cli_style_success",
     '{"response": "[\\"A\\", \\"B\\", \\"C\\"]", "stats": {}}',
     MOCK_ORIGINAL_INPUT_3,
     ["A", "B", "C"]),
    ("malformed_outer_json_fallback_success",
     '{"response": "[\\"A\\", \\"B\\"]", "stats": { ...some garbage', # Outer is broken
     MOCK_ORIGINAL_INPUT_2,
     ["A", "B"]), # But inner is findable by the purifier
    ("missing_response_key_fallback",
     '{"not_the_right_key": "[\\"A\\", \\"B\\"]"}',
     MOCK_ORIGINAL_INPUT_2,
     MOCK_ORIGINAL_INPUT_2), # Triage fails, purifier finds nothing, fallback
    ("wrong_payload_type_fallback",
     '{"response": ["A", "B"]}', # Payload is a list, not a string
     MOCK_ORIGINAL_INPUT_2,
     MOCK_ORIGINAL_INPUT_2), # Triage fails, purifier finds nothing, fallback

    # --- Regression Tests for Specific Failures ---
    ("greedy_trap_regression",
     '["국가 [concept_journal_entry]는 특정 국가 또는 소수 국가에 고유한 [concept_journal_entry]입니다."]',
     ["dummy"],
     ["국가 [concept_journal_entry]는 특정 국가 또는 소수 국가에 고유한 [concept_journal_entry]입니다."]),
    ("repair_storm_regression_with_newlines",
     '["- जर्नल प्रविष्टि [GetPlayer.GetPrimaryCulture.GetName] संस्कृति की होनी चाहिए\\n- [Root.GetCountry.GetName] को [GetPlayer.GetPrimaryCulture.GetName] संस्कृति को प्राथमिक बनाना चाहिए"]',
     ["dummy"],
     ["- जर्नल प्रविष्टि [GetPlayer.GetPrimaryCulture.GetName] संस्कृति की होनी चाहिए\n- [Root.GetCountry.GetName] को [GetPlayer.GetPrimaryCulture.GetName] संस्कृति को प्राथमिक बनाना चाहिए"]),
])
def test_ultimate_response_parser(test_name, response_text, original_input, expected_output):
    """
    Tests the JSON parser against a battery of malformed inputs from the LLM.
    Ensures it either successfully repairs the JSON or safely falls back to the original text.
    """
    result = parse_json_from_response(response_text, original_input)
    assert result == expected_output, f"Test case '{test_name}' failed."
