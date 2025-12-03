#!/usr/bin/env python3
"""
Patch ProofreadingPage.jsx to use project source_path for source files.

Key changes:
1. groupFiles: construct virtual source file objects using project.source_path
2. loadEditorData: accept source file PATH instead of ID, read directly from disk
3. handlers: pass source file path to loadEditorData
"""

import re
from pathlib import Path

def patch_proofreading_page():
    file_path = Path(__file__).parent / 'scripts' / 'react-ui' / 'src' / 'pages' / 'ProofreadingPage.jsx'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Store original
    backup_path = file_path.with_suffix('.jsx.backup2')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Backup created: {backup_path}")
    
    # Pattern 1: Replace groupFiles function
    group_files_pattern = r'(  const groupFiles = \(files\) => \{[\s\S]*?  \};)'
    
    new_group_files = r'''  const groupFiles = (files) => {
    if (!selectedProject) return;
    const sourceLang = selectedProject.source_language || 'english';
    const sourcePath = selectedProject.source_path;

    // Helper to get filename from path (handles both / and \)
    const getFileName = (path) => path.replace(/\\/g, '/').split('/').pop();

    // Construct virtual source files from translation files
    const virtualSources = [];
    const targetsMap = {};
    
    files.forEach(f => {
        if (f.file_type === 'translation') {
            const targetFileName = getFileName(f.file_path);
            
            // Extract base name: remis_demo_events_l_simp_chinese.yml -> remis_demo_events
            const match = targetFileName.match(/^(.+)_l_\w+\.yml$/);
            if (!match) return;
            
            const baseName = match[1];
            const sourceFileName = `${baseName}_l_${sourceLang}.yml`;
            
            // Construct source file path using project's source_path
            const sourceFilePath = `${sourcePath}/localisation/${sourceLang}/${sourceFileName}`.replace(/\\/g, '/');
            
            // Check if we already created a virtual source for this base name
            let virtualSource = virtualSources.find(vs => getFileName(vs.file_path) === sourceFileName);
            
            if (!virtualSource) {
                virtualSource = {
                    file_id: `virtual_source_${baseName}`,
                    file_path: sourceFilePath,
                    file_type: 'source',
                    name: sourceFileName
                };
                virtualSources.push(virtualSource);
                targetsMap[virtualSource.file_id] = [];
            }
            
            targetsMap[virtualSource.file_id].push(f);
        }
    });

    setSourceFiles(virtualSources);
    setTargetFilesMap(targetsMap);

    // Auto-load logic
    const urlFileId = searchParams.get('fileId');
    
    if (urlFileId) {
        let foundSource = null;
        let foundTarget = null;
        
        for (const vSource of virtualSources) {
            const targets = targetsMap[vSource.file_id];
            const target = targets.find(t => t.file_id === urlFileId);
            if (target) {
                foundSource = vSource;
                foundTarget = target;
                break;
            }
        }
        
        if (foundSource && foundTarget) {
            setCurrentSourceFile(foundSource);
            setCurrentTargetFile(foundTarget);
            loadEditorData(selectedProject.project_id, foundSource.file_path, foundTarget.file_id);
        }
        
    } else if (virtualSources.length > 0) {
        const firstSource = virtualSources[0];
        setCurrentSourceFile(firstSource);
        const targets = targetsMap[firstSource.file_id];
        if (targets && targets.length > 0) {
            setCurrentTargetFile(targets[0]);
            loadEditorData(selectedProject.project_id, firstSource.file_path, targets[0].file_id);
        } else {
            setCurrentTargetFile(null);
            loadEditorData(selectedProject.project_id, firstSource.file_path, null);
        }
    }
  };'''
    
    content = re.sub(group_files_pattern, new_group_files.strip(), content, count=1)
    
    # Pattern 2: Replace loadEditorData function signature and implementation
    load_editor_pattern = r'(  const loadEditorData = async \(pId, \w+, targetId\) => \{[\s\S]*?    \}\n  \};)'
    
    new_load_editor = '''  const loadEditorData = async (pId, sourceFilePath, targetId) => {
    setLoading(true);
    try {
        // 1. Load Source File - DIRECTLY FROM DISK using project source_path
        if (sourceFilePath) {
            try {
                const readRes = await axios.post('/api/system/read_file', { file_path: sourceFilePath });
                setOriginalContentStr(readRes.data.content || "");
            } catch (readError) {
                console.error("Failed to read source file from disk:", readError);
                setOriginalContentStr("");
            }
        } else {
            setOriginalContentStr("");
        }

        // 2. Load Target File - FROM DATABASE API
        if (targetId) {
            const resTarget = await axios.get(`/api/proofread/${pId}/${targetId}`);
            const data = resTarget.data;
            setFileInfo({ path: data.file_path, project_id: pId, file_id: targetId });
            setEntries(data.entries || []);
            
            if (data.file_content) {
                setAiContentStr(data.file_content);
                setFinalContentStr(data.file_content);
            } else {
                const { aiStr, finalStr } = alignEntries(data.entries || []);
                setAiContentStr(aiStr);
                setFinalContentStr(finalStr);
            }
        } else {
            setAiContentStr("");
            setFinalContentStr("");
            setEntries([]);
            setFileInfo(null);
        }

    } catch (error) {
      console.error("Failed to load editor data", error);
      notifications.show({ title: 'Error', message: "Failed to load file data.", color: 'red' });
    } finally {
      setLoading(false);
    }
  };'''
    
    content = re.sub(load_editor_pattern, new_load_editor.strip(), content, count=1)
    
    # Pattern 3: Fix handleSourceFileChange calls
    content = re.sub(
        r'loadEditorData\(selectedProject\.project_id, source\.file_id, targets\[0\]\.file_id\)',
        'loadEditorData(selectedProject.project_id, source.file_path, targets[0].file_id)',
        content
    )
    content = re.sub(
        r'loadEditorData\(selectedProject\.project_id, source\.file_id, null\)',
        'loadEditorData(selectedProject.project_id, source.file_path, null)',
        content
    )
    
    # Pattern 4: Fix handleTargetFileChange calls
    content = re.sub(
        r'loadEditorData\(selectedProject\.project_id, currentSourceFile\.file_id, target\.file_id\)',
        'loadEditorData(selectedProject.project_id, currentSourceFile.file_path, target.file_id)',
        content
    )
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Patched {file_path}")
    print("Key changes:")
    print("  - groupFiles now constructs virtual source files from project.source_path")
    print("  - loadEditorData accepts source file PATH instead of ID")
    print("  - Reads source files directly from disk using /api/system/read_file")

if __name__ == '__main__':
    patch_proofreading_page()
