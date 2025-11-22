import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Container,
  Paper,
  Title,
  Text,
  Grid,
  Textarea,
  Button,
  Group,
  Stack,
  Badge,
  Tooltip,
  LoadingOverlay,
  Select,
  ActionIcon,
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
  IconRefresh,
  IconFileText,
  IconEdit
} from '@tabler/icons-react';
import { notifications } from '@mantine/notifications';
import layoutStyles from '../components/layout/Layout.module.css';
import axios from 'axios';
import MonacoWrapper from '../components/common/MonacoWrapper';

const ProofreadingPage = () => {
  const { t, i18n } = useTranslation();

  // Tab State
  const [activeTab, setActiveTab] = useState('file');

  // --- File Mode State ---
  const [mods, setMods] = useState([]);
  const [selectedMod, setSelectedMod] = useState(null);
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [targetLang, setTargetLang] = useState('zh-CN');

  const [originalText, setOriginalText] = useState('');
  const [aiText, setAiText] = useState('');
  const [finalText, setFinalText] = useState('');
  const [translationFilePath, setTranslationFilePath] = useState('');

  const [validationResults, setValidationResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [stats, setStats] = useState({ error: 0, warning: 0 });

  // Refs for sync scrolling (Monaco Editor Instances)
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


  // --- File Mode Effects & Handlers ---
  useEffect(() => {
    const fetchMods = async () => {
      try {
        const response = await axios.get('/api/proofreading/mods');
        const modOptions = response.data.map(m => ({ value: m, label: m }));
        setMods(modOptions);
      } catch (error) {
        console.error("Failed to fetch mods", error);
        notifications.show({ title: t('api_key_error_title'), message: "Failed to load mods list", color: 'red' });
      }
    };
    fetchMods();
  }, [t]);

  useEffect(() => {
    if (!selectedMod) {
      setFiles([]);
      return;
    }
    const fetchFiles = async () => {
      try {
        const response = await axios.get('/api/proofreading/files', {
          params: { mod_name: selectedMod, game_id: '1' }
        });
        const fileOptions = response.data.map(f => ({ value: f, label: f }));
        setFiles(fileOptions);
      } catch (error) {
        console.error("Failed to fetch files", error);
        notifications.show({ title: t('api_key_error_title'), message: "Failed to load files list", color: 'red' });
      }
    };
    fetchFiles();
  }, [selectedMod, t]);

  useEffect(() => {
    if (!selectedMod || !selectedFile) return;

    const fetchContent = async () => {
      setLoading(true);
      try {
        const response = await axios.get('/api/proofreading/content', {
          params: {
            mod_name: selectedMod,
            file_path: selectedFile,
            target_lang: targetLang
          }
        });

        setOriginalText(response.data.original_content || '');
        const transContent = response.data.translation_content || '';
        setAiText(transContent);
        setFinalText(transContent);
        setTranslationFilePath(response.data.translation_file_path);

        setValidationResults([]);
        setStats({ error: 0, warning: 0 });

      } catch (error) {
        console.error("Failed to fetch content", error);
        notifications.show({ title: t('api_key_error_title'), message: "Failed to load file content", color: 'red' });
      } finally {
        setLoading(false);
      }
    };
    fetchContent();
  }, [selectedMod, selectedFile, targetLang, t]);

  // Validation Logic
  const handleValidate = async () => {
    if (!finalText) return;
    setLoading(true);
    setValidationResults([]);
    try {
      const response = await axios.post('/api/validate/localization', {
        game_id: '1', // Hardcoded for now
        content: finalText,
        source_lang_code: 'en_US' // Assuming source is English for now
      });
      setValidationResults(response.data);

      const errors = response.data.filter(r => r.level === 'error').length;
      const warnings = response.data.filter(r => r.level === 'warning').length;
      setStats({ error: errors, warning: warnings });

      if (errors === 0 && warnings === 0) {
        notifications.show({ title: t('proofreading.validation_results'), message: t('proofreading.no_issues'), color: 'green' });
      } else {
        notifications.show({ title: t('proofreading.validation_results'), message: `Found ${errors} errors and ${warnings} warnings.`, color: 'yellow' });
      }
    } catch (error) {
      console.error("Validation failed", error);
      notifications.show({ title: t('api_key_error_title'), message: "Validation request failed", color: 'red' });
    } finally {
      setLoading(false);
    }
  };

  // Save Logic
  const handleSave = async () => {
    if (!selectedMod || !selectedFile) return;
    setSaving(true);
    try {
      await axios.post('/api/proofreading/save', {
        mod_name: selectedMod,
        file_path: translationFilePath, // Might be empty if new file
        target_lang: targetLang,
        content: finalText,
        relative_path: selectedFile
      });

      notifications.show({ title: t('api_key_success_title'), message: t('proofreading.saved'), color: 'green' });

    } catch (error) {
      console.error("Save failed", error);
      notifications.show({ title: t('proofreading.save_error'), message: error.response?.data?.detail || "Unknown error", color: 'red' });
    } finally {
      setSaving(false);
    }
  };

  // Sync Scrolling Logic for Monaco
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

      // Debounce reset
      setTimeout(() => {
        isScrolling.current = false;
      }, 50);
    };

    // We need to attach listeners when editors are ready.
    // Since refs are populated by MonacoWrapper's onMount, we might need to poll or re-run this effect.
    // Or we just use a polling mechanism here since we don't have a unified "all mounted" event.

    const attachListeners = () => {
      editors.forEach(ref => {
        if (ref.current) {
          const disposable = ref.current.onDidScrollChange((e) => {
            syncScroll(ref.current, e);
          });
          disposables.push(disposable);
        }
      });
    };

    // Wait a bit for editors to mount
    const timer = setTimeout(attachListeners, 500);

    return () => {
      clearTimeout(timer);
      disposables.forEach(d => d.dispose());
    };
  }, [activeTab, originalText, aiText, finalText]); // Re-attach when content/tab changes (editors might be recreated)


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
      console.error("Validation failed:", err);
      setLinterError("Failed to validate content. Please check the backend connection.");
    } finally {
      setLinterLoading(false);
    }
  };

  const getLevelColor = (level) => {
    switch (level) {
      case 'error': return 'red';
      case 'warning': return 'yellow';
      case 'info': return 'blue';
      default: return 'gray';
    }
  };

  const getLevelIcon = (level) => {
    switch (level) {
      case 'error': return <IconX size={16} />;
      case 'warning': return <IconAlertTriangle size={16} />;
      case 'info': return <IconInfoCircle size={16} />;
      default: return null;
    }
  };


  return (
    <div style={{ height: 'calc(100vh - 20px)', display: 'flex', flexDirection: 'column', padding: '10px', width: '100%' }}>
      <Paper withBorder p="xs" radius="md" className={layoutStyles.glassCard} style={{ flex: 1, display: 'flex', flexDirection: 'column', width: '100%', overflow: 'hidden' }}>

        <Group position="apart" mb="xs">
          <Group>
            <Title order={4}>{t('page_title_proofreading')}</Title>
            <Badge color="blue" variant="light" size="sm">Beta</Badge>
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
            {/* Header & Controls */}
            <Stack spacing="xs" mb="xs">
              <Group position="apart">
                <Group spacing="xs">
                  <Select
                    placeholder={t('proofreading.select_mod_placeholder')}
                    data={mods}
                    value={selectedMod}
                    onChange={setSelectedMod}
                    searchable
                    size="xs"
                    style={{ width: 200 }}
                  />
                  <Select
                    placeholder={t('proofreading.select_file_placeholder')}
                    data={files}
                    value={selectedFile}
                    onChange={setSelectedFile}
                    searchable
                    disabled={!selectedMod}
                    size="xs"
                    style={{ width: 250 }}
                  />
                  <Select
                    placeholder={t('proofreading.target_language')}
                    data={[
                      { value: 'zh-CN', label: '简体中文' },
                    ]}
                    value={targetLang}
                    onChange={setTargetLang}
                    size="xs"
                    style={{ width: 100 }}
                  />
                </Group>

                <Group spacing="xs">
                  {/* Validation Stats */}
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
                    disabled={!finalText}
                    size="xs"
                  >
                    {t('proofreading.validate')}
                  </Button>
                  <Button
                    leftSection={<IconDeviceFloppy size={14} />}
                    onClick={handleSave}
                    loading={saving}
                    disabled={!finalText}
                    size="xs"
                  >
                    {t('proofreading.save')}
                  </Button>
                </Group>
              </Group>
            </Stack>

            {/* 3-Column Layout */}
            <div style={{ flex: 1, display: 'flex', flexDirection: 'row', gap: '10px', overflow: 'hidden', width: '100%' }}>
              {/* Column 1: Original */}
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', minWidth: 0 }}>
                <Text fw={500} mb={4} size="xs">{t('proofreading.original')}</Text>
                <MonacoWrapper
                  scrollRef={originalEditorRef}
                  value={originalText}
                  readOnly={true}
                  theme="vs-dark"
                />
              </div>

              {/* Column 2: AI Draft */}
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', minWidth: 0 }}>
                <Text fw={500} mb={4} size="xs">{t('proofreading.ai_draft')}</Text>
                <MonacoWrapper
                  scrollRef={aiEditorRef}
                  value={aiText}
                  readOnly={true}
                  theme="vs-dark"
                />
              </div>

              {/* Column 3: Final Edit */}
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', minWidth: 0 }}>
                <Text fw={500} mb={4} size="xs">{t('proofreading.final_edit')}</Text>
                <div style={{ position: 'relative', flex: 1, display: 'flex', flexDirection: 'column' }}>
                  <LoadingOverlay visible={loading || saving} overlayBlur={2} />
                  <MonacoWrapper
                    scrollRef={finalEditorRef}
                    value={finalText}
                    onChange={setFinalText}
                    theme="vs-dark"
                  />
                </div>
              </div>
            </div>

            {/* Validation Results Panel (Bottom) */}
            {validationResults.length > 0 && (
              <Paper withBorder p="xs" mt="xs" h={120} style={{ overflowY: 'auto' }}>
                <Title order={6} mb="xs" size="sm">{t('proofreading.validation_results')}</Title>
                <Stack spacing={4}>
                  {validationResults.map((res, idx) => (
                    <Group key={idx} spacing="xs" noWrap>
                      <Badge color={res.level === 'error' ? 'red' : 'yellow'} size="xs" style={{ flexShrink: 0 }}>
                        {res.level.toUpperCase()}
                      </Badge>
                      <Text size="xs" ff="monospace" style={{ flexShrink: 0 }}>L{res.line_number}</Text>
                      <Text size="xs" style={{ wordBreak: 'break-all' }}>{res.message}</Text>
                      {res.details && <Text size="xs" c="dimmed" style={{ wordBreak: 'break-all' }}>({res.details})</Text>}
                    </Group>
                  ))}
                </Stack>
              </Paper>
            )}
          </Tabs.Panel>

          {/* --- Free Mode Panel --- */}
          <Tabs.Panel value="free" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', paddingTop: '10px' }}>
            <Stack spacing="xs" style={{ flex: 1, overflow: 'hidden' }}>
              <Group position="apart">
                <Text size="sm" c="dimmed">Paste localization code here to validate.</Text>
                <Group>
                  <Select
                    placeholder="Select game"
                    data={[
                      { value: '1', label: 'Victoria 3' },
                      { value: '2', label: 'Stellaris' },
                      { value: '3', label: 'Europa Universalis IV' },
                      { value: '4', label: 'Hearts of Iron IV' },
                      { value: '5', label: 'Crusader Kings III' },
                    ]}
                    value={linterGameId}
                    onChange={setLinterGameId}
                    size="xs"
                    style={{ width: 150 }}
                  />
                  <Button
                    onClick={handleLinterValidate}
                    loading={linterLoading}
                    leftSection={<IconCheck size={14} />}
                    size="xs"
                  >
                    Validate
                  </Button>
                </Group>
              </Group>

              <div style={{ flex: 1, minHeight: 0 }}>
                <MonacoWrapper
                  value={linterContent}
                  onChange={setLinterContent}
                  theme="vs-dark"
                />
              </div>

              {linterError && (
                <Alert icon={<IconX size={16} />} title="Error" color="red" variant="light">
                  {linterError}
                </Alert>
              )}

              {linterResults.length > 0 ? (
                <Paper withBorder p="xs" h={200} style={{ overflowY: 'auto' }}>
                  <Table striped highlightOnHover size="xs">
                    <Table.Thead>
                      <Table.Tr>
                        <Table.Th>Line</Table.Th>
                        <Table.Th>Level</Table.Th>
                        <Table.Th>Key</Table.Th>
                        <Table.Th>Message</Table.Th>
                      </Table.Tr>
                    </Table.Thead>
                    <Table.Tbody>
                      {linterResults.map((result, index) => (
                        <Table.Tr key={index}>
                          <Table.Td>{result.line_number}</Table.Td>
                          <Table.Td>
                            <Badge color={getLevelColor(result.level)} leftSection={getLevelIcon(result.level)} size="xs">
                              {result.level.toUpperCase()}
                            </Badge>
                          </Table.Td>
                          <Table.Td style={{ fontFamily: 'monospace' }}>{result.key || '-'}</Table.Td>
                          <Table.Td>{result.message}</Table.Td>
                        </Table.Tr>
                      ))}
                    </Table.Tbody>
                  </Table>
                </Paper>
              ) : (
                !linterLoading && linterContent.trim() && !linterError && (
                  <Text c="dimmed" ta="center" fs="italic" size="xs">No issues found.</Text>
                )
              )}
            </Stack>
          </Tabs.Panel>

        </Tabs>
      </Paper>
    </div>
  );
};

export default ProofreadingPage;