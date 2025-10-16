import React from 'react';
import { useTranslation } from 'react-i18next';
import { Title, Text } from '@mantine/core';

const EventRenderer = () => {
    const { t } = useTranslation();
    return (
        <div style={{ padding: '24px' }}>
            <Title order={2}>{t('page_title_event_renderer')}</Title>
            <Text>
                {t('placeholder_event_renderer_description')}
            </Text>
        </div>
    );
};

export default EventRenderer;
