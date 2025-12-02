#!/usr/bin/env python3
"""
YML File Cleanup Script
Fixes formatting issues in source YML files:
1. Removes malformed/truncated entries
2. Moves inline annotations (like "Target: xxx") to comments
3. Fixes encoding issues
4. Validates YML format
"""

import os
import re
from pathlib import Path

def clean_yml_file(file_path):
    """Clean a single YML file."""
    print(f"\n{'='*60}")
    print(f"Processing: {file_path}")
    print(f"{'='*60}")
    
    # Read file
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    cleaned_lines = []
    header_found = False
    issues_found = []
    
    for i, line in enumerate(lines, 1):
        # Keep header line
        if line.strip().startswith('l_'):
            cleaned_lines.append(line)
            header_found = True
            continue
        
        # Keep comment lines
        if line.strip().startswith('#') or line.strip() == '':
            cleaned_lines.append(line)
            continue
        
        # Process entry lines
        if ':' in line and header_found:
            # Check if line is malformed
            # Valid format: key:version "value"
            match = re.match(r'^\s*([a-zA-Z0-9_\.]+):(\d+)\s+"(.*)"(?:\s*#.*)?$', line.rstrip())
            
            if match:
                key, version, value = match.groups()
                
                # Check for inline annotations that should be comments
                # Pattern: (Target: xxx) or (译名: xxx) etc.
                target_pattern = r'\s*(?:\((?:Target|译名|翻译):\s*[^)]+\))\s*'
                if re.search(target_pattern, value):
                    # Extract annotations
                    annotations = re.findall(target_pattern, value)
                    # Remove from value
                    clean_value = re.sub(target_pattern, '', value).strip()
                    # Build comment
                    comment_text = ' '.join(ann.strip() for ann in annotations)
                    cleaned_lines.append(f' {key}:{version} "{clean_value}" # {comment_text}\n')
                    issues_found.append(f"Line {i}: Moved annotation to comment")
                else:
                    cleaned_lines.append(line)
            else:
                # Line doesn't match valid format
                # Check if it's severely corrupted (truncated, encoding issues)
                if len(line.strip()) > 1000 or '\n\n\n' in line or '搂' in line:
                    issues_found.append(f"Line {i}: REMOVED corrupted entry: {line[:50]}...")
                    print(f"  WARNING: Removed corrupted line {i}")
                else:
                    # Try to salvage if it looks like a valid key
                    if re.match(r'^\s*[a-zA-Z0-9_\.]+:', line):
                        cleaned_lines.append(line)
                    else:
                        issues_found.append(f"Line {i}: REMOVED malformed entry: {line[:50]}...")
                        print(f"  WARNING: Removed malformed line {i}")
    
    # Write back
    backup_path = file_path + '.backup'
    try:
        # Create backup
        with open(backup_path, 'w', encoding='utf-8-sig') as f:
            f.writelines(lines)
        print(f"  Backup created: {backup_path}")
        
        # Write cleaned version
        with open(file_path, 'w', encoding='utf-8-sig') as f:
            f.writelines(cleaned_lines)
        print(f"  Cleaned file written")
        
        # Report
        if issues_found:
            print(f"\n  Issues fixed ({len(issues_found)}):")
            for issue in issues_found[:10]:  # Show first 10
                print(f"    - {issue}")
            if len(issues_found) > 10:
                print(f"    ... and {len(issues_found) - 10} more")
        else:
            print("  No issues found - file was clean")
        
        return True
    except Exception as e:
        print(f"  Error writing file: {e}")
        return False

def main():
    """Main function."""
    base_dir = Path(__file__).parent / 'source_mod' / 'Test_Project_Remis_stellaris' / 'localisation' / 'english'
    
    if not base_dir.exists():
        print(f"Error: Directory not found: {base_dir}")
        return
    
    yml_files = list(base_dir.glob('*.yml'))
    
    if not yml_files:
        print(f"No YML files found in {base_dir}")
        return
    
    print(f"Found {len(yml_files)} YML files to process")
    
    success_count = 0
    for yml_file in yml_files:
        if clean_yml_file(yml_file):
            success_count += 1
    
    print(f"\n{'='*60}")
    print(f"Summary: {success_count}/{len(yml_files)} files processed successfully")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
