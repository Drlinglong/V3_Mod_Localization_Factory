import React from 'react';
import { Title, Text, Grid, Card, Table, Badge, Button, Paper, Stack, ScrollArea, Group } from '@mantine/core';
import { IconCheck, IconX, IconClock, IconPlayerPlay, IconArrowLeft, IconArrowRight } from '@tabler/icons-react';
import styles from '../../pages/ProjectManagement.module.css';

const ProjectOverview = ({ projectDetails, handleStatusChange, handleProofread }) => {
    if (!projectDetails) return null;

    const rows = projectDetails.files.map((file) => {
        let color = 'gray';
        let text = '未处理';
        let Icon = IconClock;

        if (file.status === 'translated' || file.status === 'done') { color = 'green'; text = '已翻译'; Icon = IconCheck; }
        else if (file.status === 'failed') { color = 'red'; text = '翻译失败'; Icon = IconX; }
        else if (file.status === 'pending' || file.status === 'todo') { color = 'blue'; text = '待处理'; Icon = IconClock; }
        else if (file.status === 'in_progress') { color = 'yellow'; text = '进行中'; Icon = IconPlayerPlay; }

        return (
            <Table.Tr key={file.key}>
                <Table.Td><Text fw={500}>{file.name}</Text></Table.Td>
                <Table.Td>{file.lines}</Table.Td>
                <Table.Td>
                    <Badge color={color} variant="light" leftSection={<Icon size={12} />}>
                        {text}
                    </Badge>
                </Table.Td>
                <Table.Td>{file.progress}</Table.Td>
                <Table.Td><Text size="sm" truncate>{file.notes}</Text></Table.Td>
                <Table.Td>
                    <Group gap="xs">
                        {file.actions.map(action => (
                            <Button variant="subtle" size="xs" key={action} onClick={action === '继续校对' ? () => handleProofread(file) : null}>
                                {action}
                            </Button>
                        ))}
                    </Group>
                </Table.Td>
            </Table.Tr>
        );
    });

    return (
        <Stack gap="lg">
            <Paper withBorder p="md" radius="md" className={styles.glassCard}>
                <Title order={4} mb="md">项目概览</Title>
                <Grid>
                    <Grid.Col span={3}><Card withBorder className={styles.statCard}><Text size="xs" c="dimmed">文件总数</Text><Title order={3}>{projectDetails.overview.totalFiles}</Title></Card></Grid.Col>
                    <Grid.Col span={3}><Card withBorder className={styles.statCard}><Text size="xs" c="dimmed">已翻译</Text><Title order={3} c="green">{projectDetails.overview.translated}%</Title></Card></Grid.Col>
                    <Grid.Col span={3}><Card withBorder className={styles.statCard}><Text size="xs" c="dimmed">待校对</Text><Title order={3} c="yellow">{projectDetails.overview.toBeProofread}%</Title></Card></Grid.Col>
                    <Grid.Col span={3}><Card withBorder className={styles.statCard}><Text size="xs" c="dimmed">使用词典</Text><Title order={3} size="h4">{projectDetails.overview.glossary}</Title></Card></Grid.Col>
                </Grid>
            </Paper>

            <Paper withBorder p="md" radius="md" className={styles.glassCard}>
                <Title order={4} mb="md">文件详情列表</Title>
                <ScrollArea>
                    <Table verticalSpacing="sm" className={styles.table}>
                        <Table.Thead>
                            <Table.Tr>
                                <Table.Th>文件名</Table.Th>
                                <Table.Th>行数</Table.Th>
                                <Table.Th>状态</Table.Th>
                                <Table.Th>校对进度</Table.Th>
                                <Table.Th>备注</Table.Th>
                                <Table.Th>操作</Table.Th>
                            </Table.Tr>
                        </Table.Thead>
                        <Table.Tbody>{rows}</Table.Tbody>
                    </Table>
                </ScrollArea>
            </Paper>
        </Stack>
    );
};

export default ProjectOverview;
