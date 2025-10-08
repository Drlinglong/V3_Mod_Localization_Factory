import React, { useState, useEffect } from 'react';
import { Layout, Typography, Select, Tree, Spin } from 'antd';

const { Title, Paragraph } = Typography;
const { Sider, Content } = Layout;
const { Option } = Select;

// Mock API response for directory structure
const mockTreeData = {
    en: [
        {
            title: 'User Guides',
            key: 'en-user-guides',
            children: [
                { title: 'Getting Started.md', key: 'en/user-guides/getting-started.md', isLeaf: true },
                { title: 'Advanced Features.md', key: 'en/user-guides/advanced-features.md', isLeaf: true },
            ],
        },
        {
            title: 'API Reference',
            key: 'en-api-reference',
            children: [
                { title: 'Endpoints.md', key: 'en/api-reference/endpoints.md', isLeaf: true },
            ],
        },
    ],
    zh: [
        {
            title: '用户指南',
            key: 'zh-user-guides',
            children: [
                { title: '快速入门.md', key: 'zh/user-guides/getting-started.md', isLeaf: true },
                { title: '高级功能.md', key: 'zh/user-guides/advanced-features.md', isLeaf: true },
            ],
        },
    ],
};

// Mock file content
const mockFileContent = {
    'en/user-guides/getting-started.md': `
# Getting Started

Welcome to the Smart Localization Workbench v2.0!

This guide will walk you through the basic steps to complete your first translation project.
- Step 1: Upload your mod file.
- Step 2: Configure the translation settings.
- Step 3: Run the translation.
- Step 4: Download the result.
    `,
    'en/user-guides/advanced-features.md': `
# Advanced Features

Explore the powerful advanced features of our workbench.
- Incremental Updates
- Glossary Management
- Batch Processing
    `,
    'en/api-reference/endpoints.md': `
# API Reference

- \`/api/translate\`: POST, starts a new translation task.
- \`/api/status/:task_id\`: GET, checks the status of a task.
    `,
    'zh/user-guides/getting-started.md': `
# 快速入门

欢迎使用智能本地化工作台 v2.0！

本指南将引导您完成第一个翻译项目的基本步骤。
- 步骤一：上传您的MOD文件。
- 步骤二：配置翻译设置。
- 步骤三：运行翻译。
- 步骤四：下载结果。
    `,
    'zh/user-guides/advanced-features.md': `
# 高级功能

探索我们工作台强大的高级功能。
- 增量更新
- 词典管理
- 批量处理
    `,
};


// Mock API fetch functions
const fetchDocTree = (lang) => {
    return new Promise(resolve => {
        setTimeout(() => resolve(mockTreeData[lang] || []), 500);
    });
};

const fetchDocContent = (path) => {
    console.log(`Fetching content for path: ${path}`);
    return new Promise(resolve => {
        setTimeout(() => {
            resolve(mockFileContent[path] || 'Content not found.');
        }, 300); // Simulate network delay
    });
};


const Documentation = () => {
    const [selectedLang, setSelectedLang] = useState('en');
    const [treeData, setTreeData] = useState([]);
    const [treeLoading, setTreeLoading] = useState(true);

    const [selectedFile, setSelectedFile] = useState('en/user-guides/getting-started.md');
    const [content, setContent] = useState('');
    const [contentLoading, setContentLoading] = useState(true);

    // Effect for fetching the directory tree
    useEffect(() => {
        setTreeLoading(true);
        fetchDocTree(selectedLang).then(data => {
            setTreeData(data);
            setTreeLoading(false);
        });
    }, [selectedLang]);

    // Effect for fetching file content
    useEffect(() => {
        if (selectedFile) {
            setContentLoading(true);
            fetchDocContent(selectedFile).then(data => {
                setContent(data);
                setContentLoading(false);
            });
        }
    }, [selectedFile]);

    const handleLangChange = (value) => {
        setSelectedLang(value);
        // Maybe select a default file for the new language
        const defaultFile = value === 'zh' ? 'zh/user-guides/getting-started.md' : 'en/user-guides/getting-started.md';
        setSelectedFile(defaultFile);
    };

    const handleSelect = (selectedKeys, info) => {
        if (info.node.isLeaf && selectedKeys.length > 0) {
            setSelectedFile(selectedKeys[0]);
        }
    };

    return (
        <Layout style={{ padding: '24px 0', background: '#fff', height: '100%' }}>
            <Sider width={300} style={{ background: '#fff', borderRight: '1px solid #f0f0f0', padding: '10px', height: '100%', overflow: 'auto' }}>
                <div style={{ padding: '0 16px 16px 16px' }}>
                    <Title level={4}>文档导航</Title>
                    <Select value={selectedLang} style={{ width: '100%' }} onChange={handleLangChange}>
                        <Option value="en">English</Option>
                        <Option value="zh">中文</Option>
                    </Select>
                </div>
                {treeLoading ? (
                    <div style={{ textAlign: 'center', marginTop: '20px' }}><Spin /></div>
                ) : (
                    <Tree
                        showLine
                        defaultExpandAll
                        onSelect={handleSelect}
                        treeData={treeData}
                        selectedKeys={[selectedFile]}
                    />
                )}
            </Sider>
            <Content style={{ padding: '0 24px', minHeight: 280 }}>
                {contentLoading ? (
                     <div style={{ textAlign: 'center', marginTop: '50px' }}><Spin size="large" /></div>
                ) : (
                    <>
                        {/*
                            NOTE: A proper markdown renderer (like react-markdown) should be used here.
                            Using <pre> as a temporary solution.
                        */}
                        <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: '14px' }}>
                            {content}
                        </pre>
                    </>
                )}
            </Content>
        </Layout>
    );
};

export default Documentation;
