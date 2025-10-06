import json
from typing import List
import logging

# 使用标准日志记录器
logger = logging.getLogger(__name__)

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
        # 使用 removeprefix 和 removesuffix 提高健壮性
        clean_text = response_text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text.removeprefix("```json").strip()
        if clean_text.startswith("```"):
            clean_text = clean_text.removeprefix("```").strip()
        if clean_text.endswith("```"):
            clean_text = clean_text.removesuffix("```").strip()

        parsed_data = json.loads(clean_text)

        if isinstance(parsed_data, list):
            translations = parsed_data
        elif isinstance(parsed_data, dict) and 'response' in parsed_data:
            logger.info("检测到被包裹的响应，正在尝试拆包...")
            nested_text = parsed_data['response']

            nested_clean_text = nested_text.strip()
            if nested_clean_text.startswith("```json"):
                nested_clean_text = nested_clean_text.removeprefix("```json").strip()
            if nested_clean_text.startswith("```"):
                nested_clean_text = nested_clean_text.removeprefix("```").strip()
            if nested_clean_text.endswith("```"):
                nested_clean_text = nested_clean_text.removesuffix("```").strip()

            nested_data = json.loads(nested_clean_text)

            if isinstance(nested_data, list):
                translations = nested_data
            else:
                logger.warning(f"警告：拆包后，模型返回的JSON不是一个列表。内容: {nested_data}")
                return [""] * expected_count
        else:
            logger.warning(f"警告：模型返回的JSON不是一个列表。内容: {parsed_data}")
            return [""] * expected_count


        if len(translations) != expected_count:
            # 记录数量不匹配的警告
            logger.warning(f"警告：翻译数量不匹配。期望 {expected_count}，得到 {len(translations)}")
            # 用空字符串填充缺失的部分
            while len(translations) < expected_count:
                translations.append("")
            return translations[:expected_count]

        return [str(item) for item in translations]
    except json.JSONDecodeError:
        # 记录详细的解析失败日志，这对调试至关重要
        logger.error(f"错误：JSON解析失败。原始返回文本:\n-----\n{response_text}\n-----")
        return [""] * expected_count
    except Exception as e:
        # 捕获其他潜在异常
        logger.error(f"错误：解析响应时发生未知错误: {e}")
        return [""] * expected_count
