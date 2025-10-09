import React from 'react';
import { useTranslation } from 'react-i18next';
import { Typography } from 'antd';

const { Title, Paragraph } = Typography;

const UIDebugger = () => {
  const { t } = useTranslation();

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>{t('page_title_ui_debugger')}</Title>
      <Paragraph>
        {t('placeholder_ui_debugger_description')}
      </Paragraph>
    </div>
  );
};

export default UIDebugger;
