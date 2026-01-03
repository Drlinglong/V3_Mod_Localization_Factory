import React, { useContext, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Select, Group, Title, Text, Container, Paper, Stack, Divider, Tabs, Box, Button, Modal } from '@mantine/core';
import api from '../utils/api';
import { IconLanguage, IconPalette, IconSettings, IconKey, IconMessage, IconInfoCircle } from '@tabler/icons-react';
import ThemeContext from '../ThemeContext';
import { AVAILABLE_THEMES } from '../config/themes';
import ApiSettingsTab from '../components/ApiSettingsTab';
import PromptSettingsTab from '../components/PromptSettingsTab';
import VersionInfoTab from '../components/VersionInfoTab';

import styles from './SettingsPage.module.css';


const SettingsPage = () => {
    const { t, i18n } = useTranslation();
    const { theme, toggleTheme } = useContext(ThemeContext);
    const [resetModalOpen, setResetModalOpen] = React.useState(false);

    useEffect(() => {
        const savedLanguage = localStorage.getItem('language');
        if (savedLanguage) {
            i18n.changeLanguage(savedLanguage);
        }
    }, [i18n]);

    const handleLanguageChange = (value) => {
        i18n.changeLanguage(value);
        localStorage.setItem('language', value);
    };

    const handleThemeChange = (value) => {
        toggleTheme(value);
    };

    return (
        <Box style={{ flex: 1, overflowY: 'auto', height: '100%' }}>
            <Container fluid py="xl">
                <Paper withBorder p="xl" radius="md" className={styles.glassCard}>
                    <Title order={2} mb="xl" className={styles.headerTitle}>{t('page_title_settings')}</Title>

                    <Tabs defaultValue="general">
                        <Tabs.List mb="lg">
                            <Tabs.Tab value="general" leftSection={<IconSettings size={16} />}>
                                {t('settings_general') || 'General'}
                            </Tabs.Tab>
                            <Tabs.Tab value="api" leftSection={<IconKey size={16} />}>
                                {t('settings_api') || 'API Settings'}
                            </Tabs.Tab>
                            <Tabs.Tab value="prompts" leftSection={<IconMessage size={16} />}>
                                {t('settings_prompts') || 'Prompt Settings'}
                            </Tabs.Tab>
                            <Tabs.Tab value="version" leftSection={<IconInfoCircle size={16} />}>
                                {t('version_info.tab_title') || 'Version Info'}
                            </Tabs.Tab>
                        </Tabs.List>

                        <Tabs.Panel value="general">
                            <Stack gap="lg">
                                <Group justify="space-between">
                                    <Group>
                                        <IconLanguage size={20} />
                                        <Text fw={500}>{t('settings_language')}</Text>
                                    </Group>
                                    <Select
                                        value={i18n.language}
                                        onChange={handleLanguageChange}
                                        data={[
                                            { value: 'en', label: 'English' },
                                            { value: 'zh', label: '中文' },
                                        ]}
                                        style={{ width: 200 }}
                                    />
                                </Group>

                                <Divider />

                                <Group justify="space-between">
                                    <Group>
                                        <IconPalette size={20} />
                                        <Text fw={500}>{t('settings_theme')}</Text>
                                    </Group>
                                    <Select
                                        value={theme}
                                        onChange={handleThemeChange}
                                        data={AVAILABLE_THEMES.map(theme => ({ value: theme.id, label: t(theme.nameKey) }))}
                                        style={{ width: 200 }}
                                    />
                                </Group>

                                <Divider my="xl" label={t('settings_system_maintenance')} labelPosition="center" />

                                <Group justify="space-between">
                                    <Box>
                                        <Text fw={500} c="red">{t('settings_reset_db_title')}</Text>
                                        <Text size="sm" c="dimmed">
                                            {t('settings_reset_db_desc')}
                                        </Text>
                                    </Box>
                                    <Button color="red" variant="light" onClick={() => setResetModalOpen(true)}>
                                        {t('btn_reset_db')}
                                    </Button>
                                </Group>
                            </Stack>
                        </Tabs.Panel>

                        <Tabs.Panel value="api">
                            <ApiSettingsTab />
                        </Tabs.Panel>

                        <Tabs.Panel value="prompts">
                            <PromptSettingsTab />
                        </Tabs.Panel>

                        <Tabs.Panel value="version">
                            <VersionInfoTab />
                        </Tabs.Panel>
                    </Tabs>
                </Paper>
            </Container>

            <Modal
                opened={resetModalOpen}
                onClose={() => setResetModalOpen(false)}
                title={<Text c="red" fw={700}>⚠️ DANGER: Reset Project Database</Text>}
                centered
            >
                <Stack>
                    <Text size="sm">
                        Are you sure you want to wipe the internal database?
                    </Text>
                    <Text size="sm" fw={700}>
                        This action will:
                    </Text>
                    <ul style={{ fontSize: '0.9em', marginTop: 0 }}>
                        <li>Remove all projects from the "Open Recent" list.</li>
                        <li>Clear all file status (Todo/Done/Proofreading) in the dashboard.</li>
                    </ul>
                    <Text size="sm" fw={700} c="green">
                        This action will NOT:
                    </Text>
                    <ul style={{ fontSize: '0.9em', marginTop: 0 }}>
                        <li>Delete your translations.</li>
                        <li>Delete your source files.</li>
                        <li>Modify any file on your disk.</li>
                    </ul>

                    <Group justify="flex-end" mt="md">
                        <Button variant="default" onClick={() => setResetModalOpen(false)}>Cancel</Button>
                        <Button color="red" onClick={async () => {
                            try {
                                await api.post('/api/system/reset-db');
                                setResetModalOpen(false);
                                alert("Database reset successfully. The application will now reload.");
                                window.location.reload();
                            } catch (e) {
                                alert("Failed to reset database: " + e.message);
                            }
                        }}>
                            Confirm Reset
                        </Button>
                    </Group>
                </Stack>
            </Modal>
        </Box>
    );
};

export default SettingsPage;