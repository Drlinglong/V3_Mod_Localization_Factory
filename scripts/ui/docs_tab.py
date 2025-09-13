"""文档标签页模块"""
import gradio as gr
from scripts.utils.i18n import t


def create_docs_tab():
    """创建文档标签页"""
    with gr.Tab(t("docs_tab_title"), id=t("docs_tab_title_internal_id")):
        gr.Markdown(t("docs_tab_markdown"))
