import React from 'react';
import { useTranslation } from 'react-i18next';
import { Container, Paper, Title, Text, Center } from '@mantine/core';
import { IconCrane } from '@tabler/icons-react';
import layoutStyles from '../components/layout/Layout.module.css';

const UnderConstructionPage = () => {
  const { t } = useTranslation();

  return (
    <Container size="md" py="xl">
      <Paper withBorder p="xl" radius="md" className={layoutStyles.glassCard}>
        <Center style={{ flexDirection: 'column', height: '300px' }}>
          <IconCrane size={64} color="orange" style={{ marginBottom: '20px' }} />
          <Title order={2} mb="md">{t('page_title_under_construction')}</Title>
          <Text c="dimmed">We are working hard to bring you this page.</Text>
        </Center>
      </Paper>
    </Container>
  );
};

export default UnderConstructionPage;