import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Grid, Card, Title, Text, ThemeIcon, Group, Stack, Box, Button, BackgroundImage, Overlay, ActionIcon, ScrollArea } from '@mantine/core';
import { IconRocket, IconRefresh, IconChartBar, IconVocabulary, IconChecklist, IconActivity } from '@tabler/icons-react';
import ActionCard from '../components/ActionCard';
import ProjectStatusPieChart from '../components/ProjectStatusPieChart';
import GlossaryAnalysisBarChart from '../components/GlossaryAnalysisBarChart';
import StatCard from '../components/StatCard';
import RecentActivityList from '../components/RecentActivityList';

import styles from './HomePage.module.css';

const HomePage = () => {
  const { t } = useTranslation();
  const [slogan, setSlogan] = useState('');
  const [greeting, setGreeting] = useState('');

  useEffect(() => {
    const slogans = t('homepage_slogans', { returnObjects: true });
    if (Array.isArray(slogans) && slogans.length > 0) {
      const randomIndex = Math.floor(Math.random() * slogans.length);
      setSlogan(slogans[randomIndex]);
    }

    const hour = new Date().getHours();
    if (hour < 12) setGreeting('Good Morning');
    else if (hour < 18) setGreeting('Good Afternoon');
    else setGreeting('Good Evening');
  }, [t]);

  return (
    <Box h="100vh" style={{ overflow: 'hidden' }}>
      <ScrollArea h="100%" type="scroll">
        <Box p="md">
          {/* Welcome Banner */}
          <Box
            mb="xl"
            className={styles.welcomeBanner}
            p={40}
          >
            <Stack style={{ position: 'relative', zIndex: 2 }}>
              <Title order={1} className={styles.cardTitle} style={{ fontSize: '2.5rem', fontWeight: 800 }}>
                {greeting}, User!
              </Title>
              <Text size="lg" style={{ opacity: 0.9, maxWidth: '600px', color: 'var(--text-main)' }}>
                "{slogan}"
              </Text>
              <Group mt="lg">
                <Button size="md" radius="md" leftSection={<IconRocket size={20} />} className={styles.actionButton}>
                  {t('homepage_action_card_new_project')}
                </Button>
                <Button size="md" radius="md" leftSection={<IconRefresh size={20} />} className={styles.actionButton}>
                  {t('homepage_action_card_update_project')}
                </Button>
              </Group>
            </Stack>

            {/* Decorative Background Elements */}
            <IconRocket
              size={300}
              style={{
                position: 'absolute',
                right: -50,
                bottom: -50,
                opacity: 0.1,
                color: 'var(--text-highlight)',
                transform: 'rotate(-15deg)'
              }}
            />
          </Box>

          {/* Key Metrics Row */}
          <Grid gutter="md" mb="xl">
            <Grid.Col span={{ xs: 12, sm: 6, lg: 3 }}>
              <StatCard
                title="Total Projects"
                value="12"
                icon={<IconChecklist size={24} />}
                color="blue"
                progress={75}
                trend={12}
                className={styles.glassCard}
              />
            </Grid.Col>
            <Grid.Col span={{ xs: 12, sm: 6, lg: 3 }}>
              <StatCard
                title="Words Translated"
                value="45,231"
                icon={<IconVocabulary size={24} />}
                color="teal"
                progress={45}
                trend={5.4}
                className={styles.glassCard}
              />
            </Grid.Col>
            <Grid.Col span={{ xs: 12, sm: 6, lg: 3 }}>
              <StatCard
                title="Active Tasks"
                value="8"
                icon={<IconActivity size={24} />}
                color="orange"
                progress={25}
                trend={-2}
                className={styles.glassCard}
              />
            </Grid.Col>
            <Grid.Col span={{ xs: 12, sm: 6, lg: 3 }}>
              <StatCard
                title="Completion Rate"
                value="89%"
                icon={<IconChartBar size={24} />}
                color="grape"
                progress={89}
                trend={1.2}
                className={styles.glassCard}
              />
            </Grid.Col>
          </Grid>

          {/* Main Dashboard Content */}
          <Grid gutter="md">
            {/* Left Column: Charts */}
            <Grid.Col span={{ xs: 12, lg: 8 }}>
              <Stack gap="md">
                <Card shadow="sm" padding="lg" radius="md" withBorder className={styles.glassCard}>
                  <Group justify="space-between" mb="md">
                    <Title order={4} className={styles.cardTitle}>{t('homepage_chart_pie_title')}</Title>
                    <ActionIcon variant="subtle" color="gray"><IconRefresh size={16} /></ActionIcon>
                  </Group>
                  <ProjectStatusPieChart />
                </Card>
                <Card shadow="sm" padding="lg" radius="md" withBorder className={styles.glassCard}>
                  <Group justify="space-between" mb="md">
                    <Title order={4} className={styles.cardTitle}>{t('homepage_chart_bar_title')}</Title>
                    <ActionIcon variant="subtle" color="gray"><IconRefresh size={16} /></ActionIcon>
                  </Group>
                  <GlossaryAnalysisBarChart />
                </Card>
              </Stack>
            </Grid.Col>

            {/* Right Column: Recent Activity & Quick Actions */}
            <Grid.Col span={{ xs: 12, lg: 4 }}>
              <Stack gap="md">
                <RecentActivityList className={styles.glassCard} />

                <Card shadow="sm" padding="lg" radius="md" withBorder className={styles.glassCard}>
                  <Title order={4} mb="md" className={styles.cardTitle}>Quick Links</Title>
                  <Stack gap="xs">
                    <Button variant="light" color="blue" fullWidth justify="flex-start" leftSection={<IconRocket size={16} />} className={styles.actionButton}>
                      New Translation
                    </Button>
                    <Button variant="light" color="teal" fullWidth justify="flex-start" leftSection={<IconRefresh size={16} />} className={styles.actionButton}>
                      Sync Glossary
                    </Button>
                    <Button variant="light" color="orange" fullWidth justify="flex-start" leftSection={<IconChecklist size={16} />} className={styles.actionButton}>
                      Proofread Pending
                    </Button>
                  </Stack>
                </Card>
              </Stack>
            </Grid.Col>
          </Grid>
        </Box>
      </ScrollArea>
    </Box>
  );
};

export default HomePage;
