import React from 'react';
import { useTranslation } from 'react-i18next';

const UnderDevelopmentPage = () => {
  const { t } = useTranslation();

  return (
    <div>
      <h1>{t('page_title_under_development')}</h1>
      <p>This page is currently under development.</p>
    </div>
  );
};

export default UnderDevelopmentPage;