import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
    Row, Col, Select, Tree, Input, Typography, Button, Modal, Form, Popconfirm, Tag, Space, Spin, message, Tooltip
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import {
    useReactTable,
    getCoreRowModel,
    flexRender,
    getFilteredRowModel,
} from '@tanstack/react-table';
import axios from 'axios';

const { Option } = Select;
const { Search } = Input;
const { Title } = Typography;


const GlossaryManagerPage = () => {
    const { t } = useTranslation();
    const [form] = Form.useForm();

    // --- State ---
    const [treeData, setTreeData] = useState([]);
    const [data, setData] = useState([]); // This will hold the data for the current page
    const [selectedGame, setSelectedGame] = useState(null);
    const [selectedFile, setSelectedFile] = useState({ key: null, title: t('glossary_no_file_selected'), gameId: null });
    const [targetLanguages, setTargetLanguages] = useState([]);
    const [selectedTargetLang, setSelectedTargetLang] = useState(null);

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
    const [newFileForm] = Form.useForm();

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
            message.error('Failed to load initial configuration.');
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
                `/api/glossary/content?game_id=${gameId}&file_name=${title}&page=${pageIndex + 1}&pageSize=${pageSize}`
            );
            setData(response.data.entries);
            setRowCount(response.data.totalCount);
        } catch (error) {
            message.error(`Failed to load content for ${title}.`);
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
    }, [selectedFile, pagination]);


    // --- Handlers ---
    const handleAdd = () => {
        setEditingEntry(null);
        form.resetFields();
        setIsModalVisible(true);
    };

    const handleEdit = (entry) => {
        setEditingEntry(entry);
        form.setFieldsValue({
            source: entry.source,
            translation: entry.translations[selectedTargetLang] || '',
            notes: entry.notes,
            variants: Array.isArray(entry.variants) ? entry.variants.join(', ') : '',
        });
        setIsModalVisible(true);
    };

    const saveData = async () => {
        if (!selectedFile.gameId || !selectedFile.title) return;

        setIsSaving(true);
        try {
            const values = await form.validateFields();
            const { source, translation, notes, variants } = values;
            const processedVariants = variants ? variants.split(',').map(v => v.trim()).filter(Boolean) : [];

            if (editingEntry) {
                // Update existing entry
                const payload = {
                    ...editingEntry,
                    source,
                    notes,
                    variants: processedVariants,
                    translations: { ...editingEntry.translations, [selectedTargetLang]: translation },
                };
                await axios.put(
                    `/api/glossary/entry/${editingEntry.id}?game_id=${selectedFile.gameId}&file_name=${selectedFile.title}`,
                    payload
                );
            } else {
                // Create new entry
                const payload = {
                    source,
                    notes,
                    variants: processedVariants,
                    translations: { [selectedTargetLang]: translation },
                    metadata: { part_of_speech: "Noun" } // Default metadata
                };
                 await axios.post(
                    `/api/glossary/entry?game_id=${selectedFile.gameId}&file_name=${selectedFile.title}`,
                    payload
                );
            }

            message.success('Glossary saved successfully!');
            setIsModalVisible(false);
            fetchGlossaryContent(); // Refresh the current page view.
        } catch (error) {
             if (error.name !== 'ValidationException') {
                message.error('Failed to save glossary.');
                console.error('Save error:', error);
            }
        } finally {
            setIsSaving(false);
        }
    };


    const handleDelete = async (id) => {
        setIsSaving(true);
        try {
            await axios.delete(`/api/glossary/entry/${id}?game_id=${selectedFile.gameId}&file_name=${selectedFile.title}`);
            message.success('Entry deleted successfully!');

            // After deleting, check if the current page would be empty and adjust if necessary.
            const newTotalCount = rowCount - 1;
            const newPageCount = Math.ceil(newTotalCount / pagination.pageSize);
            if (pagination.pageIndex >= newPageCount && newPageCount > 0) {
                setPagination(prev => ({ ...prev, pageIndex: newPageCount - 1 }));
            } else {
                fetchGlossaryContent();
            }
        } catch (error) {
            message.error('Failed to delete entry.');
            console.error('Delete error:', error);
        } finally {
            setIsSaving(false);
        }
    };

    const onSelectTree = (selectedKeys, info) => {
        if (info.node.isLeaf) {
            const [gameId, fileName] = info.node.key.split('|');
            setSelectedFile({ key: info.node.key, title: fileName, gameId: gameId });
            setFiltering('');
            setPagination({ pageIndex: 0, pageSize: 25 }); // Reset pagination, which triggers useEffect to fetch data.
        }
    };

    // --- Table Definition ---
    const columns = [
        { accessorKey: 'source', header: () => t('glossary_source_text'), cell: info => info.getValue() },
        { id: 'translation', header: () => t('glossary_translation'), cell: ({ row }) => row.original.translations[selectedTargetLang] || '' },
        { accessorKey: 'notes', header: () => t('glossary_notes'), cell: info => info.getValue() },
        { accessorKey: 'variants', header: () => t('glossary_variants'), cell: info => <>{Array.isArray(info.getValue()) ? info.getValue().map(v => <Tag key={v}>{v}</Tag>) : null}</> },
        { id: 'actions', header: () => t('glossary_actions'), cell: ({ row }) => (
            <Space size="middle">
                <Button icon={<EditOutlined />} onClick={() => handleEdit(row.original)} />
                <Popconfirm title={t('glossary_delete_confirm')} onConfirm={() => handleDelete(row.original.id)}>
                    <Button icon={<DeleteOutlined />} danger />
                </Popconfirm>
            </Space>
        )},
    ];

    const table = useReactTable({
        data,
        columns,
        getCoreRowModel: getCoreRowModel(),
        getFilteredRowModel: getFilteredRowModel(),
        // Manual pagination setup
        manualPagination: true,
        pageCount: Math.ceil(rowCount / pagination.pageSize),
        state: {
            globalFilter: filtering,
            pagination,
        },
        onPaginationChange: setPagination,
        onGlobalFilterChange: setFiltering,
    });

    return (
        <Spin spinning={isSaving} tip="Saving...">
            <div style={{ padding: '24px' }}>
                <Row gutter={24}>
                    <Col span={6}>
                        <Spin spinning={isLoadingTree} tip="Loading games...">
                            <Space direction="vertical" style={{ width: '100%' }}>
                                <div>
                                    <Title level={5}>{t('glossary_game')}</Title>
                                    <Select value={selectedGame} style={{ width: '100%' }} onChange={setSelectedGame}>
                                        {treeData.map(gameNode => <Option key={gameNode.key} value={gameNode.key}>{gameNode.title}</Option>)}
                                    </Select>
                                </div>
                                <div>
                                   <Title level={5}>{t('glossary_target_language', 'Target Language')}</Title>
                                   <Select value={selectedTargetLang} style={{ width: '100%' }} onChange={setSelectedTargetLang} loading={!targetLanguages.length}>
                                       {targetLanguages.map(lang => <Option key={lang.code} value={lang.code}>{lang.name_local}</Option>)}
                                   </Select>
                                </div>
                                <div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                      <Title level={5} style={{ margin: 0 }}>{t('glossary_files')}</Title>
                                      <Button
                                        icon={<PlusOutlined />}
                                        size="small"
                                        onClick={() => setIsFileCreateModalVisible(true)}
                                        disabled={!selectedGame}
                                        data-testid="add-new-glossary-button"
                                      />
                                    </div>
                                    {selectedGame && <Tree
                                        defaultExpandAll
                                        treeData={treeData.find(n => n.key === selectedGame)?.children}
                                        onSelect={onSelectTree}
                                    />}
                                </div>
                            </Space>
                        </Spin>
                    </Col>
                    <Col span={18}>
                        <Spin spinning={isLoadingContent} tip="Loading content...">
                             <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                                <Title level={5} style={{ margin: 0, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                    {t('glossary_content')}: {selectedFile.title}
                                </Title>
                                <Tooltip title={t('glossary_add_entry')}>
                                    <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd} disabled={!selectedFile.key} style={{ flexShrink: 0 }}/>
                                </Tooltip>
                            </div>
                            <Search placeholder={t('glossary_filter_placeholder')} value={filtering} onChange={e => setFiltering(e.target.value)} style={{ marginBottom: 16 }} />
                            <div style={{ overflowX: 'auto' }}>
                                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                    <thead>
                                        {table.getHeaderGroups().map(hg => (
                                            <tr key={hg.id}>{hg.headers.map(header => <th key={header.id} style={{ borderBottom: '2px solid black', padding: '8px', textAlign: 'left' }}>{flexRender(header.column.columnDef.header, header.getContext())}</th>)}</tr>
                                        ))}
                                    </thead>
                                    <tbody>
                                        {table.getRowModel().rows.map(row => (
                                            <tr key={row.id}>{row.getVisibleCells().map(cell => <td key={cell.id} style={{ border: '1px solid #ddd', padding: '8px' }}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</td>)}</tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                             <div style={{ marginTop: 16, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                <Space>
                                    <Select
                                        value={table.getState().pagination.pageSize}
                                        onChange={e => {
                                            table.setPageSize(Number(e));
                                        }}
                                    >
                                        {[25, 50, 100].map(pageSize => (
                                            <Option key={pageSize} value={pageSize}>
                                                {t('glossary_show_entries', { count: pageSize })}
                                            </Option>
                                        ))}
                                    </Select>
                                    <span>
                                        {t('glossary_page_info', {
                                            page: table.getState().pagination.pageIndex + 1,
                                            total: table.getPageCount()
                                        })}
                                    </span>
                                </Space>
                                <Space>
                                    <Button
                                        onClick={() => table.previousPage()}
                                        disabled={!table.getCanPreviousPage()}
                                    >
                                        {t('glossary_previous_page')}
                                    </Button>
                                    <Button
                                        onClick={() => table.nextPage()}
                                        disabled={!table.getCanNextPage()}
                                    >
                                        {t('glossary_next_page')}
                                    </Button>
                                </Space>
                            </div>
                        </Spin>
                    </Col>
                </Row>

                <Modal title={editingEntry ? t('glossary_edit_entry') : t('glossary_add_entry')} open={isModalVisible} onOk={saveData} onCancel={() => setIsModalVisible(false)} destroyOnClose confirmLoading={isSaving}>
                    <Form form={form} layout="vertical" name="glossary_entry_form">
                        <Form.Item name="source" label={t('glossary_source_text')} rules={[{ required: true }]}>
                            <Input disabled={!!editingEntry} />
                        </Form.Item>
                        <Form.Item name="translation" label={`${t('glossary_translation')} (${targetLanguages.find(l=>l.code === selectedTargetLang)?.name_local || selectedTargetLang})`} rules={[{ required: true }]}>
                            <Input />
                        </Form.Item>
                        <Form.Item name="notes" label={t('glossary_notes')}><Input.TextArea /></Form.Item>
                        <Form.Item name="variants" label={t('glossary_variants')} tooltip={t('glossary_variants_tooltip')}><Input placeholder={t('glossary_variants_placeholder')} /></Form.Item>
                    </Form>
                </Modal>

                <Modal
                  title={t('glossary_create_new_file', 'Create New Glossary File')}
                  open={isFileCreateModalVisible}
                  onCancel={() => setIsFileCreateModalVisible(false)}
                  onOk={() => {
                      newFileForm.validateFields().then(async values => {
                          try {
                              setIsSaving(true);
                              await axios.post('/api/glossary/file', {
                                  game_id: selectedGame,
                                  file_name: values.fileName,
                              });
                              message.success(`Successfully created ${values.fileName}`);
                              setIsFileCreateModalVisible(false);
                              fetchInitialConfigs(); // Refresh the whole tree and config
                          } catch (error) {
                              message.error(error.response?.data?.detail || 'Failed to create file.');
                              console.error('Create file error:', error);
                          } finally {
                              setIsSaving(false);
                          }
                      });
                  }}
                  confirmLoading={isSaving}
                >
                    <Form form={newFileForm} layout="vertical">
                        <Form.Item
                          name="fileName"
                          label={t('glossary_file_name', 'File Name')}
                          rules={[
                              { required: true, message: t('glossary_filename_required', 'Please enter a file name.') },
                              { pattern: /^[a-zA-Z0-9_]+\.json$/, message: t('glossary_filename_invalid', 'Must be a valid name ending in .json (e.g., my_glossary.json)') }
                          ]}
                        >
                            <Input placeholder="e.g., my_new_glossary.json" />
                        </Form.Item>
                    </Form>
                </Modal>
            </div>
        </Spin>
    );
};

export default GlossaryManagerPage;
