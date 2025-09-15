"""其他工具标签页模块"""
import gradio as gr
from scripts.utils.i18n import t


def create_tools_tab():
    """创建其他工具标签页"""
    with gr.Tab(t("tools_tab_title"), id=t("tools_tab_title_internal_id")):
        gr.Markdown(t("feature_in_development"))
