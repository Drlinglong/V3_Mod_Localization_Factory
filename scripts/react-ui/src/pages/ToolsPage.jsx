import React from 'react';
import { useTranslation } from 'react-i18next';
import { Tabs, Title, Container, Paper } from '@mantine/core';
import { IconPhoto, IconTools, IconBug, IconCode } from '@tabler/icons-react';
import ThumbnailGenerator from '../components/tools/ThumbnailGenerator';
import WorkshopGenerator from '../components/tools/WorkshopGenerator';
import EventRenderer from './EventRenderer';
import UIDebugger from './UIDebugger';

const ToolsPage = () => {
    const { t } = useTranslation();

    return (
        <Container size="xl" py="xl">
            <Paper withBorder p="xl" radius="md" bg="dark.7">
                <Title order={2} mb="xl">{t('page_title_tools')}</Title>
                <Tabs defaultValue="thumbnail" variant="pills" radius="md">
                    <Tabs.List mb="lg">
                        <Tabs.Tab value="thumbnail" leftSection={<IconPhoto size={16} />}>{t('tools_tab_thumbnail_generator')}</Tabs.Tab>
                        <Tabs.Tab value="workshop" leftSection={<IconTools size={16} />}>{t('tools_tab_workshop_generator')}</Tabs.Tab>
                        <Tabs.Tab value="event" leftSection={<IconCode size={16} />}>{t('tools_tab_event_renderer')}</Tabs.Tab>
                        <Tabs.Tab value="debugger" leftSection={<IconBug size={16} />}>{t('tools_tab_ui_debugger')}</Tabs.Tab>
                    </Tabs.List>

                    <Tabs.Panel value="thumbnail">
                        <ThumbnailGenerator />
                    </Tabs.Panel>
                    <Tabs.Panel value="workshop">
                        <WorkshopGenerator />
                    </Tabs.Panel>
                    <Tabs.Panel value="event">
                        <EventRenderer />
                    </Tabs.Panel>
                    <Tabs.Panel value="debugger">
                        <UIDebugger />
                    </Tabs.Panel>
                </Tabs>
            </Paper>
        </Container>
    );
};

export default ToolsPage;