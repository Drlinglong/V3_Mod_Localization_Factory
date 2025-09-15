"""主页标签页模块"""
import gradio as gr
from scripts.utils.i18n import t


def create_home_tab():
    """创建主页标签页，返回主页按钮"""
    with gr.Tab(t("home_tab_title"), id=t("home_tab_title_internal_id")):
        gr.Markdown(f"## {t('app_welcome_header')}")
        home_btn = gr.Button(t("start_translation_button"))
    return home_btn
