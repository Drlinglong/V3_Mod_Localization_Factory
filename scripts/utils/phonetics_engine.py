import logging
from typing import List, Optional
# Optional imports with graceful fallback
try:
    import Levenshtein
    LEVENSHTEIN_AVAILABLE = True
except ImportError:
    LEVENSHTEIN_AVAILABLE = False

try:
    from pypinyin import pinyin, Style, lazy_pinyin
    PYPINYIN_AVAILABLE = True
except ImportError:
    PYPINYIN_AVAILABLE = False

try:
    import pykakasi
    PYKAKASI_AVAILABLE = True
except ImportError:
    PYKAKASI_AVAILABLE = False

try:
    import jamo
    JAMO_AVAILABLE = True
except ImportError:
    JAMO_AVAILABLE = False

class PhoneticsEngine:
    """
    Phonetic Matching Engine for CJK languages.
    Generates phonetic fingerprints and calculates phonetic similarity.
    """
    
    def __init__(self):
        self.kakasi = None
        if PYKAKASI_AVAILABLE:
            self.kakasi = pykakasi.kakasi()
            self.kakasi.setMode("H", "a") # Hiragana to Romaji
            self.kakasi.setMode("K", "a") # Katakana to Romaji
            self.kakasi.setMode("J", "a") # Kanji to Romaji
            self.kakasi_converter = self.kakasi.getConverter()
        
        # Hook for future heavy models
        self.advanced_corrector = None

    def generate_fingerprint(self, text: str, lang: str) -> str:
        """
        Generates a phonetic fingerprint for the given text based on language.
        """
        if not text:
            return ""
            
        lang = lang.lower()
        
        if lang.startswith('zh'): # Chinese
            if not PYPINYIN_AVAILABLE:
                logging.warning("pypinyin not installed, falling back to original text.")
                return text
            # lazy_pinyin returns a list of pinyin syllables without tone marks
            # e.g., "格黑娜" -> ['ge', 'hei', 'na'] -> "geheina"
            return "".join(lazy_pinyin(text))
            
        elif lang == 'ja': # Japanese
            if not PYKAKASI_AVAILABLE:
                logging.warning("pykakasi not installed, falling back to original text.")
                return text
            # Convert to Romaji
            # e.g., "科学" -> "kagaku"
            result = self.kakasi_converter.do(text)
            return result
            
        elif lang == 'ko': # Korean
            if not JAMO_AVAILABLE:
                logging.warning("jamo not installed, falling back to original text.")
                return text
            # Decompose into Jamo
            # e.g., "값" -> "ㄱㅏㅂㅅ"
            return jamo.h2j(text)
            
        else:
            # For non-CJK languages, return lowercase text as fingerprint
            return text.lower()

    def calculate_phonetic_distance(self, term_a: str, term_b: str, lang: str) -> float:
        """
        Calculates a normalized similarity score (0.0 to 1.0) based on phonetic fingerprints.
        1.0 means identical phonetic fingerprint.
        """
        fp_a = self.generate_fingerprint(term_a, lang)
        fp_b = self.generate_fingerprint(term_b, lang)
        
        if not fp_a or not fp_b:
            return 0.0
            
        if fp_a == fp_b:
            return 1.0
            
        # Calculate Levenshtein distance on fingerprints
        if LEVENSHTEIN_AVAILABLE:
            dist = Levenshtein.distance(fp_a, fp_b)
        else:
            dist = self._simple_levenshtein(fp_a, fp_b)
            
        max_len = max(len(fp_a), len(fp_b))
        
        if max_len == 0:
            return 1.0
            
        similarity = 1.0 - (dist / max_len)
        return max(0.0, similarity)

    def _simple_levenshtein(self, s1: str, s2: str) -> int:
        """
        Simple Levenshtein distance implementation for fallback.
        """
        if len(s1) < len(s2):
            return self._simple_levenshtein(s2, s1)
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

    def check_advanced_correction(self, text: str, lang: str) -> Optional[str]:
        """
        Placeholder for Tier 2 Heavyweight/LLM correction.
        """
        if self.advanced_corrector:
            # return self.advanced_corrector.correct(text)
            pass
        return None
