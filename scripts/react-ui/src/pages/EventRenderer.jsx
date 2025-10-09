import React from 'react';
import { useTranslation } from 'react-i18next';
import { Typography } from 'antd';

const { Title, Paragraph } = Typography;

const EventRenderer = () => {
  const { t } = useTranslation();

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>{t('page_title_event_renderer')}</Title>
      <Paragraph>
        {t('placeholder_event_renderer_description')}
      </Paragraph>
    </div>
  );
};

export default EventRenderer;
