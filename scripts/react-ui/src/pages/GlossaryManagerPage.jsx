import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
    Grid, Select, Input, Title, Button, Modal, Badge, Group, LoadingOverlay, Tooltip, Switch, Text, Paper, ScrollArea, Table, TextInput, NavLink, Box, Stack
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { IconPlus, IconEdit, IconTrash, IconDots, IconFolder, IconFileText } from '@tabler/icons-react';
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

    const onSelectTree = (key, info) => {
        if (info.isLeaf) {
            const [gameId, fileName] = key.split('|');
            setSelectedFile({ key: key, title: fileName, gameId: gameId });
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
        {
            accessorKey: 'source',
            header: () => <Text c="var(--text-main)" fw={700}>{t('glossary_source_text')}</Text>,
            cell: info => <Text c="var(--text-main)">{info.getValue()}</Text>
        },
        {
            id: 'translation',
            header: () => <Text c="var(--text-main)" fw={700}>{t('glossary_translation')}</Text>,
            cell: ({ row }) => <Text c="var(--text-main)">{row.original.translations[selectedTargetLang] || ''}</Text>
        },
        {
            accessorKey: 'notes',
            header: () => <Text c="var(--text-main)" fw={700}>{t('glossary_notes')}</Text>,
            cell: ({ row }) => (row.original.notes ? (<Tooltip label={t('glossary_view_edit_notes', 'View/Edit Notes')}><Button size="xs" variant="subtle" onClick={() => handleEdit(row.original)} color="var(--primary-color)"><IconDots size={14} /></Button></Tooltip>) : null)
        },
        {
            accessorKey: 'variants',
            header: () => <Text c="var(--text-main)" fw={700}>{t('glossary_variants')}</Text>,
            cell: info => <Group gap="xs">{Array.isArray(info.getValue()) ? info.getValue().map(v => <Badge key={v} color="var(--primary-color)" variant="light">{v}</Badge>) : null}</Group>
        },
        {
            id: 'actions',
            header: () => <Text c="var(--text-main)" fw={700}>{t('glossary_actions')}</Text>,
            cell: ({ row }) => (
                <Group gap="xs">
                    <Button
                        size="xs"
                        variant="outline"
                        style={{ borderColor: 'var(--primary-color)', color: 'var(--primary-color)' }}
                        onClick={() => handleEdit(row.original)}
                    >
                        <IconEdit size={14} />
                    </Button>
                    <Button
                        size="xs"
                        variant="outline"
                        color="red"
                        style={{ borderColor: 'var(--secondary-color)', color: 'var(--secondary-color)' }}
                        onClick={() => showDeleteModal(row.original.id)}
                    >
                        <IconTrash size={14} />
                    </Button>
                </Group>
            )
        },
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

    // Recursive component to render the file tree using Mantine NavLink
    const FileTree = ({ nodes, onSelect, selectedKey }) => {
        return (
            <>
                {nodes.map(node => {
                    const commonStyle = {
                        borderRadius: 'var(--card-radius)',
                        color: 'var(--text-main)',
                    };
                    if (node.isLeaf) {
                        return (
                            <NavLink
                                key={node.key}
                                label={node.title}
                                leftSection={<IconFileText size="1rem" stroke={1.5} style={{ color: 'var(--primary-color)' }} />}
                                active={node.key === selectedKey}
                                onClick={() => onSelect(node.key, node)}
                                style={{ ...commonStyle }}
                                color="var(--primary-color)"
                                variant="light"
                            />
                        );
                    } else {
                        return (
                            <NavLink
                                key={node.key}
                                label={node.title}
                                leftSection={<IconFolder size="1rem" stroke={1.5} style={{ color: 'var(--secondary-color)' }} />}
                                childrenOffset={28}
                                defaultOpened={true}
                                style={{ ...commonStyle }}
                            >
                                {node.children && (
                                    <FileTree
                                        nodes={node.children}
                                        onSelect={onSelect}
                                        selectedKey={selectedKey}
                                    />
                                )}
                            </NavLink>
                        );
                    }
                })}
            </>
        );
    };

    // Styles for container panels
    const panelStyle = {
        height: '100%',
        backgroundColor: 'var(--glass-bg)',
        border: '1px solid var(--glass-border)',
        boxShadow: 'var(--shadow-elevation)',
        borderRadius: 'var(--card-radius)',
        display: 'flex',
        flexDirection: 'column',
        backdropFilter: 'blur(10px)',
        transition: 'all 0.3s ease',
        color: 'var(--text-main)'
    };

    const titleStyle = {
        fontFamily: 'var(--font-header)',
        color: 'var(--text-highlight)',
        textShadow: '0 0 5px rgba(0,0,0,0.2)'
    };

    const buttonStyle = {
        fontFamily: 'var(--font-header)',
        // We let Mantine handle button bg usually, but we can hint colors
    };


    return (
        <div style={{ height: '100%', display: 'flex', flexDirection: 'column', position: 'relative', fontFamily: 'var(--font-body)' }}>
            <LoadingOverlay visible={isSaving} />
            <Grid gutter="md" style={{ flex: 1, overflow: 'hidden' }}>
                <Grid.Col span={3} style={{ height: '100%' }}>
                    <Paper p="md" style={panelStyle}>
                        <LoadingOverlay visible={isLoadingTree} />
                        <Title order={4} mb="md" style={titleStyle}>{t('glossary_manager_title', 'Glossary Manager')}</Title>

                        <Stack gap="sm" mb="md">
                            <div>
                                <Text size="xs" c="var(--text-muted)" mb={4}>{t('glossary_game')}</Text>
                                <Select
                                    data={treeData.map(g => ({ value: g.key, label: g.title || g.key }))}
                                    value={selectedGame}
                                    onChange={setSelectedGame}
                                    comboboxProps={{ transitionProps: { transition: 'pop', duration: 200 } }}
                                />
                            </div>
                            <div>
                                <Text size="xs" c="var(--text-muted)" mb={4}>{t('glossary_target_language')}</Text>
                                <Select
                                    data={targetLanguages.map(l => ({ value: l.code, label: l.name_local || l.code }))}
                                    value={selectedTargetLang}
                                    onChange={setSelectedTargetLang}
                                />
                            </div>
                        </Stack>

                        <Group justify="space-between" mb="xs">
                            <Text size="sm" fw={500} c="var(--text-main)">{t('glossary_files')}</Text>
                            <Tooltip label={t('glossary_create_new_file')}>
                                <Button size="xs" variant="light" onClick={() => setIsFileCreateModalVisible(true)} disabled={!selectedGame} color="var(--primary-color)">
                                    <IconPlus size={14} />
                                </Button>
                            </Tooltip>
                        </Group>

                        <ScrollArea style={{ flex: 1 }}>
                            {selectedGame && <FileTree nodes={treeData.find(n => n.key === selectedGame)?.children || []} onSelect={onSelectTree} selectedKey={selectedFile.key} />}
                        </ScrollArea>
                    </Paper>
                </Grid.Col>
                <Grid.Col span={9} style={{ height: '100%' }}>
                    <Paper p="md" style={panelStyle}>
                        <LoadingOverlay visible={isLoadingContent} />
                        <Group justify="space-between" mb="md">
                            <Title order={4} style={titleStyle}>
                                {selectedFile.title !== t('glossary_no_file_selected') ? selectedFile.title : t('glossary_select_file_prompt', 'Select a file')}
                            </Title>
                            <Button
                                leftSection={<IconPlus size={16} />}
                                onClick={handleAdd}
                                disabled={!selectedFile.key}
                                style={{
                                    backgroundColor: 'var(--primary-color)',
                                    color: 'var(--scifi-space-darker, #fff)',
                                    fontFamily: 'var(--font-header)'
                                }}
                            >
                                {t('glossary_add_entry')}
                            </Button>
                        </Group>
                        <Input
                            placeholder={t('glossary_filter_placeholder')}
                            value={filtering}
                            onChange={e => setFiltering(e.currentTarget.value)}
                            style={{ marginBottom: 16 }}
                            styles={{ input: { backgroundColor: 'rgba(0,0,0,0.1)', borderColor: 'var(--glass-border)', color: 'var(--text-main)' } }}
                        />

                        <ScrollArea style={{ flex: 1 }}>
                            <Table striped highlightOnHover withTableBorder style={{ borderColor: 'var(--glass-border)' }}>
                                <Table.Thead style={{ backgroundColor: 'rgba(0,0,0,0.1)' }}>
                                    {table.getHeaderGroups().map(hg => (
                                        <Table.Tr key={hg.id}>{hg.headers.map(header => <Table.Th key={header.id} style={{ color: 'var(--text-highlight)' }}>{flexRender(header.column.columnDef.header, header.getContext())}</Table.Th>)}</Table.Tr>
                                    ))}
                                </Table.Thead>
                                <Table.Tbody>
                                    {table.getRowModel().rows.length > 0 ? (
                                        table.getRowModel().rows.map(row => (
                                            <Table.Tr key={row.id}>{row.getVisibleCells().map(cell => <Table.Td key={cell.id} style={{ borderColor: 'var(--glass-border)' }}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</Table.Td>)}</Table.Tr>
                                        ))
                                    ) : (
                                        <Table.Tr>
                                            <Table.Td colSpan={columns.length} style={{ textAlign: 'center', padding: '20px', borderColor: 'var(--glass-border)' }}>
                                                <Text c="var(--text-muted)">{t('glossary_no_entries', 'No entries found')}</Text>
                                            </Table.Td>
                                        </Table.Tr>
                                    )}
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
                                <Text size="sm" c="var(--text-muted)">
                                    {t('glossary_page_info', { page: table.getState().pagination.pageIndex + 1, total: table.getPageCount() })}
                                </Text>
                            </Group>
                            <Button.Group>
                                <Button variant="default" onClick={() => table.previousPage()} disabled={!table.getCanPreviousPage()} style={{ fontFamily: 'var(--font-header)' }}>{t('glossary_previous_page')}</Button>
                                <Button variant="default" onClick={() => table.nextPage()} disabled={!table.getCanNextPage()} style={{ fontFamily: 'var(--font-header)' }}>{t('glossary_next_page')}</Button>
                            </Button.Group>
                        </Group>
                    </Paper>
                </Grid.Col>
            </Grid>

            <Modal
                title={<Text style={titleStyle}>{editingEntry ? t('glossary_edit_entry') : t('glossary_add_entry')}</Text>}
                opened={isModalVisible}
                onClose={() => { setIsModalVisible(false); setIsAdvancedMode(false); }}
                styles={{ header: { backgroundColor: 'var(--glass-bg)' }, body: { backgroundColor: 'var(--glass-bg)' }, content: { backgroundColor: 'transparent', border: '1px solid var(--glass-border)' } }}
            >
                <form onSubmit={form.onSubmit(saveData)}>
                    <TextInput label={<Text c="var(--text-main)">{t('glossary_source_text')}</Text>} required {...form.getInputProps('source')} />
                    <TextInput label={<Text c="var(--text-main)">{`${t('glossary_translation')} (${targetLanguages.find(l => l.code === selectedTargetLang)?.name_local || selectedTargetLang})`}</Text>} required {...form.getInputProps('translation')} />
                    <Input.Wrapper label={<Text c="var(--text-main)">{t('glossary_notes')}</Text>}><Input component="textarea" {...form.getInputProps('notes')} /></Input.Wrapper>

                    <Group justify="flex-end" my="md">
                        <Text size="sm" c="var(--text-main)">{t('glossary_advanced_mode', 'Advanced Mode')}</Text>
                        <Switch checked={isAdvancedMode} onChange={(event) => setIsAdvancedMode(event.currentTarget.checked)} />
                    </Group>

                    {isAdvancedMode && (
                        <>
                            <Input.Wrapper label={<Text c="var(--text-main)">{t('glossary_variants')}</Text>} description={t('glossary_variants_tooltip_json')}>
                                <Input component="textarea" autosize minRows={3} {...form.getInputProps('variants')} />
                            </Input.Wrapper>
                            <Input.Wrapper label={<Text c="var(--text-main)">{t('glossary_abbreviations')}</Text>} description={t('glossary_abbreviations_tooltip_json')}>
                                <Input component="textarea" autosize minRows={3} {...form.getInputProps('abbreviations')} />
                            </Input.Wrapper>
                            <Input.Wrapper label={<Text c="var(--text-main)">{t('glossary_metadata')}</Text>} description={t('glossary_metadata_tooltip_json')}>
                                <Input component="textarea" autosize minRows={3} {...form.getInputProps('metadata')} />
                            </Input.Wrapper>
                        </>
                    )}
                    <Group justify="flex-end" mt="md">
                        <Button variant="default" onClick={() => { setIsModalVisible(false); setIsAdvancedMode(false); }} style={{ fontFamily: 'var(--font-header)' }}>{t('button_cancel')}</Button>
                        <Button type="submit" loading={isSaving} style={{ backgroundColor: 'var(--primary-color)', fontFamily: 'var(--font-header)' }}>{t('button_ok')}</Button>
                    </Group>
                </form>
            </Modal>

            <Modal
                title={<Text style={titleStyle}>{t('glossary_create_new_file', 'Create New Glossary File')}</Text>}
                opened={isFileCreateModalVisible}
                onClose={() => setIsFileCreateModalVisible(false)}
                styles={{ header: { backgroundColor: 'var(--glass-bg)' }, body: { backgroundColor: 'var(--glass-bg)' }, content: { backgroundColor: 'transparent', border: '1px solid var(--glass-border)' } }}
            >
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
                    <TextInput label={<Text c="var(--text-main)">{t('glossary_file_name', 'File Name')}</Text>} placeholder="e.g., my_new_glossary.json" required {...newFileForm.getInputProps('fileName')} />
                    <Group justify="flex-end" mt="md">
                        <Button variant="default" onClick={() => setIsFileCreateModalVisible(false)} style={{ fontFamily: 'var(--font-header)' }}>{t('button_cancel')}</Button>
                        <Button type="submit" loading={isSaving} style={{ backgroundColor: 'var(--primary-color)', fontFamily: 'var(--font-header)' }}>{t('button_ok')}</Button>
                    </Group>
                </form>
            </Modal>

            <Modal
                title={<Text style={titleStyle}>{t('glossary_delete_confirm_title', 'Confirm Deletion')}</Text>}
                opened={isDeleteModalVisible}
                onClose={handleDeleteCancel}
                styles={{ header: { backgroundColor: 'var(--glass-bg)' }, body: { backgroundColor: 'var(--glass-bg)' }, content: { backgroundColor: 'transparent', border: '1px solid var(--glass-border)' } }}
            >
                <Text c="var(--text-main)">{t('glossary_delete_confirm_content', 'Are you sure you want to delete this entry? This action cannot be undone.')}</Text>
                <Group justify="flex-end" mt="md">
                    <Button variant="default" onClick={handleDeleteCancel} style={{ fontFamily: 'var(--font-header)' }}>{t('button_cancel')}</Button>
                    <Button color="red" onClick={handleDeleteConfirm} loading={isSaving} style={{ fontFamily: 'var(--font-header)', backgroundColor: 'var(--secondary-color)' }}>{t('button_ok')}</Button>
                </Group>
            </Modal>
        </div>
    );
};

export default GlossaryManagerPage;
