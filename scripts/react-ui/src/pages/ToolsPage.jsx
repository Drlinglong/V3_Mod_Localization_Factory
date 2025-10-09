import React from 'react';
import { useTranslation } from 'react-i18next';
import { Tabs } from 'antd';
import ThumbnailGenerator from '../components/tools/ThumbnailGenerator';
import UnderConstructionPage from './UnderConstructionPage';

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
      label: t('tools_tab_future_tools'),
      children: <UnderConstructionPage />,
      disabled: true,
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