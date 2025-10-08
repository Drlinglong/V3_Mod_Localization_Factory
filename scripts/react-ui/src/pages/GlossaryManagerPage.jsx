import React from 'react';
import { useTranslation } from 'react-i18next';

const GlossaryManagerPage = () => {
  const { t } = useTranslation();

  return (
    <div>
      <h1>{t('page_title_glossary_manager')}</h1>
      <p>This is the placeholder for the Glossary Manager Page.</p>
    </div>
  );
};

export default GlossaryManagerPage;