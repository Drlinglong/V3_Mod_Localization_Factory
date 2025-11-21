import React, { useContext, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Select, Group, Title, Text, Container, Paper, Stack, Divider, Tabs } from '@mantine/core';
import { IconLanguage, IconPalette, IconSettings, IconKey } from '@tabler/icons-react';
import ThemeContext from '../ThemeContext';
import { AVAILABLE_THEMES } from '../config/themes';
import ApiSettingsTab from '../components/ApiSettingsTab';

import styles from './SettingsPage.module.css';

const SettingsPage = () => {
    const { t, i18n } = useTranslation();
    const { theme, toggleTheme } = useContext(ThemeContext);

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
        <Container size="sm" py="xl">
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
                        </Stack>
                    </Tabs.Panel>

                    <Tabs.Panel value="api">
                        <ApiSettingsTab />
                    </Tabs.Panel>
                </Tabs>
            </Paper>
        </Container>
    );
};

export default SettingsPage;