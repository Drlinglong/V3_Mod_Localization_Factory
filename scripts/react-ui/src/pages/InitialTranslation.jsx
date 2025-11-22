import React, { useState, useEffect } from 'react';
import { Container, Title, Select, Button, Group, Text, Paper, Loader } from '@mantine/core';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

export default function InitialTranslation() {
  const [projects, setProjects] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState(null);
  const [targetLang, setTargetLang] = useState('zh');
  const [apiProvider, setApiProvider] = useState('gemini');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const res = await axios.get(`${API_BASE}/projects`);
      setProjects(res.data.map(p => ({ value: p.project_id, label: p.name })));
    } catch (error) {
      console.error("Failed to load projects", error);
    }
  };

  const handleStart = async () => {
    if (!selectedProjectId) {
      alert("Please select a project first!");
      return;
    }

    setLoading(true);
    try {
      await axios.post(`${API_BASE}/translate/start`, {
        project_id: selectedProjectId,
        target_language: targetLang,
        api_provider: apiProvider,
        model: 'gemini-pro' // hardcoded for MVP
      });
      alert("Translation started in background!");
      // Navigate to Project Management to see status/files
      navigate('/');
    } catch (error) {
      console.error("Failed to start translation", error);
      alert("Failed to start translation.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container size="sm" mt="xl">
      <Paper p="xl" withBorder radius="md">
        <Title order={2} mb="lg">Start New Translation</Title>

        {projects.length === 0 ? (
            <Text color="dimmed" mb="md">
                No projects found. Please <a href="#" onClick={(e) => {e.preventDefault(); navigate('/')}}>create a project</a> first.
            </Text>
        ) : (
            <>
                <Select
                    label="Select Project"
                    placeholder="Choose a project..."
                    data={projects}
                    value={selectedProjectId}
                    onChange={setSelectedProjectId}
                    mb="md"
                    required
                />

                <Select
                    label="Target Language"
                    data={[{ value: 'zh', label: 'Chinese (Simplified)' }]}
                    value={targetLang}
                    onChange={setTargetLang}
                    mb="md"
                />

                <Select
                    label="API Provider"
                    data={[
                        { value: 'gemini', label: 'Google Gemini' },
                        { value: 'openai', label: 'OpenAI' }
                    ]}
                    value={apiProvider}
                    onChange={setApiProvider}
                    mb="xl"
                />

                <Button fullWidth size="lg" onClick={handleStart} loading={loading}>
                    Start AI Translation
                </Button>
            </>
        )}
      </Paper>
    </Container>
  );
}
