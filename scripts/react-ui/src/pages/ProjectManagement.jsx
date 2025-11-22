import React, { useState, useEffect } from 'react';
import {
  Container, Title, Button, Group, Card, Text, Grid, Modal, TextInput, Select,
  Stack, Badge, ActionIcon, ScrollArea, Table, Box
} from '@mantine/core';
import { IconPlus, IconFolder, IconFileText, IconEdit } from '@tabler/icons-react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

export default function ProjectManagement() {
  const [projects, setProjects] = useState([]);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);
  const [projectFiles, setProjectFiles] = useState([]);

  // Form State
  const [newProjectName, setNewProjectName] = useState('');
  const [newProjectPath, setNewProjectPath] = useState('');
  const [newProjectGame, setNewProjectGame] = useState('stellaris'); // Default

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
      setProjectFiles(res.data);
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
      // Reset form
      setNewProjectName('');
      setNewProjectPath('');
    } catch (error) {
      alert(`Failed to create project: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleProofread = (file) => {
    if (!selectedProject) return;
    navigate(`/proofreading?projectId=${selectedProject.project_id}&fileId=${file.file_id}`);
  };

  return (
    <Container fluid p="md" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Group position="apart" mb="md">
        <Title order={2}>Project Management</Title>
        <Button leftIcon={<IconPlus size={16} />} onClick={() => setIsCreateModalOpen(true)}>
          New Project
        </Button>
      </Group>

      <Grid style={{ flex: 1 }}>
        {/* Project List Sidebar / Grid */}
        <Grid.Col span={selectedProject ? 3 : 12}>
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
                  style={{
                    cursor: 'pointer',
                    borderColor: selectedProject?.project_id === p.project_id ? '#228be6' : undefined,
                    backgroundColor: selectedProject?.project_id === p.project_id ? 'rgba(34, 139, 230, 0.1)' : undefined
                  }}
                >
                  <Group position="apart" noWrap>
                    <Box>
                        <Text weight={500}>{p.name}</Text>
                        <Text size="xs" color="dimmed">{p.game_id}</Text>
                    </Box>
                    <Badge color={p.status === 'active' ? 'green' : 'gray'}>{p.status}</Badge>
                  </Group>
                </Card>
              ))}
            </Stack>
           </ScrollArea>
        </Grid.Col>

        {/* Project Details */}
        {selectedProject && (
          <Grid.Col span={9} style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
             <Card shadow="sm" p="md" radius="md" withBorder style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                <Group position="apart" mb="md">
                    <Title order={3}>{selectedProject.name} - Files</Title>
                    <Text size="sm" color="dimmed">{selectedProject.source_path}</Text>
                </Group>

                <ScrollArea style={{ flex: 1 }}>
                    <Table highlightOnHover>
                        <thead>
                            <tr>
                                <th>File</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {projectFiles.map((f) => (
                                <tr key={f.file_id}>
                                    <td><Text size="sm">{f.file_path}</Text></td>
                                    <td>
                                        <Badge
                                            color={f.status === 'done' ? 'green' : f.status === 'proofreading' ? 'yellow' : 'gray'}
                                        >
                                            {f.status}
                                        </Badge>
                                    </td>
                                    <td>
                                        <Button
                                            size="xs"
                                            variant="light"
                                            leftIcon={<IconEdit size={14}/>}
                                            onClick={() => handleProofread(f)}
                                        >
                                            Proofread
                                        </Button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </Table>
                </ScrollArea>
             </Card>
          </Grid.Col>
        )}
      </Grid>

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
                placeholder="C:/Users/Me/Desktop/ModFolder"
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
    </Container>
  );
}
