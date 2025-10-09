import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
    Row, Col, Select, Tree, Input, Typography, Button, Modal, Form, Popconfirm, Tag, Space, Spin, message
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

// --- Config Data (previously mock) ---
const targetLanguages = [
    { code: 'zh-CN', name: '简体中文' },
    { code: 'en-US', name: 'English' },
    { code: 'ja-JP', name: '日本語' },
];


const GlossaryManagerPage = () => {
    const { t } = useTranslation();
    const [form] = Form.useForm();

    // --- State ---
    const [treeData, setTreeData] = useState([]);
    const [data, setData] = useState([]);
    const [selectedGame, setSelectedGame] = useState(null);
    const [selectedFile, setSelectedFile] = useState({ key: null, title: t('glossary_no_file_selected'), gameId: null });
    const [selectedTargetLang, setSelectedTargetLang] = useState(targetLanguages[0].code);

    // UI State
    const [filtering, setFiltering] = useState('');
    const [isModalVisible, setIsModalVisible] = useState(false);
    const [editingEntry, setEditingEntry] = useState(null);
    const [isLoadingTree, setIsLoadingTree] = useState(true);
    const [isLoadingContent, setIsLoadingContent] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [isFileCreateModalVisible, setIsFileCreateModalVisible] = useState(false);
    const [newFileForm] = Form.useForm();


    // --- Data Fetching ---
    const fetchTreeData = async () => {
        setIsLoadingTree(true);
        try {
            const response = await axios.get('/api/glossary/tree');
            setTreeData(response.data);
            if (response.data.length > 0 && !selectedGame) {
                setSelectedGame(response.data[0].key);
            }
        } catch (error) {
            message.error('Failed to load glossary file tree.');
            console.error('Fetch tree error:', error);
        } finally {
            setIsLoadingTree(false);
        }
    };

    useEffect(() => {
        fetchTreeData();
    }, []);

    const fetchGlossaryContent = async (gameId, fileName) => {
        setIsLoadingContent(true);
        try {
            const response = await axios.get(`/api/glossary/content?game_id=${gameId}&file_name=${fileName}`);
            // Ensure translations object exists for every entry
            const sanitizedData = response.data.map(entry => ({
                ...entry,
                translations: entry.translations || {}
            }));
            setData(sanitizedData);
        } catch (error) {
            message.error(`Failed to load content for ${fileName}.`);
            console.error('Fetch content error:', error);
        } finally {
            setIsLoadingContent(false);
        }
    };

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
            variants: entry.variants ? entry.variants.join(', ') : '',
        });
        setIsModalVisible(true);
    };

    const saveData = async (updatedData) => {
        if (!selectedFile.gameId || !selectedFile.title) return;
        setIsSaving(true);
        try {
            await axios.post(
                `/api/glossary/content?game_id=${selectedFile.gameId}&file_name=${selectedFile.title}`,
                { entries: updatedData }
            );
            setData(updatedData); // Sync state with successful save
            message.success('Glossary saved successfully!');
        } catch (error) {
            message.error('Failed to save glossary.');
            console.error('Save error:', error);
        } finally {
            setIsSaving(false);
        }
    };

    const handleDelete = (id) => {
        const updatedData = data.filter(item => item.id !== id);
        saveData(updatedData);
    };

    const handleModalOk = () => {
        form.validateFields().then(values => {
            setIsModalVisible(false);
            const { source, translation, notes, variants } = values;
            const processedVariants = variants ? variants.split(',').map(v => v.trim()).filter(Boolean) : [];

            let updatedData;
            if (editingEntry) {
                updatedData = data.map(item =>
                    item.id === editingEntry.id
                        ? {
                            ...item,
                            source,
                            notes,
                            variants: processedVariants,
                            translations: { ...item.translations, [selectedTargetLang]: translation },
                          }
                        : item
                );
            } else {
                const newEntry = {
                    id: `new_${Date.now()}`, // Backend should ideally generate a real ID
                    source,
                    notes,
                    variants: processedVariants,
                    translations: { [selectedTargetLang]: translation },
                    metadata: { part_of_speech: "Noun" } // Default metadata
                };
                updatedData = [...data, newEntry];
            }
            saveData(updatedData);
        }).catch(info => {
            console.log('Validate Failed:', info);
        });
    };

    const onSelectTree = (selectedKeys, info) => {
        if (info.node.isLeaf) {
            const [gameId, fileName] = info.node.key.split('|');
            setSelectedFile({ key: info.node.key, title: fileName, gameId: gameId });
            fetchGlossaryContent(gameId, fileName);
            setFiltering('');
        }
    };

    // --- Table Definition ---
    const columns = [
        { accessorKey: 'source', header: () => t('glossary_source_text'), cell: info => info.getValue() },
        { id: 'translation', header: () => t('glossary_translation'), cell: ({ row }) => row.original.translations[selectedTargetLang] || '' },
        { accessorKey: 'notes', header: () => t('glossary_notes'), cell: info => info.getValue() },
        { accessorKey: 'variants', header: () => t('glossary_variants'), cell: info => <>{info.getValue()?.map(v => <Tag key={v}>{v}</Tag>)}</> },
        { id: 'actions', header: () => t('glossary_actions'), cell: ({ row }) => (
            <Space size="middle">
                <Button icon={<EditOutlined />} onClick={() => handleEdit(row.original)} />
                <Popconfirm title={t('glossary_delete_confirm')} onConfirm={() => handleDelete(row.original.id)}>
                    <Button icon={<DeleteOutlined />} danger />
                </Popconfirm>
            </Space>
        )},
    ];

    const table = useReactTable({ data, columns, getCoreRowModel: getCoreRowModel(), getFilteredRowModel: getFilteredRowModel(), state: { globalFilter: filtering }, onGlobalFilterChange: setFiltering });

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
                                   <Select defaultValue={selectedTargetLang} style={{ width: '100%' }} onChange={setSelectedTargetLang}>
                                       {targetLanguages.map(lang => <Option key={lang.code} value={lang.code}>{lang.name}</Option>)}
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
                                <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd} disabled={!selectedFile.key}>
                                    {t('glossary_add_entry')}
                                </Button>
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
                        </Spin>
                    </Col>
                </Row>

                <Modal title={editingEntry ? t('glossary_edit_entry') : t('glossary_add_entry')} open={isModalVisible} onOk={handleModalOk} onCancel={() => setIsModalVisible(false)} destroyOnClose>
                    <Form form={form} layout="vertical" name="glossary_entry_form">
                        <Form.Item name="source" label={t('glossary_source_text')} rules={[{ required: true }]}>
                            <Input disabled={!!editingEntry} />
                        </Form.Item>
                        <Form.Item name="translation" label={`${t('glossary_translation')} (${targetLanguages.find(l=>l.code === selectedTargetLang)?.name})`} rules={[{ required: true }]}>
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
                              fetchTreeData(); // Refresh the tree
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