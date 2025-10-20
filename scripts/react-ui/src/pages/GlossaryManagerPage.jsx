import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
    Grid, Select, Input, Title, Button, Modal, Popover, Badge, Group, LoadingOverlay, Tooltip, Switch, Text, Paper, ScrollArea, Table, TextInput
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { IconPlus, IconEdit, IconTrash, IconDots } from '@tabler/icons-react';
import {
    useReactTable,
    getCoreRowModel,
    flexRender,
    getFilteredRowModel,
} from '@tanstack/react-table';
import axios from 'axios';


const GlossaryManagerPage = () => {
    const { t } = useTranslation();
    const form = useForm({
        initialValues: {
            source: '',
            translation: '',
            notes: '',
            variants: '',
            abbreviations: '',
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
                if (!value) return t('glossary_filename_required', 'Please enter a file name.');
                if (!/^[a-zA-Z0-9_]+\.json$/.test(value)) {
                    return t('glossary_filename_invalid', 'Must be a valid name ending in .json (e.g., my_glossary.json)');
                }
                return null;
            }
        }
    });

    // --- State ---
    const [treeData, setTreeData] = useState([]);
    const [data, setData] = useState([]); // This will hold the data for the current page
    const [selectedGame, setSelectedGame] = useState(null);
    const [selectedFile, setSelectedFile] = useState({ key: null, title: t('glossary_no_file_selected'), gameId: null });
    const [targetLanguages, setTargetLanguages] = useState([]);
    const [selectedTargetLang, setSelectedTargetLang] = useState('');

    // UI and Table State
    const [filtering, setFiltering] = useState('');
    const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 25 });
    const [rowCount, setRowCount] = useState(0); // Total number of rows from server
    const [isModalVisible, setIsModalVisible] = useState(false);
    const [editingEntry, setEditingEntry] = useState(null);
    const [isLoadingTree, setIsLoadingTree] = useState(true);
    const [isLoadingContent, setIsLoadingContent] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [isFileCreateModalVisible, setIsFileCreateModalVisible] = useState(false);
    const [isAdvancedMode, setIsAdvancedMode] = useState(false);

    const [isDeleteModalVisible, setIsDeleteModalVisible] = useState(false);
    const [deletingItemId, setDeletingItemId] = useState(null);

    const showDeleteModal = (id) => {
        setDeletingItemId(id);
        setIsDeleteModalVisible(true);
    };

    // --- Data Fetching ---
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
                // Default to Chinese if available, otherwise the first language in the list
                setSelectedTargetLang(languages.find(l => l.code === 'zh-CN')?.code || languages[0].code);
            }
        } catch (error) {
            notifications.show({ title: 'Error', message: 'Failed to load initial configuration.', color: 'red' });
            console.error('Fetch initial config error:', error);
        } finally {
            setIsLoadingTree(false);
        }
    };

    useEffect(() => {
        fetchInitialConfigs();
    }, []);

    const fetchGlossaryContent = async () => {
        if (!selectedFile.key) return;
        const { gameId, title } = selectedFile;
        const { pageIndex, pageSize } = pagination;

        setIsLoadingContent(true);
        try {
            const response = await axios.get(
                `/api/glossary/content?game_id=${gameId}&file_name=${title}&page=${pageIndex + 1}&pageSize=${pageSize}&filter=${filtering}`
            );
            setData(response.data.entries);
            setRowCount(response.data.totalCount);
        } catch (error) {
            notifications.show({ title: 'Error', message: `Failed to load content for ${title}.`, color: 'red' });
            console.error('Fetch content error:', error);
            setData([]);
            setRowCount(0);
        } finally {
            setIsLoadingContent(false);
        }
    };

    // Effect to fetch content when file or pagination changes
    useEffect(() => {
        fetchGlossaryContent();
    }, [selectedFile, pagination, filtering]);


    // --- Handlers ---
    const handleAdd = () => {
        setEditingEntry(null);
        form.reset();
        setIsModalVisible(true);
    };

    const handleEdit = (entry) => {
        setEditingEntry(entry);
        form.setValues({
            source: entry.source,
            translation: entry.translations[selectedTargetLang] || '',
            notes: entry.notes,
            variants: entry.variants ? JSON.stringify(entry.variants, null, 2) : '',
            abbreviations: entry.abbreviations ? JSON.stringify(entry.abbreviations, null, 2) : '',
            metadata: entry.metadata ? JSON.stringify(entry.metadata, null, 2) : '',
        });
        setIsModalVisible(true);
    };

    const saveData = async (values) => {
        if (!selectedFile.gameId || !selectedFile.title) return;

        setIsSaving(true);
        try {
            const { source, translation, notes, variants, abbreviations, metadata } = values;

            let parsedVariants = {};
            try {
                parsedVariants = variants ? JSON.parse(variants) : {};
            } catch (e) {
                notifications.show({ title: 'Error', message: 'Variants JSON is invalid.', color: 'red' });
                setIsSaving(false); return;
            }

            let parsedAbbreviations = {};
            try {
                parsedAbbreviations = abbreviations ? JSON.parse(abbreviations) : {};
            } catch (e) {
                notifications.show({ title: 'Error', message: 'Abbreviations JSON is invalid.', color: 'red' });
                setIsSaving(false); return;
            }

            let parsedMetadata = {};
            try {
                parsedMetadata = metadata ? JSON.parse(metadata) : {};
            } catch (e) {
                notifications.show({ title: 'Error', message: 'Metadata JSON is invalid.', color: 'red' });
                setIsSaving(false); return;
            }

            if (editingEntry) {
                const payload = { ...editingEntry, source, notes, variants: parsedVariants, abbreviations: parsedAbbreviations, metadata: parsedMetadata, translations: { ...editingEntry.translations, [selectedTargetLang]: translation }, };
                await axios.put(`/api/glossary/entry/${editingEntry.id}?game_id=${selectedFile.gameId}&file_name=${selectedFile.title}`, payload);
            } else {
                const payload = { source, notes, variants: parsedVariants, abbreviations: parsedAbbreviations, metadata: parsedMetadata, translations: { [selectedTargetLang]: translation }, };
                await axios.post(`/api/glossary/entry?game_id=${selectedFile.gameId}&file_name=${selectedFile.title}`, payload);
            }

            notifications.show({ title: 'Success', message: 'Glossary saved successfully!', color: 'green' });
            setIsModalVisible(false);
            fetchGlossaryContent();
        } catch (error) {
            notifications.show({ title: 'Error', message: 'Failed to save glossary.', color: 'red' });
            console.error('Save error:', error);
        } finally {
            setIsSaving(false);
        }
    };


    const handleDelete = async (id) => {
        setIsSaving(true);
        try {
            await axios.delete(`/api/glossary/entry/${id}?game_id=${selectedFile.gameId}&file_name=${selectedFile.title}`);
            notifications.show({ title: 'Success', message: 'Entry deleted successfully!', color: 'green' });

            const newTotalCount = rowCount - 1;
            const newPageCount = Math.ceil(newTotalCount / pagination.pageSize);
            if (pagination.pageIndex >= newPageCount && newPageCount > 0) {
                setPagination(prev => ({ ...prev, pageIndex: newPageCount - 1 }));
            } else {
                fetchGlossaryContent();
            }
        } catch (error) {
            notifications.show({ title: 'Error', message: 'Failed to delete entry.', color: 'red' });
            console.error('Delete error:', error);
        } finally {
            setIsSaving(false);
        }
    };

    const onSelectTree = (selectedKeys, info) => {
        if (info.isLeaf) {
            const [gameId, fileName] = info.key.split('|');
            setSelectedFile({ key: info.key, title: fileName, gameId: gameId });
            setFiltering('');
            setPagination({ pageIndex: 0, pageSize: 25 }); // Reset pagination, which triggers useEffect to fetch data.
        }
    };

    const handleDeleteConfirm = async () => {
        setIsSaving(true); // Set loading state
        try {
            await handleDelete(deletingItemId); // Call your original delete logic
            setIsDeleteModalVisible(false);
            setDeletingItemId(null);
        } finally {
            setIsSaving(false); // Reset loading state
        }
    };

    const handleDeleteCancel = () => {
        setIsDeleteModalVisible(false);
        setDeletingItemId(null);
    };

    // --- Table Definition ---
    const columns = [
        { accessorKey: 'source', header: () => t('glossary_source_text'), cell: info => info.getValue() },
        { id: 'translation', header: () => t('glossary_translation'), cell: ({ row }) => row.original.translations[selectedTargetLang] || '' },
        { accessorKey: 'notes', header: () => t('glossary_notes'), cell: ({ row }) => ( row.original.notes ? ( <Tooltip label={t('glossary_view_edit_notes', 'View/Edit Notes')}><Button size="xs" variant="subtle" onClick={() => handleEdit(row.original)}><IconDots size={14} /></Button></Tooltip>) : null ) },
        { accessorKey: 'variants', header: () => t('glossary_variants'), cell: info => <Group gap="xs">{Array.isArray(info.getValue()) ? info.getValue().map(v => <Badge key={v}>{v}</Badge>) : null}</Group> },
        { id: 'actions', header: () => t('glossary_actions'), cell: ({ row }) => (
            <Group gap="xs">
                <Button size="xs" variant="light" onClick={() => handleEdit(row.original)}><IconEdit size={14} /></Button>
                <Button size="xs" variant="light" color="red" onClick={() => showDeleteModal(row.original.id)}><IconTrash size={14} /></Button>
            </Group>
        )},
    ];


    const table = useReactTable({
        data,
        columns,
        getCoreRowModel: getCoreRowModel(),
        getFilteredRowModel: getFilteredRowModel(),
        manualPagination: true,
        pageCount: Math.ceil(rowCount / pagination.pageSize),
        state: {
            globalFilter: filtering,
            pagination,
        },
        onPaginationChange: setPagination,
        onGlobalFilterChange: setFiltering,
    });

    // A simple recursive component to render the file tree
    const FileTree = ({ nodes, onSelect, selectedKey }) => (
        <div>
            {nodes.map(node => (
                <div key={node.key} style={{ paddingLeft: '20px' }}>
                    {node.isLeaf ? (
                        <a href="#" onClick={(e) => { e.preventDefault(); onSelect(node.key, node); }}
                           style={{
                               display: 'block', padding: '5px', borderRadius: '4px',
                               backgroundColor: node.key === selectedKey ? 'var(--mantine-color-blue-light)' : 'transparent',
                               color: node.key === selectedKey ? 'var(--mantine-color-blue-filled)' : 'inherit',
                               textDecoration: 'none'
                           }}>
                            {node.title}
                        </a>
                    ) : (
                        <div>
                            <Text fw={500}>{node.title}</Text>
                            {node.children && <FileTree nodes={node.children} onSelect={onSelect} selectedKey={selectedKey} />}
                        </div>
                    )}
                </div>
            ))}
        </div>
    );


    return (
        <div style={{ position: 'relative' }}>
            <LoadingOverlay visible={isSaving} />
            <Grid>
                <Grid.Col span={4}>
                     <Paper withBorder p="md" style={{ height: '100%' }}>
                        <LoadingOverlay visible={isLoadingTree} />
                        <ScrollArea style={{ height: 'calc(100vh - 120px)' }}>
                            <Group direction="column" grow>
                                <div>
                                    <Text size="sm" fw={500}>{t('glossary_game')}</Text>
                                    <Select data={treeData.map(g => ({ value: g.key, label: g.title || g.key }))} value={selectedGame} onChange={setSelectedGame} />
                                </div>
                                <div>
                                    <Text size="sm" fw={500}>{t('glossary_target_language')}</Text>
                                    <Select data={targetLanguages.map(l => ({ value: l.code, label: l.name_local || l.code }))} value={selectedTargetLang} onChange={setSelectedTargetLang} />
                                </div>
                                <div>
                                    <Group justify="space-between">
                                        <Text size="sm" fw={500}>{t('glossary_files')}</Text>
                                        <Button size="xs" variant="light" onClick={() => setIsFileCreateModalVisible(true)} disabled={!selectedGame}><IconPlus size={14} /></Button>
                                    </Group>
                                    {selectedGame && <FileTree nodes={treeData.find(n => n.key === selectedGame)?.children || []} onSelect={onSelectTree} selectedKey={selectedFile.key} />}
                                </div>
                            </Group>
                        </ScrollArea>
                     </Paper>
                </Grid.Col>
                <Grid.Col span={8}>
                     <Paper withBorder p="md" style={{ height: '100%', position: 'relative' }}>
                        <LoadingOverlay visible={isLoadingContent} />
                        <Group justify="space-between" mb="md">
                            <Title order={5}>{t('glossary_content')}: {selectedFile.title}</Title>
                            <Tooltip label={t('glossary_add_entry')}>
                                <Button onClick={handleAdd} disabled={!selectedFile.key}><IconPlus size={16} /></Button>
                            </Tooltip>
                        </Group>
                        <Input placeholder={t('glossary_filter_placeholder')} value={filtering} onChange={e => setFiltering(e.currentTarget.value)} style={{ marginBottom: 16 }} />

                        <ScrollArea style={{ height: 'calc(100vh - 300px)' }}>
                            <Table>
                                <Table.Thead>
                                    {table.getHeaderGroups().map(hg => (
                                        <Table.Tr key={hg.id}>{hg.headers.map(header => <Table.Th key={header.id}>{flexRender(header.column.columnDef.header, header.getContext())}</Table.Th>)}</Table.Tr>
                                    ))}
                                </Table.Thead>
                                <Table.Tbody>
                                    {table.getRowModel().rows.map(row => (
                                        <Table.Tr key={row.id}>{row.getVisibleCells().map(cell => <Table.Td key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</Table.Td>)}</Table.Tr>
                                    ))}
                                </Table.Tbody>
                            </Table>
                        </ScrollArea>

                        <Group justify="space-between" mt="md">
                            <Group>
                                <Select
                                    style={{ width: 120 }}
                                    value={String(table.getState().pagination.pageSize)}
                                    onChange={value => table.setPageSize(Number(value))}
                                    data={['25', '50', '100'].map(size => ({ value: size, label: t('glossary_show_entries', { count: size }) }))}
                                />
                                <Text size="sm">
                                    {t('glossary_page_info', { page: table.getState().pagination.pageIndex + 1, total: table.getPageCount() })}
                                </Text>
                            </Group>
                            <Button.Group>
                                <Button variant="default" onClick={() => table.previousPage()} disabled={!table.getCanPreviousPage()}>{t('glossary_previous_page')}</Button>
                                <Button variant="default" onClick={() => table.nextPage()} disabled={!table.getCanNextPage()}>{t('glossary_next_page')}</Button>
                            </Button.Group>
                        </Group>
                     </Paper>
                </Grid.Col>
            </Grid>

            <Modal title={editingEntry ? t('glossary_edit_entry') : t('glossary_add_entry')} opened={isModalVisible} onClose={() => { setIsModalVisible(false); setIsAdvancedMode(false); }}>
                <form onSubmit={form.onSubmit(saveData)}>
                    <TextInput label={t('glossary_source_text')} required {...form.getInputProps('source')} />
                    <TextInput label={`${t('glossary_translation')} (${targetLanguages.find(l=>l.code === selectedTargetLang)?.name_local || selectedTargetLang})`} required {...form.getInputProps('translation')} />
                    <Input.Wrapper label={t('glossary_notes')}><Input component="textarea" {...form.getInputProps('notes')} /></Input.Wrapper>

                    <Group justify="flex-end" my="md">
                        <Text size="sm">{t('glossary_advanced_mode', 'Advanced Mode')}</Text>
                        <Switch checked={isAdvancedMode} onChange={(event) => setIsAdvancedMode(event.currentTarget.checked)} />
                    </Group>

                    {isAdvancedMode && (
                        <>
                            <Input.Wrapper label={t('glossary_variants')} description={t('glossary_variants_tooltip_json')}>
                                <Input component="textarea" autosize minRows={3} {...form.getInputProps('variants')} />
                            </Input.Wrapper>
                             <Input.Wrapper label={t('glossary_abbreviations')} description={t('glossary_abbreviations_tooltip_json')}>
                                <Input component="textarea" autosize minRows={3} {...form.getInputProps('abbreviations')} />
                            </Input.Wrapper>
                             <Input.Wrapper label={t('glossary_metadata')} description={t('glossary_metadata_tooltip_json')}>
                                <Input component="textarea" autosize minRows={3} {...form.getInputProps('metadata')} />
                            </Input.Wrapper>
                        </>
                    )}
                    <Group justify="flex-end" mt="md">
                        <Button variant="default" onClick={() => { setIsModalVisible(false); setIsAdvancedMode(false); }}>{t('button_cancel')}</Button>
                        <Button type="submit" loading={isSaving}>{t('button_ok')}</Button>
                    </Group>
                </form>
            </Modal>

            <Modal title={t('glossary_create_new_file', 'Create New Glossary File')} opened={isFileCreateModalVisible} onClose={() => setIsFileCreateModalVisible(false)}>
                <form onSubmit={newFileForm.onSubmit(async (values) => {
                    try {
                        setIsSaving(true);
                        await axios.post('/api/glossary/file', { game_id: selectedGame, file_name: values.fileName });
                        notifications.show({ title: 'Success', message: `Successfully created ${values.fileName}`, color: 'green' });
                        setIsFileCreateModalVisible(false);
                        fetchInitialConfigs();
                    } catch (error) {
                        notifications.show({ title: 'Error', message: error.response?.data?.detail || 'Failed to create file.', color: 'red' });
                        console.error('Create file error:', error);
                    } finally {
                        setIsSaving(false);
                    }
                })}>
                    <TextInput label={t('glossary_file_name', 'File Name')} placeholder="e.g., my_new_glossary.json" required {...newFileForm.getInputProps('fileName')} />
                    <Group justify="flex-end" mt="md">
                        <Button variant="default" onClick={() => setIsFileCreateModalVisible(false)}>{t('button_cancel')}</Button>
                        <Button type="submit" loading={isSaving}>{t('button_ok')}</Button>
                    </Group>
                </form>
            </Modal>

            <Modal title={t('glossary_delete_confirm_title', 'Confirm Deletion')} opened={isDeleteModalVisible} onClose={handleDeleteCancel}>
                <Text>{t('glossary_delete_confirm_content', 'Are you sure you want to delete this entry? This action cannot be undone.')}</Text>
                <Group justify="flex-end" mt="md">
                    <Button variant="default" onClick={handleDeleteCancel}>{t('button_cancel')}</Button>
                    <Button color="red" onClick={handleDeleteConfirm} loading={isSaving}>{t('button_ok')}</Button>
                </Group>
            </Modal>
        </div>
    );
};

export default GlossaryManagerPage;