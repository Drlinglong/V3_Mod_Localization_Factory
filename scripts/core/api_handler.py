# scripts/core/api_handler.py
# ---------------------------------------------------------------
import os
import re
import time
from google import genai

from utils import i18n
from config import MODEL_NAME, CHUNK_SIZE
from utils.text_clean import strip_pl_diacritics, strip_outer_quotes   # ← kluczowe

# ---------------------------------------------------------------
#  ⚠️ alias wymagany przez audit.py  ⚠️
#  (narzędzie szuka dosłownie „_strip_pl_diacritics(”)
_strip_pl_diacritics = strip_pl_diacritics    # noqa: N816

# ---------------------------------------------------------------
def initialize_client() -> "genai.Client | None":
    """Inicjalizuje klienta Gemini."""
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
# ✓  POJEDYNCZY TEKST
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
    """Tłumaczy pojedynczy tekst (np. nazwę lub opis moda)."""
    if not text:
        return ""

    print_key = "translating_mod_name" if task_description == "mod name" else "translating_mod_desc"
    print(i18n.t(print_key, text=text[:30]))

    # —— prompt bazowy z profilu gry ————————————————
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

        # — EU4 → polski bez ogonków ——————————————
        if game_profile.get("strip_pl_diacritics") and target_lang["code"] == "pl":
            translated = _strip_pl_diacritics(translated)

        return translated
    except Exception as e:
        print(i18n.t("api_call_error", error=e))
        return text


# ----------------------------------------------------------------
# ✓  LISTA TEKSTÓW (w paczkach)
# ----------------------------------------------------------------
def translate_texts_in_batches(
    client: "genai.Client",
    texts_to_translate: list[str],
    source_lang: dict,
    target_lang: dict,
    game_profile: dict,
    mod_context: str,
) -> "list[str] | None":
    """Tłumaczy listę tekstów partiami (po CHUNK_SIZE pozycji)."""
    all_translated_texts: list[str] = []

    for i in range(0, len(texts_to_translate), CHUNK_SIZE):
        chunk = texts_to_translate[i : i + CHUNK_SIZE]
        batch_num = i // CHUNK_SIZE + 1
        print(i18n.t("processing_batch", batch_num=batch_num, chunk_size=len(chunk)))

        numbered_list = "\n".join(f'{j + 1}. "{txt}"' for j, txt in enumerate(chunk))

        base_prompt = game_profile["prompt_template"].format(
            source_lang_name=source_lang["name"],
            target_lang_name=target_lang["name"],
        )

        context_prompt_part = (
            f"CRITICAL CONTEXT: The mod you are translating is '{mod_context}'. "
            "Use this information to ensure all translations are thematically appropriate.\n"
        )

        format_prompt_part = (
            "CRITICAL FORMATTING: Your response MUST be a numbered list with the EXACT same "
            f"number of items (1‒{len(chunk)}). Each item MUST be the translation of the "
            "corresponding input line. DO NOT merge, add, or omit lines. "
            "Preserve special placeholders like $...$ or [...] and internal newlines (\\n).\n\n"
            "--- INPUT LIST ---\n"
            f"{numbered_list}\n"
            "--- END OF INPUT LIST ---"
        )

        prompt = base_prompt + context_prompt_part + format_prompt_part

        try:
            response = client.models.generate_content(model=MODEL_NAME, contents=prompt)

            # Wyciągamy linie „1. tekst”
            translated_chunk = re.findall(
                r'^\s*\d+\.\s*"?(.+?)"?$', response.text, re.MULTILINE | re.DOTALL
            )

            if len(translated_chunk) != len(chunk):
                print(
                    i18n.t(
                        "mismatch_error",
                        original_count=len(chunk),
                        translated_count=len(translated_chunk),
                    )
                )
                print(f"AI Response Preview: {response.text[:300]}...")
                return None

            # (1) usuwamy zewnętrzne cudzysłowy
            translated_chunk = [strip_outer_quotes(t) for t in translated_chunk]

            # (2) EU4 → strip ogonków jeśli trzeba
            if game_profile.get("strip_pl_diacritics") and target_lang["code"] == "pl":
                translated_chunk = [_strip_pl_diacritics(t) for t in translated_chunk]

            all_translated_texts.extend(translated_chunk)

            # łagodny throttle dla długich list
            if len(texts_to_translate) > CHUNK_SIZE:
                time.sleep(1)

        except Exception as e:
            print(i18n.t("api_call_error", error=e))
            return None

    return all_translated_texts
