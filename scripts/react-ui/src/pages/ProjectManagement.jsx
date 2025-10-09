import React, { useState, useEffect } from 'react';
import { Typography, Select, Space, Row, Col, Card, Table, Tag, Button, Tabs, Empty } from 'antd';
import { ArrowLeftOutlined, ArrowRightOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;
const { Option } = Select;

// Mock data for projects
const mockProjects = [
    { id: 'project1', name: '甲MOD v1.2' },
    { id: 'project2', name: '乙MOD v2.0' },
    { id: 'project3', name: '丙MOD v3.5' },
];

// Mock data for project details - this is the initial state
const initialMockProjectDetails = {
    project1: {
        overview: { totalFiles: 15, translated: 80, toBeProofread: 35, glossary: 'my_glossary.json' },
        files: [
            { key: '1', name: 'file_A.yml', lines: 150, status: 'translated', progress: '150 / 150', notes: '无', actions: ['查看', '重译'] },
            { key: '2', name: 'file_B.yml', lines: 200, status: 'in_progress', progress: '50 / 200', notes: '部分语句不通顺', actions: ['继续校对'] },
            { key: '3', name: 'file_C.yml', lines: 120, status: 'failed', progress: '0 / 120', notes: 'API翻译失败', actions: ['重试', '查看日志'] },
            { key: '4', name: 'file_D.yml', lines: 80, status: 'pending', progress: '0 / 80', notes: '', actions: ['翻译此文件'] },
        ],
    },
    project2: {
        overview: { totalFiles: 10, translated: 95, toBeProofread: 10, glossary: 'project2_glossary.json' },
        files: [ { key: '1', name: 'another_file.yml', lines: 100, status: 'translated', progress: '100 / 100', notes: '无', actions: ['查看'] } ]
    },
    project3: {
        overview: { totalFiles: 5, translated: 100, toBeProofread: 0, glossary: 'project3_glossary.json' },
        files: [ { key: '1', name: 'final_mod_file.yml', lines: 50, status: 'translated', progress: '50 / 50', notes: '已完成', actions: ['查看'] } ]
    }
};

const statusFlow = ['pending', 'in_progress', 'translated']; // Defines the order of columns

const ProjectManagement = () => {
    const [selectedProject, setSelectedProject] = useState(null);
    const [projectDetails, setProjectDetails] = useState(null);

    useEffect(() => {
        if (selectedProject && initialMockProjectDetails[selectedProject]) {
            // Deep copy the mock data to allow for state changes
            setProjectDetails(JSON.parse(JSON.stringify(initialMockProjectDetails[selectedProject])));
        } else {
            setProjectDetails(null);
        }
    }, [selectedProject]);

    const handleProjectChange = (value) => {
        setSelectedProject(value);
    };

    const handleProofread = (file) => {
        console.log(`Preparing to navigate to proofreading for file: ${file.name}`);
        // In the future, this will handle the logic to switch tabs and pass the file info.
    };

    const fileTableColumns = [
        { title: '文件名', dataIndex: 'name', key: 'name' },
        { title: '行数', dataIndex: 'lines', key: 'lines' },
        {
            title: '状态',
            dataIndex: 'status',
            key: 'status',
            render: status => {
                let color = 'grey';
                let text = '未处理';
                if (status === 'translated') { color = 'green'; text = '✅ 已翻译'; }
                else if (status === 'failed') { color = 'red'; text = '🔴 翻译失败'; }
                else if (status === 'pending') { color = 'blue'; text = '⚪ 待处理'; }
                else if (status === 'in_progress') { color = 'gold'; text = '▶️ 进行中'; }
                return <Tag color={color}>{text}</Tag>;
            }
        },
        { title: '校对进度', dataIndex: 'progress', key: 'progress' },
        { title: '备注', dataIndex: 'notes', key: 'notes' },
        {
            title: '操作',
            key: 'actions',
            render: (_, record) => (
                <Space size="middle">
                    {record.actions.map(action => {
                        const isProofreadAction = action === '继续校对';
                        return (
                            <Button
                                type="link"
                                key={action}
                                onClick={isProofreadAction ? () => handleProofread(record) : null}
                            >
                                {action}
                            </Button>
                        );
                    })}
                </Space>
            ),
        },
    ];

    const handleStatusChange = (fileKey, direction) => {
        const currentFiles = projectDetails.files;
        const fileIndex = currentFiles.findIndex(f => f.key === fileKey);
        if (fileIndex === -1) return;

        const currentStatus = currentFiles[fileIndex].status;
        let currentStatusIndex = statusFlow.indexOf(currentStatus);

        if (currentStatus === 'failed') {
            currentStatusIndex = 0;
        }

        let newStatusIndex = currentStatusIndex;
        if (direction === 'right') {
            newStatusIndex = Math.min(currentStatusIndex + 1, statusFlow.length - 1);
        } else if (direction === 'left') {
            newStatusIndex = Math.max(currentStatusIndex - 1, 0);
        }

        if (statusFlow[newStatusIndex] !== currentStatus) {
            const updatedFiles = [...currentFiles];
            updatedFiles[fileIndex].status = statusFlow[newStatusIndex];
            setProjectDetails({ ...projectDetails, files: updatedFiles });
        }
    };

    const renderTaskCard = (file) => {
        const currentStatus = file.status === 'failed' ? 'pending' : file.status;
        const statusIndex = statusFlow.indexOf(currentStatus);

        return (
            <Card key={file.key} title={file.name} style={{ marginBottom: '10px' }}
                actions={[
                    <Button key="left" icon={<ArrowLeftOutlined />} disabled={statusIndex === 0} onClick={() => handleStatusChange(file.key, 'left')} />,
                    <Button key="right" icon={<ArrowRightOutlined />} disabled={statusIndex === statusFlow.length - 1} onClick={() => handleStatusChange(file.key, 'right')} />
                ]}
            >
                <p>行数: {file.lines}</p>
                <p>进度: {file.progress}</p>
                {file.notes && <p>备注: {file.notes}</p>}
            </Card>
        );
    };

    const renderOverview = () => (
        <div>
            <Title level={4}>项目概览: {mockProjects.find(p => p.id === selectedProject)?.name}</Title>
            <Row gutter={16}>
                <Col span={6}><Card title="文件总数">{projectDetails.overview.totalFiles}</Card></Col>
                <Col span={6}><Card title="已翻译">{projectDetails.overview.translated}%</Card></Col>
                <Col span={6}><Card title="待校对">{projectDetails.overview.toBeProofread}%</Card></Col>
                <Col span={6}><Card title="使用词典">{projectDetails.overview.glossary}</Card></Col>
            </Row>
            <Title level={4} style={{ marginTop: '20px' }}>文件详情列表</Title>
            <Table columns={fileTableColumns} dataSource={projectDetails.files} />
        </div>
    );

    const renderTaskBoard = () => {
        const files = projectDetails?.files || [];
        const todoFiles = files.filter(f => f.status === 'pending' || f.status === 'failed');
        const inProgressFiles = files.filter(f => f.status === 'in_progress');
        const doneFiles = files.filter(f => f.status === 'translated');

        return (
            <Row gutter={16}>
                <Col span={8}><Title level={4}>To Do</Title>{todoFiles.map(renderTaskCard)}</Col>
                <Col span={8}><Title level={4}>In Progress</Title>{inProgressFiles.map(renderTaskCard)}</Col>
                <Col span={8}><Title level={4}>Done</Title>{doneFiles.map(renderTaskCard)}</Col>
            </Row>
        );
    };

    return (
        <div>
            <Title level={2}>项目管理中心</Title>
            <Space align="center" style={{ marginBottom: '20px' }}>
                <Text>请选择要管理的项目:</Text>
                <Select style={{ width: 240 }} placeholder="选择一个项目" onChange={handleProjectChange} allowClear>
                    {mockProjects.map(project => (<Option key={project.id} value={project.id}>{project.name}</Option>))}
                </Select>
            </Space>

                        {selectedProject ? (
                            <Tabs
                                defaultActiveKey="overview"
                                items={[
                                    {
                                        label: '概览',
                                        key: 'overview',
                                        children: projectDetails ? renderOverview() : null, // Content handles its own state
                                    },
                                    {
                                        label: '任务看板',
                                        key: 'taskboard',
                                        children: projectDetails ? renderTaskBoard() : null, // Content handles its own state
                                    },
                                ]}
                            />
                        ) : (
                            <div style={{ marginTop: 20, textAlign: 'center' }}>
                                <Empty description="请从上方选择一个项目以查看详情" />
                            </div>
                        )}        </div>
    );
};

export default ProjectManagement;
