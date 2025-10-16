import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Grid, Card, Title, Text } from '@mantine/core';
import ActionCard from '../components/ActionCard';
import ProjectStatusPieChart from '../components/ProjectStatusPieChart';
import GlossaryAnalysisBarChart from '../components/GlossaryAnalysisBarChart';

const HomePage = () => {
  const { t } = useTranslation();
  const [slogan, setSlogan] = useState('');

  useEffect(() => {
    const slogans = t('homepage_slogans', { returnObjects: true });
    if (Array.isArray(slogans) && slogans.length > 0) {
      const randomIndex = Math.floor(Math.random() * slogans.length);
      setSlogan(slogans[randomIndex]);
    }
  }, [t]);

  return (
    <div style={{ padding: '24px' }}>
      <Card shadow="sm" padding="lg" radius="md" withBorder style={{ marginBottom: '24px', textAlign: 'center' }}>
        <Title order={3}>{t('homepage_title')}</Title>
        <Text>"{slogan}"</Text>
      </Card>

      <Grid gutter="xl">
        <Grid.Col span={{ xs: 12, sm: 6 }}>
          <ActionCard
            icon={t('homepage_action_card_new_project_icon')}
            title={t('homepage_action_card_new_project')}
            linkTo="/translation"
          />
        </Grid.Col>
        <Grid.Col span={{ xs: 12, sm: 6 }}>
          <ActionCard
            icon={t('homepage_action_card_update_project_icon')}
            title={t('homepage_action_card_update_project')}
            linkTo="/translation"
          />
        </Grid.Col>
      </Grid>

      <Grid gutter="xl" style={{ marginTop: '24px' }}>
        <Grid.Col span={{ xs: 12, lg: 6 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Title order={4}>{t('homepage_chart_pie_title')}</Title>
            <ProjectStatusPieChart />
          </Card>
        </Grid.Col>
        <Grid.Col span={{ xs: 12, lg: 6 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Title order={4}>{t('homepage_chart_bar_title')}</Title>
            <GlossaryAnalysisBarChart />
          </Card>
        </Grid.Col>
      </Grid>
    </div>
  );
};

export default HomePage;
