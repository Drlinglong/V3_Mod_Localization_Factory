import json
import os
import re
from datetime import datetime
from typing import List, Optional
import logging
from scripts.utils import i18n

logger = logging.getLogger(__name__)

class ParsingFailedAfterRepairError(Exception):
    """Custom exception raised when JSON parsing fails even after repair attempts."""
    pass

def _save_debug_file(response_text: str, error_type: str, details: str):
    """Saves a debug file to the logs directory."""
    try:
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        debug_file = os.path.join(log_dir, f"debug_parse_failure_{timestamp}.log") # Changed extension to .log

        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(i18n.t("debug_file_header") + "\n")
            f.write(i18n.t("debug_file_time", time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + "\n")
            f.write(i18n.t("debug_file_error_type", error_type=error_type) + "\n")
            f.write(i18n.t("debug_file_details", details=details) + "\n")
            f.write("=" * 80 + "\n")
            f.write(i18n.t("debug_file_raw_response") + "\n")
            f.write("-" * 40 + "\n")
            f.write(response_text)
            f.write("\n" + "=" * 80 + "\n")

        logger.info(i18n.t("debug_file_saved", debug_file=debug_file))
    except Exception as e:
        logger.error(i18n.t("debug_file_save_failed", e=e))

def _attempt_to_repair_json(json_string: str) -> str:
    """
    Attempts to repair a broken JSON string.
    Currently focuses on adding missing commas between consecutive quoted strings.
    """
    # This regex finds occurrences of "a" "b" (separated by whitespace) and replaces them with "a", "b"
    repaired_string = re.sub(r'(?<!\\)"\s+(?<!\\)"', '","', json_string)
    return repaired_string

def parse_json_response(response_text: str, expected_count: int) -> Optional[List[str]]:
    """
    Parses a JSON array string from an LLM response, with fault tolerance and repair.
    """
    if not response_text:
        return None # Handle empty string input gracefully

    # --- 1. Optimistic First Pass ---
    clean_text = response_text.strip()
    if clean_text.startswith("```json"):
        clean_text = clean_text.removeprefix("```json").strip()
    if clean_text.startswith("```"):
        clean_text = clean_text.removeprefix("```").strip()
    if clean_text.endswith("```"):
        clean_text = clean_text.removesuffix("```").strip()

    try:
        parsed_data = json.loads(clean_text)
    except json.JSONDecodeError as initial_error:
        # --- 2. Repair and Retry ---
        logger.warning(i18n.t("parser_initial_decode_failed_retrying"))
        repaired_text = _attempt_to_repair_json(clean_text)

        try:
            parsed_data = json.loads(repaired_text)
            logger.info(i18n.t("parser_repair_succeeded"))
        except json.JSONDecodeError as final_error:
            # --- 3. Final Failure ---
            logger.error(i18n.t("parser_repair_failed"))
            _save_debug_file(response_text, "JSON Decode Error After Repair", str(final_error))
            raise ParsingFailedAfterRepairError(
                "JSON parsing failed even after repair attempts."
            ) from final_error

    # --- 4. Structure Validation and Normalization ---
    translations = None
    if isinstance(parsed_data, list):
        translations = parsed_data
    elif isinstance(parsed_data, dict) and 'response' in parsed_data:
        # Handle cases where the list is nested inside a dictionary
        logger.info(i18n.t("unpacking_wrapped_response"))
        nested_text = parsed_data['response']
        try:
            translations = json.loads(nested_text)
            if not isinstance(translations, list):
                 logger.warning(i18n.t("parser_unpack_json_not_list_warning", nested_data=translations))
                 return [""] * expected_count
        except json.JSONDecodeError as e:
            logger.error(i18n.t("parser_unpack_json_decode_error", nested_text=nested_text))
            _save_debug_file(response_text, "Nested JSON Decode Error", str(e))
            raise ParsingFailedAfterRepairError("Failed to decode nested JSON.") from e
    else:
        logger.warning(i18n.t("parser_json_not_list_warning", parsed_data=parsed_data))
        # Not raising an exception here, as it's a format issue, not a parsing failure.
        # Returning an empty list or padded list might be appropriate. Let's pad it.
        return [""] * expected_count

    if translations is None:
        logger.error(i18n.t("parser_unknown_logic_error"))
        _save_debug_file(response_text, "Logic Error", "Translations variable was not assigned.")
        return [""] * expected_count

    # --- 5. Count Adjustment ---
    if len(translations) != expected_count:
        logger.warning(i18n.t("parser_translation_count_mismatch", expected_count=expected_count, actual_count=len(translations)))
        while len(translations) < expected_count:
            translations.append("")
        translations = translations[:expected_count]

    return [str(item) for item in translations]
