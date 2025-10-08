import React from 'react';
import { useTranslation } from 'react-i18next';
import { Select, Button, Space, Typography } from 'antd'; // Import Ant Design components

const { Option } = Select;
const { Title } = Typography;

const SettingsPage = () => {
  const { t, i18n } = useTranslation();

  const handleLanguageChange = (value) => {
    i18n.changeLanguage(value);
  };

  const handleThemeChange = (value) => {
    console.log(`Theme changed to: ${value}`);
    // Implement theme change logic here
  };

  const handleSaveSettings = () => {
    console.log('Settings saved!');
    // Implement save settings logic here
  };

  return (
    <div>
      <Title level={2}>{t('page_title_settings')}</Title>
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        <div>
          <label htmlFor="language-select" style={{ marginRight: '10px' }}>{t('settings_language')}:</label>
          <Select
            id="language-select"
            defaultValue={i18n.language}
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
            defaultValue="light" // Default theme
            style={{ width: 120 }}
            onChange={handleThemeChange}
          >
            <Option value="light">{t('theme_light')}</Option>
            <Option value="dark">{t('theme_dark')}</Option>
          </Select>
        </div>
        <Button type="primary" onClick={handleSaveSettings}>
          {t('settings_save')}
        </Button>
      </Space>
    </div>
  );
};

export default SettingsPage;