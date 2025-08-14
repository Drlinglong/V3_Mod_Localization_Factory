# scripts/core/glossary_manager.py
import os
import json
import logging
import re
from typing import Dict, List, Set, Optional, Tuple
from scripts.config import PROJECT_ROOT


class GlossaryManager:
    """游戏专用词典管理器"""
    
    def __init__(self):
        self.glossaries: Dict[str, Dict] = {}
        self.current_game_glossary: Optional[Dict] = None
        self.current_game_id: Optional[str] = None
        
    def load_game_glossary(self, game_id: str) -> bool:
        """
        加载指定游戏的词典文件
        
        Args:
            game_id: 游戏ID (如 'victoria3', 'stellaris')
            
        Returns:
            bool: 是否成功加载
        """
        if game_id == self.current_game_id and self.current_game_glossary:
            return True
            
        glossary_path = os.path.join(PROJECT_ROOT, 'data', 'glossary', game_id, 'glossary.json')
        
        try:
            if os.path.exists(glossary_path):
                with open(glossary_path, 'r', encoding='utf-8') as f:
                    self.current_game_glossary = json.load(f)
                    self.current_game_id = game_id
                    from scripts.utils import i18n
                    logging.info(i18n.t("glossary_loaded_success", 
                                      game_id=game_id, 
                                      count=len(self.current_game_glossary.get('entries', []))))
                    return True
            else:
                from scripts.utils import i18n
                logging.warning(i18n.t("glossary_file_not_found", path=glossary_path))
                self.current_game_glossary = None
                self.current_game_id = game_id
                return False
                
        except Exception as e:
            from scripts.utils import i18n
            logging.error(i18n.t("glossary_load_failed", error=str(e)))
            self.current_game_glossary = None
            self.current_game_id = game_id
            return False
    
    def extract_relevant_terms(self, texts: List[str], source_lang: str, target_lang: str) -> List[Dict]:
        """
        从待翻译文本中提取相关的词典术语（支持双向翻译）
        
        Args:
            texts: 待翻译的文本列表
            source_lang: 源语言代码
            target_lang: 目标语言代码
            
        Returns:
            List[Dict]: 相关术语列表
        """
        if not self.current_game_glossary:
            return []
            
        relevant_terms = []
        all_text = " ".join(texts).lower()
        
        for entry in self.current_game_glossary.get('entries', []):
            translations = entry.get('translations', {})
            source_term = translations.get(source_lang, "")
            target_term = translations.get(target_lang, "")
            
            if not source_term or not target_term:
                continue
                
            # 检查源术语是否在待翻译文本中出现（支持双向识别）
            if self._term_appears_in_text(source_term, all_text, source_lang):
                relevant_terms.append({
                    'translations': {
                        source_lang: source_term,
                        target_lang: target_term
                    },
                    'id': entry.get('id', ''),
                    'metadata': entry.get('metadata', {}),
                    'variants': entry.get('variants', {})
                })
                
        # 按术语长度排序，优先处理较长的术语
        relevant_terms.sort(key=lambda x: len(x['translations'][source_lang]), reverse=True)
        
        from scripts.utils import i18n
        logging.info(i18n.t("glossary_terms_extracted", 
                           count=len(relevant_terms), 
                           text_count=len(texts)))
        return relevant_terms
    
    def _term_appears_in_text(self, term: str, text: str, source_lang: str) -> bool:
        """
        检查术语是否在文本中出现（支持变体和多语言）
        
        Args:
            term: 术语
            text: 文本
            source_lang: 源语言代码
            
        Returns:
            bool: 是否出现
        """
        # 直接匹配
        if term.lower() in text:
            return True
            
        # 检查变体（支持多语言变体）
        if self.current_game_glossary:
            for entry in self.current_game_glossary.get('entries', []):
                if entry.get('translations', {}).get(source_lang, '').lower() == term.lower():
                    variants = entry.get('variants', {}).get(source_lang, [])
                    for variant in variants:
                        if variant.lower() in text:
                            return True
                            
        return False
    
    def create_dynamic_glossary_prompt(self, relevant_terms: List[Dict], source_lang: str, target_lang: str) -> str:
        """
        创建动态词典提示，用于注入到AI翻译请求中
        
        Args:
            relevant_terms: 相关术语列表
            source_lang: 源语言代码
            target_lang: 目标语言代码
            
        Returns:
            str: 格式化的词典提示
        """
        if not relevant_terms:
            return ""
            
        prompt_lines = [
            "🔍 CRITICAL GLOSSARY INSTRUCTIONS - HIGH PRIORITY 🔍",
            f"以下术语必须严格按照词典翻译，保持游戏术语的一致性：",
            "",
            "术语对照表："
        ]
        
        for term in relevant_terms:
            source = term['translations'][source_lang]
            target = term['translations'][target_lang]
            metadata = term.get('metadata', {})
            remarks = metadata.get('remarks', '')
            
            prompt_lines.append(f"• '{source}' → '{target}'")
            if remarks:
                prompt_lines.append(f"  备注: {remarks}")
                
        prompt_lines.extend([
            "",
            "翻译要求：",
            "1. 上述术语必须严格按照词典翻译，不得随意更改",
            "2. 保持游戏术语的一致性和准确性",
            "3. 术语在句子中的位置应该自然、恰当",
            "4. 如果遇到词典中未包含的术语，请根据上下文进行合理翻译",
            "",
            "请确保在翻译过程中严格遵循以上术语对照表。"
        ])
        
        return "\n".join(prompt_lines)
    
    def get_glossary_stats(self) -> Dict:
        """
        获取当前加载词典的统计信息
        
        Returns:
            Dict: 统计信息
        """
        if not self.current_game_glossary:
            return {"loaded": False, "game_id": self.current_game_id}
            
        entries = self.current_game_glossary.get('entries', [])
        metadata = self.current_game_glossary.get('metadata', {})
        
        return {
            "loaded": True,
            "game_id": self.current_game_id,
            "total_entries": len(entries),
            "description": metadata.get('description', ''),
            "last_updated": metadata.get('last_updated', ''),
            "sources": metadata.get('sources', [])
        }


# 全局词典管理器实例
glossary_manager = GlossaryManager()
