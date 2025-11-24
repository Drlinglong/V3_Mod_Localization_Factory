"""
单元测试：强制全量备份策略 (Mandatory Brute Force Backup Strategy)
测试目标：验证流式翻译工作流在启动前强制执行完整备份的逻辑
"""
import pytest
from unittest.mock import MagicMock, patch, call
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from scripts.workflows import initial_translate


class TestMandatoryBackupStrategy:
    """
    测试强制备份策略的 3 个核心用例：
    1. 备份失败时工作流终止
    2. 备份成功后工作流继续
    3. 从内存流式处理文件（避免重复 IO）
    """

    @pytest.fixture
    def mock_env(self):
        """设置所有必需的 mock 依赖"""
        with patch('scripts.workflows.initial_translate.discover_files') as mock_discover, \
             patch('scripts.workflows.initial_translate.file_parser') as mock_parser, \
             patch('scripts.workflows.initial_translate.archive_manager') as mock_archive, \
             patch('scripts.workflows.initial_translate.CheckpointManager') as mock_checkpoint_cls, \
             patch('scripts.workflows.initial_translate.ParallelProcessor') as mock_processor_cls, \
             patch('scripts.workflows.initial_translate.api_handler') as mock_api, \
             patch('scripts.workflows.initial_translate.directory_handler'), \
             patch('scripts.workflows.initial_translate.asset_handler'), \
             patch('scripts.workflows.initial_translate.glossary_manager'), \
             patch('scripts.workflows.initial_translate.create_proofreading_tracker') as mock_tracker, \
             patch('scripts.workflows.initial_translate.file_builder') as mock_builder, \
             patch('scripts.workflows.initial_translate.process_metadata_for_language'), \
             patch('scripts.workflows.initial_translate._handle_empty_file'), \
             patch('scripts.workflows.initial_translate._run_post_processing'):

            # 配置基本 mock 返回值
            mock_discover.return_value = [
                {
                    "path": "/fake/path/file1.yml",
                    "filename": "file1.yml",
                    "root": "/fake/root",
                    "is_custom_loc": False,
                    "loc_root": "/fake/locroot"
                }
            ]

            mock_parser.extract_translatable_content.return_value = (
                ["line1", "line2"],  # original_lines
                ["text1", "text2"],  # texts_to_translate
                {"key1": 0, "key2": 1}  # key_map
            )

            # API handler mock
            mock_handler = MagicMock()
            mock_handler.provider_name = "test_provider"
            mock_handler.client = MagicMock()
            mock_handler.translate_batch = MagicMock(side_effect=lambda batch_task: batch_task)
            mock_api.get_handler.return_value = mock_handler

            # CheckpointManager mock
            mock_checkpoint = mock_checkpoint_cls.return_value
            mock_checkpoint.is_file_completed.return_value = False

            # ParallelProcessor mock
            mock_processor = mock_processor_cls.return_value
           
            # Mock file_task for streaming results
            mock_file_task = MagicMock()
            mock_file_task.filename = "file1.yml"
            mock_file_task.texts_to_translate = ["text1", "text2"]
            mock_file_task.original_lines = ["line1", "line2"]
            mock_file_task.root = "/fake/root"
            mock_file_task.is_custom_loc = False
            
            # process_files_stream 返回一个迭代器
            mock_processor.process_files_stream.return_value = iter([
                (mock_file_task, ["translated1", "translated2"], [])
            ])

            # file_builder mock
            mock_builder.rebuild_and_write_file.return_value = "/output/file1.yml"

            # tracker mock
            mock_tracker.return_value = MagicMock()

            yield {
                "discover": mock_discover,
                "parser": mock_parser,
                "archive": mock_archive,
                "checkpoint_cls": mock_checkpoint_cls,
                "checkpoint": mock_checkpoint,
                "processor_cls": mock_processor_cls,
                "processor": mock_processor,
                "api": mock_api,
                "builder": mock_builder,
                "tracker": mock_tracker
            }

    def test_case_1_backup_failure_aborts_workflow(self, mock_env):
        """
        用例 1: 备份失败时终止工作流
        边界条件：archive_manager.create_source_version 返回 None
        预期行为：工作流提前终止，不进入翻译阶段
        """
        # 配置：模拟备份失败
        mock_env["archive"].get_or_create_mod_entry.return_value = 123  # mod_id 成功
        mock_env["archive"].create_source_version.return_value = None  # 备份失败

        # 执行
        initial_translate.run(
            mod_name="TestMod",
            source_lang={"code": "en", "name": "English", "key": "l_english"},
            target_languages=[{"code": "zh", "name": "Chinese", "key": "l_simp_chinese"}],
            game_profile={"id": "test", "source_localization_folder": "localization"},
            mod_context="test context",
            selected_provider="test_provider"
        )

        # 断言：必须调用 discover 和 create_source_version
        assert mock_env["discover"].called
        assert mock_env["archive"].create_source_version.called

        # 断言：ParallelProcessor 绝对不应该被实例化（工作流已终止）
        assert not mock_env["processor_cls"].called, \
            "ParallelProcessor should NOT be created when backup fails"

    def test_case_2_backup_success_proceeds_to_translation(self, mock_env):
        """
        用例 2: 备份成功后继续翻译
        边界条件：archive_manager.create_source_version 返回有效 version_id
        预期行为：工作流进入翻译阶段并实时归档结果
        """
        # 配置：模拟备份成功
        mock_env["archive"].get_or_create_mod_entry.return_value = 123
        mock_env["archive"].create_source_version.return_value = 999  # version_id

        # 执行
        initial_translate.run(
            mod_name="TestMod",
            source_lang={"code": "en", "name": "English", "key": "l_english"},
            target_languages=[{"code": "zh", "name": "Chinese", "key": "l_simp_chinese"}],
            game_profile={"id": "test", "source_localization_folder": "localization"},
            mod_context="test context",
            selected_provider="test_provider"
        )

        # 断言：备份成功
        assert mock_env["archive"].create_source_version.called

        # 断言：ParallelProcessor 应该被实例化
        assert mock_env["processor_cls"].called, \
            "ParallelProcessor MUST be created when backup succeeds"

        # 断言：实时归档应该被调用
        assert mock_env["archive"].archive_translated_results.called
        call_args = mock_env["archive"].archive_translated_results.call_args
        assert call_args[0][0] == 999, "Should use correct version_id"

    def test_case_3_streaming_uses_in_memory_data(self, mock_env):
        """
        用例 3: 流式处理从内存读取（避免重复 IO）
        边界条件：验证 file_parser.extract_translatable_content 只在备份阶段调用一次
        预期行为：翻译阶段复用内存中的数据，不再读取文件
        """
        # 配置：备份成功
        mock_env["archive"].get_or_create_mod_entry.return_value = 123
        mock_env["archive"].create_source_version.return_value = 999

        # 执行
        initial_translate.run(
            mod_name="TestMod",
            source_lang={"code": "en", "name": "English", "key": "l_english"},
            target_languages=[{"code": "zh", "name": "Chinese", "key": "l_simp_chinese"}],
            game_profile={"id": "test", "source_localization_folder": "localization"},
            mod_context="test context",
            selected_provider="test_provider"
        )

        # 断言：文件解析器应该只被调用一次（在备份阶段）
        assert mock_env["parser"].extract_translatable_content.call_count == 1, \
            "File parser should ONLY be called during backup phase, NOT during streaming"

        # 断言：process_files_stream 被调用
        assert mock_env["processor"].process_files_stream.called

        # 断言：翻译结果被正确写入
        assert mock_env["builder"].rebuild_and_write_file.called
