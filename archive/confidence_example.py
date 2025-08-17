#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
置信度计算和使用示例
"""

def demonstrate_confidence_calculation():
    """演示置信度计算过程"""
    
    print("🔍 置信度计算示例")
    print("=" * 50)
    
    # 示例1: 精确匹配
    print("\n1️⃣ 精确匹配 (EXACT)")
    print("文本: 'This is about Allied Hyakkiyako Academy'")
    print("术语: 'Allied Hyakkiyako Academy'")
    print("匹配类型: 完全包含")
    print("置信度: 1.0 (100%确信)")
    
    # 示例2: 变体匹配
    print("\n2️⃣ 变体匹配 (VARIANT)")
    print("文本: 'This is about Alarei ships'")
    print("术语: 'Alarai'")
    print("变体: ['Alarei']")
    print("匹配类型: 变体包含")
    print("置信度: 0.9 (90%确信)")
    
    # 示例3: 缩写匹配
    print("\n3️⃣ 缩写匹配 (ABBREVIATION)")
    print("文本: 'This is about 百鬼夜行'")
    print("术语: '百鬼夜行联合学园'")
    print("缩写: ['百鬼夜行']")
    print("匹配类型: 缩写包含")
    print("置信度: 0.8 (80%确信)")
    
    # 示例4: 部分匹配
    print("\n4️⃣ 部分匹配 (PARTIAL)")
    print("文本: 'This is about 百鬼夜行'")
    print("术语: '百鬼夜行联合学园'")
    print("匹配类型: 部分包含")
    print("计算过程:")
    print("  匹配长度: 4 字符")
    print("  总长度: 8 字符")
    print("  匹配度: 4/8 = 0.5")
    print("  置信度: 0.7 + (0.5 × 0.2) = 0.8")
    
    # 示例5: 层级匹配
    print("\n5️⃣ 层级匹配 (HIERARCHICAL)")
    print("文本: 'This is about 百鬼夜行'")
    print("术语: '百鬼夜行联合学园'")
    print("子术语: ['百鬼夜行']")
    print("匹配类型: 子术语包含")
    print("置信度: 0.75 (75%确信)")

def demonstrate_confidence_usage():
    """演示置信度的使用方式"""
    
    print("\n\n🎯 置信度的使用方式")
    print("=" * 50)
    
    # 排序示例
    print("\n1️⃣ 排序优先级")
    matches = [
        {"id": "1", "confidence": 0.8, "term": "百鬼夜行", "type": "ABBREVIATION"},
        {"id": "2", "confidence": 1.0, "term": "Allied Hyakkiyako Academy", "type": "EXACT"},
        {"id": "3", "confidence": 0.9, "term": "Alarei", "type": "VARIANT"},
        {"id": "4", "confidence": 0.75, "term": "百鬼夜行", "type": "HIERARCHICAL"}
    ]
    
    # 按置信度排序
    sorted_matches = sorted(matches, key=lambda x: x['confidence'], reverse=True)
    
    print("排序前:")
    for match in matches:
        print(f"  {match['type']}: {match['term']} (置信度: {match['confidence']})")
    
    print("\n按置信度排序后:")
    for match in sorted_matches:
        print(f"  {match['type']}: {match['term']} (置信度: {match['confidence']})")
    
    # 去重示例
    print("\n2️⃣ 去重处理")
    print("如果同一个术语有多个匹配结果，保留置信度最高的:")
    
    duplicate_matches = [
        {"id": "same_id", "confidence": 0.8, "term": "百鬼夜行", "type": "ABBREVIATION"},
        {"id": "same_id", "confidence": 0.75, "term": "百鬼夜行", "type": "HIERARCHICAL"}
    ]
    
    print("去重前:")
    for match in duplicate_matches:
        print(f"  {match['type']}: {match['term']} (置信度: {match['confidence']})")
    
    # 模拟去重逻辑
    unique_matches = {}
    for match in duplicate_matches:
        match_id = match['id']
        if match_id not in unique_matches or match['confidence'] > unique_matches[match_id]['confidence']:
            unique_matches[match_id] = match
    
    print("\n去重后 (保留最高置信度):")
    for match in unique_matches.values():
        print(f"  {match['type']}: {match['term']} (置信度: {match['confidence']})")
    
    # AI翻译指导示例
    print("\n3️⃣ AI翻译指导")
    print("系统会在翻译提示中显示置信度信息:")
    
    for match in sorted_matches[:3]:  # 显示前3个
        match_info = f"[{match['type']}]"
        if match['confidence'] < 1.0:
            match_info += f" (置信度: {match['confidence']:.1f})"
        
        print(f"• {match_info} '{match['term']}' → '对应翻译'")

def demonstrate_confidence_meaning():
    """演示置信度的实际意义"""
    
    print("\n\n💡 置信度的实际意义")
    print("=" * 50)
    
    confidence_levels = [
        (1.0, "高置信度", "AI应该严格按照词典翻译", "精确匹配、变体匹配"),
        (0.9, "高置信度", "AI应该严格按照词典翻译", "变体匹配"),
        (0.8, "中等置信度", "AI可以参考词典，但需要结合上下文", "缩写匹配、部分匹配"),
        (0.75, "中等置信度", "AI可以参考词典，但需要结合上下文", "层级匹配"),
        (0.7, "中等置信度", "AI可以参考词典，但需要结合上下文", "部分匹配"),
        (0.6, "低置信度", "AI应该谨慎使用，可能需要人工确认", "模糊匹配"),
        (0.0, "无置信度", "AI不应该使用，需要人工处理", "完全不匹配")
    ]
    
    for confidence, level, suggestion, examples in confidence_levels:
        print(f"\n置信度 {confidence:.1f} ({level})")
        print(f"  建议: {suggestion}")
        print(f"  例子: {examples}")

if __name__ == "__main__":
    demonstrate_confidence_calculation()
    demonstrate_confidence_usage()
    demonstrate_confidence_meaning()
    
    print("\n\n✅ 置信度示例演示完成！")
    print("\n💡 总结:")
    print("• 置信度是系统对匹配结果的确信程度")
    print("• 高置信度 = 高优先级 = AI应该严格遵循")
    print("• 低置信度 = 低优先级 = AI需要谨慎使用")
    print("• 系统会自动排序、去重，并指导AI翻译")
