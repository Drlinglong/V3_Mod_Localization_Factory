# scripts/utils/structured_parser.py
import logging
from typing import Type, TypeVar
from pydantic import BaseModel, ValidationError
from json_repair import repair_json

from scripts.core.schemas import TranslationResponse

logger = logging.getLogger(__name__)

# Define a TypeVar for Pydantic models to ensure type safety
T = TypeVar('T', bound=BaseModel)

def parse_response(
    response_text: str,
    pydantic_model: Type[T] = TranslationResponse
) -> T | None:
    """
    Parses a potentially malformed JSON string from an LLM response into a Pydantic model.

    This function implements a two-layer defense system:
    1.  **json_repair**: First, it uses the `json_repair` library to fix common JSON syntax
        errors (e.g., missing commas, trailing commas, incorrect quoting). This makes the
        parsing process much more robust against "dirty" LLM outputs.
    2.  **Pydantic Validation**: After the string is repaired, it's validated against the
        provided Pydantic model. This ensures that the final output strictly adheres to the
        expected data structure (schema).

    Args:
        response_text: The raw string response from the LLM.
        pydantic_model: The Pydantic model class to validate against. Defaults to
                        `TranslationResponse`.

    Returns:
        An instance of the Pydantic model if parsing and validation are successful,
        otherwise `None`.
    """
    repaired_json_str = ""
    try:
        # First Line of Defense: Use json_repair for robust fixing
        repaired_json_str = repair_json(response_text)
        logger.debug("Successfully repaired JSON string with json_repair.")

        # Second Line of Defense: Use Pydantic to validate and load the data
        model_instance = pydantic_model.model_validate_json(repaired_json_str)
        logger.debug("Successfully validated repaired JSON with Pydantic model.")
        return model_instance

    except ValidationError as e:
        logger.error(f"Pydantic validation failed after json_repair: {e}")
        # Optionally, log the failed text for debugging
        # logger.debug(f"Repaired text that failed validation: {repaired_json_str}")
        return None
    except Exception as e:
        # Catch other potential errors from repair_json or other unexpected issues
        logger.critical(f"An unexpected error occurred during parsing: {e}")
        # logger.debug(f"Original text that caused the error: {response_text}")
        return None
