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
    Alert
} from '@mantine/core';
import { IconCheck, IconX, IconEdit, IconKey, IconInfoCircle } from '@tabler/icons-react';
import { notifications } from '@mantine/notifications';
import { useTranslation } from 'react-i18next';
import styles from './ApiSettingsTab.module.css';

const ApiSettingsTab = () => {
    const { t } = useTranslation();
    const [providers, setProviders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [editingId, setEditingId] = useState(null);
    const [editValue, setEditValue] = useState('');
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        fetchProviders();
    }, []);

    const fetchProviders = async () => {
        try {
            const response = await fetch('/api/api-keys');
            if (response.ok) {
                const data = await response.json();
                setProviders(data);
            } else {
                console.error('Failed to fetch API providers');
                notifications.show({
                    title: t('api_key_error_title'),
                    message: t('api_key_error_fetch'),
                    color: 'red'
                });
            }
        } catch (error) {
            console.error('Error fetching API providers:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleEditClick = (provider) => {
        setEditingId(provider.id);
        setEditValue(''); // Start empty for security/cleanliness, or could pre-fill if we had the key (we don't)
    };

    const handleCancelEdit = () => {
        setEditingId(null);
        setEditValue('');
    };

    const handleSave = async (providerId) => {
        if (!editValue.trim()) {
            notifications.show({
                title: t('api_key_error_title'),
                message: t('api_key_validation_empty'),
                color: 'yellow'
            });
            return;
        }

        setSubmitting(true);
        try {
            const response = await fetch('/api/api-keys', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    provider_id: providerId,
                    api_key: editValue
                }),
            });

            if (response.ok) {
                notifications.show({
                    title: t('api_key_success_title'),
                    message: t('api_key_success_message'),
                    color: 'green'
                });
                setEditingId(null);
                fetchProviders(); // Refresh to get updated masked key
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to update key');
            }
        } catch (error) {
            console.error('Error updating API key:', error);
            notifications.show({
                title: t('api_key_error_title'),
                message: error.message,
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

            <Alert variant="light" color="blue" title="API Key Storage" icon={<IconInfoCircle />}>
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

                        {!provider.is_keyless && (
                            <div className={styles.actions}>
                                {editingId === provider.id ? (
                                    <Stack gap="xs">
                                        <PasswordInput
                                            placeholder={t('api_key_placeholder')}
                                            value={editValue}
                                            onChange={(event) => setEditValue(event.currentTarget.value)}
                                            size="sm"
                                            autoFocus
                                        />
                                        <Group grow>
                                            <Button
                                                size="xs"
                                                onClick={() => handleSave(provider.id)}
                                                loading={submitting}
                                                leftSection={<IconCheck size={14} />}
                                            >
                                                {t('api_key_save')}
                                            </Button>
                                            <Button
                                                variant="subtle"
                                                color="gray"
                                                size="xs"
                                                onClick={handleCancelEdit}
                                                disabled={submitting}
                                            >
                                                {t('api_key_cancel')}
                                            </Button>
                                        </Group>
                                    </Stack>
                                ) : (
                                    <Group justify="space-between" align="center">
                                        <Text family="monospace" size="xs" c="dimmed">
                                            {provider.has_key ? t('api_key_current', { key: provider.masked_key }) : t('api_key_none_set')}
                                        </Text>
                                        <Button
                                            variant="light"
                                            size="xs"
                                            leftSection={<IconEdit size={14} />}
                                            onClick={() => handleEditClick(provider)}
                                        >
                                            {provider.has_key ? t('api_key_update') : t('api_key_set')}
                                        </Button>
                                    </Group>
                                )}
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </Stack>
    );
};

export default ApiSettingsTab;
