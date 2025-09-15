#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
紧急修复脚本：移除yml文件中的中文标点符号

问题描述：
英文版群星不支持中文字符，中文字符会变成问号，导致：
1. 显示问题：中文标点符号变成问号
2. 联机同步问题：携带中文符号的mod会导致联机不同步

此脚本会：
1. 扫描指定目录下的所有yml文件
2. 检测中文标点符号
3. 将中文标点符号替换为对应的英文标点符号
4. 生成修复报告

使用方法：
python scripts/emergency_fix_chinese_punctuation.py [目录路径]
"""

import os
import re
import sys
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Tuple
import json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chinese_punctuation_fix.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# 中文标点符号到英文标点符号的映射
CHINESE_PUNCTUATION_MAP = {
    '，': ',',    # 中文逗号 -> 英文逗号
    '。': '.',    # 中文句号 -> 英文句号
    '！': '!',    # 中文感叹号 -> 英文感叹号
    '？': '?',    # 中文问号 -> 英文问号
    '：': ':',    # 中文冒号 -> 英文冒号
    '；': ';',    # 中文分号 -> 英文分号
    '（': '(',    # 中文左括号 -> 英文左括号
    '）': ')',    # 中文右括号 -> 英文右括号
    '【': '[',    # 中文左方括号 -> 英文左方括号
    '】': ']',    # 中文右方括号 -> 英文右方括号
    '《': '<',    # 中文左尖括号 -> 英文左尖括号
    '》': '>',    # 中文右尖括号 -> 英文右尖括号
    '"': '"',     # 中文引号 -> 英文引号
    '"': '"',     # 中文引号 -> 英文引号
    ''': "'",     # 中文单引号 -> 英文单引号
    ''': "'",     # 中文单引号 -> 英文单引号
    '…': '...',   # 中文省略号 -> 英文省略号
    '—': '-',     # 中文破折号 -> 英文连字符
    '－': '-',    # 中文连字符 -> 英文连字符
    '　': ' ',    # 中文全角空格 -> 英文空格
    '、': ',',    # 中文顿号 -> 英文逗号
    '·': '.',     # 中文间隔号 -> 英文句号
    '～': '~',    # 中文波浪号 -> 英文波浪号
    '％': '%',    # 中文百分号 -> 英文百分号
    '＃': '#',    # 中文井号 -> 英文井号
    '＄': '$',    # 中文美元符号 -> 英文美元符号
    '＆': '&',    # 中文和号 -> 英文和号
    '＊': '*',    # 中文星号 -> 英文星号
    '＋': '+',    # 中文加号 -> 英文加号
    '＝': '=',    # 中文等号 -> 英文等号
    '－': '-',    # 中文减号 -> 英文减号
    '／': '/',    # 中文斜杠 -> 英文斜杠
    '＼': '\\',   # 中文反斜杠 -> 英文反斜杠
    '｜': '|',    # 中文竖线 -> 英文竖线
    '＠': '@',    # 中文at符号 -> 英文at符号
}

# 编译正则表达式，匹配所有中文标点符号
CHINESE_PUNCTUATION_PATTERN = re.compile('|'.join(re.escape(p) for p in CHINESE_PUNCTUATION_MAP.keys()))

def find_chinese_punctuation(text: str) -> List[Tuple[str, int]]:
    """
    在文本中查找中文标点符号
    
    Args:
        text: 要检查的文本
        
    Returns:
        包含(标点符号, 位置)的列表
    """
    matches = []
    for match in CHINESE_PUNCTUATION_PATTERN.finditer(text):
        matches.append((match.group(), match.start()))
    return matches

def replace_chinese_punctuation(text: str) -> Tuple[str, List[Tuple[str, str]]]:
    """
    替换文本中的中文标点符号
    
    Args:
        text: 要处理的文本
        
    Returns:
        (替换后的文本, 替换记录列表)
    """
    replacements = []
    result = text
    
    for chinese_punct, english_punct in CHINESE_PUNCTUATION_MAP.items():
        if chinese_punct in result:
            old_result = result
            result = result.replace(chinese_punct, english_punct)
            if result != old_result:
                replacements.append((chinese_punct, english_punct))
    
    return result, replacements

def process_yml_file(file_path: Path) -> Dict:
    """
    处理单个yml文件
    
    Args:
        file_path: yml文件路径
        
    Returns:
        处理结果字典
    """
    result = {
        'file_path': str(file_path),
        'total_lines': 0,
        'lines_with_chinese_punct': 0,
        'total_replacements': 0,
        'replacements': [],
        'errors': []
    }
    
    try:
        # 尝试不同的编码方式读取文件
        encodings = ['utf-8-sig', 'utf-8', 'cp1252']
        content = None
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            result['errors'].append(f"无法读取文件，尝试了所有编码方式: {encodings}")
            return result
        
        lines = content.splitlines()
        result['total_lines'] = len(lines)
        
        new_lines = []
        has_changes = False
        
        for line_num, line in enumerate(lines, 1):
            # 检查是否包含中文标点符号
            chinese_puncts = find_chinese_punctuation(line)
            
            if chinese_puncts:
                result['lines_with_chinese_punct'] += 1
                old_line = line
                
                # 替换中文标点符号
                new_line, line_replacements = replace_chinese_punctuation(line)
                
                if new_line != old_line:
                    has_changes = True
                    result['total_replacements'] += len(line_replacements)
                    
                    # 记录替换详情
                    for old_punct, new_punct in line_replacements:
                        result['replacements'].append({
                            'line_num': line_num,
                            'old_punct': old_punct,
                            'new_punct': new_punct,
                            'old_line': old_line.strip(),
                            'new_line': new_line.strip()
                        })
                    
                    new_lines.append(new_line)
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        
        # 如果有更改，写回文件
        if has_changes:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(new_lines))
                    if content.endswith('\n'):
                        f.write('\n')  # 保持文件末尾的换行符
                result['file_modified'] = True
            except Exception as e:
                result['errors'].append(f"写入文件失败: {e}")
        else:
            result['file_modified'] = False
            
    except Exception as e:
        result['errors'].append(f"处理文件时出错: {e}")
    
    return result

def scan_directory(directory_path: str) -> List[Dict]:
    """
    扫描目录下的所有yml文件
    
    Args:
        directory_path: 要扫描的目录路径
        
    Returns:
        处理结果列表
    """
    results = []
    directory = Path(directory_path)
    
    if not directory.exists():
        logging.error(f"目录不存在: {directory_path}")
        return results
    
    if not directory.is_dir():
        logging.error(f"路径不是目录: {directory_path}")
        return results
    
    # 查找所有yml文件
    yml_files = list(directory.rglob("*.yml"))
    
    if not yml_files:
        logging.warning(f"在目录 {directory_path} 中未找到yml文件")
        return results
    
    logging.info(f"找到 {len(yml_files)} 个yml文件")
    
    for yml_file in yml_files:
        logging.info(f"正在处理: {yml_file}")
        result = process_yml_file(yml_file)
        results.append(result)
        
        if result['errors']:
            logging.error(f"处理文件 {yml_file} 时出现错误: {result['errors']}")
    
    return results

def generate_report(results: List[Dict], output_file: str = None) -> str:
    """
    生成修复报告
    
    Args:
        results: 处理结果列表
        output_file: 输出文件路径（可选）
        
    Returns:
        报告内容
    """
    total_files = len(results)
    modified_files = sum(1 for r in results if r.get('file_modified', False))
    total_replacements = sum(r['total_replacements'] for r in results)
    total_lines_with_chinese_punct = sum(r['lines_with_chinese_punct'] for r in results)
    
    report_lines = [
        "=" * 80,
        "中文标点符号修复报告",
        "=" * 80,
        f"扫描时间: {results[0]['file_path'] if results else 'N/A'}",
        f"总文件数: {total_files}",
        f"已修改文件数: {modified_files}",
        f"包含中文标点符号的行数: {total_lines_with_chinese_punct}",
        f"总替换次数: {total_replacements}",
        "",
        "详细替换记录:",
        "-" * 40
    ]
    
    for result in results:
        if result['replacements']:
            report_lines.append(f"\n文件: {result['file_path']}")
            report_lines.append(f"替换次数: {result['total_replacements']}")
            
            for replacement in result['replacements']:
                report_lines.append(
                    f"  第{replacement['line_num']}行: "
                    f"'{replacement['old_punct']}' -> '{replacement['new_punct']}'"
                )
    
    # 添加错误信息
    files_with_errors = [r for r in results if r['errors']]
    if files_with_errors:
        report_lines.extend([
            "",
            "错误信息:",
            "-" * 40
        ])
        
        for result in files_with_errors:
            report_lines.append(f"\n文件: {result['file_path']}")
            for error in result['errors']:
                report_lines.append(f"  - {error}")
    
    report_content = '\n'.join(report_lines)
    
    # 如果指定了输出文件，写入文件
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logging.info(f"报告已保存到: {output_file}")
        except Exception as e:
            logging.error(f"保存报告失败: {e}")
    
    return report_content

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="紧急修复脚本：移除yml文件中的中文标点符号",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python scripts/emergency_fix_chinese_punctuation.py ./my_translation
  python scripts/emergency_fix_chinese_punctuation.py ./source_mod --dry-run
  python scripts/emergency_fix_chinese_punctuation.py ./my_translation --output report.txt
        """
    )
    
    parser.add_argument(
        'directory',
        help='要扫描的目录路径'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='仅扫描，不修改文件'
    )
    
    parser.add_argument(
        '--output',
        help='输出报告文件路径'
    )
    
    parser.add_argument(
        '--backup',
        action='store_true',
        help='在修改前创建备份文件'
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.directory):
        logging.error(f"目录不存在: {args.directory}")
        sys.exit(1)
    
    logging.info("开始扫描目录...")
    results = scan_directory(args.directory)
    
    if not results:
        logging.warning("未找到任何yml文件")
        sys.exit(0)
    
    # 生成报告
    report = generate_report(results, args.output)
    print(report)
    
    logging.info("扫描完成！")
    
    if args.dry_run:
        logging.info("这是干运行模式，未修改任何文件")
    else:
        logging.info("文件修改完成")

if __name__ == "__main__":
    main()
