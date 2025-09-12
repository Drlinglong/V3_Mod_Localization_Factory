"""基于Gradio的最小化Web界面，用于启动翻译流程。"""
import socket

import gradio as gr

from scripts.workflows import initial_translate
from scripts.config import (
    LANGUAGES,
    GAME_PROFILES,
    API_PROVIDERS,
    DEFAULT_API_PROVIDER,
)

# 准备下拉菜单的数据
LANG_CHOICES = [(v["name"], k) for k, v in LANGUAGES.items()]
PROVIDER_CHOICES = list(API_PROVIDERS.keys())
GAME_CHOICES = [(v["name"], k) for k, v in GAME_PROFILES.items()]


def find_available_port(start: int = 1453) -> int:
    """从指定端口开始寻找可用端口。"""
    port = start
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", port))
                return port
            except OSError:
                port += 1


def start_translation(mod_name: str,
                      game_key: str,
                      source_key: str,
                      target_keys: list[str],
                      provider: str,
                      context: str):
    """启动翻译流程并实时返回日志。"""
    if not mod_name:
        yield "❌ 未提供模组名称"
        return

    source_lang = LANGUAGES.get(source_key)
    target_langs = [LANGUAGES[k] for k in target_keys]
    game_profile = GAME_PROFILES.get(game_key)

    log_text = ""
    for msg in initial_translate.run(mod_name, source_lang, target_langs,
                                     game_profile, context, provider):
        log_text += f"{msg}\n"
        yield log_text


with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("## 🔤 本地化工作台 - 初次翻译")

    with gr.Row():
        mod_name = gr.Textbox(label="模组文件夹名")
        game_profile = gr.Dropdown(GAME_CHOICES, label="游戏档案", value="1")

    with gr.Row():
        source_lang = gr.Dropdown(LANG_CHOICES, label="源语言", value="1")
        target_langs = gr.CheckboxGroup(LANG_CHOICES, label="目标语言", value=["2"])

    with gr.Row():
        provider = gr.Dropdown(PROVIDER_CHOICES, label="API供应商", value=DEFAULT_API_PROVIDER)
        context = gr.Textbox(label="模组上下文", lines=1)

    start_btn = gr.Button("开始翻译")
    log_output = gr.Textbox(label="日志输出", lines=15)

    start_btn.click(
        start_translation,
        inputs=[mod_name, game_profile, source_lang, target_langs, provider, context],
        outputs=log_output,
    )


if __name__ == "__main__":
    port = find_available_port()
    print(f"🌐 WebUI将在端口 {port} 启动")
    demo.queue().launch(server_port=port, inbrowser=True)

