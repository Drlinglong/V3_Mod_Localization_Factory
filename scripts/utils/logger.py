# scripts/utils/logger.py
import os
import sys
import logging
import platform
from logging.handlers import RotatingFileHandler

def setup_logger():
    """
    Configures the global root logger for the entire project.
    Implements smart path resolution (AppData vs Dev) and log rotation.
    """
    # 1. 智能路径解析 (Smart Path Resolution)
    if getattr(sys, 'frozen', False):
        # 打包环境 (Frozen/Production)
        if platform.system() == "Windows":
            base = os.getenv('APPDATA')
        else:
            # Linux/Mac fallback (though we are Windows focused)
            base = os.path.expanduser("~/.local/share")
        
        # Fallback if APPDATA is missing
        if not base:
            base = os.path.expanduser("~")
            
        logs_dir = os.path.join(base, "RemisModFactory", "logs")
    else:
        # 开发环境 (Development)
        # Assuming script is in scripts/utils/logger.py, project root is ../../
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
        logs_dir = os.path.join(project_root, "logs")
    
    os.makedirs(logs_dir, exist_ok=True)
    print(f"[LOGGER] Writing logs to: {logs_dir}")

    # 2. 飞行记录仪模式 (Rotating File Handler)
    log_filename = os.path.join(logs_dir, "remis_backend.log")

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 清除旧 Handlers 避免重复
    if logger.hasHandlers():
        logger.handlers.clear()

    # File Handler (Rotating)
    try:
        file_handler = RotatingFileHandler(
            filename=log_filename,
            mode='a',
            maxBytes=5*1024*1024,  # 5MB 单个文件限制
            backupCount=5,         # 保留最近 5 个备份
            encoding='utf-8',
            delay=0
        )
        
        # 3. 增强型格式 (Rich Formatting)
        # 显示文件名和行号，方便定位
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"[LOGGER] Failed to setup file handler: {e}")

    # Console Handler (保留控制台输出，用于黑框调试)
    stream_handler = logging.StreamHandler()
    # Console output can be simpler
    stream_formatter = logging.Formatter('%(levelname)s: %(message)s')
    stream_handler.setFormatter(stream_formatter)
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)

    logging.info(f"Logger initialized. Writing to: {logs_dir}")
    
    # Try to log i18n message if available
    try:
        from scripts.utils import i18n
        if getattr(i18n, '_language_loaded', False):
            logging.info(i18n.t("logger_initialized"))
    except ImportError:
        pass