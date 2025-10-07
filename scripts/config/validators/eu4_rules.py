# scripts/config/validators/eu4_rules.py

RULES = {
  "game_id": "3",
  "game_name": "Europa Universalis IV",
  "rules": [
    {
      "name": "non_ascii_in_brackets",
      "check_function": "banned_chars",
      "pattern": r"\[([^\]]+)\]",
      "level": "error",
      "message_key": "validation_eu4_brackets_chinese",
      "params": {
        "capture_group": 1
      }
    },
    {
      "name": "non_ascii_in_legacy_vars",
      "check_function": "banned_chars",
      "pattern": r"\$([^$\s]+)\$",
      "level": "error",
      "message_key": "validation_eu4_legacy_vars_chinese",
      "params": {
        "capture_group": 1
      }
    },
    {
      "name": "non_ascii_in_pound_icons",
      "check_function": "banned_chars",
      "pattern": r"£([^£\s]+)£",
      "level": "error",
      "message_key": "validation_eu4_pound_icons_chinese",
      "params": {
        "capture_group": 1
      }
    },
    {
      "name": "non_ascii_in_country_flags",
      "check_function": "banned_chars",
      "pattern": r"@([A-Z0-9]{3})",
      "level": "error",
      "message_key": "validation_eu4_country_flags_chinese",
      "params": {
        "capture_group": 1
      }
    },
    {
      "name": "mismatched_color_tags",
      "check_function": "mismatched_tags",
      "level": "warning",
      "message_key": "validation_eu4_color_tags_mismatch",
      "params": {
        "start_tag_pattern": r"§[a-zA-Z0-9]",
        "end_tag_string": "§!",
        "details_key": "validation_generic_color_tags_count"
      }
    },
    {
      "name": "currency_symbol_present",
      "check_function": "informational_pattern",
      "pattern": r"¤",
      "level": "info",
      "message_key": "validation_eu4_currency_symbol_detected",
      "params": {
        "details_key": "validation_eu4_currency_symbol_note"
      }
    }
  ]
}
