import React, { useState, useEffect } from 'react';
import {
    Paper,
    Title,
    Text,
    Group,
    Stack,
    Button,
    PasswordInput,
    Badge,
    Loader,
    ActionIcon,
    Tooltip,
    Box,
    Alert,
    TagsInput,
    TextInput,
    Divider,
    Select
} from '@mantine/core';
import { IconCheck, IconX, IconEdit, IconKey, IconInfoCircle, IconServer, IconRobot } from '@tabler/icons-react';
import { notifications } from '@mantine/notifications';
import { useTranslation } from 'react-i18next';
import api from '../utils/api';
import styles from './ApiSettingsTab.module.css';

const ApiSettingsTab = () => {
    const { t } = useTranslation();
    const [providers, setProviders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [editingId, setEditingId] = useState(null);

    // Edit form state
    const [editForm, setEditForm] = useState({
        apiKey: '',
        models: [],
        apiUrl: '',
        selectedModel: ''
    });

    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        fetchProviders();
    }, []);

    const fetchProviders = async () => {
        try {
            const response = await api.get('/api/api-keys');
            setProviders(response.data);
        } catch (error) {
            console.error('Error fetching API providers:', error);
            notifications.show({
                title: t('api_key_error_title'),
                message: t('api_key_error_fetch'),
                color: 'red'
            });
        } finally {
            setLoading(false);
        }
    };

    const handleEditClick = (provider) => {
        setEditingId(provider.id);
        setEditForm({
            apiKey: '', // Always start empty for security
            models: provider.custom_models || [],
            apiUrl: provider.api_url || '',
            selectedModel: provider.selected_model || ''
        });
    };

    const handleCancelEdit = () => {
        setEditingId(null);
        setEditForm({ apiKey: '', models: [], apiUrl: '', selectedModel: '' });
    };

    const handleSave = async (providerId) => {
        setSubmitting(true);
        try {
            const payload = {
                provider_id: providerId,
                models: editForm.models,
                api_url: editForm.apiUrl,
                selected_model: editForm.selectedModel
            };

            if (editForm.apiKey.trim()) {
                payload.api_key = editForm.apiKey.trim();
            }

            await api.post('/api/providers/config', payload);

            notifications.show({
                title: t('success'),
                message: t('api_settings_saved', 'Settings saved successfully'),
                color: 'green'
            });
            setEditingId(null);
            fetchProviders(); // Refresh
        } catch (error) {
            console.error('Error updating API settings:', error);
            notifications.show({
                title: t('error'),
                message: error.response?.data?.detail || error.message,
                color: 'red'
            });
        } finally {
            setSubmitting(false);
        }
    };

    if (loading) {
        return <Loader size="sm" />;
    }

    return (
        <Stack gap="md">
            <Text c="dimmed" size="sm">
                {t('api_settings_description')}
            </Text>

            <Alert variant="light" color="blue" title="API Configuration" icon={<IconInfoCircle />}>
                {t('api_settings_storage_info')}
            </Alert>

            <div className={styles.grid}>
                {providers.map((provider) => (
                    <div key={provider.id} className={styles.card}>
                        <div className={styles.header}>
                            <Text className={styles.title}>{provider.name}</Text>
                            {provider.is_keyless && (
                                <Badge color="blue" variant="light" className={styles.statusBadge}>{t('api_key_no_required')}</Badge>
                            )}
                            {!provider.is_keyless && provider.has_key && (
                                <Badge color="green" variant="light" className={styles.statusBadge}>{t('api_key_active')}</Badge>
                            )}
                            {!provider.is_keyless && !provider.has_key && (
                                <Badge color="gray" variant="light" className={styles.statusBadge}>{t('api_key_not_configured')}</Badge>
                            )}
                        </div>

                        <Text className={styles.description}>{provider.description}</Text>

                        <div className={styles.actions}>
                            {editingId === provider.id ? (
                                <Stack gap="sm">
                                    <Divider label="Configuration" labelPosition="center" />

                                    {!provider.is_keyless && (
                                        <PasswordInput
                                            label={t('api_key_label', 'API Key')}
                                            placeholder={t('api_key_placeholder')}
                                            value={editForm.apiKey}
                                            onChange={(e) => setEditForm({ ...editForm, apiKey: e.currentTarget.value })}
                                            size="xs"
                                            leftSection={<IconKey size={14} />}
                                        />
                                    )}

                                    {provider.id === 'your_favourite_api' && (
                                        <TextInput
                                            label={t('api_url_label', 'API Base URL')}
                                            placeholder="https://api.example.com/v1"
                                            value={editForm.apiUrl}
                                            onChange={(e) => setEditForm({ ...editForm, apiUrl: e.currentTarget.value })}
                                            size="xs"
                                            leftSection={<IconServer size={14} />}
                                        />
                                    )}

                                    <Select
                                        label={t('api_model_select_label', 'Active Translation Model')}
                                        placeholder={t('api_model_select_placeholder', 'Choose a model to use')}
                                        description={t('api_model_select_description', 'Select which model will perform the translations')}
                                        data={[
                                            ...(provider.available_models || []),
                                            ...(editForm.models || []),
                                            ...(editForm.selectedModel ? [editForm.selectedModel] : [])
                                        ].filter((val, index, self) => val && self.indexOf(val) === index).map(m => ({ value: m, label: m }))}
                                        value={editForm.selectedModel}
                                        onChange={(val) => setEditForm({ ...editForm, selectedModel: val })}
                                        size="xs"
                                        leftSection={<IconRobot size={14} />}
                                        searchable
                                        clearable
                                    />

                                    <TagsInput
                                        label={t('api_models_label', 'Custom Models')}
                                        placeholder={t('api_models_placeholder', 'Type and press Enter to add models')}
                                        description={t('api_models_description', 'Models defined here will appear in the selector above')}
                                        value={editForm.models}
                                        onChange={(val) => {
                                            const isAdded = val.length > editForm.models.length;
                                            setEditForm(prev => ({
                                                ...prev,
                                                models: val,
                                                selectedModel: isAdded ? val[val.length - 1] : prev.selectedModel
                                            }));
                                        }}
                                        size="xs"
                                        leftSection={<IconRobot size={14} />}
                                        clearable
                                    />

                                    <Group grow mt="xs">
                                        <Button
                                            size="xs"
                                            onClick={() => handleSave(provider.id)}
                                            loading={submitting}
                                            leftSection={<IconCheck size={14} />}
                                        >
                                            {t('save')}
                                        </Button>
                                        <Button
                                            variant="subtle"
                                            color="gray"
                                            size="xs"
                                            onClick={handleCancelEdit}
                                            disabled={submitting}
                                        >
                                            {t('cancel')}
                                        </Button>
                                    </Group>
                                </Stack>
                            ) : (
                                <Stack gap="xs">
                                    {!provider.is_keyless && (
                                        <Group justify="space-between">
                                            <Text size="xs" c="dimmed">Key:</Text>
                                            <Text family="monospace" size="xs">
                                                {provider.has_key ? provider.masked_key : t('api_key_none_set')}
                                            </Text>
                                        </Group>
                                    )}

                                    <Group justify="space-between">
                                        <Text size="xs" c="dimmed">Model:</Text>
                                        <Text size="xs" fw={500}>{provider.selected_model || 'N/A'}</Text>
                                    </Group>

                                    {provider.api_url && (
                                        <Group justify="space-between">
                                            <Text size="xs" c="dimmed">URL:</Text>
                                            <Text size="xs" truncate style={{ maxWidth: '150px' }} title={provider.api_url}>
                                                {provider.api_url}
                                            </Text>
                                        </Group>
                                    )}

                                    {provider.custom_models && provider.custom_models.length > 0 && (
                                        <Group justify="space-between">
                                            <Text size="xs" c="dimmed">Models:</Text>
                                            <Badge size="xs" variant="outline">{provider.custom_models.length} custom</Badge>
                                        </Group>
                                    )}

                                    <Button
                                        variant="light"
                                        size="xs"
                                        leftSection={<IconEdit size={14} />}
                                        onClick={() => handleEditClick(provider)}
                                        fullWidth
                                        mt="xs"
                                    >
                                        {t('configure', 'Configure')}
                                    </Button>
                                </Stack>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </Stack>
    );
};

export default ApiSettingsTab;
