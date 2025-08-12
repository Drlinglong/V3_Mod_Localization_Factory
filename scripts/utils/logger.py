# scripts/utils/logger.py
import os
import logging
from datetime import datetime

def setup_logger():
    """
    Configures the global root logger for the entire project.
    """
    logs_dir = 'logs'
    os.makedirs(logs_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = os.path.join(logs_dir, f"translation_{timestamp}.log")

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if logger.hasHandlers():
        logger.handlers.clear()

    # --- 文件处理器的配置 (无变化) ---
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # --- 终端处理器的配置 ---
    stream_handler = logging.StreamHandler()
    stream_formatter = logging.Formatter('%(message)s')
    stream_handler.setFormatter(stream_formatter)
    
    # 【核心修正】明确告诉“终端播报员”，你也必须处理INFO级别的信息
    stream_handler.setLevel(logging.INFO)
    
    logger.addHandler(stream_handler)

    logging.info("Logger initialized and ready.")