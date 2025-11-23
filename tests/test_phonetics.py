import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.utils.phonetics_engine import PhoneticsEngine

def test_phonetics_engine():
    engine = PhoneticsEngine()
    
    print("=== Testing PhoneticsEngine ===")
    
    # Test Chinese
    text_cn = "格黑娜"
    fp_cn = engine.generate_fingerprint(text_cn, 'zh-CN')
    print(f"CN: {text_cn} -> {fp_cn}")
    assert fp_cn == "geheina"
    
    typo_cn = "格黑那"
    fp_typo_cn = engine.generate_fingerprint(typo_cn, 'zh-CN')
    print(f"CN Typo: {typo_cn} -> {fp_typo_cn}")
    assert fp_typo_cn == "geheina"
    
    dist_cn = engine.calculate_phonetic_distance(text_cn, typo_cn, 'zh-CN')
    print(f"Distance CN: {dist_cn}")
    assert dist_cn == 1.0

    # Test Japanese
    text_jp = "科学"
    fp_jp = engine.generate_fingerprint(text_jp, 'ja')
    print(f"JP: {text_jp} -> {fp_jp}")
    # pykakasi might return 'kagaku'
    assert fp_jp == "kagaku"
    
    typo_jp = "化学" # kagaku
    fp_typo_jp = engine.generate_fingerprint(typo_jp, 'ja')
    print(f"JP Typo: {typo_jp} -> {fp_typo_jp}")
    assert fp_typo_jp == "kagaku"
    
    dist_jp = engine.calculate_phonetic_distance(text_jp, typo_jp, 'ja')
    print(f"Distance JP: {dist_jp}")
    assert dist_jp == 1.0

    # Test Korean
    text_ko = "값"
    fp_ko = engine.generate_fingerprint(text_ko, 'ko')
    print(f"KO: {text_ko} -> {fp_ko}")
    # jamo decomposition
    
    print("\n=== Verification Passed ===")

if __name__ == "__main__":
    try:
        test_phonetics_engine()
    except ImportError as e:
        print(f"ImportError: {e}")
        print("Please ensure pypinyin, pykakasi, and jamo are installed.")
    except AssertionError as e:
        print(f"Assertion Failed: {e}")
    except Exception as e:
        print(f"Error: {e}")
