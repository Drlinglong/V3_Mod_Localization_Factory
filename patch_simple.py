#!/usr/bin/env python3
"""
Simple script to patch ProofreadingPage.jsx - Manual string find/replace approach.
"""

from pathlib import Path

def patch_file():
    file_path = Path(__file__).parent / 'scripts' / 'react-ui' / 'src' / 'pages' / 'ProofreadingPage.jsx'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_path = file_path.with_suffix('.jsx.backup3')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Backup: {backup_path}")
    
    # Find and replace loadEditorData signature
    # Change: (pId, sourceId, targetId) => to (pId, sourceFilePath, targetId) =>
    content = content.replace(
        'const loadEditorData = async (pId, sourceId, targetId) =>',
        'const loadEditorData = async (pId, sourceFilePath, targetId) =>'
    )
    
    # Replace all calls: foundSource.file_id -> foundSource.file_path
    content = content.replace(
        'loadEditorData(selectedProject.project_id, foundSource.file_id,',
        'loadEditorData(selectedProject.project_id, foundSource.file_path,'
    )
    
    # Replace all calls: firstSource.file_id -> firstSource.file_path
    content = content.replace(
        'loadEditorData(selectedProject.project_id, firstSource.file_id,',
        'loadEditorData(selectedProject.project_id, firstSource.file_path,'
    )
    
    # Replace all calls: source.file_id -> source.file_path  
    content = content.replace(
        'loadEditorData(selectedProject.project_id, source.file_id,',
        'loadEditorData(selectedProject.project_id, source.file_path,'
    )
    
    # Replace all calls: currentSourceFile.file_id -> currentSourceFile.file_path
    content = content.replace(
        'loadEditorData(selectedProject.project_id, currentSourceFile.file_id,',
        'loadEditorData(selectedProject.project_id, currentSourceFile.file_path,'
    )
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Patched {file_path}")
    print("  - loadEditorData signature updated")
    print("  - All loadEditorData calls updated to use file_path instead of file_id")

if __name__ == '__main__':
    patch_file()
