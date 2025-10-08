import json
import os
from datetime import datetime
from typing import List
import logging
from scripts.utils import i18n

# 使用标准日志记录器
logger = logging.getLogger(__name__)

def _save_debug_file(response_text: str, error_type: str, details: str):
    """保存调试文件到 logs 目录"""
    try:
        # 确保 logs 目录存在
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        debug_file = os.path.join(log_dir, f"debug_parse_failure_{timestamp}.txt")

        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(i18n.t("debug_file_header") + "\n")
            f.write(i18n.t("debug_file_time", time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + "\n")
            f.write(i18n.t("debug_file_error_type", error_type=error_type) + "\n")
            f.write(i18n.t("debug_file_details", details=details) + "\n")
            f.write("=" * 80 + "\n")
            f.write(i18n.t("debug_file_raw_response") + "\n")
            f.write("-" * 40 + "\n")
            f.write(response_text)
            f.write("\n" + "=" * 80 + "\n")

        logger.info(i18n.t("debug_file_saved", debug_file=debug_file))
        logger.info(i18n.t("debug_file_prompt"))
    except Exception as e:
        logger.error(i18n.t("debug_file_save_failed", e=e))

def parse_json_response(response_text: str, expected_count: int) -> List[str]:
    """
    解析大语言模型返回的、可能包含Markdown代码块的JSON数组字符串。

    Args:
        response_text: 模型返回的原始文本。
        expected_count: 期望得到的翻译结果数量。

    Returns:
        一个包含翻译结果的字符串列表。解析失败时，会根据expected_count返回一个包含空字符串的列表以防止下游崩溃。
    """
    try:
        # 优先处理模型可能返回的Markdown格式 (```json ... ```)
        # 使用 removeprefix 和 removesuffix 提高健遶性
        clean_text = response_text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text.removeprefix("```json").strip()
        if clean_text.startswith("```"):
            clean_text = clean_text.removeprefix("```").strip()
        if clean_text.endswith("```"):
            clean_text = clean_text.removesuffix("```").strip()

        parsed_data = json.loads(clean_text)

        translations = None
        if isinstance(parsed_data, list):
            translations = parsed_data
        elif isinstance(parsed_data, dict) and 'response' in parsed_data:
            logger.info(i18n.t("unpacking_wrapped_response"))
            nested_text = parsed_data['response']

            nested_clean_text = nested_text.strip()
            if nested_clean_text.startswith("```json"):
                nested_clean_text = nested_clean_text.removeprefix("```json").strip()
            if nested_clean_text.startswith("```"):
                nested_clean_text = nested_clean_text.removeprefix("```").strip()
            if nested_clean_text.endswith("```"):
                nested_clean_text = nested_clean_text.removesuffix("```").strip()

            try:
                nested_data = json.loads(nested_clean_text)
                if isinstance(nested_data, list):
                    translations = nested_data
                else:
                    logger.warning(i18n.t("parser_unpack_json_not_list_warning", nested_data=nested_data))
                    _save_debug_file(response_text, "Unpack Error", f"Unpacked content is not a list: {nested_data}")
                    return [""] * expected_count
            except json.JSONDecodeError as e:
                # 拆包失败也记录
                logger.error(i18n.t("parser_unpack_json_decode_error", nested_text=nested_text))
                _save_debug_file(response_text, "Nested JSON Decode Error", str(e))
                return [""] * expected_count
        else:
            logger.warning(i18n.t("parser_json_not_list_warning", parsed_data=parsed_data))
            _save_debug_file(response_text, "Format Error", f"Expected a list, but got a dict: {parsed_data}")
            return []

        if translations is None:
             # 这是一个不应该发生的情况，但作为保险
            logger.error(i18n.t("parser_unknown_logic_error"))
            _save_debug_file(response_text, "Logic Error", "Translations variable was not assigned.")
            return [""] * expected_count

        if len(translations) != expected_count:
            # 记录数量不匹配的警告
            logger.warning(i18n.t("parser_translation_count_mismatch", expected_count=expected_count, actual_count=len(translations)))
            # 用空字符串填充缺失的部分
            while len(translations) < expected_count:
                translations.append("")
            return translations[:expected_count]

        return [str(item) for item in translations]
    except json.JSONDecodeError as e:
        # 记录详细的解析失败日志，这对调试至关重要
        logger.error(i18n.t("parser_json_decode_error", response_text=response_text))
        _save_debug_file(response_text, "JSON Decode Error", str(e))
        return [""] * expected_count
    except Exception as e:
        # 捕获其他潜在异常
        logger.error(i18n.t("parser_unknown_error", e=e))
        _save_debug_file(response_text, "Unknown Parse Error", str(e))
        return [""] * expected_count
