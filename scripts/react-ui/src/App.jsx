import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Layout, Typography, Menu } from 'antd';
import { ThemeProvider } from './ThemeContext';
import {
    ToolOutlined,
    HourglassOutlined, // New icon for placeholder pages
    BuildOutlined, // New icon for placeholder pages
    BulbOutlined, // New icon for placeholder pages
} from '@ant-design/icons';

// Custom Icons
import HomeIcon from './assets/icons/HomeIcon';
import DocsIcon from './assets/icons/DocsIcon';
import TranslationIcon from './assets/icons/TranslationIcon';
import GlossaryManagerIcon from './assets/icons/GlossaryManagerIcon';
import ProofreadingIcon from './assets/icons/ProofreadingIcon';
import ProjectManagementIcon from './assets/icons/ProjectManagementIcon';
import CICDIcon from './assets/icons/CICDIcon';
import ToolsIcon from './assets/icons/ToolsIcon';
import SettingsIcon from './assets/icons/SettingsIcon';

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
import Breadcrumbs from './components/shared/Breadcrumbs';

import { useParams } from 'react-router-dom';

const { Header, Content, Footer, Sider } = Layout;
const { Title } = Typography;

// --- Breadcrumb Generation ---
const LocalizedBreadcrumb = ({ match }) => {
    const { t } = useTranslation();
    const { i18nKey } = match.route;
    return <>{t(i18nKey)}</>;
};

const DynamicProjectBreadcrumb = () => {
    const { projectId } = useParams();
    return <span>{projectId.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}</span>;
};

// --- Single Source of Truth for Routing ---
const appRouteConfig = [
    { path: '/', element: <OriginalHomepage />, i18nKey: 'nav_home', icon: <HomeOutlined />, showInMenu: true },
    { path: '/docs', element: <OriginalDocumentation />, i18nKey: 'nav_docs', icon: <FileTextOutlined />, showInMenu: true },
    { path: '/translation', element: <OriginalInitialTranslation />, i18nKey: 'page_title_translation', icon: <RocketOutlined />, showInMenu: true },
    { path: '/glossary-manager', element: <GlossaryManagerPage />, i18nKey: 'page_title_glossary_manager', icon: <BookOutlined />, showInMenu: true },
    { path: '/proofreading', element: <ProofreadingPage />, i18nKey: 'page_title_proofreading', icon: <ExperimentOutlined />, showInMenu: true },
    { path: '/project-management', element: <OriginalProjectManagement />, i18nKey: 'page_title_project_management', icon: <DashboardOutlined />, showInMenu: true },
    { path: '/project-management/:projectId', element: <OriginalProjectManagement />, breadcrumb: DynamicProjectBreadcrumb, showInMenu: false },
    { path: '/cicd', element: <CICDPage />, i18nKey: 'page_title_cicd', icon: <BranchesOutlined />, showInMenu: true },
    { path: '/tools', element: <ToolsPage />, i18nKey: 'page_title_tools', icon: <ToolOutlined />, showInMenu: true },
    { path: '/settings', element: <SettingsPage />, i18nKey: 'page_title_settings', icon: <SettingOutlined />, showInMenu: true },
    { path: '/under-development', element: <UnderDevelopmentPage />, i18nKey: 'page_title_under_development', icon: <HourglassOutlined />, showInMenu: true },
    { path: '/under-construction', element: <UnderConstructionPage />, i18nKey: 'page_title_under_construction', icon: <BuildOutlined />, showInMenu: true },
    { path: '/in-conception', element: <InConceptionPage />, i18nKey: 'page_title_in_conception', icon: <BulbOutlined />, showInMenu: true },
];

export const routes = appRouteConfig.map(route => {
    if (route.breadcrumb) { // Handle special cases like DynamicProjectBreadcrumb
        return { path: route.path, breadcrumb: route.breadcrumb };
    }
    if (!route.i18nKey) { // Handle routes that shouldn't have a breadcrumb
        return { path: route.path, breadcrumb: null };
    }
    return {
        path: route.path,
        breadcrumb: LocalizedBreadcrumb,
        i18nKey: route.i18nKey,
    };
});


const App = () => {
    const { t } = useTranslation();
    const [collapsed, setCollapsed] = useState(true);

    const menuItems = [
        {
            key: '/',
            icon: <HomeIcon />,
            label: <Link to="/">{t('nav_home')}</Link>,
        },
        {
            key: '/docs',
            icon: <DocsIcon />,
            label: <Link to="/docs">{t('nav_docs')}</Link>,
        },
        {
            key: '/translation',
            icon: <TranslationIcon />,
            label: <Link to="/translation">{t('page_title_translation')}</Link>,
        },
        {
            key: '/glossary-manager',
            icon: <GlossaryManagerIcon />,
            label: <Link to="/glossary-manager">{t('page_title_glossary_manager')}</Link>
        },
        {
            key: '/proofreading',
            icon: <ProofreadingIcon />,
            label: <Link to="/proofreading">{t('page_title_proofreading')}</Link>,
        },
        {
            key: '/project-management',
            icon: <ProjectManagementIcon />,
            label: <Link to="/project-management">{t('page_title_project_management')}</Link>,
        },
        {
            key: '/cicd',
            icon: <CICDIcon />,
            label: <Link to="/cicd">{t('page_title_cicd')}</Link>,
        },
        {
            key: '/tools',
            icon: <ToolsIcon />,
            label: <Link to="/tools">{t('page_title_tools')}</Link>,
        },
        {
            key: '/settings',
            icon: <SettingsIcon />,
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
        <ThemeProvider>
            <Router>
                <Layout style={{ minHeight: '100vh' }}>
                    <Header>
                    <div className="logo" />
                    <Title style={{ color: 'white', lineHeight: '64px', float: 'left' }} level={3}>
                        <ToolOutlined /> {t('app_title')}
                    </Title>
                </Header>
                <Layout>
                    <Sider
                        collapsible
                        collapsed={collapsed}
                        onMouseEnter={() => setCollapsed(false)}
                        onMouseLeave={() => setCollapsed(true)}
                        trigger={null}
                        width={200}
                        style={{ background: '#fff', transition: 'width 0.2s' }}
                    >
                        <Menu
                            mode="inline"
                            defaultSelectedKeys={['/']}
                            style={{ height: '100%', borderRight: 0 }}
                            items={menuItems}
                        />
                    </Sider>
                    <Layout style={{ padding: '0 24px 24px' }}>
                        <Breadcrumbs />
                        <Content
                            style={{
                                background: '#fff',
                                padding: 24,
                                margin: 0,
                                minHeight: 280,
                            }}
                        >
                            <Routes>
                                {appRouteConfig.map(route => (
                                    <Route key={route.path} path={route.path} element={route.element} />
                                ))}
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
    );
};

export default App;
