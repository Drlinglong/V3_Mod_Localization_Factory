import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { MantineProvider, AppShell, Burger, Group, NavLink } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import '@mantine/core/styles.css';

import { ThemeProvider } from './ThemeContext';
import { NotificationProvider } from './context/NotificationContext';
import NotificationManager from './components/shared/NotificationManager';

import './App.css';

// Import pages...
import OriginalHomepage from './pages/HomePage';
import OriginalDocumentation from './pages/Documentation';
import OriginalInitialTranslation from './pages/InitialTranslation';
import OriginalProjectManagement from './pages/ProjectManagement';
import GlossaryManagerPage from './pages/GlossaryManagerPage';
import ProofreadingPage from './pages/ProofreadingPage';
import ToolsPage from './pages/ToolsPage';
import CICDPage from './pages/CICDPage';
import SettingsPage from './pages/SettingsPage';
import UnderDevelopmentPage from './pages/UnderDevelopmentPage';
import UnderConstructionPage from './pages/UnderConstructionPage';
import InConceptionPage from './pages/InConceptionPage';
import Breadcrumbs from './components/shared/Breadcrumbs';

import { useParams } from 'react-router-dom';

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
    { path: '/', element: <OriginalHomepage />, i18nKey: 'nav_home', showInMenu: true },
    { path: '/docs', element: <OriginalDocumentation />, i18nKey: 'nav_docs', showInMenu: true },
    { path: '/translation', element: <OriginalInitialTranslation />, i18nKey: 'page_title_translation', showInMenu: true },
    { path: '/glossary-manager', element: <GlossaryManagerPage />, i18nKey: 'page_title_glossary_manager', showInMenu: true },
    { path: '/proofreading', element: <ProofreadingPage />, i18nKey: 'page_title_proofreading', showInMenu: true },
    { path: '/project-management', element: <OriginalProjectManagement />, i18nKey: 'page_title_project_management', showInMenu: true },
    { path: '/project-management/:projectId', element: <OriginalProjectManagement />, breadcrumb: DynamicProjectBreadcrumb, showInMenu: false },
    { path: '/cicd', element: <CICDPage />, i18nKey: 'page_title_cicd', showInMenu: true },
    { path: '/tools', element: <ToolsPage />, i18nKey: 'page_title_tools', showInMenu: true },
    { path: '/settings', element: <SettingsPage />, i18nKey: 'page_title_settings', showInMenu: true },
    { path: '/under-development', element: <UnderDevelopmentPage />, i18nKey: 'page_title_under_development', showInMenu: true },
    { path: '/under-construction', element: <UnderConstructionPage />, i18nKey: 'page_title_under_construction', showInMenu: true },
    { path: '/in-conception', element: <InConceptionPage />, i18nKey: 'page_title_in_conception', showInMenu: true },
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
    const [opened, { toggle }] = useDisclosure();
    const { t } = useTranslation();

    return (
        <MantineProvider defaultColorScheme="dark">
            <NotificationProvider>
                <ThemeProvider>
                    <Router>
                        <NotificationManager />
                        <AppShell
                            header={{ height: 60 }}
                            navbar={{ width: 300, breakpoint: 'sm', collapsed: { mobile: !opened } }}
                            padding="md"
                        >
                            <AppShell.Header>
                                <Group h="100%" px="md">
                                    <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
                                    {t('app_title')}
                                </Group>
                            </AppShell.Header>
                            <AppShell.Navbar p="md">
                                {appRouteConfig.filter(route => route.showInMenu).map((route) => (
                                    <NavLink
                                        key={route.path}
                                        label={t(route.i18nKey)}
                                        component={Link}
                                        to={route.path}
                                        onClick={toggle}
                                    />
                                ))}
                            </AppShell.Navbar>
                            <AppShell.Main>
                                <Routes>
                                    {appRouteConfig.map(route => (
                                        <Route key={route.path} path={route.path} element={route.element} />
                                    ))}
                                </Routes>
                            </AppShell.Main>
                        </AppShell>
                    </Router>
                </ThemeProvider>
            </NotificationProvider>
        </MantineProvider>
    );
};

export default App;
