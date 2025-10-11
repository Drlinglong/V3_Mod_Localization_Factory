import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Layout, Typography, Menu } from 'antd';
import { ThemeProvider } from './ThemeContext';
import { NotificationProvider } from './context/NotificationContext';
import NotificationManager from './components/shared/NotificationManager';
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
    HourglassOutlined, // New icon for placeholder pages
    BuildOutlined, // New icon for placeholder pages
    BulbOutlined, // New icon for placeholder pages
} from '@ant-design/icons';
import './App.css';

// Import original pages
import OriginalHomepage from './pages/Homepage';
import OriginalDocumentation from './pages/Documentation';
import OriginalInitialTranslation from './pages/InitialTranslation';
import OriginalProjectManagement from './pages/ProjectManagement';

// Import new placeholder pages
import GlossaryManagerPage from './pages/GlossaryManagerPage';
import ProofreadingPage from './pages/ProofreadingPage';
import ToolsPage from './pages/ToolsPage';
import CICDPage from './pages/CICDPage';
import SettingsPage from './pages/SettingsPage';
import UnderDevelopmentPage from './pages/UnderDevelopmentPage'; // New
import UnderConstructionPage from './pages/UnderConstructionPage'; // New
import InConceptionPage from './pages/InConceptionPage'; // New

const { Header, Content, Footer, Sider } = Layout;
const { Title } = Typography;

const App = () => {
    const { t } = useTranslation();

    const menuItems = [
        {
            key: '/',
            icon: <HomeOutlined />,
            label: <Link to="/">{t('nav_home')}</Link>,
        },
        {
            key: '/docs',
            icon: <FileTextOutlined />,
            label: <Link to="/docs">{t('nav_docs')}</Link>,
        },
        {
            key: '/translation',
            icon: <RocketOutlined />,
            label: <Link to="/translation">{t('page_title_translation')}</Link>,
        },
        {
            key: '/glossary-manager',
            icon: <BookOutlined />,
            label: <Link to="/glossary-manager">{t('page_title_glossary_manager')}</Link>
        },
        {
            key: '/proofreading',
            icon: <ExperimentOutlined />,
            label: <Link to="/proofreading">{t('page_title_proofreading')}</Link>,
        },
        {
            key: '/project-management',
            icon: <DashboardOutlined />,
            label: <Link to="/project-management">{t('page_title_project_management')}</Link>,
        },
        {
            key: '/cicd',
            icon: <BranchesOutlined />,
            label: <Link to="/cicd">{t('page_title_cicd')}</Link>,
        },
        {
            key: '/tools',
            icon: <ToolOutlined />,
            label: <Link to="/tools">{t('page_title_tools')}</Link>,
        },
        {
            key: '/settings',
            icon: <SettingOutlined />,
            label: <Link to="/settings">{t('page_title_settings')}</Link>,
        },
        {
            key: '/under-development',
            icon: <HourglassOutlined />,
            label: <Link to="/under-development">{t('page_title_under_development')}</Link>,
        },
        {
            key: '/under-construction',
            icon: <BuildOutlined />,
            label: <Link to="/under-construction">{t('page_title_under_construction')}</Link>,
        },
        {
            key: '/in-conception',
            icon: <BulbOutlined />,
            label: <Link to="/in-conception">{t('page_title_in_conception')}</Link>,
        },
    ];

    return (
        <NotificationProvider>
            <ThemeProvider>
                <Router>
                    <NotificationManager />
                    <Layout style={{ minHeight: '100vh' }}>
                        <Header>
                    <div className="logo" />
                    <Title style={{ color: 'white', lineHeight: '64px', float: 'left' }} level={3}>
                        <ToolOutlined /> {t('app_title')}
                    </Title>
                </Header>
                <Layout>
                    <Sider width={200} style={{ background: '#fff' }}>
                        <Menu
                            mode="inline"
                            defaultSelectedKeys={['/']}
                            style={{ height: '100%', borderRight: 0 }}
                            items={menuItems}
                        />
                    </Sider>
                    <Layout style={{ padding: '0 24px 24px' }}>
                        <Content
                            style={{
                                background: '#fff',
                                padding: 24,
                                margin: 0,
                                minHeight: 280,
                            }}
                        >
                            <Routes>
                                <Route path="/" element={<OriginalHomepage />} />
                                <Route path="/docs" element={<OriginalDocumentation />} />
                                <Route path="/translation" element={<OriginalInitialTranslation />} />
                                <Route path="/glossary-manager" element={<GlossaryManagerPage />} />
                                <Route path="/proofreading" element={<ProofreadingPage />} />
                                <Route path="/tools" element={<ToolsPage />} />
                                <Route path="/cicd" element={<CICDPage />} />
                                <Route path="/project-management" element={<OriginalProjectManagement />} />
                                <Route path="/settings" element={<SettingsPage />} />
                                <Route path="/under-development" element={<UnderDevelopmentPage />} />
                                <Route path="/under-construction" element={<UnderConstructionPage />} />
                                <Route path="/in-conception" element={<InConceptionPage />} />
                            </Routes>
                        </Content>
                    </Layout>
                </Layout>
                <Footer style={{ textAlign: 'center' }}>
                    {t('footer_text')}
                </Footer>
            </Layout>
        </Router>
    </ThemeProvider>
    </NotificationProvider>
    );
};

export default App;
