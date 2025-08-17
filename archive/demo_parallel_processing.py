# scripts/demo_parallel_processing.py
"""
演示新的并行处理器的效果
展示多文件并行处理 vs 旧的文件串行处理
"""

import os
import sys
import time
import logging
from concurrent.futures import ThreadPoolExecutor

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.parallel_processor import ParallelProcessor, FileTask, BatchTask
from config import CHUNK_SIZE


def simulate_translation(texts, delay_factor=1):
    """模拟翻译过程"""
    # 模拟API调用延迟
    time.sleep(0.1 * delay_factor)
    return [f"translated_{text}" for text in texts]


def simulate_file_builder(original_lines, texts_to_translate, translated_texts, key_map, dest_dir, filename, source_lang, target_lang, game_profile):
    """模拟文件构建过程"""
    time.sleep(0.05)  # 模拟文件写入延迟
    return f"{dest_dir}/{filename}"


def create_demo_file_tasks():
    """创建演示用的文件任务"""
    file_tasks = []
    
    # 文件A：35条文本，1个批次
    file_tasks.append(FileTask(
        filename="file_a.yml",
        root="/source/mod/localization",
        original_lines=["line1", "line2"],
        texts_to_translate=[f"text_{i}" for i in range(35)],
        key_map={},
        is_custom_loc=False,
        target_lang={"key": "l_english"},
        source_lang={"key": "l_simp_chinese"},
        game_profile={"source_localization_folder": "localization"},
        mod_context="demo mod",
        provider_name="gemini",
        output_folder_name="demo_output",
        source_dir="/source",
        dest_dir="/dest",
        client=None,
        mod_name="demo_mod"
    ))
    
    # 文件B：105条文本，3个批次
    file_tasks.append(FileTask(
        filename="file_b.yml",
        root="/source/mod/localization",
        original_lines=["line1", "line2"],
        texts_to_translate=[f"text_{i}" for i in range(105)],
        key_map={},
        is_custom_loc=False,
        target_lang={"key": "l_english"},
        source_lang={"key": "l_simp_chinese"},
        game_profile={"source_localization_folder": "localization"},
        mod_context="demo mod",
        provider_name="gemini",
        output_folder_name="demo_output",
        source_dir="/source",
        dest_dir="/dest",
        client=None,
        mod_name="demo_mod"
    ))
    
    # 文件C：400条文本，10个批次
    file_tasks.append(FileTask(
        filename="file_c.yml",
        root="/source/mod/localization",
        original_lines=["line1", "line2"],
        texts_to_translate=[f"text_{i}" for i in range(400)],
        key_map={},
        is_custom_loc=False,
        target_lang={"key": "l_english"},
        source_lang={"key": "l_simp_chinese"},
        game_profile={"source_localization_folder": "localization"},
        mod_context="demo mod",
        provider_name="gemini",
        output_folder_name="demo_output",
        source_dir="/source",
        dest_dir="/dest",
        client=None,
        mod_name="demo_mod"
    ))
    
    return file_tasks


def demo_old_architecture(file_tasks):
    """演示旧架构：文件串行处理"""
    print("🔄 旧架构：文件串行处理")
    print("=" * 50)
    
    start_time = time.time()
    
    for i, file_task in enumerate(file_tasks):
        print(f"📁 开始处理文件 {i+1}: {file_task.filename}")
        file_start_time = time.time()
        
        # 计算批次数量
        total_batches = (len(file_task.texts_to_translate) + CHUNK_SIZE - 1) // CHUNK_SIZE
        
        # 串行处理批次
        for batch_idx in range(total_batches):
            start_idx = batch_idx * CHUNK_SIZE
            end_idx = min(start_idx + CHUNK_SIZE, len(file_task.texts_to_translate))
            batch_texts = file_task.texts_to_translate[start_idx:end_idx]
            
            batch_start_time = time.time()
            translated = simulate_translation(batch_texts)
            batch_time = time.time() - batch_start_time
            
            print(f"  📦 批次 {batch_idx + 1}/{total_batches} 完成，耗时: {batch_time:.2f}s")
        
        file_time = time.time() - file_start_time
        print(f"✅ 文件 {file_task.filename} 完成，总耗时: {file_time:.2f}s")
        print()
    
    total_time = time.time() - start_time
    print(f"⏱️  旧架构总耗时: {total_time:.2f}s")
    print()
    
    return total_time


def demo_new_architecture(file_tasks):
    """演示新架构：多文件并行处理"""
    print("🚀 新架构：多文件并行处理")
    print("=" * 50)
    
    start_time = time.time()
    
    # 创建并行处理器
    processor = ParallelProcessor(max_workers=24)
    
    # 创建模拟的校对追踪器
    mock_proofreading_tracker = type('MockTracker', (), {
        'add_file_info': lambda self, info: None
    })()
    
    # 并行处理所有文件
    processor.process_files_parallel(
        file_tasks=file_tasks,
        translation_function=lambda client, provider, texts, *args: simulate_translation(texts),
        file_builder_function=simulate_file_builder,
        proofreading_tracker=mock_proofreading_tracker
    )
    
    total_time = time.time() - start_time
    print(f"⏱️  新架构总耗时: {total_time:.2f}s")
    print()
    
    return total_time


def main():
    """主函数"""
    print("🎯 多文件并行处理器演示")
    print("=" * 60)
    print()
    
    # 设置日志级别
    logging.basicConfig(level=logging.WARNING)
    
    # 创建演示文件任务
    file_tasks = create_demo_file_tasks()
    
    # 显示文件信息
    print("📊 文件信息统计")
    print("-" * 30)
    total_batches = 0
    for file_task in file_tasks:
        batches = (len(file_task.texts_to_translate) + CHUNK_SIZE - 1) // CHUNK_SIZE
        total_batches += batches
        print(f"📁 {file_task.filename}: {len(file_task.texts_to_translate)} 条文本 → {batches} 个批次")
    
    print(f"📈 总计: {total_batches} 个批次")
    print()
    
    # 演示旧架构
    old_time = demo_old_architecture(file_tasks)
    
    # 演示新架构
    new_time = demo_new_architecture(file_tasks)
    
    # 性能对比
    print("📊 性能对比结果")
    print("=" * 30)
    speedup = old_time / new_time
    print(f"🚀 加速比: {speedup:.2f}x")
    print(f"⏱️  时间节省: {old_time - new_time:.2f}s")
    print(f"📈 效率提升: {(speedup - 1) * 100:.1f}%")
    
    if speedup > 1:
        print("✅ 新架构性能更优！")
    else:
        print("⚠️  新架构性能需要调优")


if __name__ == "__main__":
    main()
