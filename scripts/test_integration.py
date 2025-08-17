# scripts/test_integration.py
"""
集成测试脚本
测试新的并行处理器是否能与现有系统集成
"""

import os
import sys
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_imports():
    """测试所有必要的模块是否能正常导入"""
    print("🧪 测试模块导入...")
    
    try:
        # 测试核心模块导入
        from core.parallel_processor import ParallelProcessor, FileTask, BatchTask
        print("✅ 并行处理器模块导入成功")
        
        from core.directory_handler import create_output_structure
        print("✅ 目录处理器模块导入成功")
        
        from config import RECOMMENDED_MAX_WORKERS, CHUNK_SIZE
        print("✅ 配置模块导入成功")
        
        from utils import i18n
        print("✅ 国际化模块导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        return False


def test_directory_handler():
    """测试目录处理器功能"""
    print("\n🧪 测试目录处理器...")
    
    try:
        from core.directory_handler import create_output_structure
        
        # 创建测试配置
        test_game_profile = {
            "source_localization_folder": "localization"
        }
        
        # 测试创建输出目录
        result = create_output_structure("test_mod", "test_output", test_game_profile)
        
        if result:
            print("✅ 目录创建成功")
            
            # 检查目录是否存在
            test_dir = os.path.join("my_translation", "test_output")
            if os.path.exists(test_dir):
                print("✅ 目录确实存在")
                
                # 清理测试目录
                import shutil
                shutil.rmtree(test_dir)
                print("✅ 测试目录清理完成")
                
                return True
            else:
                print("❌ 目录创建失败")
                return False
        else:
            print("❌ 目录创建返回False")
            return False
            
    except Exception as e:
        print(f"❌ 目录处理器测试失败: {e}")
        return False


def test_parallel_processor():
    """测试并行处理器基本功能"""
    print("\n🧪 测试并行处理器...")
    
    try:
        from core.parallel_processor import ParallelProcessor, FileTask, BatchTask
        from config import CHUNK_SIZE
        
        # 创建测试文件任务
        test_file_task = FileTask(
            filename="test.yml",
            root="/test/root",
            original_lines=["line1", "line2"],
            texts_to_translate=["text1", "text2", "text3", "text4", "text5"],
            key_map={},
            is_custom_loc=False,
            target_lang={"key": "l_english"},
            source_lang={"key": "l_simp_chinese"},
            game_profile={"source_localization_folder": "localization"},
            mod_context="test",
            provider_name="gemini",
            output_folder_name="test_output",
            source_dir="/test",
            dest_dir="/test",
            client=None,
            mod_name="test_mod"
        )
        
        # 创建并行处理器
        processor = ParallelProcessor(max_workers=4)
        
        # 测试批次任务创建
        batch_tasks = processor._create_batch_tasks([test_file_task])
        
        if len(batch_tasks) == 1:  # 5个文本，CHUNK_SIZE=40，所以只有1个批次
            print("✅ 批次任务创建成功")
            print(f"   创建了 {len(batch_tasks)} 个批次")
            
            # 测试文件完成检查
            file_results = {"test.yml": [(0, ["translated1", "translated2", "translated3", "translated4", "translated5"])]}
            is_complete = processor._is_file_complete("test.yml", file_results, batch_tasks)
            
            if is_complete:
                print("✅ 文件完成检查功能正常")
                return True
            else:
                print("❌ 文件完成检查功能异常")
                return False
        else:
            print(f"❌ 批次任务创建异常，期望1个批次，实际{len(batch_tasks)}个")
            return False
            
    except Exception as e:
        print(f"❌ 并行处理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_i18n():
    """测试国际化功能"""
    print("\n🧪 测试国际化功能...")
    
    try:
        from utils import i18n
        
        # 测试设置语言
        i18n.load_language('zh_CN')
        print("✅ 中文语言设置成功")
        
        # 测试翻译
        text = i18n.t("parallel_processing_start", count=5)
        if "5" in text and "批次" in text:
            print("✅ 中文翻译正常")
        else:
            print(f"❌ 中文翻译异常: {text}")
            return False
        
        # 测试英文
        i18n.load_language('en_US')
        print("✅ 英文语言设置成功")
        
        text = i18n.t("parallel_processing_start", count=5)
        if "5" in text and "batches" in text:
            print("✅ 英文翻译正常")
        else:
            print(f"❌ 英文翻译异常: {text}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 国际化测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始集成测试...\n")
    
    # 设置日志级别
    logging.basicConfig(level=logging.WARNING)
    
    tests = [
        ("模块导入", test_imports),
        ("目录处理器", test_directory_handler),
        ("并行处理器", test_parallel_processor),
        ("国际化功能", test_i18n),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 测试通过\n")
            else:
                print(f"❌ {test_name} 测试失败\n")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}\n")
    
    print("=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统集成正常")
    else:
        print("⚠️  部分测试失败，需要进一步检查")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
