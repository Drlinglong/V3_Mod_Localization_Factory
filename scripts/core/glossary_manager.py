# scripts/core/glossary_manager.py
import sqlite3
import json
import logging
import re
from typing import Dict, List, Any, Optional

from scripts.app_settings import PROJECT_ROOT
from scripts.utils import i18n

DB_PATH = f"{PROJECT_ROOT}/data/database.sqlite"

class GlossaryManager:
    """游戏专用词典管理器 (SQLite 版本)"""
    
    def __init__(self):
        self.conn = self._create_connection()
        self.current_game_id: Optional[str] = None
        self.in_memory_glossary: Dict[str, Any] = {'entries': []}
        self.fuzzy_matching_mode: str = 'loose'
        
    def _create_connection(self):
        """创建并返回一个数据库连接"""
        try:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            logging.info(f"Successfully connected to SQLite database at {DB_PATH}")
            return conn
        except Exception as e:
            logging.error(f"Error connecting to database at {DB_PATH}: {e}")
            return None

    def get_available_glossaries(self, game_id: str) -> List[Dict]:
        """查询并返回指定游戏所有可用的词典元信息"""
        if not self.conn:
            logging.error("Database connection not available.")
            return []
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT glossary_id, name, description, is_main FROM glossaries WHERE game_id = ?",
                (game_id,)
            )
            glossaries = [dict(row) for row in cursor.fetchall()]
            logging.info(i18n.t("log_found_glossaries_for_game", count=len(glossaries), game_id=game_id))
            return glossaries
        except Exception as e:
            logging.error(f"Failed to get available glossaries for {game_id}: {e}")
            return []

    def load_game_glossary(self, game_id: str) -> bool:
        """默认只加载指定游戏的主词典 (is_main = 1)"""
        if not self.conn:
            logging.error("Database connection not available.")
            return False
        self.current_game_id = game_id
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT glossary_id FROM glossaries WHERE game_id = ? AND is_main = 1",
                (game_id,)
            )
            main_glossary = cursor.fetchone()

            if main_glossary:
                return self.load_selected_glossaries([main_glossary['glossary_id']])
            else:
                logging.warning(f"No main glossary found for game_id: {game_id}. No glossaries loaded.")
                self.in_memory_glossary = {'entries': []}
                return False
        except Exception as e:
            logging.error(f"Error loading main glossary for {game_id}: {e}")
            return False

    def load_selected_glossaries(self, selected_glossary_ids: List[int]) -> bool:
        """根据选定的glossary_id列表，加载并合并这些词典的条目到内存中"""
        if not self.conn:
            logging.error("Database connection not available.")
            return False
        
        if not selected_glossary_ids:
            logging.warning("No glossary IDs provided. Clearing in-memory glossary.")
            self.in_memory_glossary = {'entries': []}
            return True

        try:
            cursor = self.conn.cursor()
            placeholders = ','.join('?' for _ in selected_glossary_ids)
            query = f"SELECT * FROM entries WHERE glossary_id IN ({placeholders})"
            cursor.execute(query, selected_glossary_ids)
            rows = cursor.fetchall()
            
            self.in_memory_glossary = {'entries': []}
            for row in rows:
                entry = dict(row)
                entry['translations'] = json.loads(entry['translations'])
                entry['abbreviations'] = json.loads(entry['abbreviations']) if entry['abbreviations'] else {}
                entry['variants'] = json.loads(entry['variants']) if entry['variants'] else {}
                entry['raw_metadata'] = json.loads(entry['raw_metadata']) if entry['raw_metadata'] else {}
                self.in_memory_glossary['entries'].append(entry)
            
            logging.info(i18n.t("log_glossary_loaded_from_selected", entries_count=len(rows), glossaries_count=len(selected_glossary_ids)))
            return True

        except Exception as e:
            logging.error(f"Failed to load selected glossaries: {e}")
            self.in_memory_glossary = {'entries': []}
            return False

    def add_entry(self, glossary_id: int, entry_data: Dict) -> bool:
        if not self.conn: return False
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO entries (entry_id, glossary_id, translations, abbreviations, variants, raw_metadata)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                entry_data['id'],
                glossary_id,
                json.dumps(entry_data.get('translations', {})),
                json.dumps(entry_data.get('abbreviations', {})),
                json.dumps(entry_data.get('variants', {})),
                json.dumps(entry_data.get('metadata', {}))
            ))
            self.conn.commit()
            logging.info(f"Successfully added/replaced entry with id {entry_data['id']} to glossary {glossary_id}")
            return True
        except Exception as e:
            logging.error(f"Failed to add entry: {e}")
            return False

    def update_entry(self, entry_id: str, entry_data: Dict) -> bool:
        if not self.conn: return False
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
            UPDATE entries
            SET translations = ?, abbreviations = ?, variants = ?, raw_metadata = ?
            WHERE entry_id = ?
            """, (
                json.dumps(entry_data.get('translations', {})),
                json.dumps(entry_data.get('abbreviations', {})),
                json.dumps(entry_data.get('variants', {})),
                json.dumps(entry_data.get('metadata', {})),
                entry_id
            ))
            self.conn.commit()
            logging.info(f"Successfully updated entry with id {entry_id}")
            return True
        except Exception as e:
            logging.error(f"Failed to update entry {entry_id}: {e}")
            return False

    def delete_entry(self, entry_id: str) -> bool:
        if not self.conn: return False
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM entries WHERE entry_id = ?", (entry_id,))
            self.conn.commit()
            logging.info(f"Successfully deleted entry with id {entry_id}")
            return True
        except Exception as e:
            logging.error(f"Failed to delete entry {entry_id}: {e}")
            return False

    def get_glossary_for_translation(self) -> Optional[Dict]:
        return self.in_memory_glossary if self.in_memory_glossary.get('entries') else None

    def extract_relevant_terms(self, texts: List[str], source_lang: str, target_lang: str) -> List[Dict]:
        glossary = self.get_glossary_for_translation()
        if not glossary or not glossary.get('entries'):
            return []
        relevant_terms = []
        all_text = " ".join(texts).lower()
        matches = self._smart_term_matching(all_text, source_lang, target_lang)
        for match in matches:
            relevant_terms.append({
                'translations': {
                    source_lang: match['source_term'],
                    target_lang: match['target_term']
                },
                'id': match['id'],
                'metadata': match.get('metadata', match.get('raw_metadata', {})),
                'variants': match.get('variants', {}),
                'match_type': match['match_type'],
                'confidence': match['confidence']
            })
        relevant_terms.sort(key=lambda x: (x['confidence'], len(x['translations'][source_lang])), reverse=True)
        logging.info(i18n.t("glossary_terms_extracted", count=len(relevant_terms), text_count=len(texts)))
        return relevant_terms

    def _smart_term_matching(self, text: str, source_lang: str, target_lang: str) -> List[Dict]:
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
            if source_term.lower() in text:
                matches.append({
                    'source_term': source_term,
                    'target_term': target_term,
                    'id': entry.get('entry_id', ''),
                    'metadata': entry.get('raw_metadata', {}),
                    'variants': entry.get('variants', {}),
                    'match_type': 'exact',
                    'confidence': 1.0
                })
                continue
            variants = entry.get('variants', {}).get(source_lang, [])
            for variant in variants:
                if variant.lower() in text:
                    matches.append({
                        'source_term': source_term,
                        'target_term': target_term,
                        'id': entry.get('entry_id', ''),
                        'metadata': entry.get('raw_metadata', {}),
                        'variants': entry.get('variants', {}),
                        'match_type': 'variant',
                        'confidence': 0.9
                    })
                    break
            abbreviations = entry.get('abbreviations', {}).get(source_lang, [])
            if abbreviations:
                 for abbreviation in abbreviations:
                    if self._is_abbreviation_in_text(abbreviation, text, source_lang):
                        matches.append({
                            'source_term': source_term,
                            'target_term': target_term,
                            'id': entry.get('entry_id', ''),
                            'metadata': entry.get('raw_metadata', {}),
                            'variants': entry.get('variants', {}),
                            'match_type': 'abbreviation',
                            'confidence': 0.85
                        })
                        break
            partial_match = self._check_partial_match(source_term, text, source_lang)
            if partial_match:
                matches.append({
                    'source_term': source_term,
                    'target_term': target_term,
                    'id': entry.get('entry_id', ''),
                    'metadata': entry.get('raw_metadata', {}),
                    'variants': entry.get('variants', {}),
                    'match_type': partial_match.get('match_type', 'partial'),
                    'confidence': partial_match['confidence']
                })
        return self._deduplicate_matches(matches)

    def create_dynamic_glossary_prompt(self, relevant_terms: List[Dict], source_lang: str, target_lang: str) -> str:
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
            match_info = f"[{match_type.upper()}]"
            if confidence < 1.0:
                match_info += f" (confidence: {confidence:.1f})"
            prompt_lines.append(f"• {match_info} '{source}' → '{target}'")
            if variants:
                variant_list = ", ".join([f"'{v}'" for v in variants])
                prompt_lines.append(f"  Variants: {variant_list}")
            if remarks:
                prompt_lines.append(f"  Remarks: {remarks}")
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

    def _check_partial_match(self, source_term: str, text: str, source_lang: str) -> Optional[Dict]:
        if len(source_term) > 3 and source_term.lower() in text:
            match_ratio = len(source_term) / len(text)
            if match_ratio > 0.3:
                return {'confidence': 0.7 + (match_ratio * 0.2)}
        fuzzy_match = self._check_fuzzy_match(source_term, text, source_lang)
        if fuzzy_match:
            return fuzzy_match
        return None

    def _check_fuzzy_match(self, source_term: str, text: str, source_lang: str) -> Optional[Dict]:
        if self.fuzzy_matching_mode == 'strict':
            return None
        text_tokens = self._tokenize_text(text, source_lang)
        source_tokens = self._tokenize_text(source_term, source_lang)
        if len(source_tokens) == 1:
            return self._check_single_word_fuzzy_match(source_term, text, source_lang)
        return self._check_multi_word_fuzzy_match(source_tokens, text_tokens, source_lang)

    def _check_single_word_fuzzy_match(self, source_term: str, text: str, source_lang: str) -> Optional[Dict]:
        if self._is_similar_word(source_term, text):
            distance = self._levenshtein_distance(source_term, text)
            max_distance = max(1, len(source_term) // 4)
            confidence = 0.6 - (distance / max_distance) * 0.3
            return {'confidence': confidence, 'match_type': 'fuzzy'}
        return None

    def _check_multi_word_fuzzy_match(self, source_tokens: List[str], text_tokens: List[str], source_lang: str) -> Optional[Dict]:
        matched_tokens = 0
        total_source_tokens = len(source_tokens)
        for source_token in source_tokens:
            if len(source_token) < 2: continue
            for text_token in text_tokens:
                if len(text_token) < 2: continue
                if source_token == text_token or self._is_similar_word(source_token, text_token):
                    matched_tokens += 1
                    break
        if matched_tokens > 0:
            match_ratio = matched_tokens / total_source_tokens
            if match_ratio > 0.5:
                confidence = 0.3 + (match_ratio * 0.3)
                return {'confidence': confidence, 'match_type': 'fuzzy'}
        return None

    def _tokenize_text(self, text: str, lang: str) -> List[str]:
        if lang in ['zh-CN', 'zh-TW', 'ja', 'ko']:
            return list(text)
        else:
            return re.findall(r'\w+', text.lower())

    def _is_similar_word(self, word1: str, word2: str) -> bool:
        if len(word1) < 3 or len(word2) < 3:
            return False
        distance = self._levenshtein_distance(word1, word2)
        max_distance = max(1, len(word1) // 4)
        return distance <= max_distance

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
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

    def _is_abbreviation_in_text(self, abbreviation: str, text: str, source_lang: str) -> bool:
        if source_lang in ['en', 'fr', 'de', 'es']:
            pattern = r'\b' + re.escape(abbreviation.lower()) + r'\b'
            return bool(re.search(pattern, text.lower()))
        else:
            text_words = text.split()
            return abbreviation.lower() in [word.lower() for word in text_words]

    def _deduplicate_matches(self, matches: List[Dict]) -> List[Dict]:
        unique_matches = {}
        for match in matches:
            match_id = match['id']
            if match_id not in unique_matches or match['confidence'] > unique_matches[match_id]['confidence']:
                unique_matches[match_id] = match
        return list(unique_matches.values())
        
    def set_fuzzy_matching_mode(self, mode: str):
        if mode in ['strict', 'loose']:
            self.fuzzy_matching_mode = mode
            mode_name = i18n.t("fuzzy_mode_strict") if mode == 'strict' else i18n.t("fuzzy_mode_loose")
            logging.info(i18n.t("fuzzy_mode_set", mode=mode_name))
        else:
            logging.warning(f"Invalid fuzzy matching mode: {mode}. Using default 'loose' mode.")
            self.fuzzy_matching_mode = 'loose'

glossary_manager = GlossaryManager()
