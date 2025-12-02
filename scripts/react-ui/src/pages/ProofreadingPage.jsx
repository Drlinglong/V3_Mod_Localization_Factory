import React, { useState, useRef, useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Paper,
  Title,
  Text,
  Button,
  Group,
  Stack,
  Badge,
  Tooltip,
  LoadingOverlay,
  Select,
  Tabs,
  Table,
  TextInput,
  Textarea,
  ScrollArea,
  ActionIcon,
  Alert,
  Modal,
  Collapse,
  Divider,
  Box
} from '@mantine/core';
import {
  IconDeviceFloppy,
  IconCheck,
  IconAlertTriangle,
  IconX,
  IconFileText,
  IconEdit,
  IconFolder,
  IconArrowRight,
  IconAlertCircle,
  IconDatabase,
  IconChevronDown,
  IconChevronUp,
  IconSearch
} from '@tabler/icons-react';
import { notifications } from '@mantine/notifications';
import layoutStyles from '../components/layout/Layout.module.css';
import axios from 'axios';
import MonacoWrapper from '../components/common/MonacoWrapper';
import { useSearchParams } from 'react-router-dom';

const ProofreadingPage = () => {
  const { t } = useTranslation();
  const [searchParams, setSearchParams] = useSearchParams();

  // Project & File State
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [isHeaderOpen, setIsHeaderOpen] = useState(false);
  const [projectFilter, setProjectFilter] = useState('');

  // File Navigation State
  const [sourceFiles, setSourceFiles] = useState([]); // List of source files
  const [targetFilesMap, setTargetFilesMap] = useState({}); // Map: source_file_id -> [target_files]
  const [currentSourceFile, setCurrentSourceFile] = useState(null); // Selected Source File Object
  const [currentTargetFile, setCurrentTargetFile] = useState(null); // Selected Target File Object

  // Tab State
  const [activeTab, setActiveTab] = useState('file');
  const [zoomLevel, setZoomLevel] = useState('1');

  // Content State
  // entries: { key, original, translation, line_number }
  const [entries, setEntries] = useState([]);

  // String representations for Editors
  const [originalContentStr, setOriginalContentStr] = useState('');
  const [aiContentStr, setAiContentStr] = useState('');
  const [finalContentStr, setFinalContentStr] = useState('');

  const [validationResults, setValidationResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [stats, setStats] = useState({ error: 0, warning: 0 });

  // Key Modification Detection
  const [keyChangeWarning, setKeyChangeWarning] = useState(false);
  const [saveModalOpen, setSaveModalOpen] = useState(false);

  // Metadata
  const [fileInfo, setFileInfo] = useState(null);

  // Refs for sync scrolling
  const originalEditorRef = useRef(null);
  const aiEditorRef = useRef(null);
  const finalEditorRef = useRef(null);
  const isScrolling = useRef(false);

  // --- Free Mode (Linter) State ---
  const [linterContent, setLinterContent] = useState('');
  const [linterGameId, setLinterGameId] = useState('1');
  const [linterResults, setLinterResults] = useState([]);
  const [linterLoading, setLinterLoading] = useState(false);
  const [linterError, setLinterError] = useState(null);

  // --- Initialization & Data Fetching ---
  useEffect(() => {
    fetchProjects();
  }, []);

  // Sync URL params with state
  useEffect(() => {
    const pId = searchParams.get('projectId');
    const fId = searchParams.get('fileId');
    if (pId && projects.length > 0 && !selectedProject) {
      const proj = projects.find(p => p.project_id === pId);
      if (proj) setSelectedProject(proj);
    }
  }, [searchParams, projects]);

  useEffect(() => {
    if (selectedProject) {
      fetchProjectFiles(selectedProject.project_id);
    }
  }, [selectedProject]);

  const fetchProjects = async () => {
    try {
      const res = await axios.get('/api/projects?status=active');
      setProjects(res.data);
    } catch (error) {
      console.error("Failed to load projects", error);
    }
  };

  const fetchProjectFiles = async (pId) => {
    try {
      const res = await axios.get(`/api/project/${pId}/files`);
      const files = res.data;
      groupFiles(files);
    } catch (error) {
      console.error("Failed to load project files", error);
    }
  };

  const groupFiles = (files) => {
    if (!selectedProject) return;
    const sourceLang = selectedProject.source_language || 'english';

    // 1. Identify Source Files
    // Pattern: ends with _l_<sourceLang>.yml
    const sourcePattern = `_l_${sourceLang}.yml`;
    const sources = files.filter(f => f.file_path.endsWith(sourcePattern));

    // 2. Group Target Files
    // Map source file ID -> List of target files
    // We match by base name. 
    // Source: foo_l_english.yml -> Base: foo
    // Target: foo_l_german.yml -> Base: foo

    const targetsMap = {};
    const sourceBaseMap = {}; // base -> sourceFile

    // Helper to get filename from path (handles both / and \)
    const getFileName = (path) => path.replace(/\\/g, '/').split('/').pop();

    sources.forEach(s => {
      const fileName = getFileName(s.file_path);
      const baseName = fileName.replace(sourcePattern, '');
      sourceBaseMap[baseName] = s;
      targetsMap[s.file_id] = [];
    });

    files.forEach(f => {
      if (f.file_type === 'source') return; // Skip source files (already handled)

      const fileName = getFileName(f.file_path);
      for (const base in sourceBaseMap) {
        if (fileName.startsWith(base + '_l_') && f.file_id !== sourceBaseMap[base].file_id) {
          targetsMap[sourceBaseMap[base].file_id].push(f);
          break;
        }
      }
    });

    setSourceFiles(sources);
    setTargetFilesMap(targetsMap);

    // Auto-load logic
    // If URL has fileId, try to load that.
    // Else, load first source and its first target.
    const urlFileId = searchParams.get('fileId');

    if (urlFileId) {
      // Find which source this target belongs to
      let foundSource = null;
      let foundTarget = null;

      // Check if it is a source file
      const isSource = sources.find(s => s.file_id === urlFileId);
      if (isSource) {
        foundSource = isSource;
        // Try to find first target
        if (targetsMap[isSource.file_id]?.length > 0) {
          foundTarget = targetsMap[isSource.file_id][0];
        }
      } else {
        // Must be a target file
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
          loadEditorData(selectedProject.project_id, foundSource.file_id, foundTarget.file_id);
        } else {
          // Load source as target (fallback)
          setCurrentTargetFile(null);
          loadEditorData(selectedProject.project_id, foundSource.file_id, null);
        }
      }

    } else if (sources.length > 0) {
      const firstSource = sources[0];
      setCurrentSourceFile(firstSource);
      const targets = targetsMap[firstSource.file_id];
      if (targets && targets.length > 0) {
        setCurrentTargetFile(targets[0]);
        loadEditorData(selectedProject.project_id, firstSource.file_id, targets[0].file_id);
      } else {
        setCurrentTargetFile(null);
        loadEditorData(selectedProject.project_id, firstSource.file_id, null);
      }
    }
  };

  // Detect Key Changes
  useEffect(() => {
    if (!entries.length || !finalContentStr) return;

    // Parse current keys from finalContentStr
    const currentKeys = new Set();
    const regex = /([\w\.]+):0\s*"/g;
    let match;
    while ((match = regex.exec(finalContentStr)) !== null) {
      currentKeys.add(match[1]);
    }

    // Check against original keys
    const originalKeys = new Set(entries.map(e => e.key));

    // Simple check: Are sets equal?
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

  const loadEditorData = async (pId, sourceId, targetId) => {
    setLoading(true);
    try {
      // 1. Load Source File (for Original Column)
      // If sourceId exists in DB, load from API. Otherwise, infer from target file path.
      if (sourceId) {
        try {
          const resSource = await axios.get(`/api/proofread/${pId}/${sourceId}`);
          setOriginalContentStr(resSource.data.original_content || "");
        } catch (error) {
          // Source file not in DB, try to infer from target file
          if (targetId) {
            const resTarget = await axios.get(`/api/proofread/${pId}/${targetId}`);
            const targetPath = resTarget.data.file_path;

            // Infer source file path
            // Pattern: replace _l_<targetLang> with _l_<sourceLang>
            // Also replace target language folder with source language folder
            const sourceLang = selectedProject?.source_language || 'english';

            // Example: .../simp_chinese/xxx_l_simp_chinese.yml -> .../english/xxx_l_english.yml
            let sourcePath = targetPath;

            // Replace language suffix in filename
            sourcePath = sourcePath.replace(/_l_\w+\.yml$/, `_l_${sourceLang}.yml`);

            // Replace language folder (last component before filename)
            const parts = sourcePath.replace(/\\/g, '/').split('/');
            const filename = parts[parts.length - 1];
            const folderIdx = parts.length - 2;

            // Check if the folder is a language folder
            if (['simp_chinese', 'english', 'french', 'german', 'russian', 'spanish', 'japanese', 'korean'].includes(parts[folderIdx])) {
              parts[folderIdx] = sourceLang;
            }

            sourcePath = parts.join('/');

            console.log(`[Proofreading] Inferred source file path: ${sourcePath}`);

            // Read source file directly from disk
            try {
              const readRes = await axios.post('/api/system/read_file', { file_path: sourcePath });
              setOriginalContentStr(readRes.data.content || "");
            } catch (readError) {
              console.error("Failed to read source file from disk:", readError);
              setOriginalContentStr("");
            }
          } else {
            setOriginalContentStr("");
          }
        }
      } else {
        setOriginalContentStr("");
      }

      // 2. Load Target File (for AI/Final Columns)
      if (targetId) {
        const resTarget = await axios.get(`/api/proofread/${pId}/${targetId}`);
        const data = resTarget.data;
        setFileInfo({ path: data.file_path, project_id: pId, file_id: targetId }); // File info tracks the EDITABLE file (Target)
        setEntries(data.entries || []);

        if (data.file_content) {
          setAiContentStr(data.file_content);
          setFinalContentStr(data.file_content);
        } else {
          // Fallback alignment
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
  };

  // --- Alignment Logic ---
  const alignEntries = (entries) => {
    let originalStr = "";
    let aiStr = "";
    let finalStr = "";

    entries.forEach(e => {
      const origText = e.original || "";
      const aiText = e.translation || "";
      const finalText = e.translation || "";

      // Fixed wrap width to match Monaco 'wordWrapColumn'
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
      // We don't align finalStr anymore because it's free-text with comments
      // But we calculate it for fallback
      const l3 = calcLines(finalText);
      const maxL = Math.max(l1, l2); // Only align first two columns

      const pad1 = Math.max(0, maxL - l1);
      const pad2 = Math.max(0, maxL - l2);

      originalStr += `${e.key}:0 "${origText}"` + "\n".repeat(pad1) + "\n";
      aiStr += `${e.key}:0 "${aiText}"` + "\n".repeat(pad2) + "\n";
      finalStr += `${e.key}:0 "${finalText}"\n`; // No padding for finalStr
    });

    return { originalStr, aiStr, finalStr };
  };

  // --- Handlers ---

  const handleProjectSelect = (val) => {
    const proj = projects.find(p => p.project_id === val);
    if (proj) {
      setSelectedProject(proj);
      // Update URL without reloading
      setSearchParams({ projectId: proj.project_id });
    }
  };

  const handleSourceFileChange = (val) => {
    const source = sourceFiles.find(s => s.file_id === val);
    if (source) {
      setCurrentSourceFile(source);
      // Auto-select first target
      const targets = targetFilesMap[source.file_id];
      if (targets && targets.length > 0) {
        setCurrentTargetFile(targets[0]);
        loadEditorData(selectedProject.project_id, source.file_id, targets[0].file_id);
        setSearchParams({ projectId: selectedProject.project_id, fileId: targets[0].file_id });
      } else {
        // Fallback to source only
        setCurrentTargetFile(null);
        loadEditorData(selectedProject.project_id, source.file_id, null);
        setSearchParams({ projectId: selectedProject.project_id, fileId: source.file_id });
      }
    }
  };

  const handleTargetFileChange = (val) => {
    // Find target in current map
    if (!currentSourceFile) return;
    const targets = targetFilesMap[currentSourceFile.file_id];
    const target = targets.find(t => t.file_id === val);
    if (target) {
      setCurrentTargetFile(target);
      loadEditorData(selectedProject.project_id, currentSourceFile.file_id, target.file_id);
      setSearchParams({ projectId: selectedProject.project_id, fileId: target.file_id });
    }
  };

  const parseEditorContentToEntries = (content) => {
    const entries = [];
    const regex = /([\w\.]+):0\s*"((?:[^"\\]|\\.)*)"/g;
    let match;
    while ((match = regex.exec(content)) !== null) {
      entries.push({ key: match[1], value: match[2] });
    }
    return entries;
  };

  const handleValidate = async () => {
    setLoading(true);
    setValidationResults([]);
    try {
      // Validate current content (virtual file)
      const parsed = parseEditorContentToEntries(finalContentStr);
      let virtualContent = "";
      parsed.forEach(e => {
        virtualContent += ` ${e.key}:0 "${e.value}"\n`;
      });

      const response = await axios.post('/api/validate/localization', {
        game_id: 'victoria3', // TODO: Get from project settings
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
  };

  const handleSaveClick = () => {
    if (keyChangeWarning) {
      setSaveModalOpen(true);
    } else {
      confirmSave();
    }
  };

  const confirmSave = async () => {
    setSaveModalOpen(false);
    setSaving(true);
    try {
      const parsedEntries = parseEditorContentToEntries(finalContentStr);

      // Map back to original line numbers for patching
      // We iterate over parsedEntries (current state)
      // For each entry, find its original line_number from `entries` state

      // Create a map for fast lookup
      const originalMap = new Map(entries.map(e => [e.key, e.line_number]));

      const patchEntries = parsedEntries.map(e => ({
        key: e.key,
        value: e.value,
        line_number: originalMap.get(e.key) || null // If new key, line_number is null (append)
      }));

      await axios.post('/api/system/patch_file', {
        file_path: fileInfo.path,
        entries: patchEntries
      });

      notifications.show({ title: 'Saved', message: 'File patched successfully.', color: 'green' });

    } catch (error) {
      console.error("Save failed", error);
      notifications.show({ title: 'Error', message: "Failed to save file.", color: 'red' });
    } finally {
      setSaving(false);
    }
  };

  // Sync Scrolling
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

  // --- Free Mode Handlers ---
  const handleOpenFolder = async () => {
    if (!fileInfo || !fileInfo.path) return;
    try {
      const path = fileInfo.path.replace(/\\/g, '/');
      const dirPath = path.substring(0, path.lastIndexOf('/'));
      await axios.post('/api/system/open_folder', { path: dirPath });
      notifications.show({ title: 'Success', message: 'Folder opened', color: 'green' });
    } catch (error) {
      notifications.show({ title: 'Error', message: 'Failed to open folder', color: 'red' });
    }
  };

  const handleLinterValidate = async () => {
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
  };

  const getLevelColor = (level) => {
    switch (level) {
      case 'error': return 'red';
      case 'warning': return 'yellow';
      default: return 'gray';
    }
  };

  return (
    <div style={{ height: 'calc(100vh - 20px)', display: 'flex', flexDirection: 'column', padding: '10px', width: '100%' }}>
      <Paper withBorder p="xs" radius="md" className={layoutStyles.glassCard} style={{ flex: 1, display: 'flex', flexDirection: 'column', width: '100%', overflow: 'hidden' }}>

        {/* --- Header --- */}
        <Group position="apart" mb="xs">
          <Group>
            <Title order={4}>{t('page_title_proofreading')}</Title>
            <Button
              variant="subtle"
              size="xs"
              onClick={() => setIsHeaderOpen(!isHeaderOpen)}
              rightSection={isHeaderOpen ? <IconChevronUp size={14} /> : <IconChevronDown size={14} />}
            >
              {selectedProject ? selectedProject.name : "Select Project"}
            </Button>
          </Group>
          <Group>
            <Select
              value={zoomLevel}
              onChange={(val) => setZoomLevel(val)}
              data={[
                { value: '1', label: '100%' },
                { value: '1.1', label: '110%' },
                { value: '1.25', label: '125%' },
                { value: '1.5', label: '150%' },
                { value: '1.75', label: '175%' },
                { value: '2', label: '200%' },
              ]}
              size="xs"
              style={{ width: 80 }}
            />
            <Button
              variant="default"
              size="xs"
              leftSection={<IconFolder size={14} />}
              onClick={handleOpenFolder}
            >
              {t('proofreading.open_folder')}
            </Button>
            <Tabs value={activeTab} onChange={setActiveTab} variant="pills" radius="md">
              <Tabs.List>
                <Tabs.Tab value="file" leftSection={<IconFileText size={14} />}>{t('proofreading.tab_file_mode')}</Tabs.Tab>
                <Tabs.Tab value="free" leftSection={<IconEdit size={14} />}>{t('proofreading.tab_free_mode')}</Tabs.Tab>
              </Tabs.List>
            </Tabs>
          </Group>
        </Group>

        <Collapse in={isHeaderOpen}>
          <Paper withBorder p="sm" mb="sm" style={{ background: 'rgba(0,0,0,0.2)' }}>
            <Group>
              <Select
                label="Select Project"
                placeholder="Search projects..."
                data={projects.map(p => ({ value: p.project_id, label: `${p.name} (${p.game_id})` }))}
                value={selectedProject?.project_id}
                onChange={handleProjectSelect}
                searchable
                style={{ flex: 1 }}
              />
            </Group>
          </Paper>
        </Collapse>

        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', zoom: zoomLevel }}>
          <Tabs value={activeTab} style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <Tabs.Panel value="file" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
              <Stack spacing="xs" mb="xs">
                <Group position="apart">
                  <Group spacing="xs">
                    <Text size="sm" c="dimmed">{t('proofreading.mode.soft_protection')}</Text>
                  </Group>

                  <Group spacing="xs">
                    <Tooltip label="Errors">
                      <Badge color="red" leftSection={<IconX size={10} />} size="sm">{stats.error}</Badge>
                    </Tooltip>
                    <Tooltip label="Warnings">
                      <Badge color="yellow" leftSection={<IconAlertTriangle size={10} />} size="sm">{stats.warning}</Badge>
                    </Tooltip>

                    <Button
                      leftSection={<IconCheck size={14} />}
                      onClick={handleValidate}
                      loading={loading}
                      variant="light"
                      size="xs"
                    >
                      {t('proofreading.validate')}
                    </Button>
                    <Button
                      leftSection={<IconDeviceFloppy size={14} />}
                      onClick={handleSaveClick}
                      loading={saving}
                      size="xs"
                      color={keyChangeWarning ? "red" : "blue"}
                    >
                      {t('proofreading.save')}
                    </Button>
                  </Group>
                </Group>
              </Stack>

              {/* 3-Column Layout */}
              <div style={{ flex: 1, display: 'flex', flexDirection: 'row', gap: '10px', overflow: 'hidden', width: '100%' }}>
                {/* Column 1: Original (Read Only) */}
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', minWidth: 0 }}>
                  <Group mb={4} justify="space-between">
                    <Text fw={500} size="xs">{t('proofreading.original')}</Text>
                    <Select
                      size="xs"
                      placeholder="Select Source File"
                      data={sourceFiles.map(f => ({ value: f.file_id, label: f.file_path.split('/').pop() }))}
                      value={currentSourceFile?.file_id}
                      onChange={handleSourceFileChange}
                      style={{ width: '200px' }}
                    />
                  </Group>

                  {/* Source Hint */}
                  <Alert
                    variant="light"
                    color="gray"
                    icon={<IconFileText size={14} />}
                    style={{ marginBottom: 8, padding: '6px', minHeight: '52px', display: 'flex', alignItems: 'center' }}
                    styles={{ message: { marginTop: 0 } }}
                  >
                    <Text size="xs" c="dimmed">
                      {t('proofreading.hint.original_source')}
                    </Text>
                  </Alert>

                  <MonacoWrapper
                    scrollRef={originalEditorRef}
                    value={originalContentStr}
                    readOnly={true}
                    theme="vs-dark"
                    language="yaml"
                  />
                </div>

                {/* Column 2: AI Draft (Read Only) */}
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', minWidth: 0 }}>
                  <Group mb={4} justify="space-between">
                    <Text fw={500} size="xs">{t('proofreading.ai_draft')}</Text>
                    <Select
                      size="xs"
                      placeholder="Select Translation"
                      data={currentSourceFile && targetFilesMap[currentSourceFile.file_id]
                        ? targetFilesMap[currentSourceFile.file_id].map(f => ({ value: f.file_id, label: f.file_path.split('/').pop() }))
                        : []}
                      value={currentTargetFile?.file_id}
                      onChange={handleTargetFileChange}
                      style={{ width: '200px' }}
                      disabled={!currentSourceFile}
                    />
                  </Group>

                  {/* Source Hint */}
                  <Alert
                    variant="light"
                    color="gray"
                    icon={<IconDatabase size={14} />}
                    style={{ marginBottom: 8, padding: '6px', minHeight: '52px', display: 'flex', alignItems: 'center' }}
                    styles={{ message: { marginTop: 0 } }}
                  >
                    <Text size="xs" c="dimmed">
                      {t('proofreading.hint.ai_source')}
                    </Text>
                  </Alert>

                  <MonacoWrapper
                    scrollRef={aiEditorRef}
                    value={aiContentStr}
                    readOnly={true}
                    theme="vs-dark"
                    language="yaml"
                  />
                </div>

                {/* Column 3: Final Edit (Monaco with Warning) */}
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', minWidth: 0 }}>
                  <Group justify="space-between" mb={4}>
                    <Group>
                      <Text fw={500} size="xs">{t('proofreading.final_edit')}</Text>
                      <Select
                        size="xs"
                        placeholder="Select Translation"
                        data={currentSourceFile && targetFilesMap[currentSourceFile.file_id]
                          ? targetFilesMap[currentSourceFile.file_id].map(f => ({ value: f.file_id, label: f.file_path.split('/').pop() }))
                          : []}
                        value={currentTargetFile?.file_id}
                        onChange={handleTargetFileChange}
                        style={{ width: '200px' }}
                        disabled={!currentSourceFile}
                      />
                    </Group>
                    {keyChangeWarning && (
                      <Badge color="red" variant="filled" size="xs" leftSection={<IconAlertTriangle size={10} />}>
                        {t('proofreading.warning.key_modified')}
                      </Badge>
                    )}
                  </Group>

                  <div style={{ position: 'relative', flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0, overflow: 'hidden' }}>
                    {keyChangeWarning && (
                      <Alert
                        variant="filled"
                        color="red"
                        title={t('proofreading.warning.key_modified_title')}
                        icon={<IconAlertCircle size={16} />}
                        style={{ marginBottom: 8 }}
                      >
                        <Text size="xs">
                          {t('proofreading.warning.key_modified_desc')}
                        </Text>
                      </Alert>
                    )}

                    {/* Subtle Hint for Comments + Source */}
                    <Alert
                      variant="light"
                      color="gray"
                      icon={<IconFileText size={14} />}
                      style={{ marginBottom: 8, padding: '6px', minHeight: '52px', display: 'flex', alignItems: 'center' }}
                      styles={{ message: { marginTop: 0 } }}
                    >
                      <Stack spacing={0}>
                        <Text size="xs" c="dimmed" fw={500}>
                          {t('proofreading.hint.final_source')}
                        </Text>
                        <Text size="xs" c="dimmed">
                          {t('proofreading.hint.comments_ignored')}
                        </Text>
                      </Stack>
                    </Alert>

                    <LoadingOverlay visible={loading || saving} overlayProps={{ blur: 2 }} />
                    <MonacoWrapper
                      scrollRef={finalEditorRef}
                      value={finalContentStr}
                      onChange={setFinalContentStr}
                      theme="vs-dark"
                      language="yaml"
                    />
                  </div>
                </div>
              </div>

              {/* Validation Results */}
              {validationResults.length > 0 && (
                <Paper withBorder p="xs" mt="xs" h={120} style={{ overflowY: 'auto' }}>
                  <Title order={6} mb="xs" size="sm">{t('proofreading.validation_results')}</Title>
                  <Stack spacing={4}>
                    {validationResults.map((res, idx) => (
                      <Group key={idx} spacing="xs" noWrap>
                        <Badge color={res.level === 'error' ? 'red' : 'yellow'} size="xs">
                          {res.level.toUpperCase()}
                        </Badge>
                        <Text size="xs">{res.message}</Text>
                      </Group>
                    ))}
                  </Stack>
                </Paper>
              )}
            </Tabs.Panel>

            {/* --- Free Mode Panel --- */}
            <Tabs.Panel value="free" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', paddingTop: '10px' }}>
              <Group mb="xs">
                <Select
                  data={['1', '2', '3', '4', '5']}
                  value={linterGameId}
                  onChange={(val) => setLinterGameId(val)}
                  placeholder="Game ID"
                  size="xs"
                />
                <Button onClick={handleLinterValidate} loading={linterLoading} size="xs">Validate</Button>
              </Group>
              <MonacoWrapper value={linterContent} onChange={setLinterContent} theme="vs-dark" language="yaml" />
              {linterError && <Text color="red">{linterError}</Text>}
              {linterResults.length > 0 && (
                <Paper withBorder p="xs" mt="xs" h={150} style={{ overflowY: 'auto' }}>
                  <Table striped highlightOnHover size="xs">
                    <Table.Tbody>
                      {linterResults.map((r, i) => (
                        <Table.Tr key={i}>
                          <Table.Td><Badge color={getLevelColor(r.level)}>{r.level}</Badge></Table.Td>
                          <Table.Td>{r.message}</Table.Td>
                        </Table.Tr>
                      ))}
                    </Table.Tbody>
                  </Table>
                </Paper>
              )}
            </Tabs.Panel>

          </Tabs>
        </div>
      </Paper >

      {/* Save Confirmation Modal */}
      <Modal
        opened={saveModalOpen}
        onClose={() => setSaveModalOpen(false)}
        title={<Group><IconAlertTriangle color="red" /><Text fw={700} c="red">{t('proofreading.modal.title')}</Text></Group>}
        centered
        overlayProps={{
          backgroundOpacity: 0.55,
          blur: 3,
        }}
      >
        <Stack>
          <Text size="sm">
            <span dangerouslySetInnerHTML={{ __html: t('proofreading.modal.content_1').replace('**', '<b>').replace('**', '</b>') }} />
          </Text>
          <Alert color="red" variant="light">
            <span dangerouslySetInnerHTML={{ __html: t('proofreading.modal.content_2').replace('**', '<b>').replace('**', '</b>') }} />
          </Alert>
          <Text size="sm" fw={500}>
            {t('proofreading.modal.confirm')}
          </Text>
          <Group justify="flex-end" mt="md">
            <Button variant="default" onClick={() => setSaveModalOpen(false)}>{t('proofreading.modal.button_cancel')}</Button>
            <Button color="red" onClick={confirmSave}>{t('proofreading.modal.button_confirm')}</Button>
          </Group>
        </Stack>
      </Modal>
    </div >
  );
};

export default ProofreadingPage;
