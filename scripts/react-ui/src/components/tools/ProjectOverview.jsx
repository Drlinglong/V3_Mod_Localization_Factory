import React, { useState, useEffect } from 'react';
import { Title, Text, Grid, Card, Table, Badge, Button, Paper, Group, Modal, TextInput, ActionIcon, Stack, Textarea, Tooltip } from '@mantine/core';
import { IconCheck, IconX, IconClock, IconPlayerPlay, IconArrowLeft, IconArrowRight, IconEdit, IconPlus, IconTrash, IconFolder, IconArchive, IconRestore } from '@tabler/icons-react';
import { useTranslation } from 'react-i18next';
import { open } from '@tauri-apps/plugin-dialog';
import axios from 'axios';
import styles from '../../pages/ProjectManagement.module.css';

const ProjectOverview = ({ projectDetails, handleStatusChange, handleNotesChange, handleProofread, onPathsUpdated, onDeleteForever }) => {
    const { t } = useTranslation();
    const [managePathsOpen, setManagePathsOpen] = useState(false);
    const [translationDirs, setTranslationDirs] = useState([]);
    const [newDirPath, setNewDirPath] = useState('');
    const [notes, setNotes] = useState(projectDetails?.notes || '');

    // Update local notes state when projectDetails changes
    useEffect(() => {
        if (projectDetails) {
            setNotes(projectDetails.notes || '');
        }
    }, [projectDetails]);

    if (!projectDetails) return null;

    const onSaveNotes = () => {
        if (handleNotesChange) {
            handleNotesChange(notes);
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
            const response = await axios.post(`http://localhost:8000/api/project/${projectDetails.project_id}/config`, {
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

    const rows = projectDetails.files.map((file) => {
        let color = 'gray';
        let text = '未处理';
        let Icon = IconClock;

        if (file.status === 'translated' || file.status === 'done') { color = 'green'; text = '已翻译'; Icon = IconCheck; }
        else if (file.status === 'failed') { color = 'red'; text = '翻译失败'; Icon = IconX; }
        else if (file.status === 'pending' || file.status === 'todo') { color = 'blue'; text = '待处理'; Icon = IconClock; }
        else if (file.status === 'in_progress') { color = 'yellow'; text = '进行中'; Icon = IconPlayerPlay; }
        else if (file.status === 'proofreading') { color = 'orange'; text = '校对中'; Icon = IconEdit; }

        return (
            <Table.Tr key={file.key}>
                <Table.Td>
                    <Text fw={500} truncate title={file.name}>{file.name}</Text>
                </Table.Td>
                <Table.Td>
                    <Badge variant="dot" color={file.file_type === 'source' ? 'blue' : 'violet'}>
                        {file.file_type === 'source' ? '源文件' : '翻译'}
                    </Badge>
                </Table.Td>
                <Table.Td>{file.lines}</Table.Td>
                <Table.Td>
                    <Badge color={color} variant="light" leftSection={<Icon size={12} />}>
                        {text}
                    </Badge>
                </Table.Td>
                <Table.Td>{file.progress}</Table.Td>
                <Table.Td>
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
        <div style={{ position: 'relative', height: '100%', width: '100%' }}>
            {/* Fixed header section with stats and paths */}
            <div style={{ position: 'absolute', top: 0, left: 0, right: 0, paddingBottom: '1rem' }}>
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
                        <Button variant="outline" size="xs" onClick={onSaveNotes}>Save Notes</Button>
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
                        <Button variant="outline" size="xs" onClick={handleOpenManagePaths}>Manage Paths</Button>
                    </Group>
                </Paper>
            </div>

            {/* Scrollable file list - positioned below header */}
            <div style={{ position: 'absolute', top: '380px', bottom: 0, left: 0, right: 0, overflowY: 'auto', overflowX: 'hidden' }}>
                <Paper withBorder p="md" radius="md" className={styles.glassCard}>
                    <Group position="apart" mb="md">
                        <Title order={4}>文件详情列表 ({projectDetails.files.length} 个文件)</Title>
                    </Group>
                    <Table verticalSpacing="sm" className={styles.table} stickyHeader>
                        <Table.Thead style={{ position: 'sticky', top: 0, backgroundColor: 'var(--glass-bg)', zIndex: 1 }}>
                            <Table.Tr>
                                <Table.Th>文件名</Table.Th>
                                <Table.Th>类型</Table.Th>
                                <Table.Th>行数</Table.Th>
                                <Table.Th>状态</Table.Th>
                                <Table.Th>进度</Table.Th>
                                <Table.Th>操作</Table.Th>
                            </Table.Tr>
                        </Table.Thead>
                        <Table.Tbody>{rows}</Table.Tbody>
                    </Table>
                </Paper>
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
        </div>
    );
};

export default ProjectOverview;
