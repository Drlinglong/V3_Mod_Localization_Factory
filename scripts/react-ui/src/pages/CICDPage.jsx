import React from 'react';
import { useTranslation } from 'react-i18next';
import { Container, Paper, Title, Text, Center, Stack } from '@mantine/core';
import { IconRocket } from '@tabler/icons-react';

const CICDPage = () => {
  const { t } = useTranslation();

  return (
    <Container size="md" py="xl">
      <Paper withBorder p="xl" radius="md" bg="dark.7">
        <Center style={{ flexDirection: 'column', height: '300px' }}>
          <IconRocket size={64} color="gray" style={{ marginBottom: '20px' }} />
          <Title order={2} mb="md">{t('page_title_cicd')}</Title>
          <Text c="dimmed">This feature is coming soon.</Text>
        </Center>
      </Paper>
    </Container>
  );
};

export default CICDPage;