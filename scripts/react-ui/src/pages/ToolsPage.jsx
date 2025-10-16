import React from 'react';
import { useTranslation } from 'react-i18next';
import { Tabs, Title } from '@mantine/core';
import ThumbnailGenerator from '../components/tools/ThumbnailGenerator';
import WorkshopGenerator from '../components/tools/WorkshopGenerator'; // Import the new component
import EventRenderer from './EventRenderer';
import UIDebugger from './UIDebugger';

const ToolsPage = () => {
  const { t } = useTranslation();

  return (
    <div>
            <Title order={1}>{t('page_title_tools')}</Title>
            <Tabs defaultValue="thumbnail">
                <Tabs.List>
                    <Tabs.Tab value="thumbnail">{t('tools_tab_thumbnail_generator')}</Tabs.Tab>
                    <Tabs.Tab value="workshop">{t('tools_tab_workshop_generator')}</Tabs.Tab>
                    <Tabs.Tab value="event">{t('tools_tab_event_renderer')}</Tabs.Tab>
                    <Tabs.Tab value="debugger">{t('tools_tab_ui_debugger')}</Tabs.Tab>
                </Tabs.List>

                <Tabs.Panel value="thumbnail" pt="xs">
                    <ThumbnailGenerator />
                </Tabs.Panel>
                 <Tabs.Panel value="workshop" pt="xs">
                    <WorkshopGenerator />
                </Tabs.Panel>
                <Tabs.Panel value="event" pt="xs">
                    <EventRenderer />
                </Tabs.Panel>
                <Tabs.Panel value="debugger" pt="xs">
                    <UIDebugger />
                </Tabs.Panel>
            </Tabs>
    </div>
  );
};

export default ToolsPage;