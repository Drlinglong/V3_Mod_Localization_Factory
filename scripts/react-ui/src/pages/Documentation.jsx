import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Layout, Typography, Select, Tree, Spin } from 'antd';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';

const { Title } = Typography;
const { Sider, Content } = Layout;
const { Option } = Select;

// Map language codes to their display names for a better UI.
const languageNameMap = {
    en: 'English',
    zh: '中文',
};

const getLanguageName = (code) => {
    return languageNameMap[code] || code; // Fallback to the code itself if no mapping exists
};


const fetchDocLanguages = async () => {
    try {
        const response = await axios.get('/api/docs-languages');
        return response.data;
    } catch (error) {
        console.error("Failed to fetch doc languages:", error);
        return ['en']; // Fallback to 'en'
    }
};

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
    const { t, i18n } = useTranslation();
    const [availableLangs, setAvailableLangs] = useState([]);
    const [selectedLang, setSelectedLang] = useState('');
    const [fullTreeData, setFullTreeData] = useState({});
    const [treeData, setTreeData] = useState([]);
    const [treeLoading, setTreeLoading] = useState(true);

    const [selectedFile, setSelectedFile] = useState('');
    const [content, setContent] = useState('');
    const [contentLoading, setContentLoading] = useState(true);

    // Effect for fetching languages and the entire directory tree on component mount
    useEffect(() => {
        setTreeLoading(true);
        Promise.all([fetchDocLanguages(), fetchDocTree()]).then(([langs, tree]) => {
            setAvailableLangs(langs);
            const initialLang = langs.includes(i18n.language) ? i18n.language : (langs[0] || 'en');
            setSelectedLang(initialLang);

            setFullTreeData(tree);
            setTreeData(tree[initialLang] || []);

            // Set a default file to display initially
            const defaultFile = `${initialLang}/index.md`;
            setSelectedFile(defaultFile);

            setTreeLoading(false);
        });
    }, [i18n.language]);

    // Effect for updating the displayed tree when language changes
    useEffect(() => {
        if (!treeLoading) { // Avoid running on initial load before fullTreeData is set
            setTreeData(fullTreeData[selectedLang] || []);
        }
    }, [selectedLang, fullTreeData, treeLoading]);

    // Effect for fetching file content when selectedFile changes
    useEffect(() => {
        if (selectedFile) {
            setContentLoading(true);
            fetchDocContent(selectedFile).then(data => {
                setContent(data);
                setContentLoading(false);
            });
        } else {
            setContent('');
        }
    }, [selectedFile]);

    const handleLangChange = (value) => {
        setSelectedLang(value);
        // Select a default file for the new language
        const defaultFile = `${value}/index.md`;
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
                    <Select value={selectedLang} style={{ width: '100%' }} onChange={handleLangChange} loading={!availableLangs.length}>
                        {availableLangs.map(lang => (
                            <Option key={lang} value={lang}>
                                {getLanguageName(lang)}
                            </Option>
                        ))}
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
                    <div style={{ textAlign: 'left' }}>
                        <ReactMarkdown>
                            {content}
                        </ReactMarkdown>
                    </div>
                )}
            </Content>
        </Layout>
    );
};

export default Documentation;
