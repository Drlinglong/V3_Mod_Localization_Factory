import React from 'react';
import { useTranslation } from 'react-i18next';
import { Tabs, Title, Container, Paper } from '@mantine/core';
import { IconPhoto, IconTools, IconBug, IconCode } from '@tabler/icons-react';
import ThumbnailGenerator from '../components/tools/ThumbnailGenerator';
import WorkshopGenerator from '../components/tools/WorkshopGenerator';
import EventRenderer from './EventRenderer';
import UIDebugger from './UIDebugger';
import layoutStyles from '../components/layout/Layout.module.css';
import { FEATURES } from '../config/features';

const ToolsPage = () => {
    const { t } = useTranslation();

    return (
        <Container size="lg" py="xl">
            <Paper withBorder p="xl" radius="md" className={layoutStyles.glassCard}>
                <Title order={2} mb="xl">{t('page_title_tools')}</Title>
                <Tabs defaultValue="thumbnail" variant="pills" radius="md">
                    <Tabs.List mb="lg">
                        <Tabs.Tab value="thumbnail" leftSection={<IconPhoto size={16} />}>{t('tools_tab_thumbnail_generator')}</Tabs.Tab>

                        {FEATURES.ENABLE_WORKSHOP_GENERATOR && (
                            <Tabs.Tab value="workshop" leftSection={<IconTools size={16} />}>{t('tools_tab_workshop_generator')}</Tabs.Tab>
                        )}

                        {FEATURES.ENABLE_EVENT_RENDERER && (
                            <Tabs.Tab value="event" leftSection={<IconCode size={16} />}>{t('tools_tab_event_renderer')}</Tabs.Tab>
                        )}

                        {FEATURES.ENABLE_UI_DEBUGGER && (
                            <Tabs.Tab value="debugger" leftSection={<IconBug size={16} />}>{t('tools_tab_ui_debugger')}</Tabs.Tab>
                        )}
                    </Tabs.List>

                    <Tabs.Panel value="thumbnail">
                        <ThumbnailGenerator />
                    </Tabs.Panel>

                    {FEATURES.ENABLE_WORKSHOP_GENERATOR && (
                        <Tabs.Panel value="workshop">
                            <WorkshopGenerator />
                        </Tabs.Panel>
                    )}

                    {FEATURES.ENABLE_EVENT_RENDERER && (
                        <Tabs.Panel value="event">
                            <EventRenderer />
                        </Tabs.Panel>
                    )}

                    {FEATURES.ENABLE_UI_DEBUGGER && (
                        <Tabs.Panel value="debugger">
                            <UIDebugger />
                        </Tabs.Panel>
                    )}
                </Tabs>
            </Paper>
        </Container>
    );
};

export default ToolsPage;