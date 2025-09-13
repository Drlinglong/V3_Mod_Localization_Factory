"""词典管理标签页模块"""
import gradio as gr
from scripts.utils.i18n import t


def create_glossary_tab():
    """创建词典管理标签页"""
    with gr.Tab(t("glossary_tab_title"), id=t("glossary_tab_title_internal_id")):
        gr.Markdown(t("feature_in_development"))
