import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Layout, Typography, Select, Tree, Spin } from 'antd';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';

const { Title } = Typography;
const { Sider, Content } = Layout;
const { Option } = Select;

const fetchDocTree = async () => {
    try {
        const response = await axios.get('/api/docs-tree');
        return response.data;
    } catch (error) {
        console.error("Failed to fetch doc tree:", error);
        return {}; // Return empty object on error
    }
};

const fetchDocContent = async (path) => {
    if (!path) return 'No file selected.';
    console.log(`Fetching content from API for path: ${path}`);
    try {
        // Use axios to call the new backend endpoint
        const response = await axios.get('/api/doc-content', {
            params: { path: path }
        });
        return response.data;
    } catch (error) {
        console.error(`Failed to fetch doc content for path ${path}:`, error);
        return 'Content could not be loaded. Please check the console for more details.';
    }
};

const Documentation = () => {
    const { t } = useTranslation();
    const [selectedLang, setSelectedLang] = useState('en');
    const [fullTreeData, setFullTreeData] = useState({});
    const [treeData, setTreeData] = useState([]);
    const [treeLoading, setTreeLoading] = useState(true);

    const [selectedFile, setSelectedFile] = useState('en/index.md');
    const [content, setContent] = useState('');
    const [contentLoading, setContentLoading] = useState(true);

    // Effect for fetching the entire directory tree once on component mount
    useEffect(() => {
        setTreeLoading(true);
        fetchDocTree().then(data => {
            setFullTreeData(data);
            setTreeData(data[selectedLang] || []);
            setTreeLoading(false);
        });
    }, []);

    // Effect for updating the displayed tree when language changes
    useEffect(() => {
        setTreeData(fullTreeData[selectedLang] || []);
    }, [selectedLang, fullTreeData]);


    // Effect for fetching file content when selectedFile changes
    useEffect(() => {
        if (selectedFile) {
            setContentLoading(true);
            fetchDocContent(selectedFile).then(data => {
                setContent(data);
                setContentLoading(false);
            });
        } else {
            // No file selected, clear content
            setContent('');
        }
    }, [selectedFile]);

    const handleLangChange = (value) => {
        setSelectedLang(value);
        // Select a default file for the new language
        const defaultFile = value === 'zh'
            ? 'zh/index.md'
            : 'en/index.md';

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
                    <Title level={4}>{t('doc_nav_title')}</Title>
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
            <Content style={{ padding: '24px', minHeight: 280, overflow: 'auto', height: '100%' }}>
                {contentLoading ? (
                     <div style={{ textAlign: 'center', marginTop: '50px' }}><Spin size="large" /></div>
                ) : (
                    <ReactMarkdown>
                        {content}
                    </ReactMarkdown>
                )}
            </Content>
        </Layout>
    );
};

export default Documentation;
