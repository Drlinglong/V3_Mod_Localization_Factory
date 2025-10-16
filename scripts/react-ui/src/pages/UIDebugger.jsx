import React from 'react';
import { useTranslation } from 'react-i18next';
import { Title, Text } from '@mantine/core';

const UIDebugger = () => {
    const { t } = useTranslation();
    return (
        <div style={{ padding: '24px' }}>
            <Title order={2}>{t('page_title_ui_debugger')}</Title>
            <Text>
                {t('placeholder_ui_debugger_description')}
            </Text>
        </div>
    );
};

export default UIDebugger;
