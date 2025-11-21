import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { useTranslation } from 'react-i18next';
import {
    Grid, Select, Input, Title, Button, Modal, Badge, Group, LoadingOverlay, Tooltip, Switch, Text, Paper, ScrollArea, Table, TextInput, NavLink, Box, Stack
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { IconPlus, IconEdit, IconTrash, IconDots, IconFolder, IconFileText, IconX } from '@tabler/icons-react';
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
    const [searchScope, setSearchScope] = useState('file'); // 'file', 'game', 'all'
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

    // New State for Master-Detail View
    const [selectedTerm, setSelectedTerm] = useState(null);

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
        const { pageIndex, pageSize } = pagination;
        setIsLoadingContent(true);

        try {
            let response;
            // If searching with scope 'game' or 'all', or searching in 'file' with a query
            // (Note: The user asked for separate search options, we implement 'search' endpoint logic)
            // Actually, if searchScope is 'file' and NO filter, we use GET /content.
            // If searchScope is 'file' WITH filter, we can use GET /content (existing filter) OR the new search.
            // The user prompt implies "Search Option ... Dropdown".

            if (searchScope === 'file' && !filtering) {
                if (!selectedFile.key) {
                    setData([]);
                    setRowCount(0);
                    setIsLoadingContent(false);
                    return;
                }
                const { gameId, title } = selectedFile;
                response = await axios.get(
                    `/api/glossary/content?game_id=${gameId}&file_name=${title}&page=${pageIndex + 1}&pageSize=${pageSize}`
                );
            } else {
                // Search logic
                const payload = {
                    scope: searchScope,
                    query: filtering,
                    page: pageIndex + 1,
                    pageSize: pageSize,
                    game_id: selectedFile.gameId,
                    file_name: selectedFile.title
                };

                // Validation for scope requirements
                if (searchScope === 'file' && !selectedFile.key) {
                     // Cannot search file if no file selected
                     setData([]);
                     setRowCount(0);
                     setIsLoadingContent(false);
                     return;
                }
                if (searchScope === 'game' && !selectedFile.gameId) {
                    // Cannot search game if no game selected (we use selectedFile.gameId or selectedGame)
                    payload.game_id = selectedGame;
                    if (!payload.game_id) {
                         setData([]);
                         setRowCount(0);
                         setIsLoadingContent(false);
                         return;
                    }
                }

                response = await axios.post('/api/glossary/search', payload);
            }

            setData(response.data.entries);
            setRowCount(response.data.totalCount);
        } catch (error) {
            notifications.show({ title: 'Error', message: 'Failed to load content.', color: 'red' });
            console.error('Fetch content error:', error);
            setData([]);
            setRowCount(0);
        } finally {
            setIsLoadingContent(false);
        }
    };

    // Effect to fetch content when dependencies change
    useEffect(() => {
        // Reset pagination when filter or scope changes (optional but good UX)
        // But here we just depend on pagination. If we change filter/scope, we should probably reset page to 0 elsewhere.
        fetchGlossaryContent();
    }, [selectedFile, pagination, filtering, searchScope]);


    // --- Handlers ---
    const handleAdd = () => {
        setEditingEntry(null);
        setSelectedTerm(null); // Clear selection when adding new
        form.reset();
        setIsModalVisible(true); // Keep modal for adding new entries for now, or switch to panel? Let's keep modal for "Add" to avoid confusion, or maybe panel is better?
        // User asked for "click row -> show details". Adding new might still be better in a modal or just an empty panel.
        // Let's stick to Modal for ADD for now to minimize risk, but use Panel for EDIT/VIEW.
    };

    const { setSidebarWidth } = useSidebar();

    // ...

    const handleRowClick = (entry) => {
        setSelectedTerm(entry);
        setEditingEntry(entry);
        setSidebarWidth(450); // Widen the sidebar for editing
        form.setValues({
            source: entry.source,
            translation: entry.translations[selectedTargetLang] || '',
            notes: entry.notes,
            variants: entry.variants ? JSON.stringify(entry.variants, null, 2) : '',
            abbreviations: entry.abbreviations ? JSON.stringify(entry.abbreviations, null, 2) : '',
            metadata: entry.metadata ? JSON.stringify(entry.metadata, null, 2) : '',
        });
    };

    const handleClosePanel = () => {
        setSelectedTerm(null);
        setEditingEntry(null);
        setSidebarWidth(300); // Reset width
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

            // If we are in panel mode (editingEntry exists and selectedTerm exists), we might want to keep the panel open or update it.
            // For now, let's just refresh the data. The selectedTerm might need to be updated with new values if we want to reflect changes immediately without re-clicking.
            if (selectedTerm && editingEntry && selectedTerm.id === editingEntry.id) {
                // We can't easily update selectedTerm with full server response here without refetching, 
                // but fetchGlossaryContent will refresh the list. 
                // We might lose selection if the list rebuilds? No, selection is by ID reference usually, but here it's an object.
                // Let's rely on the list refresh.
            }

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
            if (selectedTerm && selectedTerm.id === id) {
                setSelectedTerm(null); // Deselect if deleted
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
            // When selecting a file, usually we reset to 'file' scope and clear filter?
            // User might want to keep 'All Games' search active?
            // Typically clicking a file implies "Show me this file".
            setSearchScope('file');
            setFiltering('');
            setPagination({ pageIndex: 0, pageSize: 25 }); // Reset pagination, which triggers useEffect to fetch data.
            setSelectedTerm(null); // Clear selection on file change
        } else {
            // If clicking a Game node (folder)
            // We can set the selected game, to facilitate "Current Game" search
            // key is the gameId
            setSelectedGame(key);
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
        ...(searchScope !== 'file' ? [
            {
                accessorKey: 'game_id',
                header: () => <Text className={styles.textMain} fw={700}>{t('glossary_game_id', 'Game')}</Text>,
                cell: info => <Text className={styles.textMain}>{info.getValue()}</Text>
            },
            {
                accessorKey: 'file_name',
                header: () => <Text className={styles.textMain} fw={700}>{t('glossary_file_name', 'File')}</Text>,
                cell: info => <Text className={styles.textMain}>{info.getValue()}</Text>
            }
        ] : []),
        {
            accessorKey: 'source',
            header: () => <Text className={styles.textMain} fw={700}>{t('glossary_source_text')}</Text>,
            cell: info => <Text className={styles.textMain}>{info.getValue()}</Text>
        },
        {
            id: 'translation',
            header: () => <Text className={styles.textMain} fw={700}>{t('glossary_translation')}</Text>,
            cell: ({ row }) => <Text className={styles.textMain}>{row.original.translations[selectedTargetLang] || ''}</Text>
        },
        {
            accessorKey: 'notes',
            header: () => <Text className={styles.textMain} fw={700}>{t('glossary_notes')}</Text>,
            cell: ({ row }) => (row.original.notes ? (<Tooltip label={t('glossary_view_edit_notes', 'View/Edit Notes')}><IconDots size={14} style={{ color: 'var(--text-muted)' }} /></Tooltip>) : null)
        },
        {
            accessorKey: 'variants',
            header: () => <Text className={styles.textMain} fw={700}>{t('glossary_variants')}</Text>,
            cell: info => <Group gap="xs">{Array.isArray(info.getValue()) ? info.getValue().map(v => <Badge key={v} variant="light" color="var(--color-primary)">{v}</Badge>) : null}</Group>
        },
        {
            id: 'actions',
            header: () => <Text className={styles.textMain} fw={700}>{t('glossary_actions')}</Text>,
            cell: ({ row }) => (
                <Group gap="xs" onClick={(e) => e.stopPropagation()}>
                    {/* Stop propagation so clicking delete doesn't select the row */}
                    <Button
                        size="xs"
                        variant="outline"
                        color="red"
                        className={styles.actionButton}
                        style={{ borderColor: 'var(--color-accent)', color: 'var(--color-accent)' }}
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
                    if (node.isLeaf) {
                        return (
                            <NavLink
                                key={node.key}
                                label={node.title}
                                leftSection={<IconFileText size="1rem" stroke={1.5} style={{ color: 'var(--color-primary)' }} />}
                                active={node.key === selectedKey}
                                onClick={() => onSelect(node.key, node)}
                                className={styles.actionButton}
                                style={{ borderRadius: 'var(--card-radius)', color: 'var(--text-main)' }}
                                variant="light"
                            />
                        );
                    } else {
                        return (
                            <NavLink
                                key={node.key}
                                label={node.title}
                                leftSection={<IconFolder size="1rem" stroke={1.5} style={{ color: 'var(--color-accent)' }} />}
                                childrenOffset={28}
                                defaultOpened={true}
                                className={styles.actionButton}
                                style={{ borderRadius: 'var(--card-radius)', color: 'var(--text-main)' }}
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

    return (
        <div className={styles.pageContainer}>
            <LoadingOverlay visible={isSaving} />
            <Grid gutter="md" style={{ flex: 1, overflow: 'hidden' }}>
                {/* Left Sidebar: Navigation */}
                <Grid.Col span={3} style={{ height: '100%' }}>
                    <Paper p="md" className={styles.sidebarCard}>
                        <LoadingOverlay visible={isLoadingTree} />
                        <Title order={4} className={styles.headerTitle}>{t('glossary_manager_title', 'Glossary Manager')}</Title>

                        <Stack gap="sm" mb="md">
                            <div>
                                <Text size="xs" className={styles.textMuted} mb={4}>{t('glossary_game')}</Text>
                                <Select
                                    data={treeData.map(g => ({ value: g.key, label: g.title || g.key }))}
                                    value={selectedGame}
                                    onChange={setSelectedGame}
                                    comboboxProps={{ transitionProps: { transition: 'pop', duration: 200 } }}
                                />
                            </div>
                            <div>
                                <Text size="xs" className={styles.textMuted} mb={4}>{t('glossary_target_language')}</Text>
                                <Select
                                    data={targetLanguages.map(l => ({ value: l.code, label: l.name_local || l.code }))}
                                    value={selectedTargetLang}
                                    onChange={setSelectedTargetLang}
                                />
                            </div>
                        </Stack>

                        <Group justify="space-between" mb="xs">
                            <Text size="sm" fw={500} className={styles.textMain}>{t('glossary_files')}</Text>
                            <Tooltip label={t('glossary_create_new_file')}>
                                <Button size="xs" variant="light" onClick={() => setIsFileCreateModalVisible(true)} disabled={!selectedGame} className={styles.actionButton}>
                                    <IconPlus size={14} />
                                </Button>
                            </Tooltip>
                        </Group>

                        <ScrollArea style={{ flex: 1 }}>
                            {selectedGame && <FileTree nodes={treeData.find(n => n.key === selectedGame)?.children || []} onSelect={onSelectTree} selectedKey={selectedFile.key} />}
                        </ScrollArea>
                    </Paper>
                </Grid.Col>

                {/* Middle Column: Table */}
                <Grid.Col span={9} style={{ height: '100%', transition: 'all 0.3s ease' }}>
                    <Paper p="md" className={styles.contentCard}>
                        <LoadingOverlay visible={isLoadingContent} />
                        <Group justify="space-between" mb="md">
                            <Title order={4} className={styles.headerTitle}>
                                {selectedFile.title !== t('glossary_no_file_selected') ? selectedFile.title : t('glossary_select_file_prompt', 'Select a file')}
                            </Title>
                            <Button
                                leftSection={<IconPlus size={16} />}
                                onClick={handleAdd}
                                disabled={!selectedFile.key}
                                className={styles.primaryButton}
                            >
                                {t('glossary_add_entry')}
                            </Button>
                        </Group>
                        <Group mb="md" gap="xs">
                            <Input
                                placeholder={t('glossary_filter_placeholder')}
                                value={filtering}
                                onChange={e => {
                                    setFiltering(e.currentTarget.value);
                                    setPagination(p => ({ ...p, pageIndex: 0 }));
                                }}
                                className={styles.filterInput}
                                style={{ flex: 1, marginBottom: 0 }}
                            />
                            <Select
                                value={searchScope}
                                onChange={(val) => {
                                    setSearchScope(val);
                                    setPagination(p => ({ ...p, pageIndex: 0 }));
                                }}
                                data={[
                                    { value: 'file', label: t('search_scope_file', 'Current File') },
                                    { value: 'game', label: t('search_scope_game', 'Current Game') },
                                    { value: 'all', label: t('search_scope_all', 'All Games') }
                                ]}
                                style={{ width: 160 }}
                                allowDeselect={false}
                            />
                        </Group>

                        <ScrollArea style={{ flex: 1 }}>
                            <Table striped highlightOnHover withTableBorder className={styles.dataTable}>
                                <Table.Thead>
                                    {table.getHeaderGroups().map(hg => (
                                        <Table.Tr key={hg.id}>{hg.headers.map(header => <Table.Th key={header.id}>{flexRender(header.column.columnDef.header, header.getContext())}</Table.Th>)}</Table.Tr>
                                    ))}
                                </Table.Thead>
                                <Table.Tbody>
                                    {table.getRowModel().rows.length > 0 ? (
                                        table.getRowModel().rows.map(row => (
                                            <Table.Tr
                                                key={row.id}
                                                onClick={() => handleRowClick(row.original)}
                                                className={selectedTerm && selectedTerm.id === row.original.id ? styles.selectedRow : ''}
                                            >
                                                {row.getVisibleCells().map(cell => <Table.Td key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</Table.Td>)}
                                            </Table.Tr>
                                        ))
                                    ) : (
                                        <Table.Tr>
                                            <Table.Td colSpan={columns.length} style={{ textAlign: 'center', padding: '20px' }}>
                                                <Text className={styles.textMuted}>
                                                    {searchScope === 'file'
                                                        ? t('glossary_no_entries', 'No entries found')
                                                        : t('glossary_no_search_results', `No matching terms found in ${searchScope === 'game' ? 'current game' : 'all games'}`)}
                                                </Text>
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
                                <Text size="sm" className={styles.textMuted}>
                                    {t('glossary_page_info', { page: table.getState().pagination.pageIndex + 1, total: table.getPageCount() })}
                                </Text>
                            </Group>
                            <Button.Group>
                                <Button variant="default" onClick={() => table.previousPage()} disabled={!table.getCanPreviousPage()} className={styles.actionButton}>{t('glossary_previous_page')}</Button>
                                <Button variant="default" onClick={() => table.nextPage()} disabled={!table.getCanNextPage()} className={styles.actionButton}>{t('glossary_next_page')}</Button>
                            </Button.Group>
                        </Group>
                    </Paper>
                </Grid.Col>
            </Grid>

            {/* Portal to ContextualSider */}
            {selectedTerm && document.getElementById('glossary-detail-portal') && createPortal(
                <Stack gap="md">
                    <Group justify="space-between">
                        <Title order={5} className={styles.headerTitle}>{t('glossary_edit_entry', 'Edit Entry')}</Title>
                        <Button variant="subtle" size="xs" onClick={handleClosePanel}><IconX size={16} /></Button>
                    </Group>
                    <form onSubmit={form.onSubmit(saveData)}>
                        <Stack gap="md">
                            <TextInput label={<Text className={styles.textMain}>{t('glossary_source_text')}</Text>} required {...form.getInputProps('source')} />
                            <TextInput label={<Text className={styles.textMain}>{`${t('glossary_translation')} (${targetLanguages.find(l => l.code === selectedTargetLang)?.name_local || selectedTargetLang})`}</Text>} required {...form.getInputProps('translation')} />
                            <Input.Wrapper label={<Text className={styles.textMain}>{t('glossary_notes')}</Text>}><Input component="textarea" autosize minRows={3} {...form.getInputProps('notes')} /></Input.Wrapper>

                            <Group justify="space-between" mt="xs">
                                <Text size="sm" className={styles.textMain}>{t('glossary_advanced_mode', 'Advanced Mode')}</Text>
                                <Switch checked={isAdvancedMode} onChange={(event) => setIsAdvancedMode(event.currentTarget.checked)} />
                            </Group>

                            {isAdvancedMode && (
                                <>
                                    <Input.Wrapper label={<Text className={styles.textMain}>{t('glossary_variants')}</Text>} description={t('glossary_variants_tooltip_json')}>
                                        <Input component="textarea" autosize minRows={2} {...form.getInputProps('variants')} />
                                    </Input.Wrapper>
                                    <Input.Wrapper label={<Text className={styles.textMain}>{t('glossary_abbreviations')}</Text>} description={t('glossary_abbreviations_tooltip_json')}>
                                        <Input component="textarea" autosize minRows={2} {...form.getInputProps('abbreviations')} />
                                    </Input.Wrapper>
                                    <Input.Wrapper label={<Text className={styles.textMain}>{t('glossary_metadata')}</Text>} description={t('glossary_metadata_tooltip_json')}>
                                        <Input component="textarea" autosize minRows={2} {...form.getInputProps('metadata')} />
                                    </Input.Wrapper>
                                </>
                            )}

                            <Group justify="flex-end" mt="md">
                                <Button variant="default" onClick={handleClosePanel} className={styles.actionButton}>{t('button_cancel')}</Button>
                                <Button type="submit" loading={isSaving} className={styles.primaryButton}>{t('button_save')}</Button>
                            </Group>
                        </Stack>
                    </form>
                </Stack>,
                document.getElementById('glossary-detail-portal')
            )}

            <Modal
                title={<Text className={styles.headerTitle}>{t('glossary_add_entry')}</Text>}
                opened={isModalVisible}
                onClose={() => { setIsModalVisible(false); setIsAdvancedMode(false); }}
                classNames={{ content: styles.modalContent, header: styles.modalHeader, body: styles.modalBody, title: styles.modalTitle }}
            >
                <form onSubmit={form.onSubmit(saveData)}>
                    <TextInput label={<Text className={styles.textMain}>{t('glossary_source_text')}</Text>} required {...form.getInputProps('source')} />
                    <TextInput label={<Text className={styles.textMain}>{`${t('glossary_translation')} (${targetLanguages.find(l => l.code === selectedTargetLang)?.name_local || selectedTargetLang})`}</Text>} required {...form.getInputProps('translation')} />
                    <Input.Wrapper label={<Text className={styles.textMain}>{t('glossary_notes')}</Text>}><Input component="textarea" {...form.getInputProps('notes')} /></Input.Wrapper>

                    <Group justify="flex-end" my="md">
                        <Text size="sm" className={styles.textMain}>{t('glossary_advanced_mode', 'Advanced Mode')}</Text>
                        <Switch checked={isAdvancedMode} onChange={(event) => setIsAdvancedMode(event.currentTarget.checked)} />
                    </Group>

                    {isAdvancedMode && (
                        <>
                            <Input.Wrapper label={<Text className={styles.textMain}>{t('glossary_variants')}</Text>} description={t('glossary_variants_tooltip_json')}>
                                <Input component="textarea" autosize minRows={3} {...form.getInputProps('variants')} />
                            </Input.Wrapper>
                            <Input.Wrapper label={<Text className={styles.textMain}>{t('glossary_abbreviations')}</Text>} description={t('glossary_abbreviations_tooltip_json')}>
                                <Input component="textarea" autosize minRows={3} {...form.getInputProps('abbreviations')} />
                            </Input.Wrapper>
                            <Input.Wrapper label={<Text className={styles.textMain}>{t('glossary_metadata')}</Text>} description={t('glossary_metadata_tooltip_json')}>
                                <Input component="textarea" autosize minRows={3} {...form.getInputProps('metadata')} />
                            </Input.Wrapper>
                        </>
                    )}
                    <Group justify="flex-end" mt="md">
                        <Button variant="default" onClick={() => { setIsModalVisible(false); setIsAdvancedMode(false); }} className={styles.actionButton}>{t('button_cancel')}</Button>
                        <Button type="submit" loading={isSaving} className={styles.primaryButton}>{t('button_ok')}</Button>
                    </Group>
                </form>
            </Modal>

            <Modal
                title={<Text className={styles.headerTitle}>{t('glossary_create_new_file', 'Create New Glossary File')}</Text>}
                opened={isFileCreateModalVisible}
                onClose={() => setIsFileCreateModalVisible(false)}
                classNames={{ content: styles.modalContent, header: styles.modalHeader, body: styles.modalBody, title: styles.modalTitle }}
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
                    <TextInput label={<Text className={styles.textMain}>{t('glossary_file_name', 'File Name')}</Text>} placeholder="e.g., my_new_glossary.json" required {...newFileForm.getInputProps('fileName')} />
                    <Group justify="flex-end" mt="md">
                        <Button variant="default" onClick={() => setIsFileCreateModalVisible(false)} className={styles.actionButton}>{t('button_cancel')}</Button>
                        <Button type="submit" loading={isSaving} className={styles.primaryButton}>{t('button_ok')}</Button>
                    </Group>
                </form>
            </Modal>

            <Modal
                title={<Text className={styles.headerTitle}>{t('glossary_delete_confirm_title', 'Confirm Deletion')}</Text>}
                opened={isDeleteModalVisible}
                onClose={handleDeleteCancel}
                classNames={{ content: styles.modalContent, header: styles.modalHeader, body: styles.modalBody, title: styles.modalTitle }}
            >
                <Text className={styles.textMain}>{t('glossary_delete_confirm_content', 'Are you sure you want to delete this entry? This action cannot be undone.')}</Text>
                <Group justify="flex-end" mt="md">
                    <Button variant="default" onClick={handleDeleteCancel} className={styles.actionButton}>{t('button_cancel')}</Button>
                    <Button color="red" onClick={handleDeleteConfirm} loading={isSaving} className={styles.actionButton} style={{ borderColor: 'var(--color-accent)', color: 'var(--color-accent)' }}>{t('button_ok')}</Button>
                </Group>
            </Modal>
        </div>
    );
};

export default GlossaryManagerPage;
