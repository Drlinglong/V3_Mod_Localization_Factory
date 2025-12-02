import React, { useState, useRef, useEffect } from 'react';
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
  Table
} from '@mantine/core';
import {
  IconDeviceFloppy,
  IconCheck,
  IconAlertTriangle,
  IconX,
  IconFileText,
  IconEdit,
  IconFolder
} from '@tabler/icons-react';
import { notifications } from '@mantine/notifications';
import layoutStyles from '../components/layout/Layout.module.css';
import axios from 'axios';
import MonacoWrapper from '../components/common/MonacoWrapper';
import { useSearchParams } from 'react-router-dom';

const ProofreadingPage = () => {
  const { t } = useTranslation();
  const [searchParams] = useSearchParams();
  const projectId = searchParams.get('projectId');
  const fileId = searchParams.get('fileId');

  // Tab State
  const [activeTab, setActiveTab] = useState('file');
  const [zoomLevel, setZoomLevel] = useState('1');

  // --- File Mode State ---
  const [targetLang, setTargetLang] = useState('zh-CN');

  // Content State
  // entries: { key, original, translation }
  const [entries, setEntries] = useState([]);

  // String representations for Editors
  const [originalContentStr, setOriginalContentStr] = useState('');
  const [aiContentStr, setAiContentStr] = useState(''); // Restored AI Column
  const [finalContentStr, setFinalContentStr] = useState('');

  const [validationResults, setValidationResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [stats, setStats] = useState({ error: 0, warning: 0 });

  // Metadata
  const [fileInfo, setFileInfo] = useState(null);

  // Refs for sync scrolling
  const originalEditorRef = useRef(null);
  const aiEditorRef = useRef(null); // Restored AI Ref
  const finalEditorRef = useRef(null);
  const isScrolling = useRef(false);

  // --- Free Mode (Linter) State ---
  const [linterContent, setLinterContent] = useState('');
  const [linterGameId, setLinterGameId] = useState('1');
  const [linterResults, setLinterResults] = useState([]);
  const [linterLoading, setLinterLoading] = useState(false);
  const [linterError, setLinterError] = useState(null);

  // --- Initialization Effect ---
  useEffect(() => {
    if (projectId && fileId) {
      loadProjectFile(projectId, fileId);
    }
  }, [projectId, fileId]);

  const loadProjectFile = async (pId, fId) => {
    console.log(`Loading proofreading data for Project: ${pId}, File: ${fId}`);
    setLoading(true);
    try {
      const res = await axios.get(`/api/proofread/${pId}/${fId}`);
      const data = res.data;
      console.log("Proofreading data loaded:", data);
      setFileInfo({ path: data.file_path, project_id: pId, file_id: fId });

      const loadedEntries = data.entries || [];
      setEntries(loadedEntries);

      if (loadedEntries.length === 0) {
        notifications.show({
          title: 'Info',
          message: "No entries found for this file. Please try refreshing the project.",
          color: 'blue',
          autoClose: 5000
        });
      }

      // Align entries
      const { originalStr, aiStr, finalStr } = alignEntries(loadedEntries);

      setOriginalContentStr(originalStr);
      setAiContentStr(aiStr);
      setFinalContentStr(finalStr);

    } catch (error) {
      console.error("Failed to load file", error);
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
      const finalText = e.translation || ""; // Initially same as AI

      // Fixed wrap width to match Monaco 'wordWrapColumn'
      const WRAP_WIDTH = 60;

      const calcLines = (text) => {
        if (!text) return 1;
        let len = 0;
        for (let i = 0; i < text.length; i++) {
          // Count Chinese/Full-width chars as 2 width (Monaco standard)
          len += text.charCodeAt(i) > 255 ? 2 : 1;
        }
        return Math.max(1, Math.ceil(len / WRAP_WIDTH));
      };

      const l1 = calcLines(origText);
      const l2 = calcLines(aiText);
      const l3 = calcLines(finalText);
      const maxL = Math.max(l1, l2, l3);

      const pad1 = Math.max(0, maxL - l1);
      const pad2 = Math.max(0, maxL - l2);
      const pad3 = Math.max(0, maxL - l3);

      originalStr += `${e.key}:0 "${origText}"` + "\n".repeat(pad1) + "\n";
      aiStr += `${e.key}:0 "${aiText}"` + "\n".repeat(pad2) + "\n";
      finalStr += `${e.key}:0 "${finalText}"` + "\n".repeat(pad3) + "\n";
    });

    return { originalStr, aiStr, finalStr };
  };

  // --- Handlers ---

  const parseEditorContentToEntries = (content) => {
    // Parse .yml format: key:0 "text"
    // We need to handle the extra newlines we added for alignment.
    // The regex should match the key and the quoted string, ignoring extra whitespace/newlines between entries.
    const entries = [];
    // Regex: ^\s*([\w\.]+):0\s*"((?:[^"\\]|\\.)*)"
    // We split by lines? No, because we have multi-line padding.
    // We can use a global regex match.
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
      // Parse content from Final Editor
      // We validate the file on disk, so we should save first?
      // Or we can send content to validate endpoint if supported.
      // For now, let's assume validate checks the file on disk.
      // Ideally we should auto-save or warn.

      const response = await axios.post(`/api/validate_file`, {
        file_path: fileInfo.path,
        game_id: 'victoria3' // Hardcoded for now or get from project
      });
      setValidationResults(response.data.issues || []);

      // Update stats
      const errors = (response.data.issues || []).filter(i => i.level === 'error').length;
      const warnings = (response.data.issues || []).filter(i => i.level === 'warning').length;
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

  const handleSave = async () => {
    setSaving(true);
    try {
      const parsedEntries = parseEditorContentToEntries(finalContentStr);

      // Convert back to original entry format for saving
      // We need to merge with original keys to keep order?
      // parsedEntries is [{key, value}].
      // We should map back to the `entries` state to preserve other metadata if needed.

      // Construct the file content
      // Paradox format:
      // l_english:
      //  key:0 "value"

      // We need the header!
      // The editor only shows entries.
      // We should probably preserve the header from the original file?
      // Or just reconstruct it: `l_${targetLang}:`

      // For now, simple reconstruction:
      let fileContent = `l_${targetLang}:\n`;
      parsedEntries.forEach(e => {
        fileContent += ` ${e.key}:0 "${e.value}"\n`;
      });

      await axios.post('/api/system/save_file', {
        file_path: fileInfo.path,
        content: fileContent
      });

      notifications.show({ title: 'Saved', message: 'File saved successfully.', color: 'green' });

      // Refresh?
      // loadProjectFile(); 

    } catch (error) {
      console.error("Save failed", error);
      notifications.show({ title: 'Error', message: "Failed to save file.", color: 'red' });
    } finally {
      setSaving(false);
    }
  };

  // Editor Options for Fixed Width
  const editorOptions = {
    wordWrap: 'wordWrapColumn',
    wordWrapColumn: 60,
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    lineNumbers: 'on',
    glyphMargin: false,
    folding: false,
    // Disable overview ruler to save space
    overviewRulerBorder: false,
    overviewRulerLanes: 0,
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
    console.log("handleOpenFolder called", fileInfo);
    if (!fileInfo || !fileInfo.path) {
      console.error("No file path available");
      return;
    }
    try {
      // Robust directory extraction handling mixed slashes
      const path = fileInfo.path.replace(/\\/g, '/');
      const dirPath = path.substring(0, path.lastIndexOf('/'));
      console.log("Opening folder:", dirPath);

      await axios.post('/api/system/open_folder', { path: dirPath });
      notifications.show({ title: 'Success', message: 'Folder opened', color: 'green' });
    } catch (error) {
      console.error("Failed to open folder", error);
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

        <Group position="apart" mb="xs">
          <Group>
            <Title order={4}>{t('page_title_proofreading')}</Title>
            {fileInfo && <Badge variant="outline">{fileInfo.path}</Badge>}
          </Group>
          <Group>
            <Select
              value={zoomLevel}
              onChange={setZoomLevel}
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

        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', zoom: zoomLevel }}>
          <Tabs value={activeTab} style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <Tabs.Panel value="file" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
              <Stack spacing="xs" mb="xs">
                <Group position="apart">
                  <Group spacing="xs">
                    <Text size="sm" c="dimmed">Mode: 3-Column View</Text>
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
                      onClick={handleSave}
                      loading={saving}
                      size="xs"
                    >
                      {t('proofreading.save')}
                    </Button>
                  </Group>
                </Group>
              </Stack>

              {/* 3-Column Layout Restored */}
              <div style={{ flex: 1, display: 'flex', flexDirection: 'row', gap: '10px', overflow: 'hidden', width: '100%' }}>
                {/* Column 1: Original */}
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', minWidth: 0 }}>
                  <Text fw={500} mb={4} size="xs">{t('proofreading.original')}</Text>
                  <MonacoWrapper
                    scrollRef={originalEditorRef}
                    value={originalContentStr}
                    readOnly={true}
                    theme="vs-dark"
                    language="yaml"
                  />
                </div>

                {/* Column 2: AI Draft (Restored) */}
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', minWidth: 0 }}>
                  <Text fw={500} mb={4} size="xs">{t('proofreading.ai_draft')}</Text>
                  <MonacoWrapper
                    scrollRef={aiEditorRef}
                    value={aiContentStr}
                    readOnly={true}
                    theme="vs-dark"
                    language="yaml"
                  />
                </div>

                {/* Column 3: Final Edit */}
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', minWidth: 0 }}>
                  <Text fw={500} mb={4} size="xs">{t('proofreading.final_edit')}</Text>
                  <div style={{ position: 'relative', flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0, overflow: 'hidden' }}>
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
                        <Text size="xs" ff="monospace">L{res.line_number}</Text>
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
                  onChange={setLinterGameId}
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
    </div >
  );
};

export default ProofreadingPage;
