import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Grid, Title, Select, Loader, Paper, ScrollArea } from '@mantine/core';
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import axios from 'axios';

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

    const handleSelect = (key) => {
        setSelectedFile(key);
    };

    // A simple recursive component to render the file tree
    const FileTree = ({ nodes, onSelect, selectedKey }) => {
        return (
            <div>
                {nodes.map(node => (
                    <div key={node.key} style={{ paddingLeft: '20px' }}>
                        {node.isLeaf ? (
                             <a
                                href="#"
                                onClick={(e) => { e.preventDefault(); onSelect(node.key); }}
                                style={{
                                    display: 'block',
                                    padding: '5px',
                                    borderRadius: '4px',
                                    backgroundColor: node.key === selectedKey ? 'var(--mantine-color-blue-light)' : 'transparent',
                                    color: node.key === selectedKey ? 'var(--mantine-color-blue-filled)' : 'inherit',
                                    textDecoration: 'none'
                                }}
                            >
                                {node.title}
                            </a>
                        ) : (
                            <div>
                                <strong>{node.title}</strong>
                                {node.children && <FileTree nodes={node.children} onSelect={onSelect} selectedKey={selectedKey} />}
                            </div>
                        )}
                    </div>
                ))}
            </div>
        );
    };

    return (
        <Grid style={{ height: 'calc(100vh - 120px)' }}>
            <Grid.Col span={4}>
                <Paper withBorder p="md" style={{ height: '100%' }}>
                    <ScrollArea style={{ height: '100%' }}>
                        <Title order={4}>{t('doc_nav_title')}</Title>
                        <Select
                            value={selectedLang}
                            onChange={setSelectedLang}
                            data={availableLangs.map(lang => ({ value: lang, label: getLanguageName(lang) }))}
                            disabled={!availableLangs.length}
                            style={{ marginBottom: '20px' }}
                        />
                        {treeLoading ? (
                            <div style={{ textAlign: 'center', marginTop: '20px' }}><Loader /></div>
                        ) : (
                            <FileTree nodes={treeData} onSelect={handleSelect} selectedKey={selectedFile} />
                        )}
                    </ScrollArea>
                </Paper>
            </Grid.Col>
            <Grid.Col span={8}>
                <Paper withBorder p="md" style={{ height: '100%' }}>
                    <ScrollArea style={{ height: '100%' }}>
                        {contentLoading ? (
                            <div style={{ textAlign: 'center', marginTop: '50px' }}><Loader size="xl" /></div>
                        ) : (
                            <div style={{ textAlign: 'left' }}>
                                <ReactMarkdown rehypePlugins={[rehypeRaw]}>
                                    {content}
                                </ReactMarkdown>
                            </div>
                        )}
                    </ScrollArea>
                </Paper>
            </Grid.Col>
        </Grid>
    );
};

export default Documentation;
