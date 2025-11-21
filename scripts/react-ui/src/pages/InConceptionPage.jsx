import React from 'react';
import { useTranslation } from 'react-i18next';
import { Container, Paper, Title, Text, Center } from '@mantine/core';
import { IconBulb } from '@tabler/icons-react';
import layoutStyles from '../components/layout/Layout.module.css';

const InConceptionPage = () => {
  const { t } = useTranslation();

  return (
    <Container>
      <Paper withBorder p="xl" radius="md" className={layoutStyles.glassCard}>
        <Center style={{ flexDirection: 'column', height: '300px' }}>
          <IconBulb size={64} color="yellow" style={{ marginBottom: '20px' }} />
          <Title order={2} mb="md">{t('page_title_in_conception')}</Title>
          <Text c="dimmed">This idea is still in the conception phase.</Text>
        </Center>
      </Paper>
    </Container>
  );
};

export default InConceptionPage;