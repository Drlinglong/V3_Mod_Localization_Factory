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
  Table,
  Alert
} from '@mantine/core';
import {
  IconDeviceFloppy,
  IconCheck,
  IconAlertTriangle,
  IconX,
  IconInfoCircle,
  IconFileText,
  IconEdit
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

  // --- File Mode State ---
  const [targetLang, setTargetLang] = useState('zh-CN');

  // Content State
  const [entries, setEntries] = useState([]); // Structure: { key, original, translation }
  const [originalContentStr, setOriginalContentStr] = useState('');
  const [finalContentStr, setFinalContentStr] = useState('');

  const [validationResults, setValidationResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [stats, setStats] = useState({ error: 0, warning: 0 });

  // Metadata
  const [fileInfo, setFileInfo] = useState(null);

  // Refs for sync scrolling
  const originalEditorRef = useRef(null);
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
    setLoading(true);
    try {
      const res = await axios.get(`/api/proofread/${pId}/${fId}`);
      const data = res.data;
      setFileInfo({ path: data.file_path, project_id: pId, file_id: fId });

      // Convert entries to string format for Editor
      const loadedEntries = data.entries || [];
      setEntries(loadedEntries);

      // Construct string representation for Monaco
      const originals = loadedEntries.map(e => `# ${e.key}\n${e.original}`).join('\n\n');
      const translations = loadedEntries.map(e => `${e.key}:0 "${e.translation}"`).join('\n');

      setOriginalContentStr(originals);
      setFinalContentStr(translations);

    } catch (error) {
      console.error("Failed to load file", error);
      notifications.show({ title: 'Error', message: "Failed to load file data.", color: 'red' });
    } finally {
      setLoading(false);
    }
  };

  // --- Handlers ---

  const parseEditorContentToEntries = (content) => {
    // This is a naive parser for the MVP.
    // It assumes the user keeps the "key:0 "value"" format.
    // We need to map these back to the original keys.
    // A better approach for the future is a custom Monaco diff view or line-by-line editor.
    // For now, we try to regex extract keys and values.
    const lines = content.split('\n');
    const updatedEntries = [];
    const regex = /^\s*([a-zA-Z0-9_\.]+):0\s*"(.*)"\s*$/;

    lines.forEach(line => {
        const match = line.match(regex);
        if (match) {
            updatedEntries.push({
                key: match[1],
                translation: match[2] // TODO: handle unescaping if needed
            });
        }
    });
    return updatedEntries;
  };

  const handleValidate = async () => {
    if (!finalContentStr) return;
    setLoading(true);
    setValidationResults([]);
    try {
      const response = await axios.post('/api/validate/localization', {
        game_id: '1', // TODO: Fetch game_id from project info
        content: finalContentStr,
        source_lang_code: 'en_US'
      });
      setValidationResults(response.data);

      const errors = response.data.filter(r => r.level === 'error').length;
      const warnings = response.data.filter(r => r.level === 'warning').length;
      setStats({ error: errors, warning: warnings });

      if (errors === 0 && warnings === 0) {
        notifications.show({ title: 'Validation', message: t('proofreading.no_issues'), color: 'green' });
      } else {
        notifications.show({ title: 'Validation', message: `Found ${errors} errors and ${warnings} warnings.`, color: 'yellow' });
      }
    } catch (error) {
      console.error("Validation failed", error);
      notifications.show({ title: 'Error', message: "Validation request failed", color: 'red' });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!fileInfo) return;
    setSaving(true);
    try {
      // Parse current editor content back to entries
      const updatedEntries = parseEditorContentToEntries(finalContentStr);

      await axios.post('/api/proofread/save', {
        project_id: fileInfo.project_id,
        file_id: fileInfo.file_id,
        entries: updatedEntries
      });

      notifications.show({ title: 'Success', message: t('proofreading.saved'), color: 'green' });

    } catch (error) {
      console.error("Save failed", error);
      notifications.show({ title: 'Error', message: error.response?.data?.detail || "Save failed", color: 'red' });
    } finally {
      setSaving(false);
    }
  };

  // Sync Scrolling
  useEffect(() => {
    const editors = [originalEditorRef, finalEditorRef];
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
  }, [originalContentStr, finalContentStr]);

  // --- Free Mode Handlers ---
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
          <Tabs value={activeTab} onTabChange={setActiveTab} variant="pills" radius="md">
            <Tabs.List>
              <Tabs.Tab value="file" icon={<IconFileText size={14} />}>{t('proofreading.tab_file_mode')}</Tabs.Tab>
              <Tabs.Tab value="free" icon={<IconEdit size={14} />}>{t('proofreading.tab_free_mode')}</Tabs.Tab>
            </Tabs.List>
          </Tabs>
        </Group>

        <Tabs value={activeTab} style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>

          {/* --- File Mode Panel --- */}
          <Tabs.Panel value="file" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <Stack spacing="xs" mb="xs">
              <Group position="apart">
                <Group spacing="xs">
                   {/* Project controls removed in favor of URL params for this version */}
                   <Text size="sm" c="dimmed">Project Mode</Text>
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

            <div style={{ flex: 1, display: 'flex', flexDirection: 'row', gap: '10px', overflow: 'hidden', width: '100%' }}>
              {/* Original */}
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

              {/* Final Edit */}
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', minWidth: 0 }}>
                <Text fw={500} mb={4} size="xs">{t('proofreading.final_edit')}</Text>
                <div style={{ position: 'relative', flex: 1, display: 'flex', flexDirection: 'column' }}>
                  <LoadingOverlay visible={loading || saving} overlayBlur={2} />
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
             {/* Simplified Free Mode for Restoration */}
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
      </Paper>
    </div>
  );
};

export default ProofreadingPage;
