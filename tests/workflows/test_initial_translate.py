# tests/workflows/test_initial_translate.py
import os
import yaml
import json
import pytest
from pathlib import Path
import sys
from unittest.mock import MagicMock

# FIX: Mock google.genai to prevent ImportError during collection
sys.modules['google'] = MagicMock()
sys.modules['google.genai'] = MagicMock()

# 待测试的模块
from scripts.workflows import initial_translate
from scripts.utils import i18n

# 模拟的常量和配置
TEST_MOD_NAME = "TestMod"
TEST_GAME_ID = "victoria3" # 假设使用V3的配置

# 模拟的游戏配置
MOCK_GAME_PROFILE = {
    "id": TEST_GAME_ID,
    "name": "Victoria 3",
    "source_localization_folder": "localisation",
    "descriptor_filename": "descriptor.mod",
    "metadata_file": "metadata/metadata.json" # FIX: Added missing key
}

# 模拟的语言配置
MOCK_SOURCE_LANG = {"key": "l_english", "name": "English", "code": "en"}
MOCK_TARGET_LANG = {"key": "l_simp_chinese", "name": "Simplified Chinese", "code": "zh-CN"}


@pytest.fixture(scope="function")
def setup_test_environment(tmp_path, mocker):
    """一个全面的fixture，用于创建测试所需的文件结构和模拟各种依赖"""

    # 1. 创建临时目录结构
    source_dir = tmp_path / "SOURCE"
    dest_dir = tmp_path / "DEST"

    mod_source_path = source_dir / TEST_MOD_NAME
    mod_loc_path = mod_source_path / "localisation"
    mod_loc_path.mkdir(parents=True, exist_ok=True)
    dest_dir.mkdir(exist_ok=True)

    # 2. 创建模拟的源文件 (使用正确的多行字符串格式)
    source_yml_text = """l_english:
 KEY_1:0 "Original Text 1"
 KEY_2:0 "Original Text 2"
"""
    source_yml_file = mod_loc_path / "zz_test_file_l_english.yml"
    source_yml_file.write_text(source_yml_text, encoding="utf-8-sig")

    # 3. Mock 关键模块和变量 (在它们被引用的地方)
    mocker.patch("scripts.workflows.initial_translate.SOURCE_DIR", str(source_dir))
    mocker.patch("scripts.workflows.initial_translate.DEST_DIR", str(dest_dir))

    # 直接mock词典加载，避免文件系统依赖
    mocker.patch("scripts.core.glossary_manager.glossary_manager.load_game_glossary", return_value=True)

    # Mock i18n 以避免加载语言文件
    # A better mock for i18n that includes kwargs
    mocker.patch.object(i18n, 't', side_effect=lambda key, **kwargs: f"{key} {kwargs}")

    # Mock create_proofreading_tracker
    mocker.patch("scripts.workflows.initial_translate.create_proofreading_tracker")
    # Mock post processing
    mocker.patch("scripts.core.post_processing_manager.PostProcessingManager")
    # Mock asset copying to avoid dependency on non-existent files
    mocker.patch("scripts.core.asset_handler.copy_assets")

    return {
        "source_dir": source_dir,
        "dest_dir": dest_dir,
        "mod_name": TEST_MOD_NAME,
        "game_profile": MOCK_GAME_PROFILE,
        "source_lang": MOCK_SOURCE_LANG,
        "target_languages": [MOCK_TARGET_LANG]
    }


def test_run_happy_path(setup_test_environment, mocker, capsys):
    """
    测试端到端的“Happy Path”场景：
    - API 返回完美的翻译结果
    - 文件成功创建
    - 没有词典警告
    """
    # 准备 (Arrange)
    # 完美的模拟翻译结果
    mock_translated_texts = ["完美翻译1", "完美翻译2"]
    # 模拟并行处理器返回的结果
    mock_file_results = {
        "zz_test_file_l_english.yml": mock_translated_texts
    }
    mock_warnings = []

    # 劫持并行处理器，直接返回预设结果
    mocker.patch(
        "scripts.core.parallel_processor.ParallelProcessor.process_files_parallel",
        return_value=(mock_file_results, mock_warnings)
    )

    # 劫持元数据处理函数，避免不必要的API调用
    mocker.patch(
        "scripts.workflows.initial_translate.process_metadata_for_language"
    )

    # 劫持API Handler的创建，从根源上避免API Key问题
    mock_handler = mocker.MagicMock()
    mock_handler.provider_name = "mock_provider"
    mock_handler.client = True  # 绕过 if not handler.client 的检查
    mocker.patch(
        "scripts.core.api_handler.get_handler",
        return_value=mock_handler
    )

    # 行动 (Act)
    initial_translate.run(
        mod_name=setup_test_environment["mod_name"],
        source_lang=setup_test_environment["source_lang"],
        target_languages=setup_test_environment["target_languages"],
        game_profile=setup_test_environment["game_profile"],
        mod_context="",
        selected_provider="openai" # 选择哪个都行，因为API被mock了
    )

    # 断言 (Assert)
    # 1. 验证输出文件是否已创建
    output_folder_name = f"zh-CN-{TEST_MOD_NAME}"
    expected_output_path = Path(setup_test_environment["dest_dir"]) / output_folder_name / "localisation" / "simp_chinese" / "zz_test_file_l_simp_chinese.yml"

    assert expected_output_path.exists(), "输出文件未被创建！"

    # 2. 验证文件内容是否正确
    with open(expected_output_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    # 手动构建预期的 YML 内容 (使用正确的多行字符串格式)
    expected_content = """l_simp_chinese:
 KEY_1:0 "完美翻译1"
 KEY_2:0 "完美翻译2"
"""

    # 比较时忽略空白符差异
    assert ''.join(content.split()) == ''.join(expected_content.split())

    # 3. 验证控制台没有打印警告
    captured = capsys.readouterr()
    assert "WARNING" not in captured.err
    assert "glossary_consistency_warning_header" not in captured.out


def test_run_with_glossary_warning(setup_test_environment, mocker, caplog):
    """
    测试词典验证器集成：
    - API 返回了与词典不符的翻译
    - 文件成功创建
    - 控制台打印出词典警告
    """
    # 准备 (Arrange)
    # 让源文件包含一个词典术语
    source_yml_text = '''l_english:
 KEY_1:0 "A single convoy."
'''
    source_file = Path(setup_test_environment["source_dir"]) / TEST_MOD_NAME / "localisation" / "zz_test_file_l_english.yml"
    source_file.write_text(source_yml_text, encoding="utf-8-sig")

    # 模拟一个“有问题”的翻译结果
    mock_translated_texts = ["一艘护卫舰。"]
    mock_file_results = {
        "zz_test_file_l_english.yml": mock_translated_texts
    }
    # 模拟词典验证过程返回一个警告
    mock_warnings = [{
        'message': "词典术语 'convoy' (应为 '运输船队') 在译文 '一艘护卫舰。' 中可能被错误地翻译成了 '护卫舰'。"
    }]

    # 劫持并行处理器，返回“有问题”的结果和警告
    mocker.patch(
        "scripts.core.parallel_processor.ParallelProcessor.process_files_parallel",
        return_value=(mock_file_results, mock_warnings)
    )

    # 劫持API Handler的创建
    mock_handler = mocker.MagicMock()
    mock_handler.provider_name = "mock_provider"
    mock_handler.client = True
    mocker.patch(
        "scripts.core.api_handler.get_handler",
        return_value=mock_handler
    )
    # 劫持元数据处理
    mocker.patch("scripts.workflows.initial_translate.process_metadata_for_language")

    # 行动 (Act)
    initial_translate.run(
        mod_name=setup_test_environment["mod_name"],
        source_lang=setup_test_environment["source_lang"],
        target_languages=setup_test_environment["target_languages"],
        game_profile=setup_test_environment["game_profile"],
        mod_context="",
        selected_provider="openai"
    )

    # 断言 (Assert)
    # 1. 验证文件仍然被创建
    output_folder_name = f"zh-CN-{TEST_MOD_NAME}"
    expected_output_path = Path(setup_test_environment["dest_dir"]) / output_folder_name / "localisation" / "simp_chinese" / "zz_test_file_l_simp_chinese.yml"
    assert expected_output_path.exists(), "输出文件在词典警告场景下未被创建！"

    # 2. 验证日志中成功记录了警告
    assert "glossary_consistency_warning_header" in caplog.text
    # This part of the message is dynamically generated by the mock, so it's okay to assert on the content.
    assert "可能被错误地翻译成了 '护卫舰'" in caplog.text

def test_run_without_api_key(setup_test_environment, mocker, caplog):
    """测试在没有配置API Key时，程序能优雅地失败并打印错误信息"""
    # 准备 (Arrange)
    # 模拟 get_handler 在没有key时返回None
    mocker.patch("scripts.core.api_handler.get_handler", return_value=None)

    # 行动 (Act)
    initial_translate.run(
        mod_name=setup_test_environment["mod_name"],
        source_lang=setup_test_environment["source_lang"],
        target_languages=setup_test_environment["target_languages"],
        game_profile=setup_test_environment["game_profile"],
        mod_context="",
        selected_provider="openai"
    )

    # 断言 (Assert)
    assert "api_client_init_fail" in caplog.text

def test_run_with_no_source_files(setup_test_environment, mocker, caplog):
    """测试当源目录中没有任何可本地化文件时，程序能给出提示"""
    # 准备 (Arrange)
    # 删除之前创建的yml文件
    source_file = Path(setup_test_environment["source_dir"]) / TEST_MOD_NAME / "localisation" / "zz_test_file_l_english.yml"
    source_file.unlink()

    # 劫持API Handler
    mock_handler = mocker.MagicMock()
    mock_handler.client = True
    mocker.patch("scripts.core.api_handler.get_handler", return_value=mock_handler)

    # FIX: Add mock for process_metadata_for_language to prevent it from running
    mocker.patch("scripts.workflows.initial_translate.process_metadata_for_language")

    # 行动 (Act)
    initial_translate.run(
        mod_name=setup_test_environment["mod_name"],
        source_lang=setup_test_environment["source_lang"],
        target_languages=setup_test_environment["target_languages"],
        game_profile=setup_test_environment["game_profile"],
        mod_context="",
        selected_provider="openai"
    )

    # 断言 (Assert)
    assert "no_localisable_files_found" in caplog.text
    assert MOCK_SOURCE_LANG['name'] in caplog.text # Check for the language name, e.g., "English"
