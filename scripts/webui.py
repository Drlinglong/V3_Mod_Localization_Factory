"""基于Gradio的模块化Web界面，用于启动翻译流程。"""
import os
import sys
import socket
import importlib
import time

# 保证项目根目录在路径中，避免导入失败
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import gradio as gr
from scripts.utils import i18n
from scripts.utils.ui_config import load_ui_config, save_ui_config
from scripts.utils.state_manager import StateManager

from scripts.workflows import initial_translate
from scripts.config import (
    LANGUAGES,
    GAME_PROFILES,
)

# 导入各个UI模块
from scripts.ui import (
    home_tab,
    docs_tab,
    translation_tab,
    glossary_tab,
    proofreading_tab,
    project_tab,
    tools_tab,
    control_tab,
)

RELOADABLE_MODULES = [
    home_tab,
    docs_tab,
    translation_tab,
    glossary_tab,
    proofreading_tab,
    project_tab,
    tools_tab,
    control_tab,
]

state = StateManager()

# 预先加载配置中的语言
_config = load_ui_config()
i18n.load_language(_config.get("language"))

def find_available_port(start: int = 1453) -> int:
    """从指定端口开始寻找可用端口。"""
    port = start
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
        port += 1

def wait_for_port_release(port: int, retries: int = 10, interval: float = 0.5) -> int:
    """等待指定端口释放以便复用，超过重试次数则寻找新的可用端口。

    参数:
        port: 想要复用的端口号
        retries: 重试次数
        interval: 每次重试的间隔秒数
    返回:
        可用的端口号（优先返回原端口）
    """
    for _ in range(retries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
        time.sleep(interval)
    # 若原端口始终未释放，则寻找新的可用端口
    return find_available_port(port + 1)

def start_translation(mod_name: str,
                      game_key: str,
                      source_key: str,
                      target_keys: list[str],
                      provider: str,
                      context: str):
    """启动翻译流程并实时返回日志。"""
    if not mod_name:
        yield i18n.t("error_mod_not_provided")
        return

    source_lang = LANGUAGES.get(source_key)
    target_langs = [LANGUAGES[k] for k in target_keys]
    game_profile = GAME_PROFILES.get(game_key)

    log_text = ""
    for msg in initial_translate.run(mod_name, source_lang, target_langs,
                                     game_profile, context, provider):
        log_text += f"{msg}\n"
        yield log_text

def build_demo():
    """构建并返回Gradio界面"""
    for m in RELOADABLE_MODULES:
        importlib.reload(m)

    cfg = load_ui_config()
    i18n.load_language(cfg.get("language"))
    theme_name = cfg.get("theme", "Soft")
    # 根据配置动态选择主题类
    theme_cls = getattr(gr.themes, theme_name, gr.themes.Soft)

    with gr.Blocks(theme=theme_cls()) as demo:
        with gr.Tabs() as tabs:
            home_btn = home_tab.create_home_tab()
            docs_tab.create_docs_tab()
            trans_inputs, trans_outputs, trans_btn = translation_tab.create_translation_tab()
            glossary_tab.create_glossary_tab()
            proofreading_tab.create_proofreading_tab()
            project_tab.create_project_tab()
            tools_tab.create_tools_tab()
            lang_dd, theme_dd, apply_btn, reload_btn = control_tab.create_control_tab(
                cfg.get("language"), theme_name
            )

        # 主页按钮跳转到初次汉化标签
        home_btn.click(
            lambda: gr.Tabs.update(selected=i18n.t("translation_tab_title_internal_id")),
            None,
            tabs,
        )

        # 绑定初次汉化按钮的核心逻辑
        trans_btn.click(
            start_translation,
            inputs=trans_inputs,
            outputs=trans_outputs,
        )

        def _apply(lang, theme):
            """保存语言与主题并请求重载"""
            save_ui_config({"language": lang, "theme": theme})
            print("🔄 正在重载界面…")
            state.set_command("restart")
            demo.close()
            time.sleep(0.5)  # 等待端口彻底释放

        def _reload():
            """单纯重载UI"""
            print("🔄 正在重载界面…")
            state.set_command("restart")
            demo.close()
            time.sleep(0.5)  # 等待端口彻底释放

        # 先在后端保存设置，再在前端刷新页面，避免刷新过早导致配置未写入
        apply_btn.click(
            _apply,
            inputs=[lang_dd, theme_dd],
            outputs=None,
        ).then(None, None, None, js="window.location.reload()")

        # 单纯重载同样在回调完成后再刷新
        reload_btn.click(
            _reload,
            inputs=None,
            outputs=None,
        ).then(None, None, None, js="window.location.reload()")

    return demo

if __name__ == "__main__":
    port = 1453
    reloaded = False  # 标记是否刚完成重载
    while True:
        demo = build_demo()
        port = wait_for_port_release(port)
        if reloaded:
            # 重载完成后在CLI中提示
            print(i18n.t("ui_reload_success"))
            reloaded = False
        try:
            print(f"🌐 WebUI将在端口 {port} 启动")
            # prevent_thread_lock=True 使启动非阻塞，便于后续重载
            demo.queue().launch(server_port=port, inbrowser=True, prevent_thread_lock=True)
            demo.block_thread()  # 阻塞主线程，等待 demo.close()
        except OSError:
            print(f"⚠️ 端口 {port} 已被占用，尝试下一个端口...")
            port += 1
            continue
        if state.get_command() == "restart":
            reloaded = True
            state.clear()
            time.sleep(0.5)  # 再次等待端口释放，确保下次能复用
            continue
        break
