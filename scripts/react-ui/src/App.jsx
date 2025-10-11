import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Layout, Typography, Menu } from 'antd';
import { ThemeProvider } from './ThemeContext';
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

    const menuItems = appRouteConfig
        .filter(route => route.showInMenu)
        .map(route => ({
            key: route.path,
            icon: route.icon,
            label: <Link to={route.path}>{t(route.i18nKey)}</Link>,
        }));

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
                    <Sider width={200} style={{ background: '#fff' }}>
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
