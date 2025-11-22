import React, { useState, useEffect } from 'react';
import { Container, Title, Paper, Grid, Textarea, Button, Group, Text, Loader, ScrollArea } from '@mantine/core';
import { useSearchParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { IconDeviceFloppy } from '@tabler/icons-react';

const API_BASE = 'http://localhost:8000/api';

export default function ProofreadingPage() {
  const [searchParams] = useSearchParams();
  const projectId = searchParams.get('projectId');
  const fileId = searchParams.get('fileId');

  const [loading, setLoading] = useState(true);
  const [entries, setEntries] = useState([]);
  const [fileInfo, setFileInfo] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (projectId && fileId) {
      loadData();
    }
  }, [projectId, fileId]);

  const loadData = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API_BASE}/proofread/${projectId}/${fileId}`);
      setEntries(res.data.entries);
      setFileInfo({ path: res.data.file_path });
    } catch (error) {
      console.error("Failed to load proofreading data", error);
      alert("Failed to load file data.");
    } finally {
      setLoading(false);
    }
  };

  const handleTranslationChange = (index, newValue) => {
    const newEntries = [...entries];
    newEntries[index].translation = newValue;
    setEntries(newEntries);
  };

  const handleSave = async () => {
    try {
      await axios.post(`${API_BASE}/proofread/save`, {
        project_id: projectId,
        file_id: fileId,
        entries: entries,
        content: "" // Legacy, we send entries now
      });
      alert("Saved successfully!");
    } catch (error) {
      console.error("Failed to save", error);
      alert("Failed to save changes.");
    }
  };

  if (loading) {
    return <Container><Loader /></Container>;
  }

  if (!projectId || !fileId) {
    return <Container><Text>Please select a file from the Project Management page.</Text></Container>;
  }

  return (
    <Container fluid p="md" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Group position="apart" mb="md">
        <Box>
            <Title order={3}>Proofreading</Title>
            <Text size="sm" color="dimmed">{fileInfo?.path}</Text>
        </Box>
        <Button leftIcon={<IconDeviceFloppy />} onClick={handleSave}>
          Save Changes
        </Button>
      </Group>

      <Paper withBorder p="md" style={{ flex: 1, overflow: 'hidden' }}>
        <ScrollArea style={{ height: '100%' }}>
            {entries.length === 0 && (
                <Text color="dimmed" align="center" mt="xl">
                    No entries found. Has this file been translated yet?
                </Text>
            )}
            {entries.map((entry, index) => (
                <Grid key={index} gutter="md" mb="sm" align="flex-start">
                    <Grid.Col span={6}>
                        <Paper p="xs" withBorder bg="dark.8">
                            <Text size="xs" color="dimmed" mb={4}>{entry.key}</Text>
                            <Text style={{ whiteSpace: 'pre-wrap' }}>{entry.original}</Text>
                        </Paper>
                    </Grid.Col>
                    <Grid.Col span={6}>
                        <Textarea
                            minRows={2}
                            autosize
                            value={entry.translation || ''}
                            onChange={(e) => handleTranslationChange(index, e.currentTarget.value)}
                        />
                    </Grid.Col>
                </Grid>
            ))}
        </ScrollArea>
      </Paper>
    </Container>
  );
}

import { Box } from '@mantine/core';
