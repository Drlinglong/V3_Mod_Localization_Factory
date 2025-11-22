import React from 'react';
import { Title, Text, Grid, Card, Table, Badge, Button, Paper, Group } from '@mantine/core';
import { IconCheck, IconX, IconClock, IconPlayerPlay, IconArrowLeft, IconArrowRight, IconEdit } from '@tabler/icons-react';
import { useTranslation } from 'react-i18next';
import styles from '../../pages/ProjectManagement.module.css';

const ProjectOverview = ({ projectDetails, handleStatusChange, handleProofread }) => {
    const { t } = useTranslation();
    if (!projectDetails) return null;

    const rows = projectDetails.files.map((file) => {
        let color = 'gray';
        let text = '未处理';
        let Icon = IconClock;

        if (file.status === 'translated' || file.status === 'done') { color = 'green'; text = '已翻译'; Icon = IconCheck; }
        else if (file.status === 'failed') { color = 'red'; text = '翻译失败'; Icon = IconX; }
        else if (file.status === 'pending' || file.status === 'todo') { color = 'blue'; text = '待处理'; Icon = IconClock; }
        else if (file.status === 'in_progress') { color = 'yellow'; text = '进行中'; Icon = IconPlayerPlay; }
        else if (file.status === 'proofreading') { color = 'orange'; text = '校对中'; Icon = IconEdit; }

        return (
            <Table.Tr key={file.key}>
                <Table.Td>
                    <Text fw={500} truncate title={file.name}>{file.name}</Text>
                </Table.Td>
                <Table.Td>
                    <Badge variant="dot" color={file.file_type === 'source' ? 'blue' : 'violet'}>
                        {file.file_type === 'source' ? '源文件' : '翻译'}
                    </Badge>
                </Table.Td>
                <Table.Td>{file.lines}</Table.Td>
                <Table.Td>
                    <Badge color={color} variant="light" leftSection={<Icon size={12} />}>
                        {text}
                    </Badge>
                </Table.Td>
                <Table.Td>{file.progress}</Table.Td>
                <Table.Td>
                    <Group gap="xs">
                        {file.actions.map(action => (
                            <Button variant="subtle" size="xs" key={action} onClick={action === 'Proofread' ? () => handleProofread(file) : null}>
                                {t('proofreading.proofread')}
                            </Button>
                        ))}
                    </Group>
                </Table.Td>
            </Table.Tr>
        );
    });

    return (
        <div style={{ position: 'relative', height: '100%', width: '100%' }}>
            {/* Fixed header section with stats and paths */}
            <div style={{ position: 'absolute', top: 0, left: 0, right: 0, paddingBottom: '1rem' }}>
                {/* Stats Card */}
                <Paper withBorder p="md" radius="md" className={styles.glassCard} mb="md">
                    <Title order={4} mb="md">项目概览</Title>
                    <Grid>
                        <Grid.Col span={3}><Card withBorder className={styles.statCard}><Text size="xs" c="dimmed">文件总数</Text><Title order={3}>{projectDetails.overview.totalFiles}</Title></Card></Grid.Col>
                        <Grid.Col span={3}><Card withBorder className={styles.statCard}><Text size="xs" c="dimmed">总行数</Text><Title order={3}>{projectDetails.overview.totalLines}</Title></Card></Grid.Col>
                        <Grid.Col span={3}><Card withBorder className={styles.statCard}><Text size="xs" c="dimmed">已翻译</Text><Title order={3} c="green">{projectDetails.overview.translated}%</Title></Card></Grid.Col>
                        <Grid.Col span={3}><Card withBorder className={styles.statCard}><Text size="xs" c="dimmed">待校对</Text><Title order={3} c="yellow">{projectDetails.overview.toBeProofread}%</Title></Card></Grid.Col>
                    </Grid>
                </Paper>

                {/* Path Management */}
                <Paper withBorder p="md" radius="md" className={styles.glassCard}>
                    <Group position="apart">
                        <div>
                            <Text size="sm" fw={500}>源文件目录:</Text>
                            <Text size="xs" c="dimmed" style={{ wordBreak: 'break-all' }}>{projectDetails.source_path || 'Loading...'}</Text>
                        </div>
                        <div>
                            <Text size="sm" fw={500}>翻译目录:</Text>
                            <Text size="xs" c="dimmed" style={{ wordBreak: 'break-all' }}>
                                {projectDetails.translation_dirs ? projectDetails.translation_dirs.join(', ') : 'Default'}
                            </Text>
                        </div>
                        <Button variant="outline" size="xs" onClick={() => alert("Path management coming soon!")}>Manage Paths</Button>
                    </Group>
                </Paper>
            </div>

            {/* Scrollable file list - positioned below header */}
            <div style={{ position: 'absolute', top: '280px', bottom: 0, left: 0, right: 0, overflowY: 'auto', overflowX: 'hidden' }}>
                <Paper withBorder p="md" radius="md" className={styles.glassCard}>
                    <Group position="apart" mb="md">
                        <Title order={4}>文件详情列表 ({projectDetails.files.length} 个文件)</Title>
                    </Group>
                    <Table verticalSpacing="sm" className={styles.table} stickyHeader>
                        <Table.Thead style={{ position: 'sticky', top: 0, backgroundColor: 'var(--glass-bg)', zIndex: 1 }}>
                            <Table.Tr>
                                <Table.Th>文件名</Table.Th>
                                <Table.Th>类型</Table.Th>
                                <Table.Th>行数</Table.Th>
                                <Table.Th>状态</Table.Th>
                                <Table.Th>进度</Table.Th>
                                <Table.Th>操作</Table.Th>
                            </Table.Tr>
                        </Table.Thead>
                        <Table.Tbody>{rows}</Table.Tbody>
                    </Table>
                </Paper>
            </div>
        </div>
    );
};

export default ProjectOverview;
