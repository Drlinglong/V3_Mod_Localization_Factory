import { useState, useRef, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { notifications } from '@mantine/notifications';
import axios from 'axios';
import { toParadoxLang } from '../utils/paradoxMapping';
import { groupFiles as performGrouping } from '../utils/fileGrouping';

/**
 * 校对页面的核心状态管理 Hook
 * 集中管理项目选择、文件导航、编辑器内容、验证和保存逻辑
 */
const useProofreadingState = () => {
    const [searchParams, setSearchParams] = useSearchParams();

    // ==================== 项目相关状态 ====================
    const [projects, setProjects] = useState([]);
    const [selectedProject, setSelectedProject] = useState(null);

    const [projectFilter, setProjectFilter] = useState('');

    // ==================== 文件导航状态 ====================
    const [sourceFiles, setSourceFiles] = useState([]);
    const [targetFilesMap, setTargetFilesMap] = useState({});
    const [currentSourceFile, setCurrentSourceFile] = useState(null);
    const [currentTargetFile, setCurrentTargetFile] = useState(null);

    // ==================== 编辑器内容状态 ====================
    const [entries, setEntries] = useState([]);
    const [originalContentStr, setOriginalContentStr] = useState('');
    const [aiContentStr, setAiContentStr] = useState('');
    const [finalContentStr, setFinalContentStr] = useState('');

    // ==================== 验证与保存状态 ====================
    const [validationResults, setValidationResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);
    const [stats, setStats] = useState({ error: 0, warning: 0 });
    const [keyChangeWarning, setKeyChangeWarning] = useState(false);
    const [saveModalOpen, setSaveModalOpen] = useState(false);
    const [fileInfo, setFileInfo] = useState(null);

    // ==================== Linter 模式状态 ====================
    const [linterContent, setLinterContent] = useState('');
    const [linterGameId, setLinterGameId] = useState('1');
    const [linterResults, setLinterResults] = useState([]);
    const [linterLoading, setLinterLoading] = useState(false);
    const [linterError, setLinterError] = useState(null);

    // ==================== 编辑器引用 ====================
    const originalEditorRef = useRef(null);
    const aiEditorRef = useRef(null);
    const finalEditorRef = useRef(null);
    const isScrolling = useRef(false);

    // ==================== 数据获取函数 ====================
    const fetchProjects = useCallback(async () => {
        try {
            const res = await axios.get('/api/projects?status=active');
            setProjects(res.data);
        } catch (error) {
            console.error("Failed to load projects", error);
        }
    }, []);

    // ==================== 辅助解析函数 ====================
    const alignEntries = useCallback((entries) => {
        let originalStr = "";
        let aiStr = "";
        let finalStr = "";

        entries.forEach(e => {
            const origText = e.original || "";
            const aiText = e.translation || "";
            const finalText = e.translation || "";

            const WRAP_WIDTH = 60;

            const calcLines = (text) => {
                if (!text) return 1;
                let len = 0;
                for (let i = 0; i < text.length; i++) {
                    len += text.charCodeAt(i) > 255 ? 2 : 1;
                }
                return Math.max(1, Math.ceil(len / WRAP_WIDTH));
            };

            const l1 = calcLines(origText);
            const l2 = calcLines(aiText);
            const maxL = Math.max(l1, l2);

            const pad1 = Math.max(0, maxL - l1);
            const pad2 = Math.max(0, maxL - l2);

            originalStr += `${e.key}:0 "${origText}"` + "\n".repeat(pad1) + "\n";
            aiStr += `${e.key}:0 "${aiText}"` + "\n".repeat(pad2) + "\n";
            finalStr += `${e.key}:0 "${finalText}"\n`;
        });

        return { originalStr, aiStr, finalStr };
    }, []);

    const parseEditorContentToEntries = useCallback((content) => {
        const entries = [];
        const regex = /^\s*([\w\.]+)(?:\s*:\s*\d+)?\s*"((?:[^"\\]|\\.)*)"/gm;
        let match;
        while ((match = regex.exec(content)) !== null) {
            entries.push({ key: match[1], value: match[2] });
        }
        return entries;
    }, []);

    const loadEditorData = useCallback(async (pId, sourceFilePath, targetId) => {
        setLoading(true);
        try {
            if (sourceFilePath && sourceFilePath.trim() !== '') {
                try {
                    const readRes = await axios.post('/api/system/read_file', { file_path: sourceFilePath });
                    setOriginalContentStr(readRes.data.content || "");
                } catch (readError) {
                    console.error("Failed to read source file:", readError);
                    setOriginalContentStr("");
                }
            } else {
                setOriginalContentStr("");
            }

            if (targetId) {
                const resTarget = await axios.get(`/api/proofread/${pId}/${targetId}`);
                const data = resTarget.data;
                setFileInfo({ path: data.file_path, project_id: pId, file_id: targetId });
                setEntries(data.entries || []);

                if (data.ai_content) {
                    setAiContentStr(data.ai_content);
                    setFinalContentStr(data.final_content || data.ai_content);
                } else if (data.file_content) {
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
    }, [alignEntries]);

    // ==================== 业务逻辑函数 ====================
    const groupFiles = useCallback((files) => {
        if (!selectedProject) return;

        const { sources, targetsMap } = performGrouping(files, selectedProject);

        setSourceFiles(sources);
        setTargetFilesMap(targetsMap);

        const urlFileId = searchParams.get('fileId');

        if (urlFileId) {
            let foundSource = null;
            let foundTarget = null;

            const isSource = sources.find(s => s.file_id === urlFileId);
            if (isSource) {
                foundSource = isSource;
                if (targetsMap[isSource.file_id]?.length > 0) {
                    foundTarget = targetsMap[isSource.file_id][0];
                }
            } else {
                for (const sId in targetsMap) {
                    const t = targetsMap[sId].find(t => t.file_id === urlFileId);
                    if (t) {
                        foundSource = sources.find(s => s.file_id === sId);
                        foundTarget = t;
                        break;
                    }
                }
            }

            if (foundSource) {
                setCurrentSourceFile(foundSource);
                if (foundTarget) {
                    setCurrentTargetFile(foundTarget);
                    loadEditorData(selectedProject.project_id, foundSource.file_path, foundTarget.file_id);
                } else {
                    setCurrentTargetFile(null);
                    loadEditorData(selectedProject.project_id, foundSource.file_path, null);
                }
            }

        } else if (sources.length > 0) {
            const firstSource = sources[0];
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
    }, [selectedProject, searchParams, loadEditorData]);

    const fetchProjectFiles = useCallback(async (projectId) => {
        try {
            const res = await axios.get(`/api/project/${projectId}/files`);
            if (res.data) {
                groupFiles(res.data);
            }
        } catch (error) {
            console.error("Failed to load project files", error);
        }
    }, [groupFiles]);

    // ==================== 事件处理器 ====================
    const handleProjectSelect = useCallback((val) => {
        const proj = projects.find(p => p.project_id === val);
        if (proj) {
            setSelectedProject(proj);
            setSearchParams({ projectId: proj.project_id });
        }
    }, [projects, setSearchParams]);

    const handleSourceFileChange = useCallback((val) => {
        const source = sourceFiles.find(s => s.file_id === val);
        if (source) {
            setCurrentSourceFile(source);
            const targets = targetFilesMap[source.file_id];
            if (targets && targets.length > 0) {
                setCurrentTargetFile(targets[0]);
                loadEditorData(selectedProject.project_id, source.file_path, targets[0].file_id);
                setSearchParams({ projectId: selectedProject.project_id, fileId: targets[0].file_id });
            } else {
                setCurrentTargetFile(null);
                loadEditorData(selectedProject.project_id, source.file_path, null);
                setSearchParams({ projectId: selectedProject.project_id, fileId: source.file_id });
            }
        }
    }, [sourceFiles, targetFilesMap, selectedProject, loadEditorData, setSearchParams]);

    const handleTargetFileChange = useCallback((val) => {
        if (!currentSourceFile) return;
        const targets = targetFilesMap[currentSourceFile.file_id];
        const target = targets.find(t => t.file_id === val);
        if (target) {
            setCurrentTargetFile(target);
            loadEditorData(selectedProject.project_id, currentSourceFile.file_path, target.file_id);
            setSearchParams({ projectId: selectedProject.project_id, fileId: target.file_id });
        }
    }, [currentSourceFile, targetFilesMap, selectedProject, loadEditorData, setSearchParams]);

    const handleValidate = useCallback(async () => {
        setLoading(true);
        setValidationResults([]);
        try {
            const parsed = parseEditorContentToEntries(finalContentStr);
            let virtualContent = "";
            parsed.forEach(e => {
                virtualContent += ` ${e.key}:0 "${e.value}"\n`;
            });

            const response = await axios.post('/api/validate/localization', {
                game_id: selectedProject.game_id || 'victoria3',
                content: virtualContent,
                source_lang_code: 'en_US'
            });

            const issues = response.data;
            setValidationResults(issues);

            const errors = issues.filter(i => i.level === 'error').length;
            const warnings = issues.filter(i => i.level === 'warning').length;
            setStats({ error: errors, warning: warnings });

            if (errors === 0 && warnings === 0) {
                notifications.show({ title: 'Perfect', message: 'No issues found.', color: 'green' });
            } else {
                notifications.show({ title: 'Issues Found', message: `Found ${errors} errors and ${warnings} warnings.`, color: 'yellow' });
            }

        } catch (error) {
            console.error("Validation failed", error);
            notifications.show({ title: 'Error', message: "Validation failed.", color: 'red' });
        } finally {
            setLoading(false);
        }
    }, [finalContentStr, parseEditorContentToEntries]);

    const confirmSave = useCallback(async () => {
        setSaveModalOpen(false);
        setSaving(true);
        try {
            const parsedEntries = parseEditorContentToEntries(finalContentStr);

            const savePayload = {
                project_id: fileInfo.project_id,
                file_id: fileInfo.file_id,
                entries: parsedEntries.map(e => ({
                    key: e.key,
                    translation: e.value
                })),
                target_language: `l_${toParadoxLang(selectedProject.source_language || 'english')}` // Heuristic: default to source lang if unknown, or ideally user should select target
            };

            await axios.post('/api/proofread/save', savePayload);

            notifications.show({ title: 'Saved', message: 'File saved successfully.', color: 'green' });

        } catch (error) {
            console.error("Save failed", error);
            notifications.show({ title: 'Error', message: "Failed to save file.", color: 'red' });
        } finally {
            setSaving(false);
        }
    }, [finalContentStr, fileInfo, parseEditorContentToEntries]);

    const handleSaveClick = useCallback(() => {
        if (keyChangeWarning) {
            setSaveModalOpen(true);
        } else {
            confirmSave();
        }
    }, [keyChangeWarning, confirmSave]);

    const handleOpenFolder = useCallback(async () => {
        if (!fileInfo || !fileInfo.path) return;
        try {
            const path = fileInfo.path.replace(/\\/g, '/');
            const dirPath = path.substring(0, path.lastIndexOf('/'));
            await axios.post('/api/system/open_folder', { path: dirPath });
            notifications.show({ title: 'Success', message: 'Folder opened', color: 'green' });
        } catch (error) {
            notifications.show({ title: 'Error', message: 'Failed to open folder', color: 'red' });
        }
    }, [fileInfo]);

    const handleLinterValidate = useCallback(async () => {
        if (!linterContent.trim()) return;
        setLinterLoading(true);
        setLinterError(null);
        setLinterResults([]);
        try {
            const response = await axios.post('/api/validate/localization', {
                game_id: linterGameId,
                content: linterContent,
                source_lang_code: 'en_US'
            });
            setLinterResults(response.data);
        } catch (err) {
            setLinterError("Failed to validate.");
        } finally {
            setLinterLoading(false);
        }
    }, [linterContent, linterGameId]);

    // ==================== 副作用 ====================
    // 初始化：获取项目列表
    useEffect(() => {
        fetchProjects();
    }, [fetchProjects]);

    // URL 参数同步
    useEffect(() => {
        const pId = searchParams.get('projectId');
        if (pId && projects.length > 0 && !selectedProject) {
            const proj = projects.find(p => p.project_id === pId);
            if (proj) setSelectedProject(proj);
        }
    }, [searchParams, projects, selectedProject]);

    // 项目切换：获取文件
    useEffect(() => {
        if (selectedProject) {
            fetchProjectFiles(selectedProject.project_id);
        }
    }, [selectedProject, fetchProjectFiles]);

    // 键值修改检测
    useEffect(() => {
        if (!entries.length || !finalContentStr) return;

        // Regex to extract keys from content: 
        // Matches: key:0 "value"
        // Improved: Allow whitespace around ':' and before key
        const currentKeys = new Set();
        const regex = /^\s*([\w\.]+)\s*:\s*0\s*"/gm;
        let match;
        while ((match = regex.exec(finalContentStr)) !== null) {
            currentKeys.add(match[1]);
        }

        const originalKeys = new Set(entries.map(e => e.key));

        let hasChanges = false;
        if (currentKeys.size !== originalKeys.size) {
            hasChanges = true;
        } else {
            for (let k of currentKeys) {
                if (!originalKeys.has(k)) {
                    hasChanges = true;
                    break;
                }
            }
        }

        setKeyChangeWarning(hasChanges);
    }, [finalContentStr, entries]);

    // 同步滚动
    useEffect(() => {
        const editors = [originalEditorRef, aiEditorRef, finalEditorRef];
        const disposables = [];

        const syncScroll = (sourceEditor, e) => {
            if (isScrolling.current) return;
            isScrolling.current = true;
            const scrollTop = e.scrollTop;
            const scrollLeft = e.scrollLeft;
            editors.forEach(ref => {
                if (ref.current && ref.current !== sourceEditor) {
                    ref.current.setScrollPosition({ scrollTop, scrollLeft });
                }
            });
            setTimeout(() => { isScrolling.current = false; }, 50);
        };

        const attachListeners = () => {
            editors.forEach(ref => {
                if (ref.current) {
                    const disposable = ref.current.onDidScrollChange((e) => syncScroll(ref.current, e));
                    disposables.push(disposable);
                }
            });
        };

        const timer = setTimeout(attachListeners, 500);
        return () => { clearTimeout(timer); disposables.forEach(d => d && d.dispose()); };
    }, [originalContentStr, aiContentStr, finalContentStr]);

    // ==================== 返回接口 ====================
    return {
        // 项目相关
        projects,
        selectedProject,
        setSelectedProject,

        projectFilter,
        setProjectFilter,

        // 文件相关
        sourceFiles,
        targetFilesMap,
        currentSourceFile,
        currentTargetFile,
        setCurrentSourceFile,
        setCurrentTargetFile,

        // 编辑器内容
        originalContentStr,
        aiContentStr,
        finalContentStr,
        setFinalContentStr,

        // 验证与保存
        validationResults,
        stats,
        saving,
        loading,
        keyChangeWarning,
        saveModalOpen,
        setSaveModalOpen,
        fileInfo,

        // Linter 模式
        linterContent,
        setLinterContent,
        linterGameId,
        setLinterGameId,
        linterResults,
        linterLoading,
        linterError,

        // 引用
        originalEditorRef,
        aiEditorRef,
        finalEditorRef,

        // 事件处理器
        handleProjectSelect,
        handleSourceFileChange,
        handleTargetFileChange,
        handleValidate,
        handleSaveClick,
        confirmSave,
        handleLinterValidate,
        handleOpenFolder,
    };
};

export default useProofreadingState;
