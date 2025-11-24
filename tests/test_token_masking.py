import pytest
from scripts.utils.text_clean import mask_special_tokens, restore_special_tokens, QUOTE_STYLES, MASK_NEWLINE, MASK_QUOTE

def test_masking_newlines():
    """测试换行符遮罩"""
    input_text = 'Line 1\nLine 2'
    masked = mask_special_tokens(input_text)
    assert masked == f'Line 1{MASK_NEWLINE}Line 2'

def test_masking_quotes():
    """测试引号遮罩"""
    input_text = 'He said "Hello"'
    masked = mask_special_tokens(input_text)
    assert masked == f'He said {MASK_QUOTE}Hello{MASK_QUOTE}'
    
    # Test curly quotes
    input_text = 'He said “Hello”'
    masked = mask_special_tokens(input_text)
    assert masked == f'He said {MASK_QUOTE}Hello{MASK_QUOTE}'

def test_restore_chinese():
    """测试中文引号恢复"""
    masked = f'He said {MASK_QUOTE}Hello{MASK_QUOTE}{MASK_NEWLINE}World'
    restored = restore_special_tokens(masked, "zh")
    # Expect escaped newline \\n because that's what restore_special_tokens does for Paradox files
    assert restored == 'He said “Hello”\\nWorld'

def test_restore_german():
    """测试德语引号恢复"""
    masked = f'Er sagte {MASK_QUOTE}Hallo{MASK_QUOTE}'
    restored = restore_special_tokens(masked, "de")
    assert restored == 'Er sagte „Hallo“'

def test_restore_french():
    """测试法语引号恢复"""
    masked = f'Il a dit {MASK_QUOTE}Bonjour{MASK_QUOTE}'
    restored = restore_special_tokens(masked, "fr")
    assert restored == 'Il a dit « Bonjour »'

def test_restore_english_fallback():
    """测试英语/默认引号恢复"""
    masked = f'He said {MASK_QUOTE}Hello{MASK_QUOTE}'
    restored = restore_special_tokens(masked, "en")
    assert restored == 'He said “Hello”'

def test_restore_newline_spacing():
    """测试换行符周围的空格清理"""
    # LLM might output " [[_NL_]] "
    masked = f'Line 1 {MASK_NEWLINE} Line 2'
    restored = restore_special_tokens(masked, "en")
    assert restored == 'Line 1\\nLine 2'

def test_all_languages_defined():
    """验证所有定义的语言都能正确恢复"""
    for lang, (open_q, close_q) in QUOTE_STYLES.items():
        if lang == "default":
            continue
        masked = f'{MASK_QUOTE}test{MASK_QUOTE}'
        restored = restore_special_tokens(masked, lang)
        assert restored == f'{open_q}test{close_q}'

if __name__ == "__main__":
    # Manually run tests if pytest is not available
    try:
        test_masking_newlines()
        test_masking_quotes()
        test_restore_chinese()
        test_restore_german()
        test_restore_french()
        test_restore_english_fallback()
        test_restore_newline_spacing()
        test_all_languages_defined()
        print("All tests passed!")
    except AssertionError as e:
        print(f"Test failed: {e}")
