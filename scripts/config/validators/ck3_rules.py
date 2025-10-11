# scripts/config/validators/ck3_rules.py

RULES = {
  "game_id": "5",
  "game_name": "Crusader Kings III",
  "rules": [
    {
      "name": "non_ascii_in_scopes_and_functions",
      "check_function": "banned_chars",
      "pattern": r"\[(?!Concept)([^\]]+)\]",
      "level": "error",
      "message_key": "validation_ck3_scopes_functions_chinese",
      "params": {
        "capture_group": 1
      }
    },
    {
      "name": "non_ascii_in_concept_key",
      "check_function": "banned_chars",
      "pattern": r"\[Concept\('([^']*)',",
      "level": "error",
      "message_key": "validation_ck3_concept_key_chinese",
      "params": {
        "capture_group": 1
      }
    },
    {
      "name": "non_ascii_in_trait_or_title_key",
      "check_function": "banned_chars",
      "pattern": r"\[(?:GetTrait|GetTitleByKey)'([^']*)'\]",
      "level": "error",
      "message_key": "validation_ck3_trait_title_key_chinese",
      "params": {
        "capture_group": 1
      }
    },
    {
      "name": "non_ascii_in_dollar_vars",
      "check_function": "banned_chars",
      "pattern": r"\$([^$\s]+)\$",
      "level": "error",
      "message_key": "validation_ck3_dollar_vars_chinese",
      "params": {
        "capture_group": 1
      }
    },
    {
      "name": "non_ascii_in_icon_key",
      "check_function": "banned_chars",
      "pattern": r"@([^!]+)!",
      "level": "error",
      "message_key": "validation_ck3_icon_key_chinese",
      "params": {
        "capture_group": 1
      }
    },
    {
      "name": "mismatched_formatting_tags",
      "check_function": "mismatched_tags",
      "level": "warning",
      "message_key": "validation_ck3_formatting_tags_mismatch",
      "params": {
        "start_tag_pattern": r"#[a-zA-Z0-9_;]+",
        "end_tag_string": "#!",
        "details_key": "validation_generic_color_tags_count"
      }
    },
    {
      "name": "formatting_tags",
      "check_function": "formatting_tags",
      "pattern": r"#([a-zA-Z0-9_]+)",
      "level": "warning",
      "message_key": "validation_ck3_unknown_formatting",
      "params": {
        "valid_tags": [
            "high", "medium", "low", "weak", "flavor", "f",
            "light_background", "light_background_underline",
            "help", "help_light_background", "instruction", "i",
            "warning", "x", "xb", "xlight", "enc", "alert_trial", "alert_bold",
            "value", "v", "negative_value", "positive_value", "mixed_value", "zero_value",
            "n", "p", "z", "m", "positive_value_toast",
            "clickable", "game_link", "l", "explanation_link", "e", "explanation_link_light_background", "b",
            "g", "g_light",
            "tooltip_heading", "t", "tooltip_subheading", "s", "tooltip_heading_small", "ts",
            "debug", "d", "variable", "date", "trigger_inactive",
            "difficulty_easy", "difficulty_medium", "difficulty_hard", "difficulty_very_hard",
            "true_white", "tut", "tut_kw", "same",
            "emphasis", "emp", "bol", "und", "die1", "die2", "die3",
            "ber", "poe", "sucglow", "flatulence",
            "defender_color", "attacker_color",
            "credits_title", "credits_header", "credits_subheader", "credits_entries",
            "aptitude_terrible", "aptitude_poor", "aptitude_average", "aptitude_good", "aptitude_excellent",
            "scheme_odds_abysmal", "scheme_odds_low", "scheme_odds_medium", "scheme_odds_high", "scheme_odds_excellent",
            "bold", "italic", "underline", "indent_newline"
        ],
        "no_space_required_tags": [],
        "unknown_tag_error_key": "validation_ck3_unknown_formatting",
        "unsupported_formatting_details_key": "validation_ck3_unsupported_formatting",
        "missing_space_details_key": "validation_ck3_formatting_found_at"
      }
    }
  ]
}
