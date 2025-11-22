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
  Modal,
} from '@mantine/core';
import { IconAlertCircle, IconCheck, IconX, IconSettings, IconRefresh, IconDownload, IconArrowLeft, IconPlayerStop, IconChevronDown, IconChevronUp, IconFolder, IconFolderOpen, IconPlayerPlay } from '@tabler/icons-react';
import { useNavigate } from 'react-router-dom';
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

  // Project State
  const [projects, setProjects] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState(null);
  const navigate = useNavigate();

  const [taskId, setTaskId] = useState(null);
  const [logs, setLogs] = useState([]);
  const [status, setStatus] = useState(null);
  const [resultUrl, setResultUrl] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [translationDetails, setTranslationDetails] = useState(null);
  const [availableGlossaries, setAvailableGlossaries] = useState([]);
  const [availableModels, setAvailableModels] = useState([]);

  // Resume Modal State
  const [resumeModalOpen, setResumeModalOpen] = useState(false);
  const [checkpointInfo, setCheckpointInfo] = useState(null);
  const [pendingFormValues, setPendingFormValues] = useState(null);

  const form = useForm({
    initialValues: {
      target_lang_code: 'zh-CN', // Default
      api_provider: 'gemini',
      model_name: 'gemini-pro',
      mod_context: '',
      selected_glossary_ids: [],
      use_main_glossary: true,
    },
    validate: {
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

    // Fetch Projects
    axios.get('/api/projects')
      .then(response => {
        setProjects(response.data.map(p => ({ value: p.project_id, label: p.name })));
      })
      .catch(error => {
        console.error("Failed to load projects", error);
      });
  }, [notificationStyle]);

  // Update available models based on provider
  useEffect(() => {
    if (form.values.api_provider === 'gemini') {
      setAvailableModels([
        { value: 'gemini-pro', label: 'Gemini Pro' },
        { value: 'gemini-flash', label: 'Gemini Flash' },
      ]);
    } else {
      setAvailableModels([]);
    }
  }, [form.values.api_provider]);

  const handleProjectSelect = () => {
    if (selectedProjectId) {
      setActive(1);
    }
  };

  const handleBack = () => {
    if (active > 0) {
      setActive(active - 1);
    }
  };

  const handleStartClick = async (values) => {
    // 1. Check for existing checkpoint
    const modName = projects.find(p => p.value === selectedProjectId)?.label;
    if (!modName) return;

    try {
      const response = await axios.post('/api/translation/checkpoint-status', {
        mod_name: modName,
        target_lang_codes: [values.target_lang_code]
      });

      if (response.data.exists) {
        setCheckpointInfo(response.data);
        setPendingFormValues(values);
        setResumeModalOpen(true);
      } else {
        // No checkpoint, start normally
        startTranslation(values);
      }
    } catch (error) {
      console.error("Failed to check checkpoint:", error);
      // Fallback to normal start if check fails
      startTranslation(values);
    }
  };

  const handleResume = () => {
    setResumeModalOpen(false);
    if (pendingFormValues) {
      startTranslation(pendingFormValues);
    }
  };

  const handleStartOver = async () => {
    setResumeModalOpen(false);
    if (pendingFormValues) {
      const modName = projects.find(p => p.value === selectedProjectId)?.label;
      try {
        await axios.delete('/api/translation/checkpoint', {
          data: {
            mod_name: modName,
            target_lang_codes: [pendingFormValues.target_lang_code]
          }
        });
        notificationService.success("Checkpoint cleared. Starting fresh.", notificationStyle);
        startTranslation(pendingFormValues);
      } catch (error) {
        notificationService.error("Failed to clear checkpoint.", notificationStyle);
        console.error(error);
      }
    }
  };

  const startTranslation = (values) => {
    if (!selectedProjectId) {
      notificationService.error("Please select a project first.", notificationStyle);
      return;
    }

    setTranslationDetails({
      modName: projects.find(p => p.value === selectedProjectId)?.label,
      provider: values.api_provider,
      model: values.model_name,
    });

    const payload = {
      project_id: selectedProjectId,
      target_language: values.target_lang_code, // Only supporting simplified logic for MVP
      api_provider: values.api_provider,
      model: values.model_name,
    };

    setTaskId(null);
    setStatus('pending');
    setActive(2);
    setIsProcessing(true);

    axios.post('/api/translate/start', payload)
      .then(response => {
        // setTaskId(response.data.task_id); // Background task ID if returned
        notificationService.success("Translation started in background!", notificationStyle);
        // For this MVP, we might just navigate away or show a success message since it's async
        setStatus('completed');
        setIsProcessing(false);
        setActive(3);
      })
      .catch(error => {
        notificationService.error("Failed to start translation.", notificationStyle);
        console.error('Translate API error:', error);
        setIsProcessing(false);
        setStatus('failed');
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
          <Stepper.Step label="Select Project" description="Choose a project">
          </Stepper.Step>
          <Stepper.Step label={t('initial_translation_step_configure')} description={t('initial_translation_step_configure_desc', 'Settings')}>
          </Stepper.Step>
          <Stepper.Step label={t('initial_translation_step_translate')} description={t('initial_translation_step_translate_desc', 'Processing')}>
          </Stepper.Step>
          <Stepper.Step label="Finish" description="Done">
          </Stepper.Step>
        </Stepper>

        <Paper p="md" radius="md" className={layoutStyles.glassCard}>
          {active === 0 && (
            <Center pt="xl" pb="xl">
              <Stack align="center" gap="md" w="100%" maw={400}>
                <IconFolderOpen size={48} stroke={1.5} color="var(--mantine-color-blue-5)" />
                <Text size="xl" fw={500}>Select a Project</Text>

                {projects.length > 0 ? (
                  <Select
                    data={projects}
                    value={selectedProjectId}
                    onChange={setSelectedProjectId}
                    placeholder="Choose a project..."
                    w="100%"
                  />
                ) : (
                  <Text c="dimmed">No projects found. Please create one in Project Management.</Text>
                )}

                <Button size="lg" onClick={handleProjectSelect} disabled={!selectedProjectId}>
                  Continue
                </Button>

                <Button variant="subtle" size="sm" onClick={() => navigate('/')}>
                  Go to Project Management
                </Button>
              </Stack>
            </Center>
          )}

          {active === 1 && (
            <Card withBorder padding="xl" radius="md" className={layoutStyles.glassCard}>
              <Text size="lg" fw={500} mb="md">{t('initial_translation_step_configure')}</Text>
              <form onSubmit={form.onSubmit(handleStartClick)}>
                <Stack gap="md">
                  <Select
                    label="Target Language"
                    data={[{ value: 'zh', label: 'Chinese (Simplified)' }]} // Hardcoded for MVP
                    {...form.getInputProps('target_lang_code')}
                  />
                  <Select
                    label={t('form_label_api_provider')}
                    data={config.api_providers}
                    {...form.getInputProps('api_provider')}
                  />

                  {availableModels.length > 0 && (
                    <Select
                      label="Model"
                      data={availableModels}
                      {...form.getInputProps('model_name')}
                    />
                  )}

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
                        <Textarea
                          label="Additional Prompt Injection"
                          autosize
                          minRows={3}
                          {...form.getInputProps('mod_context')}
                        />
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
                <Center p="xl">
                  <Stack align="center">
                    <Loader size="xl" type="dots" />
                    <Text size="lg" mt="md">{t('processing_translation')}</Text>
                    <Text size="sm" c="dimmed">{t('please_wait')}</Text>
                  </Stack>
                </Center>
              </Stack>
            </Card>
          )}

          {active === 3 && (
            <Center>
              <Alert
                icon={<IconCheck size="1rem" />}
                title="Translation Started"
                color="green"
                variant="light"
                style={{ maxWidth: 500, width: '100%' }}
              >
                The translation task has been submitted to the background queue. You can check the progress in the Project Management dashboard.
                <Group justify="flex-end" mt="md">
                  <Button onClick={() => navigate('/')}>
                    Go to Dashboard
                  </Button>
                </Group>
              </Alert>
            </Center>
          )}
        </Paper>
      </Stack>

      {/* Resume Confirmation Modal */}
      <Modal
        opened={resumeModalOpen}
        onClose={() => setResumeModalOpen(false)}
        title={<Group><IconAlertCircle color="orange" /> <Text fw={700}>Interrupted Session Found</Text></Group>}
        centered
      >
        <Stack>
          <Text>
            Found an interrupted translation session for this mod.
          </Text>
          {checkpointInfo && (
            <Alert color="blue" variant="light">
              <Text size="sm"><b>Completed Files:</b> {checkpointInfo.completed_count}</Text>
              {checkpointInfo.total_files_estimate > 0 && (
                <Text size="sm"><b>Estimated Progress:</b> {Math.round((checkpointInfo.completed_count / checkpointInfo.total_files_estimate) * 100)}%</Text>
              )}
              {checkpointInfo.metadata?.model_name && (
                <Text size="sm"><b>Previous Model:</b> {checkpointInfo.metadata.model_name}</Text>
              )}
            </Alert>
          )}
          <Text size="sm" c="dimmed">
            Do you want to resume from where it left off, or start over from the beginning?
          </Text>
          <Group justify="flex-end" mt="md">
            <Button variant="default" onClick={handleStartOver} leftSection={<IconRefresh size={16} />}>
              Start Over
            </Button>
            <Button onClick={handleResume} leftSection={<IconPlayerPlay size={16} />}>
              Resume
            </Button>
          </Group>
        </Stack>
      </Modal>
    </Container>
  );
};

export default InitialTranslation;
