import React, { useState, useEffect } from 'react';
import {
  Container, Title, Button, Group, Card, Text, Grid, Modal, TextInput, Select,
  Stack, Badge, ScrollArea, Table, Box, Tabs, Center, Paper, BackgroundImage,
  ActionIcon, SimpleGrid, Overlay, Input
} from '@mantine/core';
import { IconPlus, IconFolder, IconEdit, IconArrowLeft, IconSearch, IconBooks, IconCompass, IconArrowRight } from '@tabler/icons-react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import { open } from '@tauri-apps/plugin-dialog';

// Restore original components
import { KanbanBoard } from '../components/tools/KanbanBoard';
import ProjectOverview from '../components/tools/ProjectOverview';
import styles from './ProjectManagement.module.css';

// Assets
import heroBg from '../assets/project_hero_bg.png';
import cardNewProject from '../assets/card_new_project.png';
import cardOpenProject from '../assets/card_open_project.png';

const API_BASE = 'http://localhost:8000/api';

export default function ProjectManagement() {
  const { t } = useTranslation();
  const [projects, setProjects] = useState([]);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [deleteSourceFiles, setDeleteSourceFiles] = useState(false);

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
      const [filesRes, configRes] = await Promise.all([
        axios.get(`${API_BASE}/project/${projectId}/files`),
        axios.get(`${API_BASE}/project/${projectId}/config`)
      ]);

      const files = filesRes.data;
      const config = configRes.data;
      setProjectFiles(files);

      // Construct Details for Overview
      const totalLines = files.reduce((acc, f) => acc + (f.line_count || 0), 0);

      setProjectDetails({
        overview: {
          totalFiles: files.length,
          totalLines: totalLines,
          translated: Math.round((files.filter(f => f.status === 'done').length / files.length) * 100) || 0,
          toBeProofread: Math.round((files.filter(f => f.status === 'proofreading' || f.status === 'todo').length / files.length) * 100) || 0,
          glossary: 'Default'
        },
        source_path: config.source_path,
        translation_dirs: config.translation_dirs,
        files: files.map(f => ({
          key: f.file_id,
          name: f.file_path, // This is full path now, maybe show relative?
          status: f.status,
          lines: f.line_count,
          file_type: f.file_type, // Pass file_type
          progress: f.status === 'done' ? '100%' : '0%',
          actions: ['Proofread']
        }))
      });

    } catch (error) {
      console.error("Failed to load files or config", error);
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

  const handleBrowseFolder = async () => {
    try {
      const selected = await open({
        directory: true,
        multiple: false,
        title: 'Select Project Folder'
      });
      if (selected && typeof selected === 'string') {
        setNewProjectPath(selected);
      }
    } catch (err) {
      console.error('Failed to open dialog:', err);
    }
  };

  const handleProofread = (file) => {
    if (!selectedProject) return;
    const fileId = file.key || file.file_id;
    navigate(`/proofreading?projectId=${selectedProject.project_id}&fileId=${fileId}`);
  };

  // --- Render Views ---

  // View 1: Project List (Hero UI)
  const renderProjectList = () => {
    const filteredProjects = projects.filter(p =>
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.game_id.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
      <div style={{ height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {/* Hero Section */}
        <Box style={{ height: '300px', position: 'relative', flexShrink: 0 }}>
          <BackgroundImage src={heroBg} radius="md" style={{ height: '100%' }}>
            <Overlay color="#000" opacity={0.6} zIndex={1} radius="md" />
            <Center p="md" style={{ height: '100%', position: 'relative', zIndex: 2, flexDirection: 'column' }}>
              <Title order={1} style={{ color: '#fff', fontSize: '3rem', textShadow: '0 0 20px rgba(0,0,0,0.8)' }}>
                {t('page_title_project_management')}
              </Title>
              <Text c="dimmed" size="lg" mt="sm">
                Manage your localization projects with steampunk precision.
              </Text>

              <Input
                icon={<IconSearch size={16} />}
                placeholder="Search projects..."
                radius="xl"
                size="md"
                mt="xl"
                style={{ width: '400px' }}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.currentTarget.value)}
                styles={{ input: { background: 'rgba(255,255,255,0.1)', color: '#fff', border: '1px solid rgba(255,255,255,0.2)' } }}
              />
            </Center>
          </BackgroundImage>
        </Box>

        {/* Content Section */}
        <ScrollArea style={{ flex: 1, padding: '20px' }}>
          <Title order={3} mb="md">Actions</Title>
          <SimpleGrid cols={3} spacing="lg" breakpoints={[{ maxWidth: 'sm', cols: 1 }]}>

            {/* Create New Card */}
            <Card
              shadow="sm"
              padding="lg"
              radius="md"
              withBorder
              className={styles.actionCard}
              onClick={() => setIsCreateModalOpen(true)}
            >
              <Card.Section>
                <BackgroundImage src={cardNewProject} style={{ height: 140 }} />
              </Card.Section>
              <Group position="apart" mt="md" mb="xs">
                <Text weight={500}>Create New Project</Text>
                <Badge color="pink" variant="light">New</Badge>
              </Group>
              <Text size="sm" color="dimmed">
                Start a new localization journey from a local mod folder.
              </Text>
            </Card>

            {/* Import/Open Card (Placeholder for future feature) */}
            <Card
              shadow="sm"
              padding="lg"
              radius="md"
              withBorder
              className={styles.actionCard}
              style={{ opacity: 0.7 }}
            >
              <Card.Section>
                <BackgroundImage src={cardOpenProject} style={{ height: 140 }} />
              </Card.Section>
              <Group position="apart" mt="md" mb="xs">
                <Text weight={500}>Open Existing</Text>
                <Badge color="gray" variant="light">Soon</Badge>
              </Group>
              <Text size="sm" color="dimmed">
                Open a project from a different location.
              </Text>
            </Card>
          </SimpleGrid>

          <Title order={3} mt="xl" mb="md">Recent Projects</Title>

          {filteredProjects.length === 0 ? (
            <Text c="dimmed" fs="italic">No projects found. Create one above!</Text>
          ) : (
            <SimpleGrid cols={2} spacing="md">
              {filteredProjects.map((p) => (
                <Paper
                  key={p.project_id}
                  p="md"
                  withBorder
                  className={styles.projectRow}
                  onClick={() => setSelectedProject(p)}
                >
                  <Group>
                    <IconBooks size={32} color="var(--mantine-color-blue-6)" />
                    <Box style={{ flex: 1 }}>
                      <Text weight={600} size="lg">{p.name}</Text>
                      <Text size="xs" c="dimmed">{p.game_id} • {p.source_path}</Text>
                    </Box>
                    <Badge>{p.status}</Badge>
                    <IconArrowRight size={18} color="gray" />
                  </Group>
                </Paper>
              ))}
            </SimpleGrid>
          )}

        </ScrollArea>
      </div>
    );
  };

  const handleRefreshFiles = async () => {
    if (!selectedProject) return;
    try {
      await axios.post(`${API_BASE}/project/${selectedProject.project_id}/refresh`);
      fetchProjectFiles(selectedProject.project_id);
      setProjectDetails(prev => ({ ...prev, refreshKey: Date.now() }));
    } catch (error) {
      console.error("Failed to refresh files", error);
    }
  };

  const handleDeleteProject = async () => {
    if (!selectedProject) return;
    try {
      await axios.delete(`${API_BASE}/project/${selectedProject.project_id}?delete_files=${deleteSourceFiles}`);
      setDeleteModalOpen(false);
      setSelectedProject(null);
      setDeleteSourceFiles(false);
      fetchProjects();
    } catch (error) {
      alert(`Failed to delete project: ${error.response?.data?.detail || error.message}`);
    }
  };

  // View 2: Project Dashboard
  const renderProjectDashboard = () => (
    <div className={styles.container} style={{ overflow: 'hidden', height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header with Back Button */}
      <Paper p="md" style={{ background: 'rgba(0,0,0,0.2)', borderBottom: '1px solid var(--glass-border)', backdropFilter: 'blur(10px)' }}>
        <Group justify="space-between">
          <Group>
            <Button variant="subtle" onClick={() => setSelectedProject(null)} leftSection={<IconArrowLeft size={16} />}>
              Back
            </Button>
            <Title order={3} style={{ fontFamily: 'var(--font-header)', color: 'var(--text-highlight)' }}>
              {selectedProject.name}
            </Title>
          </Group>
          <Group>
            <Button variant="light" size="xs" onClick={handleRefreshFiles}>Refresh Files</Button>
            <Button variant="light" color="red" size="xs" onClick={() => setDeleteModalOpen(true)}>Delete Project</Button>
            <Badge size="lg">{selectedProject.game_id}</Badge>
          </Group>
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

        <Tabs.Panel value="overview" style={{ flex: 1, overflow: 'hidden', padding: '1rem', minHeight: 0 }}>
          {projectDetails ? (
            <ProjectOverview
              projectDetails={projectDetails}
              handleProofread={handleProofread}
              handleStatusChange={() => { }}
            />
          ) : <Text>Loading details...</Text>}
        </Tabs.Panel>

        <Tabs.Panel value="taskboard" style={{ flex: 1, overflow: 'hidden', position: 'relative' }}>
          <KanbanBoard projectId={selectedProject.project_id} key={selectedProject.project_id + (projectDetails?.refreshKey || '')} />
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
        size="lg"
      >
        <Stack>
          <TextInput
            label="Project Name"
            placeholder="My Awesome Mod"
            value={newProjectName}
            onChange={(e) => setNewProjectName(e.currentTarget.value)}
          />
          <Group align="flex-end">
            <TextInput
              label="Folder Path"
              placeholder="C:/Mods/MyMod"
              description="Select the root folder of your mod."
              value={newProjectPath}
              onChange={(e) => setNewProjectPath(e.currentTarget.value)}
              style={{ flex: 1 }}
            />
            <Button onClick={handleBrowseFolder} leftSection={<IconFolder size={16} />}>
              Browse
            </Button>
          </Group>
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
          <Button onClick={handleCreateProject} fullWidth mt="md">Create Project</Button>
        </Stack>
      </Modal>

      <Modal
        opened={deleteModalOpen}
        onClose={() => { setDeleteModalOpen(false); setDeleteSourceFiles(false); }}
        title="Delete Project"
        size="md"
      >
        <Stack>
          <Text>Are you sure you want to delete this project?</Text>
          <Text size="sm" c="dimmed">Project: {selectedProject?.name}</Text>
          <input
            type="checkbox"
            checked={deleteSourceFiles}
            onChange={(e) => setDeleteSourceFiles(e.target.checked)}
            id="delete-files-checkbox"
          />
          <label htmlFor="delete-files-checkbox">
            <Text size="sm" c="red">Also delete source files from disk</Text>
          </label>
          <Group justify="flex-end" mt="md">
            <Button variant="default" onClick={() => { setDeleteModalOpen(false); setDeleteSourceFiles(false); }}>
              Cancel
            </Button>
            <Button color="red" onClick={handleDeleteProject}>
              Delete
            </Button>
          </Group>
        </Stack>
      </Modal>
    </>
  );
}
