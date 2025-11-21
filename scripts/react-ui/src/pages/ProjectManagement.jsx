import React, { useState, useEffect } from 'react';
import { Title, Select, Group, Tabs, Center, Container, Paper, Text, Button } from '@mantine/core';
import { IconFolder, IconPlus } from '@tabler/icons-react';
import { useTranslation } from 'react-i18next';
import styles from './ProjectManagement.module.css';
import { KanbanBoard } from '../components/tools/KanbanBoard';
import ProjectOverview from '../components/tools/ProjectOverview';

// Mock data for projects (restored from original)
const mockProjects = [
    { id: 'project1', name: '甲MOD v1.2' },
    { id: 'project2', name: '乙MOD v2.0' },
    { id: 'project3', name: '丙MOD v3.5' },
];

// Mock data for project details (restored from original)
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

const ProjectManagement = () => {
    const { t } = useTranslation();
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

    // Placeholder handlers for Overview interaction
    const handleProofread = (file) => {
        console.log(`Preparing to navigate to proofreading for file: ${file.name}`);
    };

    const handleStatusChange = (fileKey, direction) => {
       console.log('Status change from Overview not fully implemented in this refactor');
    };

    return (
        <div className={styles.container} style={{ overflow: 'hidden' }}>
            {/* Header Section */}
            <Paper p="md" style={{ background: 'rgba(0,0,0,0.2)', borderBottom: '1px solid var(--glass-border)', backdropFilter: 'blur(10px)' }}>
                <Group justify="space-between">
                    <Title order={3} style={{ fontFamily: 'var(--font-header)', color: 'var(--text-highlight)' }}>
                        {t('page_title_project_management')}
                    </Title>
                    <Group>
                         <Select
                            style={{ width: 300 }}
                            placeholder="选择一个项目" // TODO: i18n
                            value={selectedProject}
                            onChange={handleProjectChange}
                            clearable
                            data={mockProjects.map(p => ({ value: p.id, label: p.name }))}
                            leftSection={<IconFolder size={16} />}
                        />
                        <Button variant="light" leftSection={<IconPlus size={16} />}>
                            新建/导入
                        </Button>
                    </Group>
                </Group>
            </Paper>

            {selectedProject ? (
                <Tabs defaultValue="taskboard" variant="outline" radius="md" style={{ height: '100%', display: 'flex', flexDirection: 'column' }} classNames={{
                    root: styles.tabsRoot,
                    list: styles.tabsList,
                    panel: styles.tabsPanel
                }}>
                    <Tabs.List style={{ paddingLeft: '1rem', paddingTop: '0.5rem', background: 'rgba(0,0,0,0.1)' }}>
                        <Tabs.Tab value="overview">{t('homepage_chart_pie_title')}</Tabs.Tab> {/* Using "Project Status Overview" key as proxy for "Overview" */}
                        <Tabs.Tab value="taskboard">任务看板</Tabs.Tab> {/* TODO: i18n key for Kanban Board */}
                    </Tabs.List>

                    <Tabs.Panel value="overview" style={{ flex: 1, overflow: 'auto', padding: '1rem' }}>
                        {projectDetails ? (
                            <ProjectOverview
                                projectDetails={projectDetails}
                                handleStatusChange={handleStatusChange}
                                handleProofread={handleProofread}
                            />
                        ) : null}
                    </Tabs.Panel>

                    <Tabs.Panel value="taskboard" style={{ flex: 1, overflow: 'hidden', position: 'relative' }}>
                        <KanbanBoard />
                    </Tabs.Panel>
                </Tabs>
            ) : (
                <Container size="sm" style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                     <Paper p="xl" withBorder radius="md" className={styles.emptyState} style={{ width: '100%' }}>
                        <Center style={{ height: 200, flexDirection: 'column' }}>
                            <IconFolder size={48} color="gray" style={{ marginBottom: 16 }} />
                            <Text c="dimmed" size="lg">请从上方选择一个项目以查看详情</Text>
                        </Center>
                    </Paper>
                </Container>
            )}
        </div>
    );
};

export default ProjectManagement;
