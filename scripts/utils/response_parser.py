import json
import os
import re
from datetime import datetime
from typing import List
import logging
from scripts.utils import i18n

logger = logging.getLogger(__name__)

def _save_critical_failure_log(response_text: str, purified_text: str, repaired_text: str, final_error: str):
    """Saves a detailed log for critical, unrecoverable parsing failures."""
    try:
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        debug_file = os.path.join(log_dir, f"critical_parse_failure_{timestamp}.log")

        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write("=== CRITICAL PARSING FAILURE LOG ===\n")
            f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Final Error: {final_error}\n")
            f.write("=" * 80 + "\n\n")
            f.write("--- Original Response Text ---\n")
            f.write(response_text + "\n\n")
            f.write("--- 1. After Purification Attempt ---\n")
            f.write(purified_text + "\n\n")
            f.write("--- 2. After Repair Attempt ---\n")
            f.write(repaired_text + "\n\n")
            f.write("=" * 80 + "\n")

        logger.critical(f"Saved critical failure log to: {debug_file}")
    except Exception as e:
        logger.error(f"Failed to save critical failure log: {e}")


def _run_repair_surgeries(dirty_json: str) -> str:
    """
    Performs a series of surgical repairs on a JSON string.
    """
    repaired_json = dirty_json

    # Surgery 1: Fix known warning messages that are not quoted
    warning_str = "WARNING: Source localization entry is incomplete"
    if warning_str in repaired_json:
        repaired_json = repaired_json.replace(warning_str, f'"{warning_str}"')

    # Surgery 2: Add missing commas between consecutive quoted strings.
    # This handles both ` "A" "B" ` and ` "A""B" `. We explicitly use [ \t]
    # instead of \s to avoid matching newlines, which was identified as a
    # source of catastrophic repair failures on already-valid JSON.
    repaired_json = re.sub(r'(?<!\\)"[ \t]*(?<!\\)"', '","', repaired_json)

    # Surgery 3: State-machine-based internal quote escaping
    in_string = False
    escaped_chars = []
    i = 0
    while i < len(repaired_json):
        char = repaired_json[i]
        
        # Pass through existing escape sequences
        if char == '\\':
            escaped_chars.append(char)
            if i + 1 < len(repaired_json):
                escaped_chars.append(repaired_json[i+1])
                i += 1
            i += 1
            continue

        if char == '"':
            if not in_string:
                # We are entering a string.
                in_string = True
                escaped_chars.append(char)
            else:
                # We are inside a string. Is this the closing quote?
                # Peek ahead to see if the next non-whitespace char is a comma or bracket.
                j = i + 1
                while j < len(repaired_json) and repaired_json[j].isspace():
                    j += 1

                if j < len(repaired_json) and (repaired_json[j] == ',' or repaired_json[j] == ']'):
                    # This is a valid closing quote.
                    in_string = False
                    escaped_chars.append(char)
                else:
                    # This is an internal quote. Escape it.
                    escaped_chars.append('\\"')
        else:
            escaped_chars.append(char)
        i += 1
    repaired_json = "".join(escaped_chars)

    return repaired_json


def parse_json_from_response(response_text: str, original_input_list: list[str]) -> list[str]:
    """
    Parses a JSON array string from an LLM response using a 3-layer defense system.

    Args:
        response_text: The raw string response from the LLM.
        original_input_list: The original list of strings that were sent for processing.
                             This is used as the ultimate fallback.

    Returns:
        A list of strings. On successful parsing, it's the parsed list.
        On any unrecoverable failure, it's the original_input_list.
    """
    purified_text = ""
    repaired_text = ""

    # --- First Line of Defense: Balanced Bracket Extractor ---
    # This robustly finds the first complete JSON array, even with nested brackets.
    start_index = response_text.find('[')
    if start_index == -1:
        logging.critical("Extractor failed: No opening bracket '[' found in the response.")
        _save_critical_failure_log(response_text, "N/A", "N/A", "No opening bracket found.")
        return original_input_list

    balance_counter = 1
    end_index = -1
    # We must also consider quoted strings, as brackets inside them do not count.
    in_string = False
    for i in range(start_index + 1, len(response_text)):
        char = response_text[i]

        # Toggle in_string state if we encounter a quote that is not escaped.
        if char == '"':
            # Check for escaped quote, e.g., \\"
            if i > 0 and response_text[i-1] != '\\':
                in_string = not in_string

        if not in_string:
            if char == '[':
                balance_counter += 1
            elif char == ']':
                balance_counter -= 1

        if balance_counter == 0:
            end_index = i
            break

    if end_index == -1:
        logging.critical("Extractor failed: Could not find matching closing bracket ']' for the initial opening bracket.")
        _save_critical_failure_log(response_text, "N/A", "N/A", "No matching closing bracket found.")
        return original_input_list

    purified_text = response_text[start_index : end_index + 1]

    # --- Second Line of Defense: The Surgeon ---
    repaired_text = _run_repair_surgeries(purified_text)

    # --- Third Line of Defense: The Judge ---
    try:
        # Attempt to parse the repaired string.
        parsed_list = json.loads(repaired_text)
        return parsed_list
    except json.JSONDecodeError as e:
        # --- The Ultimate Fallback ---
        logging.critical(f"Judge failed: Final parsing attempt failed after purification and repair. Error: {e}")
        _save_critical_failure_log(response_text, purified_text, repaired_text, str(e))
        return original_input_list
