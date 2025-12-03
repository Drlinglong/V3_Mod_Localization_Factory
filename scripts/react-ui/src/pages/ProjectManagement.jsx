import React, { useState, useEffect } from 'react';
import {
  Container, Title, Button, Group, Card, Text, Grid, Modal, TextInput, Select,
  Stack, Badge, ScrollArea, Table, Box, Tabs, Center, Paper, BackgroundImage,
  ActionIcon, SimpleGrid, Overlay, Input, Tooltip, Checkbox, Alert
} from '@mantine/core';
import { IconPlus, IconFolder, IconEdit, IconArrowLeft, IconSearch, IconBooks, IconCompass, IconArrowRight, IconArchive, IconTrash, IconRestore, IconAlertTriangle } from '@tabler/icons-react';
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
import cardOpenProject from '../assets/card_open_project.png'; // Reusing for Archives

const API_BASE = '/api';

export default function ProjectManagement() {
  const { t } = useTranslation();
  const [projects, setProjects] = useState([]);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [deleteSourceFiles, setDeleteSourceFiles] = useState(false);

  // View Mode: 'active' | 'archives'
  const [viewMode, setViewMode] = useState('active');

  // Selection State
  const [selectedProject, setSelectedProject] = useState(null);
  // const [projectFiles, setProjectFiles] = useState([]); // Unused
  const [projectDetails, setProjectDetails] = useState(null); // For Overview

  // Form State
  const [newProjectName, setNewProjectName] = useState('');
  const [newProjectPath, setNewProjectPath] = useState('');
  const [newProjectGame, setNewProjectGame] = useState('stellaris');
  const [newProjectSourceLang, setNewProjectSourceLang] = useState('english');

  // Manage Project State
  const [manageModalOpen, setManageModalOpen] = useState(false);
  const [editGameId, setEditGameId] = useState('');
  const [editSourceLang, setEditSourceLang] = useState('');

  const navigate = useNavigate();

  useEffect(() => {
    fetchProjects();
  }, [viewMode]);

  useEffect(() => {
    if (selectedProject) {
      fetchProjectFiles(selectedProject.project_id);
    }
  }, [selectedProject]);

  const fetchProjects = async () => {
    try {
      let res;
      if (viewMode === 'active') {
        res = await axios.get(`${API_BASE}/projects?status=active`);
        setProjects(res.data);
      } else {
        // Fetch both archived and deleted for archives view
        const [archivedRes, deletedRes] = await Promise.all([
          axios.get(`${API_BASE}/projects?status=archived`),
          axios.get(`${API_BASE}/projects?status=deleted`)
        ]);
        setProjects([...archivedRes.data, ...deletedRes.data]);
      }
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
      // setProjectFiles(files);

      // Construct Details for Overview
      const totalLines = files.reduce((acc, f) => acc + (f.line_count || 0), 0);

      setProjectDetails({
        project_id: projectId,
        name: selectedProject.name, // Pass name
        status: selectedProject.status, // Pass status
        notes: selectedProject.notes, // Pass notes
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
          name: f.file_path,
          status: f.status,
          lines: f.line_count,
          file_type: f.file_type,
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
        game_id: newProjectGame,
        source_language: newProjectSourceLang
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
    console.log("handleProofread called with:", file);
    if (!selectedProject) {
      console.error("No selected project!");
      return;
    }

    // Ensure we have a file ID
    const fileId = file.key || file.file_id;
    if (!fileId) {
      console.error("No fileId found in file object:", file);
      alert("Error: Cannot identify file. Please refresh the project.");
      return;
    }

    const url = `/proofreading?projectId=${selectedProject.project_id}&fileId=${fileId}`;
    console.log("Navigating to:", url);
    navigate(url);
  };

  const handleUpdateNotes = async (notes) => {
    if (!selectedProject) return;
    try {
      await axios.post(`${API_BASE}/project/${selectedProject.project_id}/notes`, { notes });
      // Update local state
      setSelectedProject(prev => ({ ...prev, notes }));
      setProjectDetails(prev => ({ ...prev, notes }));
    } catch (error) {
      console.error("Failed to update notes", error);
      alert("Failed to save notes");
    }
  };

  const handleUpdateStatus = async (status) => {
    if (!selectedProject) return;
    try {
      await axios.post(`${API_BASE}/project/${selectedProject.project_id}/status`, { status });
      // If status changes such that it leaves the current view, we might want to go back or refresh
      // But for now, just update local state and refresh list
      setSelectedProject(prev => ({ ...prev, status }));
      setProjectDetails(prev => ({ ...prev, status }));
      fetchProjects(); // Refresh list to reflect changes

      // If we archived/deleted while in active view, go back to list
      if (viewMode === 'active' && status !== 'active') {
        setSelectedProject(null);
      }
      // If we restored while in archives view, go back to list
      if (viewMode === 'archives' && status === 'active') {
        setSelectedProject(null);
      }

    } catch (error) {
      console.error("Failed to update status", error);
      alert("Failed to update status");
    }
  };

  const handleOpenManage = () => {
    if (selectedProject) {
      setEditGameId(selectedProject.game_id);
      setEditSourceLang(selectedProject.source_language || 'english');
      setManageModalOpen(true);
    }
  };

  const handleUpdateMetadata = async () => {
    if (!selectedProject) return;
    try {
      await axios.post(`${API_BASE}/project/${selectedProject.project_id}/metadata`, {
        game_id: editGameId,
        source_language: editSourceLang
      });

      // Update local state
      setSelectedProject(prev => ({
        ...prev,
        game_id: editGameId,
        source_language: editSourceLang
      }));

      // Also update projectDetails if it exists
      if (projectDetails) {
        setProjectDetails(prev => ({
          ...prev,
          game_id: editGameId,
          source_language: editSourceLang
        }));
      }

      setManageModalOpen(false);
      fetchProjects(); // Refresh list
    } catch (error) {
      alert(`Failed to update project: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleDeleteForever = async () => {
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
                {viewMode === 'active' ? t('page_title_project_management') : t('project_management.archives_title')}
              </Title>
              <Text c="dimmed" size="lg" mt="sm">
                {viewMode === 'active' ? 'Manage your localization projects with steampunk precision.' : t('project_management.actions.archives_desc')}
              </Text>

              <Group mt="xl">
                {viewMode === 'archives' && (
                  <Button variant="outline" color="gray" leftSection={<IconArrowLeft />} onClick={() => setViewMode('active')}>
                    {t('button_back')}
                  </Button>
                )}
                <Input
                  icon={<IconSearch size={16} />}
                  placeholder="Search projects..."
                  radius="xl"
                  size="md"
                  style={{ width: '400px' }}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.currentTarget.value)}
                  styles={{ input: { background: 'rgba(255,255,255,0.1)', color: '#fff', border: '1px solid rgba(255,255,255,0.2)' } }}
                />
              </Group>
            </Center>
          </BackgroundImage>
        </Box>

        {/* Content Section */}
        <ScrollArea style={{ flex: 1, padding: '20px' }}>
          {viewMode === 'active' && (
            <>
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
                    <Text weight={500}>{t('project_management.actions.create_new')}</Text>
                    <Badge color="pink" variant="light">New</Badge>
                  </Group>
                  <Text size="sm" color="dimmed">
                    {t('project_management.actions.create_new_desc')}
                  </Text>
                </Card>

                {/* Archives Card */}
                <Card
                  shadow="sm"
                  padding="lg"
                  radius="md"
                  withBorder
                  className={styles.actionCard}
                  onClick={() => setViewMode('archives')}
                >
                  <Card.Section>
                    <BackgroundImage src={cardOpenProject} style={{ height: 140 }} />
                  </Card.Section>
                  <Group position="apart" mt="md" mb="xs">
                    <Text weight={500}>{t('project_management.actions.archives')}</Text>
                    <Badge color="gray" variant="light">View</Badge>
                  </Group>
                  <Text size="sm" color="dimmed">
                    {t('project_management.actions.archives_desc')}
                  </Text>
                </Card>
              </SimpleGrid>
            </>
          )}

          <Title order={3} mt="xl" mb="md">{viewMode === 'active' ? 'Recent Projects' : 'Archived Projects'}</Title>

          {filteredProjects.length === 0 ? (
            <Text c="dimmed" fs="italic">
              {viewMode === 'active' ? t('no_existing_mods') : t('project_management.empty_archives')}
            </Text>
          ) : (
            <SimpleGrid cols={2} spacing="md">
              {filteredProjects.map((p) => (
                <Paper
                  key={p.project_id}
                  p="md"
                  withBorder
                  className={styles.projectRow}
                  onClick={() => setSelectedProject(p)}
                  style={{ opacity: p.status === 'deleted' ? 0.6 : 1 }}
                >
                  <Group>
                    {p.status === 'deleted' ? <IconTrash size={32} color="red" /> : <IconBooks size={32} color="var(--mantine-color-blue-6)" />}
                    <Box style={{ flex: 1 }}>
                      <Text weight={600} size="lg" td={p.status === 'deleted' ? 'line-through' : 'none'}>{p.name}</Text>
                      <Text size="xs" c="dimmed">{p.game_id} • {p.source_path}</Text>
                    </Box>
                    <Badge color={p.status === 'active' ? 'blue' : p.status === 'archived' ? 'orange' : 'red'}>
                      {t(`project_management.status.${p.status}`)}
                    </Badge>
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

  // View 2: Project Dashboard
  const renderProjectDashboard = () => (
    <div className={styles.container} style={{ overflow: 'hidden', height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header with Back Button */}
      <Paper p="md" radius={0} style={{ background: 'rgba(0,0,0,0.2)', borderBottom: '1px solid var(--glass-border)', backdropFilter: 'blur(10px)' }}>
        <Group justify="space-between">
          <Group>
            <Button variant="subtle" onClick={() => setSelectedProject(null)} leftSection={<IconArrowLeft size={16} />}>
              {t('button_back')}
            </Button>
            <Title order={3} style={{ fontFamily: 'var(--font-header)', color: 'var(--text-highlight)' }}>
              {selectedProject.name}
            </Title>
            <Badge color={selectedProject.status === 'active' ? 'blue' : selectedProject.status === 'archived' ? 'orange' : 'red'}>
              {t(`project_management.status.${selectedProject.status}`)}
            </Badge>
          </Group>
          <Group>
            <Button variant="light" size="xs" onClick={handleRefreshFiles}>{t('project_management.refresh_files')}</Button>
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
              handleStatusChange={handleUpdateStatus}
              handleNotesChange={handleUpdateNotes}
              onPathsUpdated={() => fetchProjectFiles(selectedProject.project_id)}
              onDeleteForever={() => setDeleteModalOpen(true)}
              onManageProject={handleOpenManage}
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
        title={t('project_management.actions.create_new')}
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
            onChange={(val) => setNewProjectGame(val)}
          />
          <Select
            label="Source Language"
            description="The language of the original files (e.g., english)."
            data={[
              { value: 'english', label: 'English' },
              { value: 'simp_chinese', label: 'Simplified Chinese' },
              { value: 'german', label: 'German' },
              { value: 'french', label: 'French' },
              { value: 'russian', label: 'Russian' },
              { value: 'spanish', label: 'Spanish' },
              { value: 'japanese', label: 'Japanese' },
              { value: 'korean', label: 'Korean' }
            ]}
            value={newProjectSourceLang}
            onChange={(val) => setNewProjectSourceLang(val)}
          />
          <Button onClick={handleCreateProject} fullWidth mt="md">{t('project_management.actions.create_new')}</Button>
        </Stack>
      </Modal>

      <Modal
        opened={deleteModalOpen}
        onClose={() => { setDeleteModalOpen(false); setDeleteSourceFiles(false); }}
        title={
          <Group>
            <IconAlertTriangle color="red" size={24} />
            <Text fw={700} c="red">{t('project_management.delete_forever')}</Text>
          </Group>
        }
        size="md"
        centered
      >
        <Stack>
          <Alert color="red" variant="light" icon={<IconAlertTriangle size={16} />}>
            <Text size="sm" fw={600}>此操作不可撤销！</Text>
            <Text size="xs" c="dimmed" mt={4}>删除后项目配置将永久丢失，请谨慎操作。</Text>
          </Alert>

          <Text size="sm">
            确认要永久删除以下项目吗？
          </Text>
          <Paper withBorder p="xs" bg="rgba(255, 0, 0, 0.05)">
            <Text size="sm" fw={600}>{selectedProject?.name}</Text>
            <Text size="xs" c="dimmed">{selectedProject?.source_path}</Text>
          </Paper>

          <Checkbox
            checked={deleteSourceFiles}
            onChange={(e) => setDeleteSourceFiles(e.currentTarget.checked)}
            label={
              <div>
                <Text size="sm" fw={600} c="red">同时删除硬盘上的原始文件</Text>
                <Text size="xs" c="dimmed">如果勾选，将永久删除项目文件夹中的所有原始文件</Text>
              </div>
            }
            color="red"
            size="md"
            mt="md"
          />

          <Group justify="flex-end" mt="xl">
            <Button variant="default" onClick={() => { setDeleteModalOpen(false); setDeleteSourceFiles(false); }}>
              {t('button_cancel')}
            </Button>
            <Button color="red" leftSection={<IconTrash size={16} />} onClick={handleDeleteForever}>
              {deleteSourceFiles ? '删除配置 + 原始文件' : '仅删除配置'}
            </Button>
          </Group>
        </Stack>
      </Modal>

      <Modal
        opened={manageModalOpen}
        onClose={() => setManageModalOpen(false)}
        title={t('project_management.manage_project')}
        size="lg"
      >
        <Stack>
          <Select
            label={t('form_label_game')}
            data={[
              { value: 'stellaris', label: 'Stellaris' },
              { value: 'hoi4', label: 'Hearts of Iron IV' },
              { value: 'vic3', label: 'Victoria 3' },
              { value: 'ck3', label: 'Crusader Kings III' },
              { value: 'eu4', label: 'Europa Universalis IV' }
            ]}
            value={editGameId}
            onChange={setEditGameId}
          />
          <Select
            label={t('form_label_source_language')}
            data={[
              { value: 'english', label: 'English' },
              { value: 'simp_chinese', label: 'Simplified Chinese' },
              { value: 'german', label: 'German' },
              { value: 'french', label: 'French' },
              { value: 'russian', label: 'Russian' },
              { value: 'spanish', label: 'Spanish' },
              { value: 'japanese', label: 'Japanese' },
              { value: 'korean', label: 'Korean' }
            ]}
            value={editSourceLang}
            onChange={setEditSourceLang}
          />
          <Group justify="flex-end" mt="md">
            <Button variant="default" onClick={() => setManageModalOpen(false)}>{t('button_cancel')}</Button>
            <Button onClick={handleUpdateMetadata}>{t('settings_save')}</Button>
          </Group>
        </Stack>
      </Modal>
    </>
  );
}
