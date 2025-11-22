import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { useTranslation } from 'react-i18next';
import {
    Select, Input, Title, Button, Modal, Badge, Group, LoadingOverlay, Tooltip, Switch, Text, Paper, ScrollArea, Table, TextInput, NavLink, Stack, ActionIcon, Textarea
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { IconPlus, IconTrash, IconDots, IconFolder, IconFileText, IconX, IconSparkles } from '@tabler/icons-react';
import {
    useReactTable,
    getCoreRowModel,
    flexRender,
    getFilteredRowModel,
} from '@tanstack/react-table';
import axios from 'axios';
import { useSidebar } from '../context/SidebarContext';
import styles from './GlossaryManager.module.css';


const GlossaryManagerPage = () => {
    const { t } = useTranslation();
    const form = useForm({
        initialValues: {
            source: '',
            translation: '',
            notes: '',
            variants: [],
            abbreviations: [],
            metadata: '',
        },
        validate: {
            source: (value) => (value.trim().length > 0 ? null : 'Source text is required'),
            translation: (value) => (value.trim().length > 0 ? null : 'Translation is required'),
        },
    });

    const newFileForm = useForm({
        initialValues: { fileName: '' },
        validate: {
            fileName: (value) => {
                if (!value) return t('glossary_filename_required');
                if (!/^[a-zA-Z0-9_]+\.json$/.test(value)) {
                    return t('glossary_filename_invalid');
                }
                return null;
            }
        }
    });

    // --- State ---
    const [treeData, setTreeData] = useState([]);
    const [data, setData] = useState([]);
    const [selectedGame, setSelectedGame] = useState(null);
    const [selectedFile, setSelectedFile] = useState({ key: null, title: t('glossary_no_file_selected'), gameId: null, glossaryId: null });
    const [targetLanguages, setTargetLanguages] = useState([]);
    const [selectedTargetLang, setSelectedTargetLang] = useState('');
    const [searchScope, setSearchScope] = useState('file');
    const [filtering, setFiltering] = useState('');
    const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 25 });
    const [rowCount, setRowCount] = useState(0);
    const [isModalVisible, setIsModalVisible] = useState(false);
    const [editingEntry, setEditingEntry] = useState(null);
    const [isLoadingTree, setIsLoadingTree] = useState(true);
    const [isLoadingContent, setIsLoadingContent] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [isFileCreateModalVisible, setIsFileCreateModalVisible] = useState(false);
    const [isAdvancedMode, setIsAdvancedMode] = useState(false);
    const [isDeleteModalVisible, setIsDeleteModalVisible] = useState(false);
    const [deletingItemId, setDeletingItemId] = useState(null);
    const [jsonError, setJsonError] = useState(null);
    const [selectedTerm, setSelectedTerm] = useState(null);

    const showDeleteModal = (id) => {
        setDeletingItemId(id);
        setIsDeleteModalVisible(true);
    };

    // --- Data Fetching & Handlers ---
    useEffect(() => {
        const fetchInitialConfigs = async () => {
            setIsLoadingTree(true);
            try {
                const [treeResponse, configResponse] = await Promise.all([
                    axios.get('/api/glossary/tree'),
                    axios.get('/api/config')
                ]);
                setTreeData(treeResponse.data);
                if (treeResponse.data.length > 0 && !selectedGame) {
                    setSelectedGame(treeResponse.data[0].key);
                }
                const languages = Object.values(configResponse.data.languages);
                setTargetLanguages(languages);
                if (languages.length > 0 && !selectedTargetLang) {
                    setSelectedTargetLang(languages.find(l => l.code === 'zh-CN')?.code || languages[0].code);
                }
            } catch (error) {
                notifications.show({ title: 'Error', message: 'Failed to load initial configuration.', color: 'red' });
            } finally {
                setIsLoadingTree(false);
            }
        };
        fetchInitialConfigs();
    }, []);

    useEffect(() => {
        const fetchGlossaryContent = async () => {
            const { pageIndex, pageSize } = pagination;
            setIsLoadingContent(true);
            try {
                let response;
                if (searchScope === 'file' && !filtering) {
                    if (!selectedFile.glossaryId) {
                        setData([]); setRowCount(0); setIsLoadingContent(false); return;
                    }
                    response = await axios.get(`/api/glossary/content?glossary_id=${selectedFile.glossaryId}&page=${pageIndex + 1}&pageSize=${pageSize}`);
                } else {
                    const payload = {
                        scope: searchScope, query: filtering, page: pageIndex + 1, pageSize: pageSize,
                        game_id: searchScope === 'game' ? (selectedFile.gameId || selectedGame) : null,
                        file_name: searchScope === 'file' ? selectedFile.key : null,
                    };
                    if ((payload.scope === 'file' && !payload.file_name) || (payload.scope === 'game' && !payload.game_id)) {
                        setData([]); setRowCount(0); setIsLoadingContent(false); return;
                    }
                    response = await axios.post('/api/glossary/search', payload);
                }
                setData(response.data.entries);
                setRowCount(response.data.totalCount);
            } catch (error) {
                notifications.show({ title: 'Error', message: 'Failed to load content.', color: 'red' });
                setData([]); setRowCount(0);
            } finally {
                setIsLoadingContent(false);
            }
        };
        fetchGlossaryContent();
    }, [selectedFile, pagination, filtering, searchScope]);

    const { setSidebarWidth } = useSidebar();

    const handleRowClick = (entry) => {
        setSelectedTerm(entry);
        setEditingEntry(entry);
        setSidebarWidth(450);
        
        const variantsArray = entry.variants ? Object.entries(entry.variants).map(([lang, values]) => ({ lang, value: values.join(', ') })) : [];
        const abbreviationsArray = entry.abbreviations ? Object.entries(entry.abbreviations).map(([lang, value]) => ({ lang, value })) : [];

        form.setValues({
            source: entry.source,
            translation: entry.translations[selectedTargetLang] || '',
            notes: entry.notes,
            variants: variantsArray,
            abbreviations: abbreviationsArray,
            metadata: JSON.stringify(entry.metadata || {}, null, 2),
        });
        setJsonError(null);
    };

    const handleClosePanel = () => {
        setSelectedTerm(null);
        setEditingEntry(null);
        setSidebarWidth(300);
    };

    const saveData = async (values) => {
        if (!selectedFile.glossaryId) return;
        if (jsonError) {
            notifications.show({ title: 'Error', message: t('glossary_editor.error_invalid_json'), color: 'red' });
            return;
        }
        try {
            JSON.parse(values.metadata);
        } catch (e) {
            notifications.show({ title: 'Error', message: t('glossary_editor.error_invalid_json'), color: 'red' });
            setJsonError(t('glossary_editor.error_invalid_json'));
            return;
        }
        setIsSaving(true);
        try {
            const { source, translation, notes, variants, abbreviations, metadata } = values;

            const variantsObject = variants.reduce((acc, item) => {
                if (item.lang && item.value) {
                    acc[item.lang] = item.value.split(',').map(s => s.trim()).filter(Boolean);
                }
                return acc;
            }, {});
            const abbreviationsObject = abbreviations.reduce((acc, item) => {
                if (item.lang && item.value) {
                    acc[item.lang] = item.value;
                }
                return acc;
            }, {});

            const payload = {
                source, notes, 
                variants: variantsObject,
                abbreviations: abbreviationsObject,
                metadata: JSON.parse(metadata),
                translations: { ...editingEntry?.translations, [selectedTargetLang]: translation },
                id: editingEntry?.id
            };

            if (editingEntry) {
                await axios.put(`/api/glossary/entry/${editingEntry.id}`, payload);
            } else {
                await axios.post(`/api/glossary/entry?glossary_id=${selectedFile.glossaryId}`, payload);
            }
            notifications.show({ title: 'Success', message: 'Glossary saved successfully!', color: 'green' });
            setIsModalVisible(false);
            fetchGlossaryContent();
        } catch (error) {
            notifications.show({ title: 'Error', message: 'Failed to save glossary.', color: 'red' });
        } finally {
            setIsSaving(false);
        }
    };

    const handleDelete = async (id) => {
        setIsSaving(true);
        try {
            await axios.delete(`/api/glossary/entry/${id}`);
            notifications.show({ title: 'Success', message: 'Entry deleted successfully!', color: 'green' });
            const newTotalCount = rowCount - 1;
            const newPageCount = Math.ceil(newTotalCount / pagination.pageSize);
            if (pagination.pageIndex >= newPageCount && newPageCount > 0) {
                setPagination(prev => ({ ...prev, pageIndex: newPageCount - 1 }));
            } else {
                fetchGlossaryContent();
            }
            if (selectedTerm && selectedTerm.id === id) {
                setSelectedTerm(null);
            }
        } catch (error) {
            notifications.show({ title: 'Error', message: 'Failed to delete entry.', color: 'red' });
        } finally {
            setIsSaving(false);
        }
    };

    const onSelectTree = (key, info) => {
        if (info.isLeaf) {
            const [gameId, glossaryId, fileName] = key.split('|');
            setSelectedFile({ key, title: fileName, gameId, glossaryId: parseInt(glossaryId, 10) });
            setSearchScope('file');
            setFiltering('');
            setPagination({ pageIndex: 0, pageSize: 25 });
            setSelectedTerm(null);
        } else {
            setSelectedGame(key);
        }
    };

    const handleDeleteConfirm = async () => {
        setIsSaving(true);
        try {
            await handleDelete(deletingItemId);
            setIsDeleteModalVisible(false);
            setDeletingItemId(null);
        } finally {
            setIsSaving(false);
        }
    };

    const handleDeleteCancel = () => {
        setIsDeleteModalVisible(false);
        setDeletingItemId(null);
    };

    const columns = [
        { accessorKey: 'source', header: () => <Text fw={700}>{t('glossary_source_text')}</Text>, cell: info => <Text>{info.getValue()}</Text> },
        { id: 'translation', header: () => <Text fw={700}>{t('glossary_translation')}</Text>, cell: ({ row }) => <Text>{row.original.translations[selectedTargetLang] || ''}</Text> },
        { accessorKey: 'notes', header: () => <Text fw={700}>{t('glossary_notes')}</Text>, cell: ({ row }) => (row.original.notes ? <Tooltip label={t('glossary_view_edit_notes')}><IconDots size={14} /></Tooltip> : null) },
        { id: 'actions', header: () => <Text fw={700}>{t('glossary_actions')}</Text>, cell: ({ row }) => (<Group gap="xs" onClick={(e) => e.stopPropagation()}><ActionIcon color="red" onClick={() => showDeleteModal(row.original.id)}><IconTrash size={14} /></ActionIcon></Group>) },
    ];

    const table = useReactTable({
        data, columns, getCoreRowModel: getCoreRowModel(), getFilteredRowModel: getFilteredRowModel(), manualPagination: true, manualFiltering: true, pageCount: Math.ceil(rowCount / pagination.pageSize),
        state: { globalFilter: filtering, pagination },
        onPaginationChange: setPagination, onGlobalFilterChange: setFiltering,
    });

    const FileTree = ({ nodes, onSelect, selectedKey }) => (
        <>
            {nodes.map(node => node.isLeaf ? (
                <NavLink key={node.key} label={node.title} leftSection={<IconFileText size="1rem" />} active={node.key === selectedKey} onClick={() => onSelect(node.key, node)} variant="light" />
            ) : (
                <NavLink key={node.key} label={node.title} leftSection={<IconFolder size="1rem" />} childrenOffset={28} defaultOpened>
                    {node.children && <FileTree nodes={node.children} onSelect={onSelect} selectedKey={selectedKey} />}
                </NavLink>
            ))}
        </>
    );

    const DynamicListEditor = ({ field, label, description }) => {
        const items = form.values[field] || [];
        return (
            <Stack>
                <Text size="sm" fw={500}>{label}</Text>
                {description && <Text size="xs" c="dimmed" mt={-10} mb={5}>{description}</Text>}
                {items.map((item, index) => (
                    <Group key={index} wrap="nowrap">
                        <Select
                            data={targetLanguages.map(l => ({ value: l.code, label: l.name_local || l.code }))}
                            value={item.lang}
                            onChange={(value) => form.setFieldValue(`${field}.${index}.lang`, value)}
                            placeholder={t('glossary_editor.language')}
                            style={{ width: 120 }}
                        />
                        <TextInput
                            placeholder={t('glossary_editor.value')}
                            value={item.value}
                            onChange={(event) => form.setFieldValue(`${field}.${index}.value`, event.currentTarget.value)}
                            style={{ flex: 1 }}
                        />
                        <ActionIcon color="red" onClick={() => form.removeListItem(field, index)}>
                            <IconTrash size={16} />
                        </ActionIcon>
                    </Group>
                ))}
                <Button
                    leftSection={<IconPlus size={14} />}
                    variant="light"
                    fullWidth
                    onClick={() => form.insertListItem(field, { lang: '', value: '' })}
                >
                    {t('glossary_editor.add')}
                </Button>
            </Stack>
        );
    };

    return (
        <div className={styles.pageContainer}>
            <LoadingOverlay visible={isSaving} />
            <div className={styles.columnsWrapper}>
                <div className={styles.leftPanel}>
                    <Paper p="md" className={styles.sidebarCard}>
                        <LoadingOverlay visible={isLoadingTree} />
                        <Title order={4}>{t('glossary_manager_title')}</Title>
                        <Stack gap="sm" mb="md" mt="md">
                            <Select label={t('glossary_game')} data={treeData.map(g => ({ value: g.key, label: g.title || g.key }))} value={selectedGame} onChange={setSelectedGame} />
                            <Select label={t('glossary_target_language')} data={targetLanguages.map(l => ({ value: l.code, label: l.name_local || l.code }))} value={selectedTargetLang} onChange={setSelectedTargetLang} />
                        </Stack>
                        <Group justify="space-between" mb="xs">
                            <Text size="sm" fw={500}>{t('glossary_files')}</Text>
                            <Tooltip label={t('glossary_create_new_file')}><Button size="xs" variant="light" onClick={() => setIsFileCreateModalVisible(true)} disabled={!selectedGame}><IconPlus size={14} /></Button></Tooltip>
                        </Group>
                        <ScrollArea style={{ flex: 1, minHeight: 0 }}>
                            {selectedGame && <FileTree nodes={treeData.find(n => n.key === selectedGame)?.children || []} onSelect={onSelectTree} selectedKey={selectedFile.key} />}
                        </ScrollArea>
                    </Paper>
                </div>
                <div className={styles.mainPanel}>
                    <Paper p="md" className={styles.contentCard}>
                        <LoadingOverlay visible={isLoadingContent} />
                        <Group justify="space-between" mb="md">
                            <Title order={4}>{selectedFile.title !== t('glossary_no_file_selected') ? selectedFile.title : t('glossary_select_file_prompt')}</Title>
                            <Button leftSection={<IconPlus size={16} />} onClick={() => setIsModalVisible(true)} disabled={!selectedFile.key}>{t('glossary_add_entry')}</Button>
                        </Group>
                        <Group mb="md" gap="xs">
                            <Input placeholder={t('glossary_filter_placeholder')} value={filtering} onChange={e => { setFiltering(e.currentTarget.value); setPagination(p => ({ ...p, pageIndex: 0 })); }} style={{ flex: 1 }} />
                            <Select value={searchScope} onChange={(val) => { setSearchScope(val); setPagination(p => ({ ...p, pageIndex: 0 })); }}
                                data={[{ value: 'file', label: t('search_scope_file') }, { value: 'game', label: t('search_scope_game') }, { value: 'all', label: t('search_scope_all') }]}
                                style={{ width: 160 }} allowDeselect={false} />
                        </Group>
                        <ScrollArea style={{ flex: 1, minHeight: 0 }}>
                            <Table striped highlightOnHover withTableBorder>
                                <Table.Thead>
                                    {table.getHeaderGroups().map(hg => (<Table.Tr key={hg.id}>{hg.headers.map(header => <Table.Th key={header.id}>{flexRender(header.column.columnDef.header, header.getContext())}</Table.Th>)}</Table.Tr>))}
                                </Table.Thead>
                                <Table.Tbody>
                                    {table.getRowModel().rows.length > 0 ? table.getRowModel().rows.map(row => (
                                        <Table.Tr key={row.id} onClick={() => handleRowClick(row.original)} className={selectedTerm && selectedTerm.id === row.original.id ? styles.selectedRow : ''}>
                                            {row.getVisibleCells().map(cell => <Table.Td key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</Table.Td>)}
                                        </Table.Tr>
                                    )) : (
                                        <Table.Tr><Table.Td colSpan={columns.length} style={{ textAlign: 'center', padding: '20px' }}><Text c="dimmed">{t('glossary_no_entries')}</Text></Table.Td></Table.Tr>
                                    )}
                                </Table.Tbody>
                            </Table>
                        </ScrollArea>
                        <Group justify="space-between" mt="md">
                            <Group>
                                <Select style={{ width: 120 }} value={String(table.getState().pagination.pageSize)} onChange={value => table.setPageSize(Number(value))} data={['25', '50', '100'].map(size => ({ value: size, label: t('glossary_show_entries', { count: size }) }))} />
                                <Text size="sm" c="dimmed">{t('glossary_page_info', { page: table.getState().pagination.pageIndex + 1, total: table.getPageCount() })}</Text>
                            </Group>
                            <Button.Group>
                                <Button variant="default" onClick={() => table.previousPage()} disabled={!table.getCanPreviousPage()}>{t('glossary_previous_page')}</Button>
                                <Button variant="default" onClick={() => table.nextPage()} disabled={!table.getCanNextPage()}>{t('glossary_next_page')}</Button>
                            </Button.Group>
                        </Group>
                    </Paper>
                </div>
            </div>

            {selectedTerm && document.getElementById('glossary-detail-portal') && createPortal(
                <Stack gap="md" style={{ height: '100%' }}>
                    <Group justify="space-between">
                        <Title order={5}>{t('glossary_edit_entry')}</Title>
                        <ActionIcon variant="subtle" onClick={handleClosePanel}><IconX size={16} /></ActionIcon>
                    </Group>
                    <form onSubmit={form.onSubmit(saveData)} style={{ display: 'flex', flexDirection: 'column', flex: 1, minHeight: 0 }}>
                        <ScrollArea style={{ flex: 1 }}>
                            <Stack p="xs" gap="md">
                                <TextInput label={t('glossary_source_text')} required {...form.getInputProps('source')} />
                                <TextInput label={`${t('glossary_translation')} (${targetLanguages.find(l => l.code === selectedTargetLang)?.name_local || selectedTargetLang})`} required {...form.getInputProps('translation')} />
                                <Textarea label={t('glossary_notes')} autosize minRows={3} {...form.getInputProps('notes')} />
                                
                                <Switch
                                    label={t('glossary_advanced_mode')}
                                    checked={isAdvancedMode}
                                    onChange={(event) => setIsAdvancedMode(event.currentTarget.checked)}
                                />

                                {isAdvancedMode && (
                                    <>
                                        <DynamicListEditor field="variants" label={t('glossary_variants')} description={t('glossary_editor.variants_desc')} />
                                        <DynamicListEditor field="abbreviations" label={t('glossary_abbreviations')} description={t('glossary_editor.abbreviations_desc')} />
                                        
                                        <Textarea
                                            label={t('glossary_editor.metadata_label')}
                                            placeholder='{ "key": "value" }'
                                            autosize
                                            minRows={4}
                                            {...form.getInputProps('metadata')}
                                            error={jsonError}
                                            styles={{ input: { fontFamily: 'monospace' } }}
                                            onChange={(event) => {
                                                const val = event.currentTarget.value;
                                                form.setFieldValue('metadata', val);
                                                try {
                                                    JSON.parse(val);
                                                    setJsonError(null);
                                                } catch (e) {
                                                    setJsonError(t('glossary_editor.error_invalid_json'));
                                                }
                                            }}
                                        />
                                    </>
                                )}
                            </Stack>
                        </ScrollArea>
                        <Paper withBorder p="sm" mt="md" radius="md" style={{ flexShrink: 0 }}>
                            <Group justify="flex-end">
                                <Button variant="default" onClick={handleClosePanel}>{t('button_cancel')}</Button>
                                <Button type="submit" loading={isSaving}>{t('button_save')}</Button>
                            </Group>
                        </Paper>
                    </form>
                </Stack>,
                document.getElementById('glossary-detail-portal')
            )}
        </div>
    );
};

export default GlossaryManagerPage;
