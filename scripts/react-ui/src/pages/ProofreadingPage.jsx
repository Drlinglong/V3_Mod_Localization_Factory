
import React from 'react';
import { useTranslation } from 'react-i18next';
import { Container, Paper, Title, Text, Center } from '@mantine/core';
import { IconChecklist } from '@tabler/icons-react';
import layoutStyles from '../components/layout/Layout.module.css';

const ProofreadingPage = () => {
  const { t } = useTranslation();

  return (
    <Container>
      <Paper withBorder p="xl" radius="md" className={layoutStyles.glassCard}>
        <Center style={{ flexDirection: 'column', height: '300px' }}>
          <IconChecklist size={64} color="teal" style={{ marginBottom: '20px' }} />
          <Title order={2} mb="md">{t('page_title_proofreading')}</Title>
          <Text c="dimmed">Proofreading features are coming soon.</Text>
        </Center>
      </Paper>
    </Container>
  );
};

export default ProofreadingPage;