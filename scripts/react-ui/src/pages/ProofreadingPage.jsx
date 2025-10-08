import React from 'react';
import { useTranslation } from 'react-i18next';

const ProofreadingPage = () => {
  const { t } = useTranslation();

  return (
    <div>
      <h1>{t('page_title_proofreading')}</h1>
      <p>This is the placeholder for the Proofreading Page.</p>
    </div>
  );
};

export default ProofreadingPage;