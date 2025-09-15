"""
主题管理器模块
负责定义所有可用的Gradio主题，以便在控制面板中动态加载。
"""
import gradio as gr

def create_victoria_theme():
    """
    创建一个贴近 Victoria 3 游戏风格的华丽主题。
    主色调为深墨绿，强调色为暗金色，按钮使用深墨绿和酒红色。
    """
    theme = gr.themes.Soft( # Soft 主题在圆角和间距上更贴近游戏UI
        primary_hue=gr.themes.colors.amber,  # 用于生成金色系（强调色）
        secondary_hue=gr.themes.colors.red,   # 用于生成红色系（次强调色，酒红）
        neutral_hue=gr.themes.colors.teal,    # 核心中性色调，我们用深墨绿/青色
        font=(gr.themes.GoogleFont("Cinzel"), "serif") # 华丽的衬线字体
    ).set(
        # --- 全局背景与文字 ---
        # 整个页面最底层的深色背景，模仿游戏中的暗色调和纹理
        body_background_fill="#1A2B2F", # 一个非常深的墨绿色/青色
        body_background_fill_dark="#1A2B2F",
        body_text_color="#E0DDCF",     # 偏米白或淡金色的文字，确保在深色背景上清晰
        body_text_color_dark="#E0DDCF",

        # --- 块与容器 (Block/Panel) ---
        # 模仿游戏中的UI面板，背景比body稍浅，有金色边框
        block_background_fill="#2A3B3F", # 稍亮一点的深墨绿色
        block_background_fill_dark="#2A3B3F",
        block_border_width="1.5px",        # 稍细的边框
        block_border_color="*primary_700", # 使用琥珀色板中较深的金色作为边框色
        block_radius="*radius_md",         # 中等圆角，可以模拟一些弧度
        block_shadow="*shadow_lg",         # 较深的阴影，增加立体感

        # --- 按钮 ---
        # 模仿游戏中的按钮样式：深绿色背景，金色文字，金色边框
        button_primary_background_fill="#2A3B3F",       # 主要按钮背景色（与block背景一致）
        button_primary_background_fill_dark="#2A3B3F",
        button_primary_background_fill_hover="#3F5257", # 悬停时稍亮一点的墨绿
        button_primary_background_fill_hover_dark="#3F5257",
        button_primary_text_color="#FFD700",             # 纯金色文字
        button_primary_border_color="#B8860B",          # 暗金色边框

        # 次要按钮可以参考 Image 2 的酒红色标题背景
        button_secondary_background_fill="#6C2E3C",       # 较深的酒红色/勃艮第红
        button_secondary_background_fill_dark="#6C2E3C",
        button_secondary_background_fill_hover="#8A3E4F", # 悬停时稍亮的酒红
        button_secondary_background_fill_hover_dark="#8A3E4F",
        button_secondary_text_color="#FFD700",            # 金色文字

         # --- 输入框 ---
         # 输入框背景可以稍浅，便于用户区分和输入
         input_background_fill="#3B4C50", # 比block背景更浅一些的墨绿
         input_background_fill_dark="#3B4C50",
         input_border_color="*primary_700", # 输入框边框也可以用金色

        # --- 其他可能需要调整的元素 (可以根据需要解注释) ---
        # header_background_fill="#2A3B3F", # 头部背景色，如果你的UI有header
        # header_text_color="#FFD700",
        # link_text_color="*primary_500", # 链接颜色
    )
    return theme


def create_remis_theme():
    """
    创建一个拜占庭风格的 Gradio 主题（纯 Theme 系统实现）。
    
    核心元素:
    - 主色调: 拜占庭紫 (Tyrian Purple)
    - 强调色: 金色/琥珀色 (Gold/Amber)
    - 背景/中性色: 象牙白/石头色 (Ivory/Stone)
    """
    
    # 使用 Soft 主题作为基础，它有柔和的圆角和间距
    theme = gr.themes.Soft(
        primary_hue=gr.themes.colors.purple,  # 将紫色系作为主色调的基础
        secondary_hue=gr.themes.colors.amber, # 将琥珀/金色系作为次色调
        neutral_hue=gr.themes.colors.stone,   # 石头色系作为中性色，比纯灰更暖
        font=(gr.themes.GoogleFont("Cinzel"), "serif") # 保持古典华丽的字体
    ).set(
        # --- 全局：温暖的象牙白背景与深棕色文字 ---
        body_background_fill="#F5F1E9",  # 一个温暖、偏灰的象牙白，有石头/壁画质感
        body_background_fill_dark="#2A2430", # 暗模式下的深紫色背景
        body_text_color="#4A403A",        # 深棕色文字，比纯黑更柔和、复古
        body_text_color_dark="#F5F1E9",   # 暗模式下使用象牙白文字

        # --- 块与容器： subtle a separation ---
        block_background_fill="#FFFFFF",     # 容器用纯白背景，与象牙白背景形成微妙的层次
        block_background_fill_dark="#3C3547",
        block_border_width="1px",
        block_border_color="*neutral_200",   # 用非常浅的灰色作为边框
        block_border_color_dark="*neutral_700",
        block_radius="*radius_md",

        # --- 按钮：核心配色方案 ---
        # 主要按钮: 拜占庭紫底 + 象牙白文字 + 金色悬停效果
        button_primary_background_fill="#B8860B",        # 标志性的拜占庭紫
        button_primary_background_fill_dark="#B8860B",
        button_primary_text_color="#FFFFFF",             # 纯白/象牙白文字以保证清晰度
        button_primary_background_fill_hover="*primary_500", # 悬停时变为色板里更亮的紫色
        button_primary_background_fill_hover_dark="*primary_500",
        button_primary_border_color_dark="*primary_500",

        # 次要按钮: 柔和的金色底 + 深棕色文字
        button_secondary_background_fill="#C49102", # 一个更偏向青铜质感的暗金色
        button_secondary_background_fill_dark="#C49102",
        button_secondary_text_color="#FFFFFF",           # 使用与正文一致的深棕色文字
        button_secondary_background_fill_hover="#D1A42C", # 悬停时金色加深
        button_secondary_background_fill_hover_dark="#D1A42C",

        # --- 输入框与交互元素 ---
        input_background_fill="#FFFFFF",
        input_background_fill_dark="#5C5566",
        input_border_color="*neutral_300",
        input_shadow_focus="*primary_300", # 输入框聚焦时显示柔和的紫色光晕
        slider_color="*primary_500",      # 滑块等元素的颜色也使用紫色系
        slider_color_dark="*primary_500",
        # ... 在 .set() 方法内部，可以放在按钮设置的后面 ...

        # 统一其他交互元素的选中颜色
        #checkbox_background_color_selected="#C49102",
        #checkbox_background_color_selected_dark="#C49102",
        #checkbox_label_background_fill_selected="#C49102",
        #checkbox_label_background_fill_selected_dark="#C49102",
    )
    return theme

# --- 主题注册表 ---

AVAILABLE_THEMES = {
    "Project Remis": create_remis_theme,
    "Victoria": create_victoria_theme,
    "Soft": gr.themes.Soft,
    "Monochrome": gr.themes.Monochrome,
    "Glass": gr.themes.Glass,
}