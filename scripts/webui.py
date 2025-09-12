"""简单的Gradio Web界面示例。"""
import gradio as gr

# 创建一个最小的页面，验证Gradio是否工作
with gr.Blocks() as demo:
    gr.Markdown("Hello World")

if __name__ == "__main__":
    # 启动本地Web服务器
    demo.launch()
