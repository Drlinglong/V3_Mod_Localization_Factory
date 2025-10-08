import React, { useState } from 'react';
import { Layout, Typography, Tabs } from 'antd';
import {
    ToolOutlined,
    HomeOutlined,
    FileTextOutlined,
    RocketOutlined,
    BookOutlined,
    ExperimentOutlined,
    SettingOutlined,
    BranchesOutlined,
    DashboardOutlined,
} from '@ant-design/icons';
import './App.css';
import InitialTranslation from './pages/InitialTranslation';
import Homepage from './pages/Homepage';
import ProjectManagement from './pages/ProjectManagement';
import Documentation from './pages/Documentation';

const { Header, Content, Footer } = Layout;
const { Title } = Typography;

// Placeholder components for other pages
const Placeholder = ({ title }) => (
    <div style={{ padding: '20px' }}>
        <Title level={2}>{title}</Title>
        <p>This page is under construction.</p>
    </div>
);

const App = () => {
    const [activeTab, setActiveTab] = useState('home');

    const handleTabChange = (key) => {
        setActiveTab(key);
    };

    const handleStartProject = () => {
        setActiveTab('translation');
    };

    const items = [
        {
            key: 'home',
            label: (
                <span>
                    <HomeOutlined />
                    主页
                </span>
            ),
            children: <Homepage onStart={handleStartProject} />,
        },
        {
            key: 'docs',
            label: (
                <span>
                    <FileTextOutlined />
                    文档
                </span>
            ),
            children: <Documentation />,
        },
        {
            key: 'translation',
            label: (
                <span>
                    <RocketOutlined />
                    初次汉化
                </span>
            ),
            children: <InitialTranslation />,
        },
        {
            key: 'projects',
            label: (
                <span>
                    <DashboardOutlined />
                    项目管理
                </span>
            ),
            children: <ProjectManagement />,
        },
        {
            key: 'glossary',
            label: (
                <span>
                    <BookOutlined />
                    词典管理
                </span>
            ),
            children: <Placeholder title="词典管理" />,
        },
        {
            key: 'proofreading',
            label: (
                <span>
                    <ExperimentOutlined />
                    文件校对
                </span>
            ),
            children: <Placeholder title="文件校对" />,
        },
        {
            key: 'tools',
            label: (
                <span>
                    <ToolOutlined />
                    其他工具
                </span>
            ),
            children: <Placeholder title="其他工具" />,
        },
        {
            key: 'cicd',
            label: (
                <span>
                    <BranchesOutlined />
                    CI/CD
                </span>
            ),
            children: <Placeholder title="CI/CD" />,
        },
        {
            key: 'settings',
            label: (
                <span>
                    <SettingOutlined />
                    控制面板
                </span>
            ),
            children: <Placeholder title="控制面板" />,
        },
    ];

    return (
        <Layout className="layout">
            <Header>
                <div className="logo" />
                <Title style={{ color: 'white', lineHeight: '64px', float: 'left' }} level={3}>
                    <ToolOutlined /> Paradox Mod Localization Factory
                </Title>
            </Header>
            <Content style={{ padding: '0 50px', marginTop: '24px' }}>
                <div className="site-layout-content" style={{ background: '#fff', padding: '0 24px 24px 24px' }}>
                    <Tabs activeKey={activeTab} onChange={handleTabChange} items={items} />
                </div>
            </Content>
            <Footer style={{ textAlign: 'center' }}>
                Paradox Mod Localization Factory ©2025 Created by Jules
            </Footer>
        </Layout>
    );
};

export default App;
