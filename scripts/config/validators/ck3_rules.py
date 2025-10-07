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
      "pattern": r"\[(?:GetTrait|GetTitleByKey)\\'([^\']*)'\]",
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
    }
  ]
}
