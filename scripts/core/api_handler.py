# scripts/core/api_handler.py
# ---------------------------------------------------------------
import os
import re
import time
import concurrent.futures # Import the library for parallel processing
from google import genai

from utils import i18n
from config import MODEL_NAME, CHUNK_SIZE
from utils.text_clean import strip_pl_diacritics, strip_outer_quotes # Key imports from Strategian

# ---------------------------------------------------------------
#  Alias required by audit.py
#  (The tool literally searches for "_strip_pl_diacritics(")
_strip_pl_diacritics = strip_pl_diacritics # noqa: N816

# ---------------------------------------------------------------
def initialize_client() -> "genai.Client | None":
    """Initializes the Gemini client."""
    if not os.getenv("GEMINI_API_KEY"):
        print("API Key not found in environment variables.")
        return None
    try:
        client = genai.Client()
        print(f"Gemini client initialized successfully, using model: {MODEL_NAME}")
        return client
    except Exception as e:
        print(f"Error initializing Gemini client: {e}")
        return None

# ----------------------------------------------------------------
# ✓ SINGLE TEXT
# ----------------------------------------------------------------
def translate_single_text(
    client: "genai.Client",
    text: str,
    task_description: str,
    mod_name: str,
    source_lang: dict,
    target_lang: dict,
    mod_context: str,
    game_profile: dict,
) -> str:
    """Translates a single text (e.g., mod name or description)."""
    if not text:
        return ""

    print_key = "translating_mod_name" if task_description == "mod name" else "translating_mod_desc"
    print(i18n.t(print_key, text=text[:30]))

    # Base prompt from the game profile
    base_prompt = game_profile["single_prompt_template"].format(
        mod_name=mod_name,
        task_description=task_description,
        source_lang_name=source_lang["name"],
        target_lang_name=target_lang["name"],
    )

    prompt = (
        base_prompt
        + f"CRITICAL CONTEXT: The mod's theme is '{mod_context}'. Use this to ensure accuracy.\n"
        "CRITICAL FORMATTING: Your response MUST ONLY contain the translated text. "
        "DO NOT include explanations, pinyin, or any other text.\n"
        'For example, if the input is "Flavor Pack", your output must be "风味包" and nothing else.\n\n'
        f'Translate this: "{text}"'
    )

    try:
        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
        translated = strip_outer_quotes(response.text.strip())

        # EU4 → Polish without diacritics
        if game_profile.get("strip_pl_diacritics") and target_lang["code"] == "pl":
            translated = _strip_pl_diacritics(translated)

        return translated
    except Exception as e:
        print(i18n.t("api_call_error", error=e))
        return text

# In scripts/core/api_handler.py

def _translate_chunk(client, chunk, source_lang, target_lang, game_profile, mod_context):
    """
    [Worker Function] Translates a single chunk of text and performs post-processing.
    This function is called by each thread in the parallel executor.
    """
    # 1. Format the list of texts into a numbered list for the prompt.
    numbered_list = "\n".join([f"{j+1}. \"{text}\"" for j, text in enumerate(chunk)])
    
    # 2. Get the base prompt template from the game profile.
    base_prompt = game_profile['prompt_template'].format(
        source_lang_name=source_lang['name'],
        target_lang_name=target_lang['name']
    )
    
    # 3. Prepare the contextual and formatting instructions.
    context_prompt_part = (
        f"CRITICAL CONTEXT: The mod you are translating is '{mod_context}'. "
        "Use this information to ensure all translations are thematically appropriate.\n"
    )
    format_prompt_part = (
        "CRITICAL FORMATTING: Your response MUST be a numbered list with the EXACT same number of items, from 1 to "
        f"{len(chunk)}. "
        "Each item in your list MUST be the translation of the corresponding item in the input list.\n"
        "DO NOT merge, add, or omit lines. DO NOT add any explanations. "
        "There are two types of special syntax:\n"
        "1.  **Variables** like `$variable$`, `[Concept('key', '$concept_name$')]`, `[SCOPE.some.Function]`. You MUST preserve these variables completely. DO NOT translate any text inside them.\n"
        "2.  **Formatting Tags** like `#R ... #!`, `§Y...§!`. You MUST preserve the tags themselves (e.g., `#R`, `#!`), but you SHOULD translate the plain text that is inside them.\n\n"
        "Preserve all internal newlines (\\n).\n\n"
        "--- INPUT LIST ---\n"
        f"{numbered_list}\n"
        "--- END OF INPUT LIST ---"
    )
    
    # 4. Assemble the final prompt.
    prompt = base_prompt + context_prompt_part + format_prompt_part
    
    try:
        # 5. Call the Gemini API.
        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
        
        # 6. Parse the numbered list from the AI's response using regex.
        translated_chunk = re.findall(r'^\s*\d+\.\s*"?(.+?)"?$', response.text, re.DOTALL | re.MULTILINE)

        # 7. Validate that the number of translated lines matches the number of source lines.
        if len(translated_chunk) != len(chunk):
            print(i18n.t("mismatch_error", original_count=len(chunk), translated_count=len(translated_chunk)))
            print(f"AI Response Preview: {response.text[:300]}...")
            return None # Return None to indicate failure.
        
        # 8. Perform post-processing on the translated text (e.g., stripping quotes or diacritics).
        translated_chunk = [strip_outer_quotes(t) for t in translated_chunk]
        if game_profile.get("strip_pl_diacritics") and target_lang["code"] == "pl":
            translated_chunk = [_strip_pl_diacritics(t) for t in translated_chunk]
        
        return translated_chunk
        
    except Exception as e:
        print(i18n.t("api_call_error", error=e))
        return None

def translate_texts_in_batches(
    client: "genai.Client",
    texts_to_translate: list[str],
    source_lang: dict,
    target_lang: dict,
    game_profile: dict,
    mod_context: str,
) -> "list[str] | None":
    """
    [Foreman Function] Translates a list of texts in batches, using a thread pool for parallel execution.
    It preserves the results of successfully translated chunks even if other chunks fail.
    """
    # If there's only one chunk or less, run in simple serial mode to avoid overhead.
    if len(texts_to_translate) <= CHUNK_SIZE:
        print(i18n.t("processing_batch", batch_num=1, chunk_size=len(texts_to_translate)))
        return _translate_chunk(client, texts_to_translate, source_lang, target_lang, game_profile, mod_context)

    # Pre-split the entire job into chunks.
    chunks = [texts_to_translate[i : i + CHUNK_SIZE] for i in range(0, len(texts_to_translate), CHUNK_SIZE)]
    
    # Pre-allocate a list to store results in the correct order.
    results = [None] * len(chunks)
    
    # Use a ThreadPoolExecutor to manage a pool of worker threads.
    with concurrent.futures.ThreadPoolExecutor() as executor:
        print(i18n.t("parallel_processing_start", count=len(chunks)))

        # Submit all chunks to the thread pool, mapping each future back to its original index.
        future_to_index = {
            executor.submit(_translate_chunk, client, chunk, source_lang, target_lang, game_profile, mod_context): i
            for i, chunk in enumerate(chunks)
        }
        
        # As each future (worker) completes, retrieve the result.
        for future in concurrent.futures.as_completed(future_to_index):
            index = future_to_index[future]
            try:
                # Place the result in the correct slot in the results list to maintain order.
                results[index] = future.result()
            except Exception as e:
                print(f"A translation thread failed with a critical error: {e}")
                results[index] = None # Mark as failed.

    # Assemble the final list, preserving successful results.
    all_translated_texts: list[str] = []
    has_failures = False
    for i, translated_chunk in enumerate(results):
        if translated_chunk is None:
            # If a chunk failed, keep the original English text for that chunk.
            has_failures = True
            print(f"Warning: Batch {i+1} failed. The original English text for this batch will be used as a fallback.")
            original_chunk = chunks[i]
            all_translated_texts.extend(original_chunk)
        else:
            all_translated_texts.extend(translated_chunk)
    
    if has_failures:
        print("Warning: Some translation batches failed. Original English text has been used for the failed parts.")

    print(i18n.t("parallel_processing_end"))
    return all_translated_texts