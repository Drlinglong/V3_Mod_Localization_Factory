import React, { useState, useEffect } from 'react';
import {
    Stack,
    Title,
    Text,
    Select,
    Textarea,
    Button,
    Group,
    Paper,
    Divider,
    Alert,
    Modal,
    Loader,
    ActionIcon,
    Tooltip
} from '@mantine/core';
import { IconDeviceFloppy, IconRefresh, IconAlertTriangle, IconInfoCircle } from '@tabler/icons-react';
import { notifications } from '@mantine/notifications';
import { useTranslation } from 'react-i18next';
import axios from 'axios';

const PromptSettingsTab = () => {
    const { t } = useTranslation();
    const [loading, setLoading] = useState(true);
    const [promptsData, setPromptsData] = useState(null);
    const [selectedGameId, setSelectedGameId] = useState(null);

    // Form states
    const [currentSystemPrompt, setCurrentSystemPrompt] = useState('');
    const [customGlobalPrompt, setCustomGlobalPrompt] = useState('');

    // UI states
    const [submittingSystem, setSubmittingSystem] = useState(false);
    const [submittingCustom, setSubmittingCustom] = useState(false);
    const [resetModalOpen, setResetModalOpen] = useState(false);
    const [resetTarget, setResetTarget] = useState(null); // 'system' or 'custom'

    useEffect(() => {
        fetchPrompts();
    }, []);

    useEffect(() => {
        if (promptsData && selectedGameId) {
            const gameData = promptsData.system_prompts[selectedGameId];
            if (gameData) {
                setCurrentSystemPrompt(gameData.current);
            }
        }
    }, [selectedGameId, promptsData]);

    const fetchPrompts = async () => {
        try {
            const response = await axios.get('/api/prompts');
            setPromptsData(response.data);
            setCustomGlobalPrompt(response.data.custom_global_prompt || '');

            // Select first game by default if not selected
            if (!selectedGameId && response.data.system_prompts) {
                const firstGame = Object.keys(response.data.system_prompts)[0];
                if (firstGame) setSelectedGameId(firstGame);
            }
        } catch (error) {
            console.error("Failed to fetch prompts:", error);
            notifications.show({
                title: t('error'),
                message: t('prompt_fetch_error', 'Failed to load prompts'),
                color: 'red'
            });
        } finally {
            setLoading(false);
        }
    };

    const handleSaveSystemPrompt = async () => {
        if (!selectedGameId) return;
        setSubmittingSystem(true);
        try {
            await axios.post('/api/prompts/system', {
                game_id: selectedGameId,
                prompt_template: currentSystemPrompt
            });
            notifications.show({
                title: t('success'),
                message: t('prompt_save_success', 'System prompt saved successfully'),
                color: 'green'
            });
            // Refresh data to update "is_overridden" status if needed
            fetchPrompts();
        } catch (error) {
            console.error("Failed to save system prompt:", error);
            notifications.show({
                title: t('error'),
                message: t('prompt_save_error', 'Failed to save system prompt'),
                color: 'red'
            });
        } finally {
            setSubmittingSystem(false);
        }
    };

    const handleSaveCustomPrompt = async () => {
        setSubmittingCustom(true);
        try {
            await axios.post('/api/prompts/custom', {
                custom_prompt: customGlobalPrompt
            });
            notifications.show({
                title: t('success'),
                message: t('prompt_save_success', 'Custom prompt saved successfully'),
                color: 'green'
            });
        } catch (error) {
            console.error("Failed to save custom prompt:", error);
            notifications.show({
                title: t('error'),
                message: t('prompt_save_error', 'Failed to save custom prompt'),
                color: 'red'
            });
        } finally {
            setSubmittingCustom(false);
        }
    };

    const handleResetClick = (target) => {
        setResetTarget(target);
        setResetModalOpen(true);
    };

    const confirmReset = async () => {
        setResetModalOpen(false);
        try {
            const payload = {
                game_id: resetTarget === 'system' ? selectedGameId : null,
                reset_custom: resetTarget === 'custom'
            };

            await axios.post('/api/prompts/reset', payload);

            notifications.show({
                title: t('success'),
                message: t('prompt_reset_success', 'Prompt reset to default'),
                color: 'green'
            });
            fetchPrompts();
        } catch (error) {
            console.error("Failed to reset prompt:", error);
            notifications.show({
                title: t('error'),
                message: t('prompt_reset_error', 'Failed to reset prompt'),
                color: 'red'
            });
        }
    };

    if (loading) return <Loader />;

    const gameOptions = promptsData?.system_prompts
        ? Object.entries(promptsData.system_prompts).map(([id, data]) => ({
            value: id,
            label: data.name
        }))
        : [];

    const selectedGameData = selectedGameId && promptsData?.system_prompts
        ? promptsData.system_prompts[selectedGameId]
        : null;

    return (
        <Stack spacing="xl">
            <Alert variant="light" color="orange" title={t('prompt_settings_warning_title')} icon={<IconAlertTriangle />}>
                {t('prompt_settings_warning_desc')}
            </Alert>

            {/* --- System Prompts Section --- */}
            <Paper p="md" withBorder>
                <Group justify="space-between" mb="md">
                    <Title order={4}>{t('prompt_settings_system_title', 'System Prompt Configuration')}</Title>
                    <Select
                        data={gameOptions}
                        value={selectedGameId}
                        onChange={setSelectedGameId}
                        placeholder="Select Game"
                        allowDeselect={false}
                    />
                </Group>

                {selectedGameData && (
                    <Stack>
                        <Alert icon={<IconInfoCircle size={16} />} color="blue" variant="light">
                            {t('prompt_settings_system_desc', 'This is the core instruction sent to the AI for batch translation. Modify with caution.')}
                        </Alert>

                        <Group align="flex-start" grow>
                            <Stack spacing="xs">
                                <Text size="sm" fw={500}>{t('prompt_default', 'Default System Prompt (Read-only)')}</Text>
                                <Textarea
                                    value={selectedGameData.default}
                                    readOnly
                                    minRows={10}
                                    maxRows={10}
                                    variant="filled"
                                    styles={{ input: { fontFamily: 'monospace', fontSize: '12px', color: 'gray' } }}
                                />
                            </Stack>
                            <Stack spacing="xs">
                                <Group justify="space-between">
                                    <Text size="sm" fw={500}>
                                        {t('prompt_current', 'Current Effective Prompt')}
                                        {selectedGameData.is_overridden && (
                                            <Text span c="orange" ml="xs" size="xs">({t('prompt_overridden', 'Overridden')})</Text>
                                        )}
                                    </Text>
                                    <Button
                                        variant="subtle"
                                        color="red"
                                        size="xs"
                                        onClick={() => handleResetClick('system')}
                                        disabled={!selectedGameData.is_overridden}
                                        leftSection={<IconRefresh size={14} />}
                                    >
                                        {t('prompt_reset', 'Reset to Default')}
                                    </Button>
                                </Group>
                                <Textarea
                                    value={currentSystemPrompt}
                                    onChange={(e) => setCurrentSystemPrompt(e.currentTarget.value)}
                                    minRows={10}
                                    maxRows={10}
                                    styles={{ input: { fontFamily: 'monospace', fontSize: '12px' } }}
                                />
                            </Stack>
                        </Group>

                        <Group justify="flex-end">
                            <Button
                                leftSection={<IconDeviceFloppy size={16} />}
                                onClick={handleSaveSystemPrompt}
                                loading={submittingSystem}
                            >
                                {t('prompt_save_override', 'Save System Prompt Override')}
                            </Button>
                        </Group>
                    </Stack>
                )}
            </Paper>

            {/* --- Custom Global Prompt Section --- */}
            <Paper p="md" withBorder>
                <Title order={4} mb="sm">{t('prompt_settings_custom_title', 'Persistent Custom Prompt')}</Title>
                <Alert icon={<IconInfoCircle size={16} />} color="green" variant="light" mb="md">
                    {t('prompt_settings_custom_desc', 'This prompt will be automatically pre-filled into the "Additional Prompt" field for every new translation task. Useful for consistent style instructions.')}
                </Alert>

                <Textarea
                    placeholder={t('prompt_custom_placeholder', 'Enter your custom instructions here... (e.g. "Always use formal tone", "Do not translate proper nouns")')}
                    value={customGlobalPrompt}
                    onChange={(e) => setCustomGlobalPrompt(e.currentTarget.value)}
                    minRows={4}
                    mb="md"
                />

                <Group justify="space-between">
                    <Button
                        variant="subtle"
                        color="red"
                        onClick={() => handleResetClick('custom')}
                        disabled={!customGlobalPrompt}
                        leftSection={<IconRefresh size={16} />}
                    >
                        {t('prompt_clear', 'Clear Custom Prompt')}
                    </Button>
                    <Button
                        leftSection={<IconDeviceFloppy size={16} />}
                        onClick={handleSaveCustomPrompt}
                        loading={submittingCustom}
                    >
                        {t('prompt_save_custom', 'Save Custom Prompt')}
                    </Button>
                </Group>
            </Paper>

            {/* --- Reset Confirmation Modal --- */}
            <Modal
                opened={resetModalOpen}
                onClose={() => setResetModalOpen(false)}
                title={<Group><IconAlertTriangle color="red" /><Text fw={700}>{t('prompt_reset_confirm_title', 'Confirm Reset')}</Text></Group>}
                centered
            >
                <Text mb="lg">
                    {t('prompt_reset_confirm_message', 'This will revert your changes to the default system settings. This action cannot be undone. Are you sure?')}
                </Text>
                <Group justify="flex-end">
                    <Button variant="default" onClick={() => setResetModalOpen(false)}>{t('cancel')}</Button>
                    <Button color="red" onClick={confirmReset}>{t('confirm_reset', 'Yes, Reset')}</Button>
                </Group>
            </Modal>
        </Stack>
    );
};

export default PromptSettingsTab;
