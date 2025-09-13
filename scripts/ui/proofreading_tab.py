"""文件校对标签页模块"""
import gradio as gr
from scripts.utils.i18n import t


def create_proofreading_tab():
    """创建文件校对标签页"""
    with gr.Tab(t("proofreading_tab_title"), id=t("proofreading_tab_title_internal_id")):
        gr.Markdown(t("feature_in_development"))
