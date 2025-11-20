import React, { useState, useEffect } from 'react';
import { Title, Text, Select, Group, Grid, Card, Table, Badge, Button, Tabs, Center, Container, Paper, Stack, ScrollArea } from '@mantine/core';
import { IconArrowLeft, IconArrowRight, IconCheck, IconX, IconClock, IconPlayerPlay, IconFolder } from '@tabler/icons-react';

// Mock data for projects
const mockProjects = [
    { id: 'project1', name: '甲MOD v1.2' },
    { id: 'project2', name: '乙MOD v2.0' },
    { id: 'project3', name: '丙MOD v3.5' },
];

// Mock data for project details - this is the initial state
const initialMockProjectDetails = {
    project1: {
        overview: { totalFiles: 15, translated: 80, toBeProofread: 35, glossary: 'my_glossary.json' },
        files: [
            { key: '1', name: 'file_A.yml', lines: 150, status: 'translated', progress: '150 / 150', notes: '无', actions: ['查看', '重译'] },
            { key: '2', name: 'file_B.yml', lines: 200, status: 'in_progress', progress: '50 / 200', notes: '部分语句不通顺', actions: ['继续校对'] },
            { key: '3', name: 'file_C.yml', lines: 120, status: 'failed', progress: '0 / 120', notes: 'API翻译失败', actions: ['重试', '查看日志'] },
            { key: '4', name: 'file_D.yml', lines: 80, status: 'pending', progress: '0 / 80', notes: '', actions: ['翻译此文件'] },
        ],
    },
    project2: {
        overview: { totalFiles: 10, translated: 95, toBeProofread: 10, glossary: 'project2_glossary.json' },
        files: [{ key: '1', name: 'another_file.yml', lines: 100, status: 'translated', progress: '100 / 100', notes: '无', actions: ['查看'] }]
    },
    project3: {
        overview: { totalFiles: 5, translated: 100, toBeProofread: 0, glossary: 'project3_glossary.json' },
        files: [{ key: '1', name: 'final_mod_file.yml', lines: 50, status: 'translated', progress: '50 / 50', notes: '已完成', actions: ['查看'] }]
    }
};

const statusFlow = ['pending', 'in_progress', 'translated']; // Defines the order of columns

const ProjectManagement = () => {
    const [selectedProject, setSelectedProject] = useState(null);
    const [projectDetails, setProjectDetails] = useState(null);

    useEffect(() => {
        if (selectedProject && initialMockProjectDetails[selectedProject]) {
            // Deep copy the mock data to allow for state changes
            setProjectDetails(JSON.parse(JSON.stringify(initialMockProjectDetails[selectedProject])));
        } else {
            setProjectDetails(null);
        }
    }, [selectedProject]);

    const handleProjectChange = (value) => {
        setSelectedProject(value);
    };

    const handleProofread = (file) => {
        console.log(`Preparing to navigate to proofreading for file: ${file.name}`);
        // In the future, this will handle the logic to switch tabs and pass the file info.
    };

    const handleStatusChange = (fileKey, direction) => {
        const currentFiles = projectDetails.files;
        const fileIndex = currentFiles.findIndex(f => f.key === fileKey);
        if (fileIndex === -1) return;

        const currentStatus = currentFiles[fileIndex].status;
        let currentStatusIndex = statusFlow.indexOf(currentStatus);

        if (currentStatus === 'failed') {
            currentStatusIndex = 0;
        }

        let newStatusIndex = currentStatusIndex;
        if (direction === 'right') {
            newStatusIndex = Math.min(currentStatusIndex + 1, statusFlow.length - 1);
        } else if (direction === 'left') {
            newStatusIndex = Math.max(currentStatusIndex - 1, 0);
        }

        if (statusFlow[newStatusIndex] !== currentStatus) {
            const updatedFiles = [...currentFiles];
            updatedFiles[fileIndex].status = statusFlow[newStatusIndex];
            setProjectDetails({ ...projectDetails, files: updatedFiles });
        }
    };

    const renderTaskCard = (file) => {
        const currentStatus = file.status === 'failed' ? 'pending' : file.status;
        const statusIndex = statusFlow.indexOf(currentStatus);

        return (
            <Card key={file.key} withBorder shadow="sm" radius="md" mb="sm" bg="dark.6">
                <Text fw={500} truncate>{file.name}</Text>
                <Group justify="space-between" mt="xs">
                    <Text size="xs" c="dimmed">Lines: {file.lines}</Text>
                    <Text size="xs" c="dimmed">{file.progress}</Text>
                </Group>
                {file.notes && <Text size="xs" c="red" mt={4}>{file.notes}</Text>}
                <Group justify="flex-end" mt="sm">
                    <Button.Group>
                        <Button variant="default" size="xs" disabled={statusIndex === 0} onClick={() => handleStatusChange(file.key, 'left')}><IconArrowLeft size={14} /></Button>
                        <Button variant="default" size="xs" disabled={statusIndex === statusFlow.length - 1} onClick={() => handleStatusChange(file.key, 'right')}><IconArrowRight size={14} /></Button>
                    </Button.Group>
                </Group>
            </Card>
        );
    };

    const renderOverview = () => {
        const rows = projectDetails.files.map((file) => {
            let color = 'gray';
            let text = '未处理';
            let Icon = IconClock;

            if (file.status === 'translated') { color = 'green'; text = '已翻译'; Icon = IconCheck; }
            else if (file.status === 'failed') { color = 'red'; text = '翻译失败'; Icon = IconX; }
            else if (file.status === 'pending') { color = 'blue'; text = '待处理'; Icon = IconClock; }
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
                <Paper withBorder p="md" radius="md" bg="dark.7">
                    <Title order={4} mb="md">项目概览: {mockProjects.find(p => p.id === selectedProject)?.name}</Title>
                    <Grid>
                        <Grid.Col span={3}><Card withBorder bg="dark.6"><Text size="xs" c="dimmed">文件总数</Text><Title order={3}>{projectDetails.overview.totalFiles}</Title></Card></Grid.Col>
                        <Grid.Col span={3}><Card withBorder bg="dark.6"><Text size="xs" c="dimmed">已翻译</Text><Title order={3} c="green">{projectDetails.overview.translated}%</Title></Card></Grid.Col>
                        <Grid.Col span={3}><Card withBorder bg="dark.6"><Text size="xs" c="dimmed">待校对</Text><Title order={3} c="yellow">{projectDetails.overview.toBeProofread}%</Title></Card></Grid.Col>
                        <Grid.Col span={3}><Card withBorder bg="dark.6"><Text size="xs" c="dimmed">使用词典</Text><Title order={3} size="h4">{projectDetails.overview.glossary}</Title></Card></Grid.Col>
                    </Grid>
                </Paper>

                <Paper withBorder p="md" radius="md" bg="dark.7">
                    <Title order={4} mb="md">文件详情列表</Title>
                    <ScrollArea>
                        <Table verticalSpacing="sm">
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

    const renderTaskBoard = () => {
        const files = projectDetails?.files || [];
        const todoFiles = files.filter(f => f.status === 'pending' || f.status === 'failed');
        const inProgressFiles = files.filter(f => f.status === 'in_progress');
        const doneFiles = files.filter(f => f.status === 'translated');

        return (
            <Grid gutter="xl">
                <Grid.Col span={4}>
                    <Paper p="sm" radius="md" bg="dark.8" withBorder>
                        <Group justify="space-between" mb="md">
                            <Title order={5}>To Do</Title>
                            <Badge color="gray">{todoFiles.length}</Badge>
                        </Group>
                        <Stack gap="xs">
                            {todoFiles.map(renderTaskCard)}
                        </Stack>
                    </Paper>
                </Grid.Col>
                <Grid.Col span={4}>
                    <Paper p="sm" radius="md" bg="dark.8" withBorder>
                        <Group justify="space-between" mb="md">
                            <Title order={5}>In Progress</Title>
                            <Badge color="yellow">{inProgressFiles.length}</Badge>
                        </Group>
                        <Stack gap="xs">
                            {inProgressFiles.map(renderTaskCard)}
                        </Stack>
                    </Paper>
                </Grid.Col>
                <Grid.Col span={4}>
                    <Paper p="sm" radius="md" bg="dark.8" withBorder>
                        <Group justify="space-between" mb="md">
                            <Title order={5}>Done</Title>
                            <Badge color="green">{doneFiles.length}</Badge>
                        </Group>
                        <Stack gap="xs">
                            {doneFiles.map(renderTaskCard)}
                        </Stack>
                    </Paper>
                </Grid.Col>
            </Grid>
        );
    };

    return (
        <Container size="xl" py="xl">
            <Group justify="space-between" mb="xl">
                <Title order={2}>项目管理中心</Title>
                <Select
                    style={{ width: 300 }}
                    placeholder="选择一个项目"
                    onChange={handleProjectChange}
                    clearable
                    data={mockProjects.map(p => ({ value: p.id, label: p.name }))}
                    leftSection={<IconFolder size={16} />}
                />
            </Group>

            {selectedProject ? (
                <Tabs defaultValue="overview" variant="pills" radius="md">
                    <Tabs.List mb="lg">
                        <Tabs.Tab value="overview">概览</Tabs.Tab>
                        <Tabs.Tab value="taskboard">任务看板</Tabs.Tab>
                    </Tabs.List>

                    <Tabs.Panel value="overview">
                        {projectDetails ? renderOverview() : null}
                    </Tabs.Panel>
                    <Tabs.Panel value="taskboard">
                        {projectDetails ? renderTaskBoard() : null}
                    </Tabs.Panel>
                </Tabs>
            ) : (
                <Paper p="xl" withBorder radius="md" bg="dark.7">
                    <Center style={{ height: 200, flexDirection: 'column' }}>
                        <IconFolder size={48} color="gray" style={{ marginBottom: 16 }} />
                        <Text c="dimmed" size="lg">请从上方选择一个项目以查看详情</Text>
                    </Center>
                </Paper>
            )}
        </Container>
    );
};

export default ProjectManagement;
