import React from 'react';
import { useTranslation } from 'react-i18next';
import { Stack, Group, Text, Title, Paper, Anchor, Alert, ThemeIcon, List, Box, Divider } from '@mantine/core';
import { IconBrandGithub, IconInfoCircle, IconStar, IconBug, IconFileCode } from '@tabler/icons-react';

const VersionInfoTab = () => {
    const { t } = useTranslation();
    const version = "v2.1.0-stable"; // Project version
    const lastUpdated = "2026-01-02"; // Last updated date
    const githubRepoUrl = "https://github.com/Drlinglong/V3_Mod_Localization_Factory";

    return (
        <Stack gap="xl" py="md">
            {/* Project Summary */}
            <Paper withBorder p="lg" radius="md" style={{ background: 'rgba(255, 255, 255, 0.05)', backdropFilter: 'blur(10px)' }}>
                <Group justify="space-between" align="flex-start">
                    <Stack gap={0}>
                        <Title order={3}>{t('app_title')}</Title>
                        <Group gap="xs" mt="xs">
                            <Text size="sm" c="dimmed">{t('version_info.project_version')}:</Text>
                            <Text size="sm" fw={700} c="cyan">{version}</Text>
                        </Group>
                        <Group gap="xs">
                            <Text size="sm" c="dimmed">{t('version_info.last_updated')}:</Text>
                            <Text size="sm">{lastUpdated}</Text>
                        </Group>
                    </Stack>
                    <Anchor href={githubRepoUrl} target="_blank">
                        <ThemeIcon size={48} radius="xl" variant="light" color="gray">
                            <IconBrandGithub size={30} />
                        </ThemeIcon>
                    </Anchor>
                </Group>

                <Divider my="lg" opacity={0.5} />

                <Group>
                    <IconStar size={20} color="var(--mantine-color-yellow-filled)" />
                    <Text size="sm" fw={500}>{t('version_info.star_encouragement')}</Text>
                    <Anchor href={githubRepoUrl} target="_blank" size="sm" ml="auto">
                        {t('version_info.github_link_text')}
                    </Anchor>
                </Group>
            </Paper>

            {/* Feedback & Integrity */}
            <Alert
                icon={<IconBug size={20} />}
                title={t('version_info.issue_title')}
                color="blue"
                radius="md"
                variant="light"
            >
                <Stack gap="xs">
                    <Text size="sm">
                        {t('version_info.issue_desc')}
                    </Text>
                    <Box
                        p="xs"
                        style={{
                            background: 'rgba(0, 0, 0, 0.2)',
                            borderRadius: '4px',
                            border: '1px solid rgba(255, 255, 255, 0.1)'
                        }}
                    >
                        <Group gap="xs" align="flex-start">
                            <IconFileCode size={18} style={{ marginTop: 2 }} />
                            <Text size="xs" style={{ whiteSpace: 'pre-wrap' }}>
                                {t('version_info.log_hint')}
                            </Text>
                        </Group>
                    </Box>
                    <Anchor href={`${githubRepoUrl}/issues`} target="_blank" size="sm" fw={700}>
                        Go to Issues
                    </Anchor>
                </Stack>
            </Alert>

            {/* Credits / Additional Links can go here */}
            <Paper p="md" radius="md" style={{ background: 'transparent' }}>
                <Text size="xs" c="dimmed" ta="center">
                    {t('footer_text')}
                </Text>
            </Paper>
        </Stack>
    );
};

export default VersionInfoTab;
