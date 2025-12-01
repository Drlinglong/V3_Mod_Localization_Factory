import React, { useState, useEffect } from 'react';
import {
    Stack, Badge, ScrollArea, Table, Box, Tabs, Center, Paper, BackgroundImage,
    ActionIcon, SimpleGrid, Overlay, Input, Tooltip, Textarea, Group, Title, Text, Button, Grid, Card, Modal, TextInput
} from '@mantine/core';
import { IconCheck, IconX, IconClock, IconPlayerPlay, IconArrowLeft, IconArrowRight, IconEdit, IconPlus, IconTrash, IconFolder, IconArchive, IconRestore } from '@tabler/icons-react';
import { useTranslation } from 'react-i18next';
import { open } from '@tauri-apps/plugin-dialog';
import axios from 'axios';
import styles from '../../pages/ProjectManagement.module.css';

import { useSidebar } from '../../context/SidebarContext';

const ProjectOverview = ({ projectDetails, handleStatusChange, handleNotesChange, handleProofread, onPathsUpdated, onDeleteForever }) => {
    const { t } = useTranslation();
    const [managePathsOpen, setManagePathsOpen] = useState(false);
    const [translationDirs, setTranslationDirs] = useState([]);
    const [newDirPath, setNewDirPath] = useState('');
    const [notes, setNotes] = useState(''); // Current input for new note
    const [deleteModalOpen, setDeleteModalOpen] = useState(false);
    const [deleteNoteId, setDeleteNoteId] = useState(null);

    // Sidebar Context
    const { setSidebarContent, setSidebarWidth, sidebarWidth } = useSidebar();

    // Cleanup sidebar on unmount (leaving the page)
    useEffect(() => {
        return () => {
            setSidebarContent(null);
        };
    }, []);

    if (!projectDetails) return null;

    const onSaveNote = async () => {
        if (!notes.trim()) return;
        try {
            await axios.post(`/api/project/${projectDetails.project_id}/notes`, { notes });
            setNotes(''); // Clear input
            // Refresh sidebar if it's showing notes
            handleViewNotesHistory();
            // Refresh sidebar if it's showing notes
            handleViewNotesHistory();
            // alert(t('project_management.note_added')); // Removed as per user request
        } catch (error) {
            console.error("Failed to save note", error);
            alert("Failed to save note");
        }
    };

    const handleDeleteNote = (noteId) => {
        setDeleteNoteId(noteId);
        setDeleteModalOpen(true);
    };

    const confirmDeleteNote = async () => {
        if (!deleteNoteId) return;
        try {
            await axios.delete(`/api/project/${projectDetails.project_id}/notes/${deleteNoteId}`);
            // Refresh sidebar
            handleViewNotesHistory();
            setDeleteModalOpen(false);
            setDeleteNoteId(null);
            // alert(t('project_management.note_deleted')); // Removed default alert
        } catch (error) {
            console.error("Failed to delete note", error);
            alert("Failed to delete note");
        }
    };

    const handleViewNotesHistory = async () => {
        try {
            const res = await axios.get(`/api/project/${projectDetails.project_id}/notes`);
            const history = res.data;

            // Auto-expand sidebar if collapsed or too narrow
            if (!sidebarWidth || sidebarWidth < 300) {
                setSidebarWidth(350);
            }

            const NotesHistoryView = (
                <Stack>
                    <Group justify="space-between" mb="sm">
                        <Title order={5}>{t('project_management.notes_history_title')}</Title>
                        <ActionIcon variant="subtle" color="gray" onClick={() => setSidebarContent(null)}>
                            <IconX size={16} />
                        </ActionIcon>
                    </Group>
                    {history.length === 0 ? (
                        <Text c="dimmed" fs="italic">No notes recorded yet.</Text>
                    ) : (
                        history.map((note) => (
                            <Paper key={note.id} withBorder p="sm" radius="md" style={{ background: 'rgba(255,255,255,0.05)' }}>
                                <Group justify="space-between" mb="xs">
                                    <Text size="xs" c="dimmed">{new Date(note.created_at).toLocaleString()}</Text>
                                    <ActionIcon color="red" variant="subtle" size="xs" onClick={() => handleDeleteNote(note.id)}>
                                        <IconTrash size={14} />
                                    </ActionIcon>
                                </Group>
                                <Text style={{ whiteSpace: 'pre-wrap' }} size="sm">{note.content}</Text>
                            </Paper>
                        ))
                    )}
                </Stack>
            );

            setSidebarContent(NotesHistoryView);
            // Ensure sidebar is open/visible (ContextualSider handles this via content not null)
        } catch (error) {
            console.error("Failed to load notes history", error);
        }
    };

    const handleOpenManagePaths = () => {
        setTranslationDirs(projectDetails.translation_dirs || []);
        setManagePathsOpen(true);
    };

    const handleBrowseFolder = async () => {
        try {
            const selected = await open({
                directory: true,
                multiple: false,
                title: 'Select Translation Directory'
            });
            if (selected && typeof selected === 'string') {
                setNewDirPath(selected);
            }
        } catch (err) {
            console.error('Failed to open dialog:', err);
        }
    };

    const handleAddDir = () => {
        if (newDirPath && !translationDirs.includes(newDirPath)) {
            setTranslationDirs([...translationDirs, newDirPath]);
            setNewDirPath('');
        }
    };

    const handleRemoveDir = (index) => {
        setTranslationDirs(translationDirs.filter((_, i) => i !== index));
    };

    const handleSavePaths = async () => {
        try {
            const response = await axios.post(`/api/project/${projectDetails.project_id}/config`, {
                translation_dirs: translationDirs
            });
            console.log('Save response:', response.data);
            setManagePathsOpen(false);
            if (onPathsUpdated) {
                onPathsUpdated();
            }
        } catch (error) {
            console.error('Failed to save paths:', error);
            alert(`Failed to save translation directories: ${error.response?.data?.detail || error.message}`);
        }
    };

    // Helper to get relative path
    const getRelativePath = (fullPath) => {
        if (!fullPath) return '';

        // Check source path
        if (projectDetails.source_path && fullPath.startsWith(projectDetails.source_path)) {
            let rel = fullPath.substring(projectDetails.source_path.length);
            if (rel.startsWith('/') || rel.startsWith('\\')) rel = rel.substring(1);
            return rel;
        }

        // Check translation dirs
        if (projectDetails.translation_dirs) {
            for (const dir of projectDetails.translation_dirs) {
                if (fullPath.startsWith(dir)) {
                    let rel = fullPath.substring(dir.length);
                    if (rel.startsWith('/') || rel.startsWith('\\')) rel = rel.substring(1);
                    return rel;
                }
            }
        }

        return fullPath; // Fallback
    };

    const rows = projectDetails.files.map((file) => {
        let color = 'gray';
        let text = '未处理';
        let Icon = IconClock;

        if (file.status === 'translated' || file.status === 'done') { color = 'green'; text = '已翻译'; Icon = IconCheck; }
        else if (file.status === 'failed') { color = 'red'; text = '翻译失败'; Icon = IconX; }
        else if (file.status === 'pending' || file.status === 'todo') { color = 'blue'; text = '待处理'; Icon = IconClock; }
        else if (file.status === 'in_progress') { color = 'yellow'; text = '进行中'; Icon = IconPlayerPlay; }
        else if (file.status === 'proofreading') { color = 'orange'; text = '校对中'; Icon = IconEdit; }

        const relativePath = getRelativePath(file.name);

        return (
            <Table.Tr key={file.key}>
                <Table.Td style={{ maxWidth: '300px' }}>
                    <Tooltip label={file.name} openDelay={500}>
                        <Text fw={500} truncate>{relativePath}</Text>
                    </Tooltip>
                </Table.Td>
                <Table.Td style={{ width: '100px' }}>
                    <Badge variant="dot" color={file.file_type === 'source' ? 'blue' : 'violet'}>
                        {file.file_type === 'source' ? '源文件' : '翻译'}
                    </Badge>
                </Table.Td>
                <Table.Td style={{ width: '80px' }}>{file.lines}</Table.Td>
                <Table.Td style={{ width: '120px' }}>
                    <Badge color={color} variant="light" leftSection={<Icon size={12} />}>
                        {text}
                    </Badge>
                </Table.Td>
                <Table.Td style={{ width: '80px' }}>{file.progress}</Table.Td>
                <Table.Td style={{ width: '120px' }}>
                    <Group gap="xs">
                        {file.actions.map(action => (
                            <Button variant="subtle" size="xs" key={action} onClick={action === 'Proofread' ? () => handleProofread(file) : null}>
                                {t('proofreading.proofread')}
                            </Button>
                        ))}
                    </Group>
                </Table.Td>
            </Table.Tr>
        );
    });

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', width: '100%', overflow: 'hidden', gap: '1rem' }}>
            {/* Header section with stats and paths - Natural height */}
            <div style={{ flexShrink: 0 }}>
                {/* Stats Card */}
                <Paper withBorder p="md" radius="md" className={styles.glassCard} mb="md">
                    <Group justify="space-between" mb="md">
                        <Title order={4}>{t('project_management.overview_title') || 'Project Overview'}</Title>
                        <Group>
                            {projectDetails.status === 'active' && (
                                <Tooltip label={t('project_management.archive_project')}>
                                    <Button variant="light" color="orange" size="xs" leftSection={<IconArchive size={16} />} onClick={() => handleStatusChange('archived')}>
                                        {t('project_management.archive_project')}
                                    </Button>
                                </Tooltip>
                            )}
                            {projectDetails.status === 'archived' && (
                                <>
                                    <Tooltip label={t('project_management.restore_project')}>
                                        <Button variant="light" color="blue" size="xs" leftSection={<IconRestore size={16} />} onClick={() => handleStatusChange('active')}>
                                            {t('project_management.restore_project')}
                                        </Button>
                                    </Tooltip>
                                    <Tooltip label={t('project_management.delete_project')}>
                                        <Button variant="light" color="red" size="xs" leftSection={<IconTrash size={16} />} onClick={() => handleStatusChange('deleted')}>
                                            {t('project_management.delete_project')}
                                        </Button>
                                    </Tooltip>
                                </>
                            )}
                            {projectDetails.status === 'deleted' && (
                                <>
                                    <Tooltip label={t('project_management.restore_project')}>
                                        <Button variant="light" color="blue" size="xs" leftSection={<IconRestore size={16} />} onClick={() => handleStatusChange('active')}>
                                            {t('project_management.restore_project')}
                                        </Button>
                                    </Tooltip>
                                    <Tooltip label={t('project_management.delete_forever')}>
                                        <Button variant="filled" color="red" size="xs" leftSection={<IconTrash size={16} />} onClick={onDeleteForever}>
                                            {t('project_management.delete_forever')}
                                        </Button>
                                    </Tooltip>
                                </>
                            )}
                        </Group>
                    </Group>
                    <Grid>
                        <Grid.Col span={3}><Card withBorder className={styles.statCard}><Text size="xs" c="dimmed">文件总数</Text><Title order={3}>{projectDetails.overview.totalFiles}</Title></Card></Grid.Col>
                        <Grid.Col span={3}><Card withBorder className={styles.statCard}><Text size="xs" c="dimmed">总行数</Text><Title order={3}>{projectDetails.overview.totalLines}</Title></Card></Grid.Col>
                        <Grid.Col span={3}><Card withBorder className={styles.statCard}><Text size="xs" c="dimmed">已翻译</Text><Title order={3} c="green">{projectDetails.overview.translated}%</Title></Card></Grid.Col>
                        <Grid.Col span={3}><Card withBorder className={styles.statCard}><Text size="xs" c="dimmed">待校对</Text><Title order={3} c="yellow">{projectDetails.overview.toBeProofread}%</Title></Card></Grid.Col>
                    </Grid>
                </Paper>

                {/* Notes Section */}
                <Paper withBorder p="md" radius="md" className={styles.glassCard} mb="md">
                    <Group justify="space-between" mb="xs">
                        <Title order={4}>{t('project_management.notes')}</Title>
                        <Group>
                            <Button variant="light" size="xs" onClick={handleViewNotesHistory}>{t('project_management.view_notes_history')}</Button>
                            <Button variant="filled" size="xs" onClick={onSaveNote}>{t('project_management.add_note')}</Button>
                        </Group>
                    </Group>
                    <Textarea
                        value={notes}
                        onChange={(event) => setNotes(event.currentTarget.value)}
                        placeholder={t('project_management.notes_placeholder')}
                        autosize
                        minRows={2}
                    />
                </Paper>

                {/* Path Management */}
                <Paper withBorder p="md" radius="md" className={styles.glassCard}>
                    <Group position="apart">
                        <div>
                            <Text size="sm" fw={500}>源文件目录:</Text>
                            <Text size="xs" c="dimmed" style={{ wordBreak: 'break-all' }}>{projectDetails.source_path || 'Loading...'}</Text>
                        </div>
                        <div>
                            <Text size="sm" fw={500}>翻译目录:</Text>
                            <Text size="xs" c="dimmed" style={{ wordBreak: 'break-all' }}>
                                {projectDetails.translation_dirs ? projectDetails.translation_dirs.join(', ') : 'Default'}
                            </Text>
                        </div>
                        <Button variant="outline" size="xs" onClick={handleOpenManagePaths}>{t('project_management.manage_paths_button')}</Button>
                    </Group>
                </Paper>
            </div>

            {/* Scrollable file list - Fills remaining space using Absolute-in-Flex pattern */}
            <div style={{ flex: 1, position: 'relative', minHeight: 0 }}>
                <div style={{ position: 'absolute', top: 0, bottom: 0, left: 0, right: 0, overflowY: 'auto', overflowX: 'hidden' }}>
                    <Paper withBorder p="md" radius="md" className={styles.glassCard}>
                        <Group position="apart" mb="md">
                            <Title order={4}>文件详情列表 ({projectDetails.files.length} 个文件)</Title>
                        </Group>
                        <Table verticalSpacing="sm" className={styles.table} stickyHeader>
                            <Table.Thead style={{ position: 'sticky', top: 0, backgroundColor: 'var(--glass-bg)', zIndex: 1 }}>
                                <Table.Tr>
                                    <Table.Th>文件名</Table.Th>
                                    <Table.Th style={{ width: '100px' }}>类型</Table.Th>
                                    <Table.Th style={{ width: '80px' }}>行数</Table.Th>
                                    <Table.Th style={{ width: '120px' }}>状态</Table.Th>
                                    <Table.Th style={{ width: '80px' }}>进度</Table.Th>
                                    <Table.Th style={{ width: '120px' }}>操作</Table.Th>
                                </Table.Tr>
                            </Table.Thead>
                            <Table.Tbody>{rows}</Table.Tbody>
                        </Table>
                    </Paper>
                </div>
            </div>

            {/* Manage Paths Modal */}
            <Modal
                opened={managePathsOpen}
                onClose={() => setManagePathsOpen(false)}
                title={t('project_management.manage_paths.title')}
                size="lg"
            >
                <Stack gap="md">
                    <div>
                        <Text size="sm" fw={500} mb="xs">{t('project_management.manage_paths.current_dirs')}:</Text>
                        {translationDirs.length === 0 ? (
                            <Text size="sm" c="dimmed">{t('project_management.manage_paths.no_dirs')}</Text>
                        ) : (
                            <Stack gap="xs">
                                {translationDirs.map((dir, index) => (
                                    <Group key={index} position="apart">
                                        <Text size="sm" style={{ flex: 1, wordBreak: 'break-all' }}>{dir}</Text>
                                        <ActionIcon color="red" onClick={() => handleRemoveDir(index)}>
                                            <IconTrash size={16} />
                                        </ActionIcon>
                                    </Group>
                                ))}
                            </Stack>
                        )}
                    </div>

                    <div>
                        <Text size="sm" fw={500} mb="xs">{t('project_management.manage_paths.add_new')}:</Text>
                        <Group align="flex-end">
                            <TextInput
                                placeholder={t('project_management.manage_paths.placeholder')}
                                value={newDirPath}
                                onChange={(e) => setNewDirPath(e.currentTarget.value)}
                                style={{ flex: 1 }}
                            />
                            <Button onClick={handleBrowseFolder} leftSection={<IconFolder size={16} />}>
                                {t('project_management.manage_paths.browse')}
                            </Button>
                            <Button onClick={handleAddDir} leftSection={<IconPlus size={16} />} disabled={!newDirPath}>
                                {t('project_management.manage_paths.add')}
                            </Button>
                        </Group>
                    </div>

                    <Group justify="flex-end" mt="md">
                        <Button variant="default" onClick={() => setManagePathsOpen(false)}>
                            {t('project_management.manage_paths.cancel')}
                        </Button>
                        <Button onClick={handleSavePaths}>
                            {t('project_management.manage_paths.save')}
                        </Button>
                    </Group>
                </Stack>
            </Modal>

            {/* Delete Note Confirmation Modal */}
            <Modal
                opened={deleteModalOpen}
                onClose={() => setDeleteModalOpen(false)}
                title={t('project_management.delete_note_confirm_title')}
                centered
            >
                <Text size="sm">{t('project_management.delete_note_confirm_content')}</Text>
                <Group justify="flex-end" mt="md">
                    <Button variant="default" onClick={() => setDeleteModalOpen(false)}>
                        {t('button_cancel')}
                    </Button>
                    <Button color="red" onClick={confirmDeleteNote}>
                        {t('project_management.delete_note')}
                    </Button>
                </Group>
            </Modal>
        </div >
    );
};


export default ProjectOverview;
