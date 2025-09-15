"""控制面板标签页模块"""
import gradio as gr
from scripts.utils.i18n import t

# 导入新的主题管理器
from scripts.ui.theme_manager import AVAILABLE_THEMES

def create_control_tab(current_lang: str, current_theme: str):
    """创建控制面板标签页，提供语言与主题切换以及重载按钮"""
    # 從主題管理器獲取所有可用的主題名稱
    theme_choices = list(AVAILABLE_THEMES.keys())
    # 確保當前主題在選項中，如果不在就用第一個作為預設
    if current_theme not in theme_choices:
        current_theme = theme_choices[0]

    with gr.Tab(t("control_tab_title"), id=t("control_tab_title_internal_id")):
        gr.Markdown(f"## {t('control_tab_header')}")
        
        with gr.Row():
            # 语言选择下拉框
            lang_dd = gr.Dropdown(
                choices=[(t("language_option_zh"), "zh_CN"), (t("language_option_en"), "en_US")],
                value=current_lang,
                label=t("language_dropdown_label"),
                container=False,  # 讓組件更緊湊
            )
            # 主题选择下拉框
            theme_dd = gr.Dropdown(
                choices=theme_choices,
                value=current_theme,
                label=t("theme_dropdown_label"),
                container=False,  # 讓組件更緊湊
            )

        with gr.Row():
            apply_btn = gr.Button(t("apply_settings_button"), variant="primary")
            reload_btn = gr.Button(t("reload_ui_button"))
            
    return lang_dd, theme_dd, apply_btn, reload_btn