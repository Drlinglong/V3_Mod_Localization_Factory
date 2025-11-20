import React, { useContext, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Select, Group, Title, Text, Container, Paper, Stack, Divider } from '@mantine/core';
import { IconLanguage, IconPalette } from '@tabler/icons-react';
import ThemeContext from '../ThemeContext';
import { AVAILABLE_THEMES } from '../config/themes';

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
            <Paper withBorder p="xl" radius="md" bg="dark.7">
                <Title order={2} mb="xl">{t('page_title_settings')}</Title>

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
            </Paper>
        </Container>
    );
};

export default SettingsPage;