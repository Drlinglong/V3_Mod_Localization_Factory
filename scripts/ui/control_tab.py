"""控制面板标签页模块"""
import gradio as gr
from scripts.utils.i18n import t


def create_control_tab(current_lang: str):
    """创建控制面板标签页，提供语言切换和重载按钮"""
    with gr.Tab(t("control_tab_title"), id=t("control_tab_title_internal_id")):
        gr.Markdown(f"## {t('control_tab_header')}")
        lang_dd = gr.Dropdown(
            [(t("language_option_zh"), "zh_CN"), (t("language_option_en"), "en_US")],
            value=current_lang,
            label=t("language_dropdown_label"),
        )
        apply_btn = gr.Button(t("apply_settings_button"))
        reload_btn = gr.Button(t("reload_ui_button"))
    return lang_dd, apply_btn, reload_btn
