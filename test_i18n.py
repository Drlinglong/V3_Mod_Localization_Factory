#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试国际化系统是否正常工作
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

def test_i18n():
    """测试国际化系统"""
    print("🧪 测试国际化系统...")
    
    try:
        # 导入国际化模块
        from utils import i18n
        
        # 测试加载语言
        print("1. 测试语言加载...")
        success = i18n.load_language('zh_CN')
        print(f"   语言加载结果: {'成功' if success else '失败'}")
        
        # 测试关键键
        print("\n2. 测试关键国际化键...")
        test_keys = [
            'processing_metadata',
            'translating_mod_name', 
            'metadata_success',
            'processing_assets',
            'asset_copied',
            'parsing_file',
            'extracted_texts',
            'writing_file_success'
        ]
        
        for key in test_keys:
            result = i18n.t(key)
            print(f"   {key}: {result}")
            
        # 测试带参数的键
        print("\n3. 测试带参数的国际化键...")
        test_with_params = [
            ('parsing_file', {'filename': 'test.yml'}),
            ('extracted_texts', {'count': 42}),
            ('asset_copied', {'asset_name': 'thumbnail.png'}),
            ('writing_file_success', {'filename': 'output.yml'})
        ]
        
        for key, params in test_with_params:
            result = i18n.t(key, **params)
            print(f"   {key}({params}): {result}")
            
        print("\n✅ 国际化系统测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_i18n()
