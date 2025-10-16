import React, { useContext, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Select, Group, Title, Text } from '@mantine/core';
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
        <div>
            <Title order={2}>{t('page_title_settings')}</Title>
            <Group direction="column" gap="lg" mt="md">
                <Group>
                    <Text>{t('settings_language')}:</Text>
                    <Select
                        value={i18n.language}
                        onChange={handleLanguageChange}
                        data={[
                            { value: 'en', label: 'English' },
                            { value: 'zh', label: '中文' },
                        ]}
                        style={{ width: 150 }}
                    />
                </Group>
                <Group>
                    <Text>{t('settings_theme')}:</Text>
                    <Select
                        value={theme}
                        onChange={handleThemeChange}
                        data={AVAILABLE_THEMES.map(theme => ({ value: theme.id, label: t(theme.nameKey) }))}
                        style={{ width: 150 }}
                    />
                </Group>
            </Group>
        </div>
    );
};

export default SettingsPage;