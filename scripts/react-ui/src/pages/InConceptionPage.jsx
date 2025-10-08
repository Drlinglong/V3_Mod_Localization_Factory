import React from 'react';
import { useTranslation } from 'react-i18next';

const InConceptionPage = () => {
  const { t } = useTranslation();

  return (
    <div>
      <h1>{t('page_title_in_conception')}</h1>
      <p>This page is currently in conception.</p>
    </div>
  );
};

export default InConceptionPage;