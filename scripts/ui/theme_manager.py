"""
主题管理器模块
负责定义所有可用的Gradio主题，以便在控制面板中动态加载。
"""
import gradio as gr

def create_victoria_theme():
    """
    创建一个维多利亚风格的金红黑配色主题。
    主色黑，按钮黑，金色镶边。
    """
    theme = gr.themes.Monochrome(
        primary_hue=gr.themes.colors.amber,
        secondary_hue=gr.themes.colors.red,
        neutral_hue=gr.themes.colors.slate,
        font=(gr.themes.GoogleFont("Cinzel"), "serif")
    ).set(
        # --- 全局 ---
        body_background_fill="*neutral_950",
        body_background_fill_dark="*neutral_950",
        body_text_color="*neutral_200",

        # --- 块与容器 ---
        block_background_fill="*neutral_900",
        block_background_fill_dark="*neutral_900",
        block_border_width="2px",
        block_border_color="*primary_500",
        block_radius="*radius_sm",
        
        # --- 按钮 ---
        # 使用指定的颜色方案
        button_primary_background_fill="#ED2939",  # Primary 按钮背景色
        button_primary_background_fill_dark="#ED2939",
        button_primary_background_fill_hover="#D41E2F",  # 悬停时颜色变深
        button_primary_background_fill_hover_dark="#D41E2F",
        button_primary_text_color="#FFCC00",  # Primary 按钮文字颜色
        button_primary_border_color="#C41E3A",

        button_secondary_background_fill="#B76E79",  # Secondary 按钮背景色
        button_secondary_background_fill_dark="#B76E79",
        button_secondary_background_fill_hover="#A55A6B",  # 悬停时颜色变深
        button_secondary_background_fill_hover_dark="#A55A6B",
        button_secondary_text_color="#FFCC00",  # Secondary 按钮文字颜色
        
        # --- 输入框 ---
        input_background_fill="*neutral_800",
        input_border_color="*neutral_700",
    )
    return theme

def create_remis_theme():
    """
    创建一个Project Remis风格的紫/靛蓝色现代主题。
    """
    theme = gr.themes.Soft(
        primary_hue=gr.themes.colors.purple,
        secondary_hue=gr.themes.colors.indigo,
        neutral_hue=gr.themes.colors.slate,
        font=(gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"),
    ).set(
        body_background_fill="*neutral_950",
        body_background_fill_dark="*neutral_950",
        block_background_fill="*neutral_900",
        block_background_fill_dark="*neutral_900",
        block_radius="*radius_lg",
        block_shadow="*shadow_drop_lg",
        button_primary_background_fill="*primary_600",
        button_primary_background_fill_dark="*primary_600",
        button_primary_background_fill_hover="*primary_500",
        button_primary_background_fill_hover_dark="*primary_500",
        button_primary_text_color="white",
        input_background_fill="*neutral_800",
        input_border_color="*neutral_700",
        input_shadow="*shadow_inset",
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