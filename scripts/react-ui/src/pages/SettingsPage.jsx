import React, { useContext, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Select, Space, Typography } from 'antd';
import ThemeContext from '../ThemeContext';
import { AVAILABLE_THEMES } from '../config/themes';

const { Option } = Select;
const { Title } = Typography;

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
      <Title level={2}>{t('page_title_settings')}</Title>
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        <div>
          <label htmlFor="language-select" style={{ marginRight: '10px' }}>{t('settings_language')}:</label>
          <Select
            id="language-select"
            value={i18n.language}
            style={{ width: 120 }}
            onChange={handleLanguageChange}
          >
            <Option value="en">English</Option>
            <Option value="zh">中文</Option>
          </Select>
        </div>
        <div>
          <label htmlFor="theme-select" style={{ marginRight: '10px' }}>{t('settings_theme')}:</label>
          <Select
            id="theme-select"
            value={theme}
            style={{ width: 120 }}
            onChange={handleThemeChange}
          >
            {AVAILABLE_THEMES.map((themeOption) => (
              <Option key={themeOption.id} value={themeOption.id}>
                {t(themeOption.nameKey)}
              </Option>
            ))}
          </Select>
        </div>
      </Space>
    </div>
  );
};

export default SettingsPage;
