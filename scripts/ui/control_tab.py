"""控制面板标签页模块"""
import gradio as gr
from scripts.utils.i18n import t


def create_control_tab(current_lang: str, current_theme: str):
    """创建控制面板标签页，提供语言与主题切换以及重载按钮"""
    with gr.Tab(t("control_tab_title"), id=t("control_tab_title_internal_id")):
        gr.Markdown(f"## {t('control_tab_header')}")
        # 语言选择下拉框
        lang_dd = gr.Dropdown(
            [(t("language_option_zh"), "zh_CN"), (t("language_option_en"), "en_US")],
            value=current_lang,
            label=t("language_dropdown_label"),
        )
        # 主题选择下拉框
        theme_dd = gr.Dropdown(
            [
                (t("theme_option_soft"), "Soft"),
                (t("theme_option_monochrome"), "Monochrome"),
                (t("theme_option_glass"), "Glass"),
            ],
            value=current_theme,
            label=t("theme_dropdown_label"),
        )
        apply_btn = gr.Button(t("apply_settings_button"))
        reload_btn = gr.Button(t("reload_ui_button"))
    return lang_dd, theme_dd, apply_btn, reload_btn
