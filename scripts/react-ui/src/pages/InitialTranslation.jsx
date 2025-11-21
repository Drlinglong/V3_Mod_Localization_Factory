import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import { useNotification } from '../context/NotificationContext';
import notificationService from '../services/notificationService';
import { useForm } from '@mantine/form';
import {
  Stepper,
  Button,
  Group,
  TextInput,
  Select,
  MultiSelect,
  Text,
  Card,
  Space,
  Alert,
  Center,
  Container,
  Paper,
  Stack,
  Grid,
  Loader,
  Textarea,
  Switch,
  Collapse,
  Tabs,
  ScrollArea,
} from '@mantine/core';
import { IconAlertCircle, IconCheck, IconX, IconFileUpload, IconSettings, IconRefresh, IconDownload, IconArrowLeft, IconPlayerStop, IconChevronDown, IconChevronUp, IconFolder, IconFolderOpen } from '@tabler/icons-react';
import { openProjectDialog } from '../services/fileService';
import '../App.css';
import layoutStyles from '../components/layout/Layout.module.css';

const InitialTranslation = () => {
  const { t } = useTranslation();
  const { notificationStyle } = useNotification();
  const [active, setActive] = useState(0);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [config, setConfig] = useState({
    game_profiles: {},
    languages: {},
    api_providers: [],
  });
  const [projectPath, setProjectPath] = useState('');
  const [isExistingSource, setIsExistingSource] = useState(false);
  const [existingMods, setExistingMods] = useState([]);
  const [taskId, setTaskId] = useState(null);
  const [logs, setLogs] = useState([]);
  const [status, setStatus] = useState(null);
  const [resultUrl, setResultUrl] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [translationDetails, setTranslationDetails] = useState(null);
  const [availableGlossaries, setAvailableGlossaries] = useState([]);
  const [availableModels, setAvailableModels] = useState([]);

  const form = useForm({
    initialValues: {
      game_profile_id: '',
      source_lang_code: '',
      target_lang_codes: [],
      api_provider: '',
      mod_context: '',
      selected_glossary_ids: [],
      model_name: '',
      use_main_glossary: true,
      clean_source: false,
    },
    validate: {
      game_profile_id: (value) => (value ? null : t('form_validation_required')),
      source_lang_code: (value) => (value ? null : t('form_validation_required')),
      target_lang_codes: (value) => (value.length > 0 ? null : t('form_validation_required')),
      api_provider: (value) => (value ? null : t('form_validation_required')),
    },
  });

  useEffect(() => {
    axios.get('/api/config')
      .then(response => {
        setConfig(response.data);
      })
      .catch(error => {
        console.error('Failed to load config:', error);
        notificationService.error(t('message_error_load_config'), notificationStyle);
      });

    // Fetch existing mods
    axios.get('/api/source-mods')
      .then(response => {
        setExistingMods(response.data);
      })
      .catch(error => {
        console.error('Failed to load source mods:', error);
      });
  }, [notificationStyle]);

  // Fetch glossaries when game profile changes
  useEffect(() => {
    const profileId = form.values.game_profile_id;
    if (profileId && config.game_profiles[profileId]) {
      const gameId = config.game_profiles[profileId].id;
      axios.get(`/api/glossaries/${gameId}`)
        .then(response => {
          setAvailableGlossaries(response.data.map(g => ({
            value: String(g.glossary_id),
            label: g.name || `Glossary ${g.glossary_id}`,
            is_main: g.is_main // Keep this for filtering
          })));
        })
        .catch(error => {
          console.error('Failed to load glossaries:', error);
          setAvailableGlossaries([]);
        });
    } else {
      setAvailableGlossaries([]);
    }
  }, [form.values.game_profile_id, config.game_profiles]);

  // Update available models based on provider
  useEffect(() => {
    if (form.values.api_provider === 'gemini_cli') {
      setAvailableModels([
        { value: 'gemini-2.5-pro', label: 'Gemini 2.5 Pro' },
        { value: 'gemini-2.5-flash', label: 'Gemini 2.5 Flash' },
      ]);
      if (!form.values.model_name) {
        form.setFieldValue('model_name', 'gemini-2.5-pro');
      }
    } else {
      setAvailableModels([]);
      form.setFieldValue('model_name', '');
    }
  }, [form.values.api_provider]);

  useEffect(() => {
    if (!taskId || !isProcessing) return;

    const poll = setInterval(() => {
      axios.get(`/api/status/${taskId}`)
        .then(response => {
          const { status: newStatus, log: newLogs } = response.data;
          const formattedLogs = newLogs.map(l => (typeof l === 'string' ? { level: 'INFO', message: l } : l));
          setLogs(formattedLogs);

          if (newStatus === 'completed' || newStatus === 'failed') {
            clearInterval(poll);
            setStatus(newStatus);
            setIsProcessing(false);
            setActive(3);
            if (newStatus === 'completed') {
              notificationService.success(t('message_success_translation_complete'), notificationStyle);
              setResultUrl(`/api/result/${taskId}`);
            } else {
              notificationService.error(t('message_error_translation_failed'), notificationStyle);
            }
          } else {
            setStatus(newStatus);
          }
        })
        .catch(error => {
          clearInterval(poll);
          notificationService.error(t('message_error_get_status'), notificationStyle);
          console.error('Polling error:', error);
          setStatus('failed');
          setIsProcessing(false);
          setActive(3);
        });
    }, 2000);

    return () => clearInterval(poll);
  }, [taskId, isProcessing, t, notificationStyle]);

  const handleBrowseClick = async () => {
    const fileName = await openProjectDialog();
    if (fileName) {
      setProjectPath(fileName);
      setIsExistingSource(false);
      setActive(1);
    }
  };

  const handleSelectExistingMod = (modPath) => {
    setProjectPath(modPath);
    setIsExistingSource(true);
    setActive(1);
  };

  const handleBack = () => {
    if (active > 0) {
      setActive(active - 1);
    }
  };

  const handleAbort = async () => {
    if (!taskId) return;
    try {
      console.log(`Aborting task ${taskId}`);
      notificationService.error(t('message_warn_aborted'), notificationStyle);
      setIsProcessing(false);
      setStatus('failed');
      setLogs(prev => [...prev, { level: 'WARN', message: t('log_aborted') }]);
    } catch (error) {
      notificationService.error(t('message_error_abort_failed'), notificationStyle);
      console.error('Abort error:', error);
    }
  };

  const startTranslation = (values) => {
    if (!projectPath) {
      notificationService.error(t('message_error_upload_first'), notificationStyle);
      return;
    }

    const { game_profile_id, source_lang_code, target_lang_codes, api_provider, mod_context, selected_glossary_ids, model_name, use_main_glossary, clean_source } = values;
    const gameProfile = config.game_profiles[game_profile_id]?.name || 'Unknown Game';
    const sourceLang = config.languages[source_lang_code]?.name || source_lang_code;
    const targetLangs = target_lang_codes.map(code => config.languages[code]?.name || code).join(', ');

    setTranslationDetails({
      modName: projectPath,
      game: gameProfile,
      source: sourceLang,
      targets: targetLangs,
      provider: api_provider,
      model: model_name,
      useMainGlossary: use_main_glossary,
      cleanSource: clean_source,
    });

    const payload = {
      ...values,
      project_path: projectPath,
      selected_glossary_ids: selected_glossary_ids.map(Number), // Ensure numbers
      is_existing_source: isExistingSource,
    };

    setTaskId(null);
    setLogs([]);
    setStatus('pending');
    setResultUrl(null);
    setActive(2);
    setIsProcessing(true);

    axios.post('/api/translate_v2', payload)
      .then(response => {
        setTaskId(response.data.task_id);
        notificationService.success(t('message_success_task_started'), notificationStyle);
      })
      .catch(error => {
        notificationService.error(t('message_error_task_start_failed'), notificationStyle);
        console.error('Translate API error:', error);
        setIsProcessing(false);
        setStatus('failed');
        setActive(1);
      });
  };

  const renderBackButton = () => (
    <Button onClick={handleBack} leftSection={<IconArrowLeft size={14} />} variant="default">
      {t('button_back')}
    </Button>
  );

  return (
    <Container size="lg" py="xl">
      <Stack gap="xl">
        <Stepper active={active} onStepClick={setActive} allowNextStepsSelect={false}>
          <Stepper.Step label={t('initial_translation_step_upload')} description={t('initial_translation_step_upload_desc', 'Select Mod')}>
            {/* Step 1: Upload/Select Mod */}
          </Stepper.Step>
          <Stepper.Step label={t('initial_translation_step_configure')} description={t('initial_translation_step_configure_desc', 'Settings')}>
            {/* Step 2: Configure */}
          </Stepper.Step>
          <Stepper.Step label={t('initial_translation_step_translate')} description={t('initial_translation_step_translate_desc', 'Processing')}>
            {/* Step 3: Translate */}
          </Stepper.Step>
          <Stepper.Step label={t('initial_translation_step_download')} description={t('initial_translation_step_download_desc', 'Finish')}>
            {/* Step 4: Download */}
          </Stepper.Step>
        </Stepper>

        <Paper p="md" radius="md" className={layoutStyles.glassCard}>
          {active === 0 && (
            <Tabs defaultValue="import">
              <Tabs.List grow>
                <Tabs.Tab value="import" leftSection={<IconFolderOpen size={16} />}>
                  {t('tab_import_folder', 'Import Folder')}
                </Tabs.Tab>
                <Tabs.Tab value="existing" leftSection={<IconFolder size={16} />}>
                  {t('tab_existing_mod', 'Select Existing Mod')}
                </Tabs.Tab>
              </Tabs.List>

              <Tabs.Panel value="import" pt="xl">
                <Center>
                  <Stack align="center" gap="md">
                    <IconFileUpload size={64} stroke={1.5} color="var(--mantine-color-blue-5)" />
                    <Text size="xl" fw={500}>{t('initial_translation_upload_text', 'Select a Mod Folder')}</Text>
                    <Text size="sm" c="dimmed" maw={500} ta="center">
                      {t('initial_translation_upload_hint', 'Select a local folder containing your mod files. It will be copied to the workspace.')}
                    </Text>
                    <Button size="lg" onClick={handleBrowseClick} leftSection={<IconFolderOpen />}>
                      {t('button_browse_folder', 'Browse Folder')}
                    </Button>
                  </Stack>
                </Center>
              </Tabs.Panel>

              <Tabs.Panel value="existing" pt="xl">
                {existingMods.length > 0 ? (
                  <ScrollArea h={300} offsetScrollbars>
                    <Stack gap="xs">
                      {existingMods.map((mod) => (
                        <Card
                          key={mod.path}
                          withBorder
                          padding="sm"
                          radius="sm"
                          className={layoutStyles.glassCard}
                          style={{ cursor: 'pointer', transition: 'background-color 0.2s' }}
                          onClick={() => handleSelectExistingMod(mod.path)}
                        >
                          <Group justify="space-between">
                            <Group>
                              <IconFolder size={20} color="var(--mantine-color-yellow-5)" />
                              <Text fw={500}>{mod.name}</Text>
                            </Group>
                            <Text size="xs" c="dimmed">{new Date(mod.mtime * 1000).toLocaleString()}</Text>
                          </Group>
                        </Card>
                      ))}
                    </Stack>
                  </ScrollArea>
                ) : (
                  <Center h={200}>
                    <Text c="dimmed">{t('no_existing_mods', 'No existing mods found in workspace.')}</Text>
                  </Center>
                )}
              </Tabs.Panel>
            </Tabs>
          )}

          {active === 1 && (
            <Card withBorder padding="xl" radius="md" className={layoutStyles.glassCard}>
              <Text size="lg" fw={500} mb="md">{t('initial_translation_step_configure')}</Text>
              <form onSubmit={form.onSubmit(startTranslation)}>
                <Stack gap="md">
                  <Select
                    label={t('form_label_game')}
                    placeholder={t('form_placeholder_game')}
                    data={Object.entries(config.game_profiles).map(([id, profile]) => ({ value: id, label: profile.name }))}
                    {...form.getInputProps('game_profile_id')}
                  />
                  <Select
                    label={t('form_label_source_language')}
                    placeholder={t('form_placeholder_source_language')}
                    data={Object.values(config.languages).map(lang => ({ value: lang.code, label: lang.name }))}
                    {...form.getInputProps('source_lang_code')}
                  />
                  <MultiSelect
                    label={t('form_label_target_languages')}
                    placeholder={t('form_placeholder_target_languages')}
                    data={Object.values(config.languages).map(lang => ({ value: lang.code, label: lang.name }))}
                    {...form.getInputProps('target_lang_codes')}
                  />
                  <Select
                    label={t('form_label_api_provider')}
                    placeholder={t('form_placeholder_api_provider')}
                    data={config.api_providers}
                    {...form.getInputProps('api_provider')}
                  />

                  {availableModels.length > 0 && (
                    <Select
                      label={t('form_label_model', 'Model')}
                      placeholder={t('form_placeholder_model', 'Select Model')}
                      data={availableModels}
                      {...form.getInputProps('model_name')}
                    />
                  )}

                  <Space h="md" />

                  <Button
                    variant="subtle"
                    onClick={() => setShowAdvanced(!showAdvanced)}
                    rightSection={showAdvanced ? <IconChevronUp size={14} /> : <IconChevronDown size={14} />}
                    fullWidth
                    styles={{ inner: { justifyContent: 'space-between' } }}
                  >
                    {t('advanced_options', 'Advanced Options')}
                  </Button>

                  <Collapse in={showAdvanced}>
                    <Card withBorder className={layoutStyles.glassCard} p="md" mt="xs">
                      <Stack gap="md">
                        {/* Option 1: Use Main Glossary */}
                        <Switch
                          label={t('form_label_use_main_glossary', 'Use Main Glossary')}
                          description={t('form_desc_use_main_glossary', 'Automatically use the primary dictionary for this game.')}
                          {...form.getInputProps('use_main_glossary', { type: 'checkbox' })}
                        />

                        {/* Option 2: Extra Glossaries */}
                        <MultiSelect
                          label={t('form_label_extra_glossaries', 'Extra Glossaries')}
                          placeholder={availableGlossaries.filter(g => !g.is_main).length > 0 ? t('form_placeholder_extra_glossaries', 'Select additional dictionaries') : t('no_extra_glossaries', 'No extra dictionaries available')}
                          data={availableGlossaries.filter(g => !g.is_main)}
                          disabled={availableGlossaries.filter(g => !g.is_main).length === 0}
                          {...form.getInputProps('selected_glossary_ids')}
                        />

                        {/* Option 3: Additional Prompt Injection */}
                        <Textarea
                          label={t('form_label_additional_prompt', 'Additional Prompt Injection')}
                          placeholder={t('form_placeholder_additional_prompt', 'Add custom instructions for the AI...')}
                          autosize
                          minRows={3}
                          {...form.getInputProps('mod_context')}
                        />

                        {/* Option 4: Clean Source Files */}
                        <Card withBorder color="red" radius="sm" style={{ borderColor: 'var(--mantine-color-red-8)' }}>
                          <Switch
                            label={t('form_label_clean_source', 'Clean Source Files')}
                            color="red"
                            {...form.getInputProps('clean_source', { type: 'checkbox' })}
                          />
                          <Text size="xs" c="red" mt={4}>
                            {t('warning_clean_source', 'WARNING: This will delete all files in the translation source folder EXCEPT metadata and localization files. Use with caution.')}
                          </Text>
                        </Card>
                      </Stack>
                    </Card>
                  </Collapse>

                  <Group justify="flex-end" mt="xl">
                    {renderBackButton()}
                    <Button type="submit">{t('button_start_translation')}</Button>
                  </Group>
                </Stack>
              </form>
            </Card>
          )}

          {active === 2 && (
            <Card withBorder padding="xl" radius="md" className={layoutStyles.glassCard}>
              <Stack gap="md">
                {translationDetails && (
                  <Card withBorder className={layoutStyles.glassCard}>
                    <Text fw={500} mb="xs">{t('job_details_title')}</Text>
                    <Grid>
                      <Grid.Col span={6}><Text size="sm" c="dimmed">{t('job_details_mod_name')}:</Text> <Text size="sm">{translationDetails.modName}</Text></Grid.Col>
                      <Grid.Col span={6}><Text size="sm" c="dimmed">{t('job_details_game')}:</Text> <Text size="sm">{translationDetails.game}</Text></Grid.Col>
                      <Grid.Col span={6}><Text size="sm" c="dimmed">{t('job_details_source_language')}:</Text> <Text size="sm">{translationDetails.source}</Text></Grid.Col>
                      <Grid.Col span={6}><Text size="sm" c="dimmed">{t('job_details_target_languages')}:</Text> <Text size="sm">{translationDetails.targets}</Text></Grid.Col>
                      <Grid.Col span={6}><Text size="sm" c="dimmed">{t('job_details_api_provider')}:</Text> <Text size="sm">{translationDetails.provider}</Text></Grid.Col>
                      {translationDetails.model && <Grid.Col span={6}><Text size="sm" c="dimmed">{t('job_details_model', 'Model')}:</Text> <Text size="sm">{translationDetails.model}</Text></Grid.Col>}
                      <Grid.Col span={6}><Text size="sm" c="dimmed">{t('job_details_use_glossary', 'Use Glossary')}:</Text> <Text size="sm">{translationDetails.useGlossary ? 'Yes' : 'No'}</Text></Grid.Col>
                    </Grid>
                  </Card>
                )}

                <Center p="xl">
                  <Stack align="center">
                    <Loader size="xl" type="dots" />
                    <Text size="lg" mt="md">{t('processing_translation')}</Text>
                    <Text size="sm" c="dimmed">{t('please_wait')}</Text>
                  </Stack>
                </Center>

                <Group justify="space-between" mt="md">
                  {renderBackButton()}
                  {isProcessing && (
                    <Button onClick={handleAbort} leftSection={<IconPlayerStop size={14} />} color="red" variant="light">
                      {t('button_abort_translation')}
                    </Button>
                  )}
                </Group>
              </Stack>
            </Card>
          )}

          {active === 3 && (
            <Center>
              <Alert
                icon={status === 'completed' ? <IconCheck size="1rem" /> : <IconX size="1rem" />}
                title={status === 'completed' ? t('result_title_success') : t('result_title_failed')}
                color={status === 'completed' ? 'green' : 'red'}
                variant="light"
                style={{ maxWidth: 500, width: '100%' }}
              >
                {status === 'completed' ? t('result_subtitle_success') : t('result_subtitle_failed')}
                <Group justify="flex-end" mt="md">
                  {renderBackButton()}
                  {status === 'completed' && resultUrl && (
                    <Button component="a" href={resultUrl} leftSection={<IconDownload size={14} />}>
                      {t('button_download_mod')}
                    </Button>
                  )}
                </Group>
              </Alert>
            </Center>
          )}
        </Paper>
      </Stack>
    </Container>
  );
};

export default InitialTranslation;
