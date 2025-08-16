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
        self.current_auxiliary_glossaries: List[Dict] = []  # 外挂词典列表
        self.merged_glossary: Optional[Dict] = None  # 合并后的词典
        self.fuzzy_matching_mode: str = 'loose'  # 模糊匹配模式: 'strict' 或 'loose'
        
    def scan_auxiliary_glossaries(self, game_id: str) -> List[Dict]:
        """
        扫描指定游戏目录下的外挂词典
        
        Args:
            game_id: 游戏ID
            
        Returns:
            List[Dict]: 外挂词典信息列表
        """
        glossary_dir = os.path.join(PROJECT_ROOT, 'data', 'glossary', game_id)
        if not os.path.exists(glossary_dir):
            return []
            
        auxiliary_glossaries = []
        
        for filename in os.listdir(glossary_dir):
            if filename.endswith('.json') and filename != 'glossary.json':
                file_path = os.path.join(glossary_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        glossary_data = json.load(f)
                        
                    # 提取词典信息
                    metadata = glossary_data.get('metadata', {})
                    auxiliary_glossaries.append({
                        'filename': filename,
                        'file_path': file_path,
                        'name': metadata.get('name', filename.replace('.json', '')),
                        'description': metadata.get('description', ''),
                        'entry_count': len(glossary_data.get('entries', [])),
                        'data': glossary_data
                    })
                except Exception as e:
                    logging.warning(f"Failed to load auxiliary glossary {filename}: {e}")
                    
        return auxiliary_glossaries
    
    def load_game_glossary(self, game_id: str) -> bool:
        """
        加载指定游戏的主词典文件
        
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
    
    def has_any_glossary(self) -> bool:
        """
        检查是否有任何可用的词典（主词典或外挂词典）
        
        Returns:
            bool: 是否有任何词典可用
        """
        return (self.current_game_glossary is not None or 
                len(self.current_auxiliary_glossaries) > 0 or 
                self.merged_glossary is not None)
    
    def get_glossary_status_summary(self) -> str:
        """
        获取词典状态摘要
        
        Returns:
            str: 词典状态描述
        """
        if not self.current_game_id:
            return "未加载任何词典"
            
        if self.merged_glossary:
            main_count = len(self.current_game_glossary.get('entries', [])) if self.current_game_glossary else 0
            aux_count = len(self.current_auxiliary_glossaries)
            total_count = len(self.merged_glossary.get('entries', []))
            return f"主词典({main_count}条) + 外挂词典({aux_count}个) = 总计({total_count}条)"
        elif self.current_game_glossary:
            count = len(self.current_game_glossary.get('entries', []))
            return f"仅主词典({count}条)"
        elif self.current_auxiliary_glossaries:
            aux_count = len(self.current_auxiliary_glossaries)
            return f"仅外挂词典({aux_count}个)"
        else:
            return "无可用词典"
    
    def load_auxiliary_glossaries(self, selected_indices: List[int]) -> bool:
        """
        加载选中的外挂词典
        
        Args:
            selected_indices: 选中的外挂词典索引列表
            
        Returns:
            bool: 是否成功加载
        """
        if not self.current_game_id:
            return False
            
        auxiliary_glossaries = self.scan_auxiliary_glossaries(self.current_game_id)
        self.current_auxiliary_glossaries = []
        
        for idx in selected_indices:
            if 0 <= idx < len(auxiliary_glossaries):
                self.current_auxiliary_glossaries.append(auxiliary_glossaries[idx])
                
        # 合并词典
        self._merge_glossaries()
        return True
    
    def _merge_glossaries(self):
        """合并主词典和外挂词典"""
        if not self.current_game_glossary:
            self.merged_glossary = None
            return
            
        # 深拷贝主词典
        merged = json.loads(json.dumps(self.current_game_glossary))
        merged_entries = merged.get('entries', [])
        
        # 添加外挂词典条目
        for aux_glossary in self.current_auxiliary_glossaries:
            aux_entries = aux_glossary['data'].get('entries', [])
            for entry in aux_entries:
                # 检查是否已存在相同ID的条目
                existing_entry = next((e for e in merged_entries if e.get('id') == entry.get('id')), None)
                if existing_entry:
                    # 如果存在，外挂词典的条目优先级更高
                    existing_entry.update(entry)
                else:
                    # 如果不存在，直接添加
                    merged_entries.append(entry)
                    
        self.merged_glossary = merged
        
        # 记录合并结果
        total_entries = len(merged_entries)
        main_entries = len(self.current_game_glossary.get('entries', []))
        aux_entries = total_entries - main_entries
        
        from scripts.utils import i18n
        if i18n.get_current_language() == "en_US":
            logging.info(f"Glossary merged: {main_entries} main entries + {aux_entries} auxiliary entries = {total_entries} total")
        else:
            logging.info(f"词典合并完成: {main_entries} 个主词典条目 + {aux_entries} 个外挂词典条目 = {total_entries} 个总计")
    
    def get_glossary_for_translation(self) -> Optional[Dict]:
        """获取用于翻译的词典（优先使用合并后的词典）"""
        return self.merged_glossary if self.merged_glossary else self.current_game_glossary
    
    def extract_relevant_terms(self, texts: List[str], source_lang: str, target_lang: str) -> List[Dict]:
        """
        从待翻译文本中提取相关的词典术语（支持双向识别、变体查找和智能匹配）
        
        Args:
            texts: 待翻译的文本列表
            source_lang: 源语言代码
            target_lang: 目标语言代码
            
        Returns:
            List[Dict]: 相关术语列表
        """
        glossary = self.get_glossary_for_translation()
        if not glossary:
            return []
            
        relevant_terms = []
        all_text = " ".join(texts).lower()
        
        # 使用智能匹配算法
        matches = self._smart_term_matching(all_text, source_lang, target_lang)
        
        # 转换为标准格式
        for match in matches:
            relevant_terms.append({
                'translations': {
                    source_lang: match['source_term'],
                    target_lang: match['target_term']
                },
                'id': match['id'],
                'metadata': match['metadata'],
                'variants': match.get('variants', {}),
                'match_type': match['match_type'],  # 新增：匹配类型
                'confidence': match['confidence']   # 新增：匹配置信度
            })
        
        # 按置信度和术语长度排序
        relevant_terms.sort(key=lambda x: (x['confidence'], len(x['translations'][source_lang])), reverse=True)
        
        from scripts.utils import i18n
        logging.info(i18n.t("glossary_terms_extracted", 
                           count=len(relevant_terms), 
                           text_count=len(texts)))
        return relevant_terms
    
    def _smart_term_matching(self, text: str, source_lang: str, target_lang: str) -> List[Dict]:
        """
        智能术语匹配，支持多种匹配模式
        
        Args:
            text: 待匹配的文本
            source_lang: 源语言代码
            target_lang: 目标语言代码
            
        Returns:
            List[Dict]: 匹配结果列表
        """
        matches = []
        glossary = self.get_glossary_for_translation()
        
        if not glossary:
            return matches
        
        for entry in glossary.get('entries', []):
            translations = entry.get('translations', {})
            source_term = translations.get(source_lang, "")
            target_term = translations.get(target_lang, "")
            
            if not source_term or not target_term:
                continue
            
            # 1. 精确匹配（最高优先级）
            if source_term.lower() in text:
                matches.append({
                    'source_term': source_term,
                    'target_term': target_term,
                    'id': entry.get('id', ''),
                    'metadata': entry.get('metadata', {}),
                    'variants': entry.get('variants', {}),
                    'match_type': 'exact',
                    'confidence': 1.0
                })
                continue
            
            # 2. 变体匹配（包括简称、同义词等）
            variants = entry.get('variants', {}).get(source_lang, [])
            for variant in variants:
                if variant.lower() in text:
                    matches.append({
                        'source_term': source_term,
                        'target_term': target_term,
                        'id': entry.get('id', ''),
                        'metadata': entry.get('metadata', {}),
                        'variants': entry.get('variants', {}),
                        'match_type': 'variant',
                        'confidence': 0.9
                    })
                    break
            
            # 3. 简称匹配（如果有abbreviations字段）
            abbreviations = entry.get('abbreviations', {}).get(source_lang, [])
            for abbreviation in abbreviations:
                if abbreviation.lower() in text:
                    matches.append({
                        'source_term': source_term,
                        'target_term': target_term,
                        'id': entry.get('id', ''),
                        'metadata': entry.get('metadata', {}),
                        'variants': entry.get('variants', {}),
                        'match_type': 'abbreviation',
                        'confidence': 0.85  # 简称匹配，置信度稍高
                    })
                    break
            
            # 4. 智能部分匹配（自动识别简称和全称关系）
            partial_match = self._check_partial_match(source_term, text, source_lang)
            if partial_match:
                # 检查是否是模糊匹配
                if partial_match.get('match_type') == 'fuzzy':
                    match_type = 'fuzzy'
                else:
                    match_type = 'partial'
                
                matches.append({
                    'source_term': source_term,
                    'target_term': target_term,
                    'id': entry.get('id', ''),
                    'metadata': entry.get('metadata', {}),
                    'variants': entry.get('variants', {}),
                    'match_type': match_type,
                    'confidence': partial_match['confidence']
                })
        
        return self._deduplicate_matches(matches)
    
    def _check_partial_match(self, source_term: str, text: str, source_lang: str) -> Optional[Dict]:
        """
        智能部分匹配，识别简称和全称关系，支持模糊匹配
        如："百鬼夜行" 匹配 "百鬼夜行联合学园"
        如："小日本帝国联邦舰队" 模糊匹配 "小日本帝国联合舰队"
        """
        # 1. 精确部分匹配（当前实现）
        if len(source_term) > 3 and source_term.lower() in text:
            match_ratio = len(source_term) / len(text)
            if match_ratio > 0.3:
                return {
                    'confidence': 0.7 + (match_ratio * 0.2)
                }
        
        # 2. 模糊匹配（新增功能）
        fuzzy_match = self._check_fuzzy_match(source_term, text, source_lang)
        if fuzzy_match:
            return fuzzy_match
        
        return None
    
    def _check_fuzzy_match(self, source_term: str, text: str, source_lang: str) -> Optional[Dict]:
        """
        模糊匹配，容忍拼写错误和轻微差异
        """
        # 严格模式下禁用模糊匹配
        if self.fuzzy_matching_mode == 'strict':
            return None
            
        # 根据语言类型进行智能分词
        text_tokens = self._tokenize_text(text, source_lang)
        source_tokens = self._tokenize_text(source_term, source_lang)
        
        if len(source_tokens) < 2:
            return None
        
        # 计算单词/字符级别的匹配度
        matched_tokens = 0
        total_source_tokens = len(source_tokens)
        
        for source_token in source_tokens:
            if len(source_token) < 2:  # 忽略太短的词
                continue
                
            # 检查是否有相似单词/字符
            for text_token in text_tokens:
                if len(text_token) < 2:
                    continue
                
                # 精确匹配
                if source_token == text_token:
                    matched_tokens += 1
                    break
                
                # 模糊匹配（编辑距离）
                if self._is_similar_word(source_token, text_token):
                    matched_tokens += 1
                    break
        
        # 计算匹配度
        if matched_tokens > 0:
            match_ratio = matched_tokens / total_source_tokens
            if match_ratio > 0.5:  # 超过50%的单词匹配
                # 调整置信度范围到0.3-0.6
                confidence = 0.3 + (match_ratio * 0.3)
                return {
                    'confidence': confidence,
                    'match_type': 'fuzzy'
                }
        
        return None
    
    def _tokenize_text(self, text: str, lang: str) -> List[str]:
        """
        根据语言类型进行智能分词
        """
        if lang in ['zh-CN', 'zh-TW', 'ja', 'ko']:
            # 中文、日文、韩文：按字符分割
            return list(text)
        else:
            # 英文等：按空格和标点分割
            return re.findall(r'\w+', text.lower())
    
    def _is_similar_word(self, word1: str, word2: str) -> bool:
        """
        检查两个单词是否相似（使用编辑距离）
        """
        if len(word1) < 3 or len(word2) < 3:
            return False
        
        # 计算编辑距离
        distance = self._levenshtein_distance(word1, word2)
        
        # 允许的编辑距离：单词越长，允许的差异越大
        max_distance = max(1, len(word1) // 4)
        
        return distance <= max_distance
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        计算两个字符串的编辑距离
        """
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _deduplicate_matches(self, matches: List[Dict]) -> List[Dict]:
        """
        去重匹配结果，保留最高置信度的匹配
        """
        # 按ID分组，保留最高置信度的匹配
        unique_matches = {}
        for match in matches:
            match_id = match['id']
            if match_id not in unique_matches or match['confidence'] > unique_matches[match_id]['confidence']:
                unique_matches[match_id] = match
        
        return list(unique_matches.values())
    
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
        glossary = self.get_glossary_for_translation()
        if glossary:
            for entry in glossary.get('entries', []):
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
            f"The following terms must be translated strictly according to the glossary to maintain consistency:",
            "",
            "Glossary Reference:"
        ]
        
        for term in relevant_terms:
            source = term['translations'][source_lang]
            target = term['translations'][target_lang]
            metadata = term.get('metadata', {})
            remarks = metadata.get('remarks', '')
            variants = term.get('variants', {}).get(source_lang, [])
            match_type = term.get('match_type', 'unknown')
            confidence = term.get('confidence', 1.0)
            
            # 显示匹配类型和置信度
            match_info = f"[{match_type.upper()}]"
            if confidence < 1.0:
                match_info += f" (confidence: {confidence:.1f})"
            
            prompt_lines.append(f"• {match_info} '{source}' → '{target}'")
            
            # 如果有变体词汇，在提示中说明
            if variants:
                variant_list = ", ".join([f"'{v}'" for v in variants])
                prompt_lines.append(f"  Variants: {variant_list}")
                
            if remarks:
                prompt_lines.append(f"  Remarks: {remarks}")
        
        # 添加匹配类型说明
        prompt_lines.extend([
            "",
            "Match Type Explanation:",
            "• EXACT: Exact match, highest priority",
            "• VARIANT: Variant match, such as plural forms, synonyms, abbreviations",
            "• ABBREVIATION: Abbreviation match, such as organization abbreviations, person name abbreviations",
            "• PARTIAL: Smart partial match, automatically identifies abbreviation and full name relationships",
            "• FUZZY: Fuzzy match, tolerates spelling errors and minor differences",
            "",
            "Translation Requirements:",
            "1. The above terms must be translated strictly according to the glossary, no arbitrary changes allowed",
            "2. Variant forms of terms should also be translated to the same target language equivalent",
            "3. For abbreviation and partial match terms, choose the most appropriate translation based on context",
            "4. For fuzzy match terms, translate reasonably based on context and glossary",
            "5. Maintain consistency and accuracy of game terminology",
            "6. Term placement in sentences should be natural and appropriate",
            "7. If encountering terms not in the glossary, translate reasonably based on context",
            "",
            "Please ensure strict adherence to the above glossary reference during translation."
        ])
        
        return "\n".join(prompt_lines)
        
        # 中文版本注释（仅供参考）:
        # prompt_lines = [
        #     "🔍 关键词典指示 - 高优先级 🔍",
        #     f"以下术语必须严格按照词典翻译，保持游戏术语的一致性：",
        #     "",
        #     "术语对照表："
        # ]
        # 
        # for term in relevant_terms:
        #     source = term['translations'][source_lang]
        #     target = term['translations'][target_lang]
        #     metadata = term.get('metadata', {})
        #     remarks = metadata.get('remarks', '')
        #     variants = term.get('variants', {}).get(source_lang, [])
        #     match_type = term.get('match_type', 'unknown')
        #     confidence = term.get('confidence', 1.0)
        #     
        #     # 显示匹配类型和置信度
        #     match_info = f"[{match_type.upper()}]"
        #     if confidence < 1.0:
        #         match_info += f" (置信度: {confidence:.1f})"
        #     
        #     prompt_lines.append(f"• {match_info} '{source}' → '{target}'")
        #     
        #     # 如果有变体词汇，在提示中说明
        #     if variants:
        #         variant_list = ", ".join([f"'{v}'" for v in variants])
        #         prompt_lines.append(f"  变体: {variant_list}")
        #             
        #     if remarks:
        #         prompt_lines.append(f"  备注: {remarks}")
        # 
        # # 添加匹配类型说明
        # prompt_lines.extend([
        #     "",
        #     "匹配类型说明：",
        #     "• EXACT: 精确匹配，最高优先级",
        #     "• VARIANT: 变体匹配，如复数形式、同义词、简称",
        #     "• ABBREVIATION: 简称匹配，如组织简称、人名简称",
        #     "• PARTIAL: 智能部分匹配，自动识别简称和全称关系",
        #     "• FUZZY: 模糊匹配，容忍拼写错误和轻微差异",
        #     "",
        #     "翻译要求：",
        #     "1. 上述术语必须严格按照词典翻译，不得随意更改",
        #     "2. 术语的变体形式也应该翻译成相同的中文",
        #     "3. 简称和部分匹配的术语，请根据上下文选择最合适的翻译",
        #     "4. 模糊匹配的术语，请根据上下文和词典进行合理翻译",
        #     "5. 保持游戏术语的一致性和准确性",
        #     "6. 术语在句子中的位置应该自然、恰当",
        #     "7. 如果遇到词典中未包含的术语，请根据上下文进行合理翻译",
        #     "",
        #     "请确保在翻译过程中严格遵循以上术语对照表。"
        # ])
    
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
            "sources": metadata.get('sources', []),
            "auxiliary_count": len(self.current_auxiliary_glossaries)
        }
    
    def get_auxiliary_glossaries_info(self) -> List[Dict]:
        """获取外挂词典信息列表"""
        if not self.current_game_id:
            return []
        return self.scan_auxiliary_glossaries(self.current_game_id)
    
    def set_fuzzy_matching_mode(self, mode: str):
        """
        设置模糊匹配模式
        
        Args:
            mode: 模式类型 ('strict' 或 'loose')
        """
        if mode in ['strict', 'loose']:
            self.fuzzy_matching_mode = mode
            from scripts.utils import i18n
            mode_name = "严格模式" if mode == 'strict' else "宽松模式"
            logging.info(i18n.t("fuzzy_mode_set", mode=mode_name))
        else:
            logging.warning(f"Invalid fuzzy matching mode: {mode}. Using default 'loose' mode.")
            self.fuzzy_matching_mode = 'loose'


# 全局词典管理器实例
glossary_manager = GlossaryManager()
