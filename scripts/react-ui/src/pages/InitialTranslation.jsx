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
} from '@mantine/core';
import { IconAlertCircle, IconCheck, IconX, IconFileUpload, IconSettings, IconRefresh, IconDownload, IconArrowLeft, IconPlayerStop } from '@tabler/icons-react';
import { openProjectDialog } from '../services/fileService';
import '../App.css';
import LogViewer from '../components/shared/LogViewer';

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
    <div>
      <Stepper active={active} onStepClick={setActive}>
        <Stepper.Step label={t('initial_translation_step_upload')} icon={<IconFileUpload size="1.1rem" />} />
        <Stepper.Step label={t('initial_translation_step_configure')} icon={<IconSettings size="1.1rem" />} />
        <Stepper.Step label={t('initial_translation_step_translate')} icon={isProcessing ? <IconRefresh size="1.1rem" className="spin-icon" /> : <IconRefresh size="1.1rem" />} />
        <Stepper.Step label={t('initial_translation_step_download')} icon={<IconDownload size="1.1rem" />} />
      </Stepper>

      <div style={{ marginTop: '24px' }}>
        {active === 0 && (
          <Group>
            <TextInput
              label={t('form_label_project_path')}
              placeholder={t('form_placeholder_project_path')}
              readOnly
              value={projectPath}
              style={{ flexGrow: 1 }}
            />
            <Button onClick={handleBrowseClick} style={{ alignSelf: 'flex-end' }}>
              {t('button_browse')}
            </Button>
          </Group>
        )}

        {active === 1 && (
          <form onSubmit={form.onSubmit(startTranslation)}>
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
            <Group justify="flex-start" mt="md">
              {renderBackButton()}
              <Button type="submit">{t('button_start_translation')}</Button>
            </Group>
          </form>
        )}

        {active === 2 && (
          <Space direction="vertical" style={{ width: '100%' }}>
            {translationDetails && (
               <Card withBorder>
                    <Text fw={500}>{t('job_details_title')}</Text>
                    <Text size="sm">{t('job_details_mod_name')}: {translationDetails.modName}</Text>
                    <Text size="sm">{t('job_details_game')}: {translationDetails.game}</Text>
                    <Text size="sm">{t('job_details_source_language')}: {translationDetails.source}</Text>
                    <Text size="sm">{t('job_details_target_languages')}: {translationDetails.targets}</Text>
                    <Text size="sm">{t('job_details_api_provider')}: {translationDetails.provider}</Text>
              </Card>
            )}
            <LogViewer logs={logs} />
            <Group>
              {renderBackButton()}
              {isProcessing && (
                <Button onClick={handleAbort} leftSection={<IconPlayerStop size={14} />} color="red">
                  {t('button_abort_translation')}
                </Button>
              )}
            </Group>
          </Space>
        )}

        {active === 3 && (
            <Center>
            <Alert
                icon={status === 'completed' ? <IconCheck size="1rem" /> : <IconX size="1rem" />}
                title={status === 'completed' ? t('result_title_success') : t('result_title_failed')}
                color={status === 'completed' ? 'green' : 'red'}
                variant="light"
                style={{ maxWidth: 400 }}
            >
                {status === 'completed' ? t('result_subtitle_success') : t('result_subtitle_failed')}
                <Group justify="center" mt="md">
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
    </div>
  );
};

export default InitialTranslation;
