import React, { useState, useEffect } from 'react';
import { Title, Text, Select, Group, Grid, Card, Table, Badge, Button, Tabs, Center } from '@mantine/core';
import { IconArrowLeft, IconArrowRight } from '@tabler/icons-react';

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
        files: [ { key: '1', name: 'another_file.yml', lines: 100, status: 'translated', progress: '100 / 100', notes: '无', actions: ['查看'] } ]
    },
    project3: {
        overview: { totalFiles: 5, translated: 100, toBeProofread: 0, glossary: 'project3_glossary.json' },
        files: [ { key: '1', name: 'final_mod_file.yml', lines: 50, status: 'translated', progress: '50 / 50', notes: '已完成', actions: ['查看'] } ]
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
            <Card key={file.key} withBorder shadow="sm" radius="md" style={{ marginBottom: '10px' }}>
                <Text fw={500}>{file.name}</Text>
                <Text size="sm">行数: {file.lines}</Text>
                <Text size="sm">进度: {file.progress}</Text>
                {file.notes && <Text size="sm">备注: {file.notes}</Text>}
                <Group justify="flex-end" mt="sm">
                    <Button.Group>
                        <Button variant="default" size="xs" disabled={statusIndex === 0} onClick={() => handleStatusChange(file.key, 'left')}><IconArrowLeft size={16} /></Button>
                        <Button variant="default" size="xs" disabled={statusIndex === statusFlow.length - 1} onClick={() => handleStatusChange(file.key, 'right')}><IconArrowRight size={16} /></Button>
                    </Button.Group>
                </Group>
            </Card>
        );
    };

    const renderOverview = () => {
        const rows = projectDetails.files.map((file) => {
            let color = 'gray';
            let text = '未处理';
            if (file.status === 'translated') { color = 'green'; text = '✅ 已翻译'; }
            else if (file.status === 'failed') { color = 'red'; text = '🔴 翻译失败'; }
            else if (file.status === 'pending') { color = 'blue'; text = '⚪ 待处理'; }
            else if (file.status === 'in_progress') { color = 'yellow'; text = '▶️ 进行中'; }

            return (
                <Table.Tr key={file.key}>
                    <Table.Td>{file.name}</Table.Td>
                    <Table.Td>{file.lines}</Table.Td>
                    <Table.Td><Badge color={color}>{text}</Badge></Table.Td>
                    <Table.Td>{file.progress}</Table.Td>
                    <Table.Td>{file.notes}</Table.Td>
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
            <div>
                <Title order={4}>项目概览: {mockProjects.find(p => p.id === selectedProject)?.name}</Title>
                <Grid>
                    <Grid.Col span={3}><Card withBorder><Text>文件总数</Text><Title order={3}>{projectDetails.overview.totalFiles}</Title></Card></Grid.Col>
                    <Grid.Col span={3}><Card withBorder><Text>已翻译</Text><Title order={3}>{projectDetails.overview.translated}%</Title></Card></Grid.Col>
                    <Grid.Col span={3}><Card withBorder><Text>待校对</Text><Title order={3}>{projectDetails.overview.toBeProofread}%</Title></Card></Grid.Col>
                    <Grid.Col span={3}><Card withBorder><Text>使用词典</Text><Title order={3}>{projectDetails.overview.glossary}</Title></Card></Grid.Col>
                </Grid>
                <Title order={4} style={{ marginTop: '20px' }}>文件详情列表</Title>
                <Table>
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
            </div>
        );
    };

    const renderTaskBoard = () => {
        const files = projectDetails?.files || [];
        const todoFiles = files.filter(f => f.status === 'pending' || f.status === 'failed');
        const inProgressFiles = files.filter(f => f.status === 'in_progress');
        const doneFiles = files.filter(f => f.status === 'translated');

        return (
            <Grid>
                <Grid.Col span={4}><Title order={4}>To Do</Title>{todoFiles.map(renderTaskCard)}</Grid.Col>
                <Grid.Col span={4}><Title order={4}>In Progress</Title>{inProgressFiles.map(renderTaskCard)}</Grid.Col>
                <Grid.Col span={4}><Title order={4}>Done</Title>{doneFiles.map(renderTaskCard)}</Grid.Col>
            </Grid>
        );
    };

    return (
        <div>
            <Title order={2}>项目管理中心</Title>
            <Group align="center" style={{ marginBottom: '20px' }}>
                <Text>请选择要管理的项目:</Text>
                <Select
                    style={{ width: 240 }}
                    placeholder="选择一个项目"
                    onChange={handleProjectChange}
                    clearable
                    data={mockProjects.map(p => ({ value: p.id, label: p.name }))}
                />
            </Group>

            {selectedProject ? (
                <Tabs defaultValue="overview">
                    <Tabs.List>
                        <Tabs.Tab value="overview">概览</Tabs.Tab>
                        <Tabs.Tab value="taskboard">任务看板</Tabs.Tab>
                    </Tabs.List>

                    <Tabs.Panel value="overview" pt="xs">
                        {projectDetails ? renderOverview() : null}
                    </Tabs.Panel>
                    <Tabs.Panel value="taskboard" pt="xs">
                        {projectDetails ? renderTaskBoard() : null}
                    </Tabs.Panel>
                </Tabs>
            ) : (
                <Center style={{ marginTop: 20 }}>
                    <Text c="dimmed">请从上方选择一个项目以查看详情</Text>
                </Center>
            )}
        </div>
    );
};

export default ProjectManagement;
