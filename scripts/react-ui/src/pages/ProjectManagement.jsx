import React, { useState, useEffect } from 'react';
import {
  Container, Title, Button, Group, Card, Text, Grid, Modal, TextInput, Select,
  Stack, Badge, ScrollArea, Table, Box, Tabs, Center
} from '@mantine/core';
import { IconPlus, IconFolder, IconEdit, IconArrowLeft } from '@tabler/icons-react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useTranslation } from 'react-i18next';

// Restore original components
import { KanbanBoard } from '../components/tools/KanbanBoard';
import ProjectOverview from '../components/tools/ProjectOverview';
import styles from './ProjectManagement.module.css';

const API_BASE = 'http://localhost:8000/api';

export default function ProjectManagement() {
  const { t } = useTranslation();
  const [projects, setProjects] = useState([]);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  // Selection State
  const [selectedProject, setSelectedProject] = useState(null);
  const [projectFiles, setProjectFiles] = useState([]);
  const [projectDetails, setProjectDetails] = useState(null); // For Overview

  // Form State
  const [newProjectName, setNewProjectName] = useState('');
  const [newProjectPath, setNewProjectPath] = useState('');
  const [newProjectGame, setNewProjectGame] = useState('stellaris');

  const navigate = useNavigate();

  useEffect(() => {
    fetchProjects();
  }, []);

  useEffect(() => {
    if (selectedProject) {
      fetchProjectFiles(selectedProject.project_id);
    }
  }, [selectedProject]);

  const fetchProjects = async () => {
    try {
      const res = await axios.get(`${API_BASE}/projects`);
      setProjects(res.data);
    } catch (error) {
      console.error("Failed to load projects", error);
    }
  };

  const fetchProjectFiles = async (projectId) => {
    try {
      const res = await axios.get(`${API_BASE}/project/${projectId}/files`);
      const files = res.data;
      setProjectFiles(files);

      // Construct Mock-like details for the Overview component
      // The original used a specific structure, we try to emulate it
      setProjectDetails({
          overview: {
              totalFiles: files.length,
              translated: files.filter(f => f.status === 'done').length,
              toBeProofread: files.filter(f => f.status === 'proofreading' || f.status === 'todo').length,
              glossary: 'Default'
          },
          files: files.map(f => ({
              key: f.file_id,
              name: f.file_path,
              status: f.status,
              progress: f.status === 'done' ? '100%' : '0%',
              actions: ['Proofread']
          }))
      });

    } catch (error) {
      console.error("Failed to load files", error);
    }
  };

  const handleCreateProject = async () => {
    try {
      await axios.post(`${API_BASE}/project/create`, {
        name: newProjectName,
        folder_path: newProjectPath,
        game_id: newProjectGame
      });
      setIsCreateModalOpen(false);
      fetchProjects();
      setNewProjectName('');
      setNewProjectPath('');
    } catch (error) {
      alert(`Failed to create project: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleProofread = (file) => {
    if (!selectedProject) return;
    // If file object passed from Overview table (custom structure)
    const fileId = file.key || file.file_id;
    navigate(`/proofreading?projectId=${selectedProject.project_id}&fileId=${fileId}`);
  };

  // --- Render Views ---

  // View 1: Project List (New Implementation)
  const renderProjectList = () => (
    <Container fluid p="md" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Group position="apart" mb="md">
        <Title order={2}>{t('page_title_project_management')}</Title>
        <Button leftIcon={<IconPlus size={16} />} onClick={() => setIsCreateModalOpen(true)}>
          New Project
        </Button>
      </Group>

      <Grid style={{ flex: 1 }}>
        <Grid.Col span={12}>
           <ScrollArea style={{ height: 'calc(100vh - 150px)' }}>
            <Stack spacing="sm">
              {projects.map((p) => (
                <Card
                  key={p.project_id}
                  shadow="sm"
                  p="sm"
                  radius="md"
                  withBorder
                  onClick={() => setSelectedProject(p)}
                  style={{ cursor: 'pointer', transition: 'background-color 0.2s' }}
                  className={styles.projectCard} // Add styling hook
                >
                  <Group position="apart" noWrap>
                    <Box>
                        <Text weight={500} size="lg">{p.name}</Text>
                        <Text size="xs" color="dimmed">{p.game_id} • {p.source_path}</Text>
                    </Box>
                    <Badge color={p.status === 'active' ? 'green' : 'gray'}>{p.status}</Badge>
                  </Group>
                </Card>
              ))}
              {projects.length === 0 && (
                  <Center p="xl">
                      <Text c="dimmed">No projects found. Create one to get started.</Text>
                  </Center>
              )}
            </Stack>
           </ScrollArea>
        </Grid.Col>
      </Grid>
    </Container>
  );

  // View 2: Project Dashboard (Restored Original Layout)
  const renderProjectDashboard = () => (
    <div className={styles.container} style={{ overflow: 'hidden', height: '100%', display: 'flex', flexDirection: 'column' }}>
        {/* Header with Back Button */}
        <Paper p="md" style={{ background: 'rgba(0,0,0,0.2)', borderBottom: '1px solid var(--glass-border)', backdropFilter: 'blur(10px)' }}>
            <Group justify="space-between">
                <Group>
                    <Button variant="subtle" onClick={() => setSelectedProject(null)} leftSection={<IconArrowLeft size={16}/>}>
                        Back
                    </Button>
                    <Title order={3} style={{ fontFamily: 'var(--font-header)', color: 'var(--text-highlight)' }}>
                        {selectedProject.name}
                    </Title>
                </Group>
                <Badge size="lg">{selectedProject.game_id}</Badge>
            </Group>
        </Paper>

        <Tabs defaultValue="overview" variant="outline" radius="md" style={{ flex: 1, display: 'flex', flexDirection: 'column' }} classNames={{
            root: styles.tabsRoot,
            list: styles.tabsList,
            panel: styles.tabsPanel
        }}>
            <Tabs.List style={{ paddingLeft: '1rem', paddingTop: '0.5rem', background: 'rgba(0,0,0,0.1)' }}>
                <Tabs.Tab value="overview">{t('homepage_chart_pie_title')}</Tabs.Tab>
                <Tabs.Tab value="taskboard">任务看板</Tabs.Tab>
            </Tabs.List>

            <Tabs.Panel value="overview" style={{ flex: 1, overflow: 'auto', padding: '1rem' }}>
                {projectDetails ? (
                    <ProjectOverview
                        projectDetails={projectDetails}
                        handleProofread={handleProofread}
                        // Pass dummy handler for status change as it's not fully wired yet
                        handleStatusChange={() => {}}
                    />
                ) : <Text>Loading details...</Text>}
            </Tabs.Panel>

            <Tabs.Panel value="taskboard" style={{ flex: 1, overflow: 'hidden', position: 'relative' }}>
                {/*
                    KanbanBoard might need props or context.
                    Since I don't see props in the original usage, assuming it handles itself
                    or I need to check if it breaks without specific context.
                    For now, rendering it as requested.
                */}
                <KanbanBoard />
            </Tabs.Panel>
        </Tabs>
    </div>
  );

  return (
    <>
      {selectedProject ? renderProjectDashboard() : renderProjectList()}

      <Modal
        opened={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Create New Project"
      >
        <Stack>
            <TextInput
                label="Project Name"
                placeholder="My Awesome Mod"
                value={newProjectName}
                onChange={(e) => setNewProjectName(e.currentTarget.value)}
            />
            <TextInput
                label="Folder Path"
                placeholder="C:/Mods/MyMod"
                description="If outside source folder, it will be moved."
                value={newProjectPath}
                onChange={(e) => setNewProjectPath(e.currentTarget.value)}
            />
            <Select
                label="Game"
                data={[
                    { value: 'stellaris', label: 'Stellaris' },
                    { value: 'hoi4', label: 'Hearts of Iron IV' },
                    { value: 'vic3', label: 'Victoria 3' },
                    { value: 'ck3', label: 'Crusader Kings III' },
                    { value: 'eu4', label: 'Europa Universalis IV' }
                ]}
                value={newProjectGame}
                onChange={setNewProjectGame}
            />
            <Button onClick={handleCreateProject}>Create Project</Button>
        </Stack>
      </Modal>
    </>
  );
}
