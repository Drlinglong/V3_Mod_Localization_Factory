import React, { useState, useEffect } from 'react';
import {
    Container, Grid, Paper, Title, Text, Stack, Group, Button,
    TextInput, ScrollArea, Badge, ActionIcon, LoadingOverlay, Box,
    ThemeIcon, Divider, Select, Tabs, Checkbox, Card, Code, MultiSelect
} from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { notifications } from '@mantine/notifications';
import {
    IconCheck, IconX, IconBulb, IconQuote, IconSearch, IconRadar2,
    IconGavel, IconCpu, IconFileText, IconSparkles
} from '@tabler/icons-react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';

const API_BASE_URL = '/api';

// --- Sub-Component: Mining Dashboard ---
const MiningDashboard = () => {
    const { t } = useTranslation();
    const [projects, setProjects] = useState([]);
    const [selectedProject, setSelectedProject] = useState(null);
    const [files, setFiles] = useState([]);
    const [selectedFiles, setSelectedFiles] = useState([]);
    const [apiProvider, setApiProvider] = useState('gemini');
    const [targetLang, setTargetLang] = useState('zh-CN');
    const [scanning, setScanning] = useState(false);

    useEffect(() => {
        fetchProjects();
    }, []);

    useEffect(() => {
        if (selectedProject) {
            fetchFiles(selectedProject);
        } else {
            setFiles([]);
            setSelectedFiles([]);
        }
    }, [selectedProject]);

    const fetchProjects = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/projects`);
            setProjects(response.data.map(p => ({ value: p.project_id, label: p.name })));
        } catch (error) {
            console.error("Failed to fetch projects", error);
        }
    };

    const fetchFiles = async (projectId) => {
        try {
            const response = await axios.get(`${API_BASE_URL}/projects/${projectId}/files`);
            setFiles(response.data);
            // Default select all? No, maybe none or let user choose.
        } catch (error) {
            console.error("Failed to fetch files", error);
        }
    };

    const handleScan = async () => {
        if (!selectedProject) return;
        setScanning(true);
        try {
            await axios.post(`${API_BASE_URL}/neologisms/mine`, {
                project_id: selectedProject,
                api_provider: apiProvider,
                target_lang: targetLang,
                file_paths: selectedFiles.length > 0 ? selectedFiles : null // null means all
            });
            notifications.show({
                title: t('neologism_review.mining.start_mining'),
                message: 'The AI is now mining neologisms in the background.',
                color: 'blue',
                icon: <IconSparkles size={18} />
            });
        } catch (error) {
            notifications.show({ title: 'Error', message: 'Failed to start scan', color: 'red' });
        } finally {
            setScanning(false);
        }
    };

    return (
        <Container size="lg" py="xl">
            <Title order={2} mb="xl" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <IconCpu size={32} color="var(--mantine-color-blue-4)" />
                {t('neologism_review.tab_mining')}
            </Title>

            <Grid>
                <Grid.Col span={4}>
                    <Stack>
                        <Select
                            label={t('neologism_review.mining.select_project')}
                            placeholder={t('neologism_review.mining.select_project_placeholder')}
                            data={projects}
                            value={selectedProject}
                            onChange={setSelectedProject}
                            size="md"
                        />

                        <Select
                            label="Target Language"
                            description="AI will provide suggestions in this language"
                            data={[
                                { value: 'zh-CN', label: 'Simplified Chinese (简体中文)' },
                                { value: 'zh-TW', label: 'Traditional Chinese (繁體中文)' },
                                { value: 'en', label: 'English' },
                                { value: 'ja', label: 'Japanese (日本語)' },
                                { value: 'ko', label: 'Korean (한국어)' },
                                { value: 'fr', label: 'French (Français)' },
                                { value: 'de', label: 'German (Deutsch)' },
                                { value: 'ru', label: 'Russian (Русский)' },
                                { value: 'es', label: 'Spanish (Español)' },
                                { value: 'pt', label: 'Portuguese (Português)' },
                                { value: 'pl', label: 'Polish (Polski)' }
                            ]}
                            value={targetLang}
                            onChange={setTargetLang}
                            size="md"
                        />

                        <Select
                            label={t('neologism_review.mining.select_provider')}
                            data={[
                                { value: 'gemini', label: 'Google Gemini (Recommended)' },
                                { value: 'openai', label: 'OpenAI GPT-4' },
                                { value: 'qwen', label: 'Qwen (Tongyi Qianwen)' },
                                { value: 'deepseek', label: 'DeepSeek' },
                                { value: 'grok', label: 'Grok (xAI)' },
                                { value: 'ollama', label: 'Ollama (Local)' },
                                { value: 'modelscope', label: 'ModelScope' },
                                { value: 'siliconflow', label: 'SiliconFlow' },
                                { value: 'your_favourite_api', label: 'Custom API' }
                            ]}
                            value={apiProvider}
                            onChange={setApiProvider}
                            size="md"
                        />

                        <Button
                            size="xl"
                            mt="xl"
                            leftSection={<IconRadar2 />}
                            onClick={handleScan}
                            loading={scanning}
                            disabled={!selectedProject}
                            variant="gradient"
                            gradient={{ from: 'blue', to: 'cyan', deg: 90 }}
                        >
                            {t('neologism_review.mining.start_mining')}
                        </Button>
                        <Text size="xs" c="dimmed" ta="center">
                            {t('neologism_review.mining.mining_disclaimer')}
                        </Text>
                    </Stack>
                </Grid.Col>

                <Grid.Col span={8}>
                    <Paper p="md" withBorder h={500} style={{ display: 'flex', flexDirection: 'column' }}>
                        <Text fw={700} mb="sm">{t('neologism_review.mining.select_files')}</Text>
                        <Text size="xs" c="dimmed" mb="md">{t('neologism_review.mining.select_files_desc')}</Text>

                        <ScrollArea style={{ flex: 1 }}>
                            {files.length > 0 ? (
                                <Checkbox.Group value={selectedFiles} onChange={setSelectedFiles}>
                                    <Stack gap="xs">
                                        {files.map(f => (
                                            <Checkbox
                                                key={f.path}
                                                value={f.path}
                                                label={
                                                    <Group gap="xs">
                                                        <IconFileText size={14} />
                                                        <Text size="sm">{f.rel_path}</Text>
                                                    </Group>
                                                }
                                            />
                                        ))}
                                    </Stack>
                                </Checkbox.Group>
                            ) : (
                                <Text c="dimmed" fs="italic">{t('neologism_review.mining.no_files')}</Text>
                            )}
                        </ScrollArea>
                    </Paper>
                </Grid.Col>
            </Grid>
        </Container>
    );
};

// --- Sub-Component: Judgment Court ---
const JudgmentCourt = () => {
    const { t } = useTranslation();
    const [projects, setProjects] = useState([]);
    const [selectedProject, setSelectedProject] = useState(null);
    const [candidates, setCandidates] = useState([]);
    const [selectedId, setSelectedId] = useState(null);
    const [loading, setLoading] = useState(false);
    const [processing, setProcessing] = useState(false);
    const [editSuggestion, setEditSuggestion] = useState("");

    useEffect(() => {
        fetchProjects();
    }, []);

    useEffect(() => {
        if (selectedProject) {
            fetchCandidates(selectedProject);
        } else {
            setCandidates([]);
        }
    }, [selectedProject]);

    useEffect(() => {
        if (selectedId) {
            const candidate = candidates.find(c => c.id === selectedId);
            if (candidate) {
                setEditSuggestion(candidate.suggestion || "");
            }
        }
    }, [selectedId, candidates]);

    const fetchProjects = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/projects`);
            setProjects(response.data);
            if (response.data.length > 0) {
                setSelectedProject(response.data[0].project_id);
            }
        } catch (error) {
            console.error("Failed to fetch projects", error);
        }
    };

    const fetchCandidates = async (projectId) => {
        setLoading(true);
        try {
            const response = await axios.get(`${API_BASE_URL}/neologisms?project_id=${projectId}`);
            setCandidates(response.data);
            if (response.data.length > 0 && !selectedId) {
                setSelectedId(response.data[0].id);
            }
        } catch (error) {
            notifications.show({ title: 'Error', message: 'Failed to load candidates', color: 'red' });
        } finally {
            setLoading(false);
        }
    };

    const handleApprove = async () => {
        if (!selectedId || !selectedProject) return;
        const candidate = candidates.find(c => c.id === selectedId);
        if (!candidate) return;

        setProcessing(true);
        try {
            await axios.post(`${API_BASE_URL}/neologisms/${selectedId}/approve`, {
                project_id: selectedProject,
                final_translation: editSuggestion,
                glossary_id: 1
            });
            notifications.show({ title: 'Approved', message: 'Term added to glossary', color: 'green' });
            removeCandidate(selectedId);
        } catch (error) {
            notifications.show({ title: 'Error', message: 'Failed to approve', color: 'red' });
        } finally {
            setProcessing(false);
        }
    };

    const handleReject = async () => {
        if (!selectedId || !selectedProject) return;
        setProcessing(true);
        try {
            await axios.post(`${API_BASE_URL}/neologisms/${selectedId}/reject`, {
                project_id: selectedProject
            });
            notifications.show({ title: 'Rejected', message: 'Term ignored', color: 'gray' });
            removeCandidate(selectedId);
        } catch (error) {
            notifications.show({ title: 'Error', message: 'Failed to reject', color: 'red' });
        } finally {
            setProcessing(false);
        }
    };

    const removeCandidate = (id) => {
        const newList = candidates.filter(c => c.id !== id);
        setCandidates(newList);
        if (newList.length > 0) {
            setSelectedId(newList[0].id);
        } else {
            setSelectedId(null);
        }
    };

    const selectedCandidate = candidates.find(c => c.id === selectedId);
    const currentProject = projects.find(p => p.project_id === selectedProject);

    const HighlightedText = ({ text, term }) => {
        if (!text || !term) return <Text>{text}</Text>;
        const parts = text.split(new RegExp(`(${term})`, 'gi'));
        return (
            <Text size="sm" c="dimmed" lh={1.6}>
                {parts.map((part, i) =>
                    part.toLowerCase() === term.toLowerCase() ?
                        <span key={i} style={{
                            color: 'var(--mantine-color-yellow-4)',
                            fontWeight: 'bold',
                            backgroundColor: 'rgba(255, 255, 0, 0.1)',
                            padding: '0 4px',
                            borderRadius: '4px'
                        }}>{part}</span> :
                        part
                )}
            </Text>
        );
    };

    return (
        <Box h="100%" style={{ display: 'flex', flexDirection: 'column' }}>
            {/* Project Context Header */}
            <Paper p="md" mb="md" style={{ background: 'var(--glass-bg)', borderBottom: '1px solid var(--glass-border)' }}>
                <Group justify="space-between" align="center">
                    <Box style={{ flex: 1 }}>
                        <Text size="xs" c="dimmed" tt="uppercase" fw={700} ls={1}>Current Project</Text>
                        <Select
                            data={projects.map(p => ({ value: p.project_id, label: p.name }))}
                            value={selectedProject}
                            onChange={setSelectedProject}
                            placeholder="Select a project..."
                            size="md"
                            mt="xs"
                        />
                    </Box>
                    {currentProject && (
                        <Badge size="lg" variant="light" color="blue">
                            {candidates.length} Pending Terms
                        </Badge>
                    )}
                </Group>
            </Paper>

            <Grid h="100%" gutter={0} style={{ flex: 1, overflow: 'hidden' }}>
                {/* Sidebar List */}
                <Grid.Col span={3} h="100%" style={{ borderRight: '1px solid var(--glass-border)', display: 'flex', flexDirection: 'column' }}>
                    <Stack p="md" h="100%">
                        <Group justify="space-between">
                            <Title order={4} c="dimmed">{t('neologism_review.court.docket')}</Title>
                            <Badge variant="dot" size="lg">{candidates.length}</Badge>
                        </Group>
                        <ScrollArea style={{ flex: 1, margin: '0 -16px' }} p="md">
                            <Stack gap="xs">
                                {candidates.map(c => (
                                    <Paper
                                        key={c.id}
                                        p="md"
                                        radius="md"
                                        onClick={() => setSelectedId(c.id)}
                                        style={{
                                            cursor: 'pointer',
                                            backgroundColor: selectedId === c.id ? 'var(--mantine-color-blue-light)' : 'var(--glass-bg)',
                                            border: selectedId === c.id ? '1px solid var(--mantine-color-blue-filled)' : '1px solid transparent',
                                            transition: 'all 0.2s ease'
                                        }}
                                    >
                                        <Text fw={600} lineClamp={1}>{c.original}</Text>
                                        <Text size="xs" c="dimmed" truncate>{c.suggestion}</Text>
                                    </Paper>
                                ))}
                                {candidates.length === 0 && !loading && (
                                    <Stack align="center" mt="xl" c="dimmed">
                                        <IconCheck size={32} />
                                        <Text>{t('neologism_review.court.caught_up')}</Text>
                                    </Stack>
                                )}
                            </Stack>
                        </ScrollArea>
                    </Stack>
                </Grid.Col>

                {/* Main Review Area */}
                <Grid.Col span={9} h="100%" style={{ position: 'relative' }}>
                    {selectedCandidate ? (
                        <Stack h="100%" p="xl" gap="xl">
                            <LoadingOverlay visible={processing} />

                            {/* Header Section */}
                            <Paper p="xl" radius="lg" style={{ background: 'var(--glass-bg)', backdropFilter: 'blur(10px)' }}>
                                <Group align="flex-start" justify="space-between">
                                    <Box>
                                        <Text size="xs" c="dimmed" tt="uppercase" fw={700} ls={1}>{t('neologism_review.court.candidate_term')}</Text>
                                        <Title order={1} style={{ fontSize: '2.5rem', color: 'var(--mantine-color-blue-3)' }}>
                                            {selectedCandidate.original}
                                        </Title>
                                    </Box>
                                    <Badge size="lg" variant="outline" color="gray">
                                        {selectedCandidate.source_file.split('\\').pop()}
                                    </Badge>
                                </Group>
                            </Paper>

                            <Grid gutter="xl" style={{ flex: 1 }}>
                                {/* Left Column: Analysis & Action */}
                                <Grid.Col span={7}>
                                    <Stack gap="lg" h="100%">
                                        <Paper p="lg" radius="md" style={{ background: 'rgba(0,0,0,0.2)' }} withBorder>
                                            <Group mb="sm">
                                                <ThemeIcon color="yellow" variant="light" size="lg"><IconBulb size={20} /></ThemeIcon>
                                                <Text fw={700}>{t('neologism_review.court.ai_analysis')}</Text>
                                            </Group>
                                            <Text size="sm" style={{ lineHeight: 1.6 }}>
                                                {selectedCandidate.reasoning}
                                            </Text>
                                        </Paper>

                                        <Box mt="auto">
                                            <TextInput
                                                label={t('neologism_review.court.final_translation')}
                                                description={t('neologism_review.court.final_translation_desc')}
                                                size="xl"
                                                radius="md"
                                                value={editSuggestion}
                                                onChange={(e) => setEditSuggestion(e.currentTarget.value)}
                                                rightSection={
                                                    <ActionIcon variant="subtle" onClick={() => setEditSuggestion(selectedCandidate.suggestion)}>
                                                        <IconSparkles size={18} />
                                                    </ActionIcon>
                                                }
                                            />
                                            <Group mt="lg" grow>
                                                <Button
                                                    size="lg"
                                                    variant="default"
                                                    color="gray"
                                                    leftSection={<IconX />}
                                                    onClick={handleReject}
                                                >
                                                    {t('neologism_review.court.ignore')}
                                                </Button>
                                                <Button
                                                    size="lg"
                                                    variant="gradient"
                                                    gradient={{ from: 'teal', to: 'lime', deg: 105 }}
                                                    leftSection={<IconGavel />}
                                                    onClick={handleApprove}
                                                >
                                                    {t('neologism_review.court.approve')}
                                                </Button>
                                            </Group>
                                        </Box>
                                    </Stack>
                                </Grid.Col>

                                {/* Right Column: Evidence */}
                                <Grid.Col span={5}>
                                    <Stack h="100%">
                                        <Text fw={700} c="dimmed" tt="uppercase" size="xs">{t('neologism_review.court.context_evidence')}</Text>
                                        <ScrollArea style={{ flex: 1 }} type="auto">
                                            <Stack gap="sm">
                                                {selectedCandidate.context_snippets.map((snippet, idx) => (
                                                    <Paper key={idx} p="md" radius="md" style={{ background: 'rgba(0,0,0,0.3)' }}>
                                                        <Group align="flex-start" gap="xs" wrap="nowrap">
                                                            <IconQuote size={16} style={{ opacity: 0.5, marginTop: 4 }} />
                                                            <HighlightedText text={snippet} term={selectedCandidate.original} />
                                                        </Group>
                                                    </Paper>
                                                ))}
                                            </Stack>
                                        </ScrollArea>
                                    </Stack>
                                </Grid.Col>
                            </Grid>
                        </Stack>
                    ) : (
                        <Stack align="center" justify="center" h="100%" c="dimmed">
                            <IconGavel size={64} style={{ opacity: 0.2 }} />
                            <Text size="xl">{t('neologism_review.court.select_case')}</Text>
                        </Stack>
                    )}
                </Grid.Col>
            </Grid>
        </Box>
    );
};

// --- Main Page Component ---
const NeologismReviewPage = () => {
    const { t } = useTranslation();
    return (
        <Box h="100%" style={{ overflow: 'hidden' }}>
            <Tabs defaultValue="dashboard" h="100%" variant="pills" radius="md">
                <Box p="md" pb={0}>
                    <Tabs.List>
                        <Tabs.Tab value="dashboard" leftSection={<IconCpu size={16} />}>
                            {t('neologism_review.tab_mining')}
                        </Tabs.Tab>
                        <Tabs.Tab value="court" leftSection={<IconGavel size={16} />}>
                            {t('neologism_review.tab_court')}
                        </Tabs.Tab>
                    </Tabs.List>
                </Box>

                <Tabs.Panel value="dashboard" h="calc(100% - 60px)">
                    <MiningDashboard />
                </Tabs.Panel>

                <Tabs.Panel value="court" h="calc(100% - 60px)">
                    <JudgmentCourt />
                </Tabs.Panel>
            </Tabs>
        </Box>
    );
};

export default NeologismReviewPage;
