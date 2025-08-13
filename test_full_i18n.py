#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面测试国际化系统，模拟实际运行环境
"""

import sys
import os
import logging

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

def test_full_i18n():
    """全面测试国际化系统"""
    print("🧪 全面测试国际化系统...")
    
    try:
        # 设置日志系统
        from utils import logger
        logger.setup_logger()
        
        # 导入国际化模块
        from utils import i18n
        
        print("1. 测试语言加载...")
        success = i18n.load_language('zh_CN')
        print(f"   语言加载结果: {'成功' if success else '失败'}")
        
        print("\n2. 测试不需要参数的键...")
        no_param_keys = [
            'processing_metadata',
            'metadata_success',
            'processing_assets'
        ]
        
        for key in no_param_keys:
            result = i18n.t(key)
            print(f"   {key}: {result}")
            
        print("\n3. 测试需要参数的键...")
        param_keys = [
            ('asset_copied', {'asset_name': 'thumbnail.png'}),
            ('parsing_file', {'filename': 'test.yml'}),
            ('extracted_texts', {'count': 42}),
            ('writing_file_success', {'filename': 'output.yml'})
        ]
        
        for key, params in param_keys:
            result = i18n.t(key, **params)
            print(f"   {key}({params}): {result}")
            
        print("\n4. 测试缺失的键...")
        missing_keys = [
            'nonexistent_key_1',
            'another_missing_key'
        ]
        
        for key in missing_keys:
            result = i18n.t(key)
            print(f"   {key}: {result}")
            
        print("\n5. 测试日志输出...")
        logging.info("=== 开始日志测试 ===")
        logging.info(i18n.t("processing_metadata"))
        logging.info(i18n.t("metadata_success"))
        logging.info(i18n.t("processing_assets"))
        logging.info(i18n.t("asset_copied", asset_name="test.png"))
        logging.info("=== 日志测试完成 ===")
        
        print("\n✅ 全面测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_full_i18n()
