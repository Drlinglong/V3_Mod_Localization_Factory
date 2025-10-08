import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Row, Col, Select, Tree, Input, Typography } from 'antd';
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

// --- Mock Data ---

// 1. Game Selection Data
const games = ['Victoria 3', 'Stellaris'];

// 2. File Tree Structure
const glossaryFileTree = {
  'Victoria 3': [
    {
      title: 'Base Game',
      key: 'v3-base',
      children: [
        { title: 'glossary_art.yml', key: 'v3-art', isLeaf: true },
        { title: 'glossary_economy.yml', key: 'v3-eco', isLeaf: true },
      ],
    },
  ],
  'Stellaris': [
    {
      title: 'Base Game',
      key: 's-base',
      children: [
        { title: 'glossary_ships.yml', key: 's-ships', isLeaf: true },
        { title: 'glossary_events.yml', key: 's-events', isLeaf: true },
      ],
    },
     {
      title: 'DLC',
      key: 's-dlc',
      children: [
        { title: 'glossary_overlord.yml', key: 's-overlord', isLeaf: true },
      ],
    },
  ],
};

// 3. Detailed Glossary Content for each file key
const mockGlossaryData = {
    'v3-art': [
        { id: 'v3_art_001', source: 'concept_art', translation: '概念艺术' },
        { id: 'v3_art_002', source: 'impressionism', translation: '印象主义' },
    ],
    'v3-eco': [
        { id: 'v3_eco_001', source: 'gdp', translation: '国内生产总值' },
        { id: 'v3_eco_002', source: 'market_price', translation: '市场价格' },
    ],
    's-ships': [
        { id: 's_ships_001', source: 'corvette', translation: '护卫舰' },
        { id: 's_ships_002', source: 'destroyer', translation: '驱逐舰' },
        { id: 's_ships_003', source: 'battleship', translation: '战列舰' },
    ],
    's-events': [
        { id: 's_events_001', source: 'anomaly', translation: '异常' },
    ],
    's-overlord': [
        { id: 's_overlord_001', source: 'holding', translation: '附属建筑' },
        { id: 's_overlord_002', source: 'liege', translation: '宗主' },
    ]
};


// --- Components ---

const EditableCell = ({ getValue, row, column, table }) => {
    const initialValue = getValue();
    const [value, setValue] = useState(initialValue);
    const [isEditing, setIsEditing] = useState(false);

    const onBlur = () => {
        table.options.meta?.updateData(row.index, column.id, value);
        setIsEditing(false);
    };

    const onDoubleClick = () => setIsEditing(true);

    useEffect(() => {
        setValue(initialValue);
    }, [initialValue]);

    if (isEditing) {
        return <Input value={value} onChange={e => setValue(e.target.value)} onBlur={onBlur} autoFocus />;
    }
    return <div onDoubleClick={onDoubleClick} data-testid={`cell-${row.id}-${column.id}`}>{value}</div>;
}


const GlossaryManagerPage = () => {
  const { t } = useTranslation();
  const [selectedGame, setSelectedGame] = useState(games[0]);
  const [data, setData] = useState(mockGlossaryData['v3-art']); // Initial data
  const [selectedFile, setSelectedFile] = useState('glossary_art.yml');
  const [filtering, setFiltering] = useState('');
  const [sorting, setSorting] = useState([]);

  const columns = [
    { accessorKey: 'id', header: 'ID', cell: info => info.getValue() },
    { accessorKey: 'source', header: 'Source Text', cell: info => info.getValue() },
    { accessorKey: 'translation', header: 'Translation', cell: EditableCell },
  ];

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    state: { globalFilter: filtering, sorting: sorting },
    onGlobalFilterChange: setFiltering,
    onSortingChange: setSorting,
    meta: {
        updateData: (rowIndex, columnId, value) => {
            setData(old =>
                old.map((row, index) => (index === rowIndex ? { ...old[rowIndex], [columnId]: value } : row))
            );
        }
    }
  });

  const handleGameChange = (value) => {
    setSelectedGame(value);
    // Reset selection when game changes
    setData([]);
    setSelectedFile('No file selected');
  };

  const onSelectTree = (selectedKeys, info) => {
    if (info.node.isLeaf) {
        const fileKey = info.node.key;
        setSelectedFile(info.node.title);
        setData(mockGlossaryData[fileKey] || []); // Load new data or empty array if not found
        setFiltering(''); // Reset filter on new data
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      <Row gutter={24}>
        {/* Column 1: Game Selection */}
        <Col span={4}>
          <Title level={5}>Game</Title>
          <Select defaultValue={selectedGame} style={{ width: '100%' }} onChange={handleGameChange}>
            {games.map(game => <Option key={game} value={game}>{game}</Option>)}
          </Select>
        </Col>

        {/* Column 2: Glossary File Tree */}
        <Col span={6}>
            <Title level={5}>Glossary Files</Title>
           <Tree defaultExpandAll treeData={glossaryFileTree[selectedGame]} onSelect={onSelectTree} />
        </Col>

        {/* Column 3: Data Table */}
        <Col span={14}>
            <Title level={5}>Content: {selectedFile}</Title>
           <Search
            placeholder="Filter content..."
            value={filtering}
            onChange={e => setFiltering(e.target.value)}
            style={{ marginBottom: 16 }}
            />
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              {table.getHeaderGroups().map(headerGroup => (
                <tr key={headerGroup.id}>
                  {headerGroup.headers.map(header => (
                    <th key={header.id} style={{ borderBottom: '2px solid black', padding: '8px', cursor: 'pointer' }} onClick={header.column.getToggleSortingHandler()}>
                      {flexRender(header.column.columnDef.header, header.getContext())}
                       {{ asc: ' 🔼', desc: ' 🔽' }[header.column.getIsSorted()] ?? null}
                    </th>
                  ))}
                </tr>
              ))}
            </thead>
            <tbody>
              {table.getRowModel().rows.map(row => (
                <tr key={row.id}>
                  {row.getVisibleCells().map(cell => (
                    <td key={cell.id} style={{ border: '1px solid #ddd', padding: '8px' }}>
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </Col>
      </Row>
    </div>
  );
};

export default GlossaryManagerPage;