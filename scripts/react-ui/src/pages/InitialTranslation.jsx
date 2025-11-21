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
} from '@mantine/core';
import { IconAlertCircle, IconCheck, IconX, IconFileUpload, IconSettings, IconRefresh, IconDownload, IconArrowLeft, IconPlayerStop } from '@tabler/icons-react';
import { openProjectDialog } from '../services/fileService';
import '../App.css';
import layoutStyles from '../components/layout/Layout.module.css';

const InitialTranslation = () => {
  const { t } = useTranslation();
  const { notificationStyle } = useNotification();
  const [active, setActive] = useState(0);
  const [config, setConfig] = useState({
    game_profiles: {},
    languages: {},
    api_providers: [],
  });
  const [projectPath, setProjectPath] = useState('');
  const [taskId, setTaskId] = useState(null);
  const [logs, setLogs] = useState([]);
  const [status, setStatus] = useState(null);
  const [resultUrl, setResultUrl] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [translationDetails, setTranslationDetails] = useState(null);

  const form = useForm({
    initialValues: {
      game_profile_id: '',
      source_lang_code: '',
      target_lang_codes: [],
      api_provider: '',
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
      .then(response => setConfig(response.data))
      .catch(error => {
        notificationService.error(t('message_error_load_config'), notificationStyle);
        console.error('Config fetch error:', error);
      });
  }, [notificationStyle]);

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
      setActive(1);
    }
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
      notificationService.error(t('message_error_select_project_first'), notificationStyle);
      return;
    }

    const { game_profile_id, source_lang_code, target_lang_codes, api_provider } = values;
    const gameProfile = config.game_profiles[game_profile_id]?.name || 'Unknown Game';
    const sourceLang = config.languages[source_lang_code]?.name || source_lang_code;
    const targetLangs = target_lang_codes.map(code => config.languages[code]?.name || code).join(', ');

    setTranslationDetails({
      modName: projectPath,
      game: gameProfile,
      source: sourceLang,
      targets: targetLangs,
      provider: api_provider,
    });

    // NOTE: The actual file upload is replaced by sending the path.
    // The backend will need to be adapted to handle a local file path instead of an upload.
    const payload = {
      ...values,
      project_path: projectPath
    };

    setTaskId(null);
    setLogs([{ level: 'INFO', message: t('log_starting') }]);
    setStatus('pending');
    setResultUrl(null);
    setActive(2);
    setIsProcessing(true);

    axios.post('/api/translate_v2', payload) // Assuming a new endpoint for path-based translation
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
      <Paper p="xl" radius="md" withBorder className={layoutStyles.glassCard}>
        <Stepper active={active} onStepClick={setActive} breakpoint="sm">
          <Stepper.Step label={t('initial_translation_step_upload')} description={t('initial_translation_step_upload_desc')} icon={<IconFileUpload size="1.1rem" />} />
          <Stepper.Step label={t('initial_translation_step_configure')} description={t('initial_translation_step_configure_desc')} icon={<IconSettings size="1.1rem" />} />
          <Stepper.Step label={t('initial_translation_step_translate')} description={t('initial_translation_step_translate_desc')} icon={isProcessing ? <IconRefresh size="1.1rem" className="spin-icon" /> : <IconRefresh size="1.1rem" />} />
          <Stepper.Step label={t('initial_translation_step_download')} description={t('initial_translation_step_download_desc')} icon={<IconDownload size="1.1rem" />} />
        </Stepper>

        <div style={{ marginTop: '40px' }}>
          {active === 0 && (
            <Card withBorder padding="xl" radius="md" className={layoutStyles.glassCard}>
              <Text size="lg" fw={500} mb="md">{t('initial_translation_step_upload')}</Text>
              <Group align="flex-end">
                <TextInput
                  label={t('form_label_project_path')}
                  placeholder={t('form_placeholder_project_path')}
                  readOnly
                  value={projectPath}
                  style={{ flexGrow: 1 }}
                />
                <Button onClick={handleBrowseClick} leftSection={<IconFileUpload size={16} />}>
                  {t('button_browse')}
                </Button>
              </Group>
            </Card>
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
        </div>
      </Paper>
    </Container>
  );
};

export default InitialTranslation;
