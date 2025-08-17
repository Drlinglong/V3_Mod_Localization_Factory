# scripts/tests/test_parallel_processor.py
"""
测试并行处理器的功能
"""

import os
import sys
import logging
from unittest.mock import Mock, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from scripts.core.parallel_processor import ParallelProcessor, FileTask, BatchTask
from scripts.config import CHUNK_SIZE


def test_batch_task_creation():
    """测试批次任务创建"""
    print("测试批次任务创建...")
    
    # 创建模拟的文件任务
    mock_file_task = Mock()
    mock_file_task.filename = "test.yml"
    mock_file_task.texts_to_translate = ["text1", "text2", "text3", "text4", "text5"]
    
    # 创建批次任务
    batch_task = BatchTask(
        file_task=mock_file_task,
        batch_index=0,
        start_index=0,
        end_index=3,
        texts=["text1", "text2", "text3"]
    )
    
    assert batch_task.batch_index == 0
    assert batch_task.start_index == 0
    assert batch_task.end_index == 3
    assert len(batch_task.texts) == 3
    print("✓ 批次任务创建测试通过")


def test_batch_tasks_creation():
    """测试批次任务列表创建"""
    print("测试批次任务列表创建...")
    
    # 创建模拟的文件任务
    mock_file_task = Mock()
    mock_file_task.filename = "test.yml"
    mock_file_task.texts_to_translate = ["text" + str(i) for i in range(100)]  # 100个文本
    
    # 创建并行处理器
    processor = ParallelProcessor(max_workers=4)
    
    # 创建批次任务
    batch_tasks = processor._create_batch_tasks([mock_file_task])
    
    # 验证批次数量
    expected_batches = (100 + CHUNK_SIZE - 1) // CHUNK_SIZE
    assert len(batch_tasks) == expected_batches
    
    # 验证第一个批次
    first_batch = batch_tasks[0]
    assert first_batch.batch_index == 0
    assert first_batch.start_index == 0
    assert first_batch.end_index == CHUNK_SIZE
    assert len(first_batch.texts) == CHUNK_SIZE
    
    # 验证最后一个批次
    last_batch = batch_tasks[-1]
    assert last_batch.batch_index == expected_batches - 1
    assert last_batch.end_index == 100
    
    print(f"✓ 批次任务列表创建测试通过，共创建 {len(batch_tasks)} 个批次")


def test_file_completion_check():
    """测试文件完成检查"""
    print("测试文件完成检查...")
    
    # 创建模拟的批次任务
    mock_file_task = Mock()
    mock_file_task.filename = "test.yml"
    
    batch_tasks = [
        BatchTask(mock_file_task, 0, 0, 40, []),
        BatchTask(mock_file_task, 1, 40, 80, []),
        BatchTask(mock_file_task, 2, 80, 100, [])
    ]
    
    processor = ParallelProcessor(max_workers=4)
    
    # 测试未完成状态
    file_results = {"test.yml": [(0, ["translated1"])]}
    is_complete = processor._is_file_complete("test.yml", file_results, batch_tasks)
    assert not is_complete
    
    # 测试完成状态
    file_results = {"test.yml": [(0, ["translated1"]), (1, ["translated2"]), (2, ["translated3"])]}
    is_complete = processor._is_file_complete("test.yml", file_results, batch_tasks)
    assert is_complete
    
    print("✓ 文件完成检查测试通过")


def test_parallel_processor_initialization():
    """测试并行处理器初始化"""
    print("测试并行处理器初始化...")
    
    processor = ParallelProcessor(max_workers=16)
    assert processor.max_workers == 16
    assert processor.logger is not None
    
    print("✓ 并行处理器初始化测试通过")


def run_all_tests():
    """运行所有测试"""
    print("开始运行并行处理器测试...\n")
    
    try:
        test_parallel_processor_initialization()
        test_batch_task_creation()
        test_batch_tasks_creation()
        test_file_completion_check()
        
        print("\n🎉 所有测试通过！")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    # 运行测试
    run_all_tests()
