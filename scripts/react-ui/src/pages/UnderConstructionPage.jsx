import React from 'react';
import { useTranslation } from 'react-i18next';

const UnderConstructionPage = () => {
  const { t } = useTranslation();

  return (
    <div>
      <h1>{t('page_title_under_construction')}</h1>
      <p>This page is currently under construction.</p>
    </div>
  );
};

export default UnderConstructionPage;