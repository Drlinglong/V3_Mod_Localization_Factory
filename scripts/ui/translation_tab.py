"""初次汉化标签页模块"""
import gradio as gr
from scripts.utils.i18n import t
from scripts.config import (
    LANGUAGES,
    GAME_PROFILES,
    API_PROVIDERS,
    DEFAULT_API_PROVIDER,
    SOURCE_DIR,
)
from scripts.core.directory_handler import scan_source_directory


def create_translation_tab():
    """创建初次汉化标签页，返回输入输出组件和按钮"""
    lang_choices = [(v["name"], k) for k, v in LANGUAGES.items()]
    provider_choices = list(API_PROVIDERS.keys())
    game_choices = [(v["name"], k) for k, v in GAME_PROFILES.items()]
    mod_choices = scan_source_directory(SOURCE_DIR)

    with gr.Tab(t("translation_tab_title"), id=t("translation_tab_title_internal_id")):
        gr.Markdown(f"## {t('translation_tab_header')}")

        with gr.Row():
            mod_name = gr.Dropdown(
                mod_choices,
                label=t("mod_dropdown_label"),
                value=mod_choices[0] if mod_choices else None,
            )
            game_profile = gr.Dropdown(game_choices, label=t("game_dropdown_label"), value="1")

        with gr.Row():
            source_lang = gr.Dropdown(lang_choices, label=t("source_language_label"), value="1")
            target_langs = gr.CheckboxGroup(lang_choices, label=t("target_language_label"), value=["2"])

        with gr.Row():
            provider = gr.Dropdown(provider_choices, label=t("api_provider_label"), value=DEFAULT_API_PROVIDER)
            context = gr.Textbox(label=t("context_label"), lines=1)

        start_btn = gr.Button(t("start_translation_button"))
        log_output = gr.Textbox(label=t("log_output_label"), lines=15)

    inputs = [mod_name, game_profile, source_lang, target_langs, provider, context]
    outputs = log_output
    return inputs, outputs, start_btn
