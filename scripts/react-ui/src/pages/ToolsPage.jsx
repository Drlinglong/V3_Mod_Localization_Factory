import React from 'react';
import { useTranslation } from 'react-i18next';
import ThumbnailGenerator from '../components/tools/ThumbnailGenerator';

const ToolsPage = () => {
  const { t } = useTranslation();

  return (
    <div>
      <h1>{t('page_title_tools')}</h1>
      <ThumbnailGenerator />
    </div>
  );
};

export default ToolsPage;