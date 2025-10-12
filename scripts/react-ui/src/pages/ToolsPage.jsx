import React from 'react';
import { useTranslation } from 'react-i18next';
import { Tabs } from 'antd';
import ThumbnailGenerator from '../components/tools/ThumbnailGenerator';
import WorkshopGenerator from '../components/tools/WorkshopGenerator'; // Import the new component
import EventRenderer from './EventRenderer';
import UIDebugger from './UIDebugger';

const ToolsPage = () => {
  const { t } = useTranslation();

  const items = [
    {
      key: '1',
      label: t('tools_tab_thumbnail_generator'),
      children: <ThumbnailGenerator />,
    },
    {
      key: '2',
      label: t('workshop_generator.tab_title'), // Add new tab
      children: <WorkshopGenerator />,
    },
    {
      key: '3',
      label: t('tools_tab_event_renderer'),
      children: <EventRenderer />,
    },
    {
      key: '4',
      label: t('tools_tab_ui_debugger'),
      children: <UIDebugger />,
    },
  ];

  return (
    <div>
      <h1>{t('page_title_tools')}</h1>
      <Tabs defaultActiveKey="1" items={items} />
    </div>
  );
};

export default ToolsPage;