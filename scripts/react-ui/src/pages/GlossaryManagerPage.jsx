import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
    Row, Col, Select, Tree, Input, Typography, Button, Modal, Form, Popconfirm, Tag, Space
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import {
    useReactTable,
    getCoreRowModel,
    flexRender,
    getFilteredRowModel,
    getSortedRowModel,
} from '@tanstack/react-table';

const { Option } = Select;
const { Search } = Input;
const { Title } = Typography;

// --- Enhanced Mock Data & Config ---

const games = ['Victoria 3', 'Stellaris'];
const targetLanguages = [
    { code: 'zh-CN', name: '简体中文' },
    { code: 'en-US', name: 'English' },
    { code: 'ja-JP', name: '日本語' },
];

const glossaryFileTree = {
    'Victoria 3': [
        { title: 'glossary_art.yml', key: 'v3-art', isLeaf: true },
        { title: 'glossary_economy.yml', key: 'v3-eco', isLeaf: true },
    ],
    'Stellaris': [
        { title: 'glossary_ships.yml', key: 's-ships', isLeaf: true },
    ],
};

const mockGlossaryData = {
    'v3-art': [
        { id: 'v3_art_001', source: 'concept_art', notes: '美术专有名词', variants: ['观念艺术'], translations: { 'zh-CN': '概念艺术', 'en-US': 'Concept Art', 'ja-JP': 'コンセプトアート' } },
        { id: 'v3_art_002', source: 'impressionism', notes: '', variants: [], translations: { 'zh-CN': '印象主义', 'en-US': 'Impressionism', 'ja-JP': '印象派' } },
    ],
    'v3-eco': [
        { id: 'v3_eco_001', source: 'gdp', notes: '宏观经济学指标', variants: ['GDP'], translations: { 'zh-CN': '国内生产总值', 'en-US': 'GDP', 'ja-JP': '国内総生産' } },
    ],
    's-ships': [
        { id: 's_ships_001', source: 'corvette', notes: '小型舰船', variants: ['小型护卫舰'], translations: { 'zh-CN': '护卫舰', 'en-US': 'Corvette', 'ja-JP': 'コルベット' } },
    ],
};

// --- Main Component ---

const GlossaryManagerPage = () => {
    const { t } = useTranslation();
    const [form] = Form.useForm();

    // State
    const [selectedGame, setSelectedGame] = useState(games[0]);
    const [selectedTargetLang, setSelectedTargetLang] = useState(targetLanguages[0].code);
    const [data, setData] = useState(mockGlossaryData['v3-art']);
    const [selectedFile, setSelectedFile] = useState({ key: 'v3-art', title: 'glossary_art.yml' });
    const [filtering, setFiltering] = useState('');
    const [isModalVisible, setIsModalVisible] = useState(false);
    const [editingEntry, setEditingEntry] = useState(null);

    // --- CRUD Handlers ---
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
            variants: entry.variants.join(', '),
        });
        setIsModalVisible(true);
    };

    const handleDelete = (id) => {
        const updatedData = data.filter(item => item.id !== id);
        setData(updatedData);
        mockGlossaryData[selectedFile.key] = updatedData;
    };

    const handleModalOk = () => {
        form.validateFields().then(values => {
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
                    id: `new_${Date.now()}`,
                    source,
                    notes,
                    variants: processedVariants,
                    translations: { [selectedTargetLang]: translation },
                };
                updatedData = [...data, newEntry];
            }
            setData(updatedData);
            mockGlossaryData[selectedFile.key] = updatedData;
            setIsModalVisible(false);
        }).catch(info => {
            console.log('Validate Failed:', info);
        });
    };

    // --- Table Definition ---
    const columns = [
        { accessorKey: 'source', header: () => t('glossary_source_text'), cell: info => info.getValue() },
        {
            id: 'translation',
            header: () => t('glossary_translation'),
            cell: ({ row }) => row.original.translations[selectedTargetLang] || '',
        },
        { accessorKey: 'notes', header: () => t('glossary_notes'), cell: info => info.getValue() },
        {
            accessorKey: 'variants',
            header: () => t('glossary_variants'),
            cell: info => <>{info.getValue().map(v => <Tag key={v}>{v}</Tag>)}</>,
        },
        {
            id: 'actions',
            header: () => t('glossary_actions'),
            cell: ({ row }) => (
                <Space size="middle">
                    <Button icon={<EditOutlined />} onClick={() => handleEdit(row.original)} />
                    <Popconfirm title={t('glossary_delete_confirm')} onConfirm={() => handleDelete(row.original.id)}>
                        <Button icon={<DeleteOutlined />} danger />
                    </Popconfirm>
                </Space>
            ),
        },
    ];

    const table = useReactTable({ data, columns, getCoreRowModel: getCoreRowModel(), getFilteredRowModel: getFilteredRowModel(), state: { globalFilter: filtering }, onGlobalFilterChange: setFiltering });

    // --- Other Handlers ---
    const handleGameChange = (value) => {
        setSelectedGame(value);
        setData([]);
        setSelectedFile({ key: null, title: t('glossary_no_file_selected') });
    };

    const onSelectTree = (selectedKeys, info) => {
        if (info.node.isLeaf) {
            const fileKey = info.node.key;
            setSelectedFile({ key: fileKey, title: info.node.title });
            setData(mockGlossaryData[fileKey] || []);
            setFiltering('');
        }
    };

    return (
        <div style={{ padding: '24px' }}>
            <Row gutter={24}>
                <Col span={6}>
                    <Space direction="vertical" style={{ width: '100%' }}>
                        <div>
                            <Title level={5}>{t('glossary_game')}</Title>
                            <Select defaultValue={selectedGame} style={{ width: '100%' }} onChange={handleGameChange}>
                                {games.map(game => <Option key={game} value={game}>{game}</Option>)}
                            </Select>
                        </div>
                        <div>
                           <Title level={5}>{t('glossary_target_language', 'Target Language')}</Title>
                           <Select defaultValue={selectedTargetLang} style={{ width: '100%' }} onChange={setSelectedTargetLang}>
                               {targetLanguages.map(lang => <Option key={lang.code} value={lang.code}>{lang.name}</Option>)}
                           </Select>
                        </div>
                        <div>
                            <Title level={5}>{t('glossary_files')}</Title>
                            <Tree defaultExpandAll treeData={glossaryFileTree[selectedGame]} onSelect={onSelectTree} />
                        </div>
                    </Space>
                </Col>

                <Col span={18}>
                     <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                        <Title level={5} style={{ margin: 0 }}>{t('glossary_content')}: {selectedFile.title}</Title>
                        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd} disabled={!selectedFile.key}>
                            {t('glossary_add_entry')}
                        </Button>
                    </div>
                    <Search placeholder={t('glossary_filter_placeholder')} value={filtering} onChange={e => setFiltering(e.target.value)} style={{ marginBottom: 16 }} />
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                            {table.getHeaderGroups().map(hg => (
                                <tr key={hg.id}>{hg.headers.map(header => <th key={header.id} style={{ borderBottom: '2px solid black', padding: '8px' }}>{flexRender(header.column.columnDef.header, header.getContext())}</th>)}</tr>
                            ))}
                        </thead>
                        <tbody>
                            {table.getRowModel().rows.map(row => (
                                <tr key={row.id}>{row.getVisibleCells().map(cell => <td key={cell.id} style={{ border: '1px solid #ddd', padding: '8px' }}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</td>)}</tr>
                            ))}
                        </tbody>
                    </table>
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
        </div>
    );
};

export default GlossaryManagerPage;