import React from 'react';
import { useTranslation } from 'react-i18next';
import { Container, Paper, Title, Text, Center } from '@mantine/core';
import { IconCode } from '@tabler/icons-react';
import layoutStyles from '../components/layout/Layout.module.css';

const UnderDevelopmentPage = () => {
  const { t } = useTranslation();

  return (
    <Container>
      <Paper withBorder p="xl" radius="md" className={layoutStyles.glassCard}>
        <Center style={{ flexDirection: 'column', height: '300px' }}>
          <IconCode size={64} color="blue" style={{ marginBottom: '20px' }} />
          <Title order={2} mb="md">{t('page_title_under_development')}</Title>
          <Text c="dimmed">This feature is currently in development.</Text>
        </Center>
      </Paper>
    </Container>
  );
};

export default UnderDevelopmentPage;