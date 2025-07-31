# scripts/main.py

# 在所有其他模块之前，首先初始化i18n
from utils import i18n
i18n.load_language()

# 然后再导入其他模块
from workflows import initial_translate
from core import directory_handler

def main_menu():
    # 打印欢迎信息
    # 注意我们现在如何使用 i18n.t() 来获取文本
    
    # 1. 让用户选择一个Mod
    selected_mod = directory_handler.select_mod_directory()
    
    # 2. 如果用户成功选择了，就启动首次翻译工作流
    if selected_mod:
        initial_translate.run(selected_mod)

if __name__ == '__main__':
    main_menu()