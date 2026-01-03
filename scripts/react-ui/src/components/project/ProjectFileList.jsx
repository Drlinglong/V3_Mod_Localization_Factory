import React from 'react';
import { Paper, Group, Title, Table, Tooltip, Text, Badge, Button } from '@mantine/core';
import { IconClock, IconCheck, IconX, IconPlayerPlay, IconEdit } from '@tabler/icons-react';
import { useTranslation } from 'react-i18next';
import styles from '../../pages/ProjectManagement.module.css';

const ProjectFileList = ({ projectDetails, handleProofread }) => {
    const { t } = useTranslation();

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
        let text = t('project_management.file_status.todo');
        let Icon = IconClock;

        if (file.status === 'translated' || file.status === 'done') { color = 'green'; text = t('project_management.file_status.done'); Icon = IconCheck; }
        else if (file.status === 'failed') { color = 'red'; text = t('project_management.file_status.failed'); Icon = IconX; }
        else if (file.status === 'pending' || file.status === 'todo') { color = 'blue'; text = t('project_management.file_status.todo'); Icon = IconClock; }
        else if (file.status === 'in_progress') { color = 'yellow'; text = t('project_management.file_status.in_progress'); Icon = IconPlayerPlay; }
        else if (file.status === 'proofreading') { color = 'orange'; text = t('project_management.file_status.proofreading'); Icon = IconEdit; }

        const relativePath = getRelativePath(file.name);

        return (
            <Table.Tr key={file.key}>
                <Table.Td style={{ maxWidth: '300px' }}>
                    <Tooltip label={relativePath} openDelay={500}>
                        <Text fw={500} truncate>{relativePath.split('/').pop().split('\\').pop()}</Text>
                    </Tooltip>
                </Table.Td>
                <Table.Td style={{ width: '100px' }}>
                    <Badge variant="dot" color={file.file_type === 'source' ? 'blue' : 'violet'}>
                        {file.file_type === 'source' ? t('project_management.file_type.source') : t('project_management.file_type.translation')}
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
                            <Button
                                variant="subtle"
                                size="xs"
                                key={action}
                                onClick={() => {
                                    if (action === 'Proofread') handleProofread(file);
                                }}
                            >
                                {t('proofreading.proofread')}
                            </Button>
                        ))}
                    </Group>
                </Table.Td>
            </Table.Tr>
        );
    });

    return (
        <div style={{ flex: 1, position: 'relative', minHeight: 0 }}>
            <div style={{ position: 'absolute', top: 0, bottom: 0, left: 0, right: 0, overflowY: 'auto', overflowX: 'hidden' }}>
                <Paper withBorder p="md" radius="md" className={styles.glassCard}>
                    <Group position="apart" mb="md">
                        <Title order={4}>{t('project_management.file_list_title', { count: projectDetails.files.length })}</Title>
                    </Group>
                    <Table verticalSpacing="sm" className={styles.table} stickyHeader>
                        <Table.Thead style={{ position: 'sticky', top: 0, backgroundColor: 'var(--glass-bg)', zIndex: 1 }}>
                            <Table.Tr>
                                <Table.Th>{t('project_management.file_list.table.name')}</Table.Th>
                                <Table.Th style={{ width: '100px' }}>{t('project_management.file_list.table.type')}</Table.Th>
                                <Table.Th style={{ width: '80px' }}>{t('project_management.file_list.table.lines')}</Table.Th>
                                <Table.Th style={{ width: '120px' }}>{t('project_management.file_list.table.status')}</Table.Th>
                                <Table.Th style={{ width: '80px' }}>{t('project_management.file_list.table.progress')}</Table.Th>
                                <Table.Th style={{ width: '120px' }}>{t('project_management.file_list.table.actions')}</Table.Th>
                            </Table.Tr>
                        </Table.Thead>
                        <Table.Tbody>{rows}</Table.Tbody>
                    </Table>
                </Paper>
            </div>
        </div>
    );
};

export default ProjectFileList;
