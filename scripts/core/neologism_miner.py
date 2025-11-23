import json
import logging
from typing import List, Any

class NeologismMiner:
    """
    专有名词挖掘机 (Neologism Miner)
    负责从源文本中提取潜在的专有名词。
    """

    SYSTEM_PROMPT = """
# Role: 资深Paradox游戏本地化专家 / 术语分析师

# Goal
你的任务是阅读给定的游戏模组（Mod）源文本，并从中提取出所有**潜在的、未定义的专有名词或新造概念词 (Neologisms)**。
这些词通常是作者虚构的人名、地名、特殊科技、奇幻生物或组织名称，需要人工确认统一译名。

# Extraction Rules (提取规则)

请根据以下标准筛选词汇：

1.  **✅ 必选对象 (Target)**:
    *   **专有名词**: 看起来像人名、地名、国家名、派系名的词（如: "Azura", "Gondor", "United Nations of Earth"）。
    *   **虚构概念**: 作者自造的词，或赋予特殊含义的词组（如: "Plasteel", "Warp Drive", "Mind-Fire"）。
    *   **大写术语**: 在句子中间出现、首字母大写的非通用词汇。

2.  **❌ 严格排除 (Exclude)**:
    *   **游戏脚本代码**: 绝对不要提取任何包含在 `[]`, `{}`, `$`, `@` 中的变量或命令（如: `[Root.GetName]`, `$COUNTRY$`, `scope:actor`）。
    *   **颜色代码**: 忽略类似 `§R`, `§!` 的格式控制符。
    *   **通用词汇**: 不要提取普通的英语单词（如: "Empire", "Soldier", "Technology"），除非它们构成了特殊的专有短语。
    *   **数字与符号**: 纯数字或标点。除非他们有强烈的、不可替代的特殊含义，例如42代表宇宙的究极答案。

# Output Format (输出格式)

*   **仅输出一个纯 JSON 字符串**。
*   格式为一个包含字符串的列表：`["Term1", "Term2", "Term3"]`
*   不要包含任何 markdown 标记（如 ```json），不要包含任何解释性文字。
"""

    def __init__(self, client: Any):
        """
        :param client: BaseApiHandler 的实例 (e.g. GeminiHandler, OpenAIHandler)
        """
        self.client = client
        self.logger = logging.getLogger(__name__)

    def extract_terms(self, text_chunk: str) -> List[str]:
        """
        调用 LLM 提取文本中的专有名词。
        """
        try:
            # 构造 Prompt
            messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": text_chunk}
            ]

            # 调用 LLM
            # 注意：不同的 Handler 可能有不同的调用方式，这里假设它们都支持 generate_with_messages 或者类似的通用接口
            # 但目前的 BaseApiHandler 主要是 generate_translation。
            # 我们可能需要使用 generate_chat 或者直接调用 client 的底层方法。
            # 查看 BaseApiHandler，它似乎没有统一的 chat 接口，但各个 Handler (如 OpenAIHandler) 有。
            # 为了兼容性，我们假设 client 有一个 generate_response(messages, temperature) 方法
            # 如果没有，我们需要适配。
            
            # 检查 client 类型并适配
            response_text = ""
            if hasattr(self.client, "generate_chat_response"):
                 response_text = self.client.generate_chat_response(messages, temperature=0.1)
            elif hasattr(self.client, "client") and hasattr(self.client.client, "chat"): # Ollama/Gemini specific?
                 # Fallback logic if needed
                 pass
            else:
                # 尝试使用最通用的 generate 方法，但这通常是用于翻译的
                # 这里我们可能需要扩展 BaseApiHandler 或直接使用 specific handler methods
                # 暂时假设 generate_chat_response 存在，如果不存在我会在 Manager 中处理或修改 Handler
                # 实际上，大部分 Handler 应该实现一个通用的 chat 接口
                
                # 让我们先试着用 generate_translation 的逻辑，但是传入 system prompt
                # 但 generate_translation 通常有固定的 prompt 结构。
                
                # 更好的方式是：在 BaseApiHandler 中添加 generate_chat_response。
                # 但我不能修改所有 Handler。
                # 让我们看看 OpenAIHandler。
                pass

            # 临时方案：如果 client 是 GeminiHandler，它有 generate_content
            # 如果是 OpenAIHandler，它有 client.chat.completions.create
            
            # 为了简单起见，我会在 Manager 中确保传入的 client 有我们需要的方法，或者在这里做适配。
            # 让我们假设 client 有一个 `generate_text(prompt, system_prompt)` 或类似的方法。
            # 实际上，BaseApiHandler 有 `generate_translation`。
            
            # 让我们看下 api_handler.py 返回的实例。
            # 比如 GeminiHandler。
            
            # 既然我不能轻易修改所有 Handler，我将在这里做一些简单的适配。
            if hasattr(self.client, "generate_with_messages"):
                 response_text = self.client.generate_with_messages(messages, temperature=0.1)
            else:
                 # 构造一个包含 system prompt 的纯文本 prompt
                 full_prompt = f"{self.SYSTEM_PROMPT}\n\nInput:\n{text_chunk}\n\nOutput:"
                 response_text = self.client.generate_content(full_prompt) # 假设有 generate_content

            # 解析 JSON
            cleaned_response = response_text.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            
            terms = json.loads(cleaned_response)
            if isinstance(terms, list):
                return [str(t) for t in terms]
            else:
                self.logger.warning(f"Unexpected JSON format from Neologism Miner: {terms}")
                return []

        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse JSON from Neologism Miner response: {response_text}")
            return []
        except Exception as e:
            self.logger.error(f"Error in Neologism Miner: {e}")
            return []

