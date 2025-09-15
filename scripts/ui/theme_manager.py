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
    创建一个专门为暗色模式优化的拜占庭风格主题。
    
    核心元素:
    - 背景: 深邃、低饱和度的紫色，而非纯黑。
    - 文字: 温暖的象牙白，而非刺眼的纯白。
    - 交互: 标志性的拜占庭紫与赭石金按钮。
    """
    
    # 我们可以直接在 Soft 主题上构建，然后用 .set() 全盘覆盖
    theme = gr.themes.Soft(
        primary_hue=gr.themes.colors.purple,
        secondary_hue=gr.themes.colors.amber,
        neutral_hue=gr.themes.colors.stone,
        font=(gr.themes.GoogleFont("Cinzel"), "serif")
    ).set(
        # --- 为了确保主题在任何情况下都显示为暗色，我们同时设置亮色和暗色参数 ---

        # --- 全局：深紫背景与象牙白文字 ---
        body_background_fill="#2A2430",             # 深邃、略带温暖的紫色作为基底
        body_background_fill_dark="#2A2430",
        body_text_color="#F5F1E9",                  # 温暖的象牙白文字，护眼且有质感
        body_text_color_dark="#F5F1E9",

        # --- 块与容器：创造层次感 ---
        block_background_fill="#3C3547",            # 比背景稍亮一些的紫色，用于容器
        block_background_fill_dark="#3C3547",
        block_border_width="1px",
        block_border_color="*primary_800",           # 用非常深的紫色作为边框， subtle
        block_border_color_dark="*primary_800",
        block_radius="*radius_md",

        # --- 按钮：在暗色中成为焦点 ---
        # 主要按钮: 使用标志性的、更亮的拜占庭紫
        button_primary_background_fill="#66023C",
        button_primary_background_fill_dark="#66023C",
        button_primary_text_color="#FFFFFF",
        button_primary_background_fill_hover="*primary_500",
        button_primary_background_fill_hover_dark="*primary_500",

        # 次要按钮: 使用我们之前选定的赭石金
        button_secondary_background_fill="#C49102",
        button_secondary_background_fill_dark="#C49102",
        button_secondary_text_color="#2A2430",       # 文字使用背景的深紫色，对比鲜明
        button_secondary_background_fill_hover="#D1A42C",
        button_secondary_background_fill_hover_dark="#D1A42C",

        # --- 输入框与其他交互元素 ---
        input_background_fill="#332D40",            # 比容器背景更深一些，以示区分
        input_background_fill_dark="#332D40",
        input_border_color="*neutral_700",
        input_border_color_dark="*neutral_700",
        input_shadow_focus="*primary_500",           # 聚焦时光晕效果不变
        
        # 修正单选框和复选框的颜色
        checkbox_background_color_selected="#C49102",
        checkbox_background_color_selected_dark="#C49102",
        checkbox_label_background_fill_selected="#C49102",
        checkbox_label_background_fill_selected_dark="#C49102",
        checkbox_label_text_color_selected="#2A2430",
        checkbox_label_text_color_selected_dark="#2A2430",
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