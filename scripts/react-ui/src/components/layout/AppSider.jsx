import React, { useState } from 'react';
import { Stack, Tooltip, UnstyledButton, rem, Text, Box } from '@mantine/core';
import {
    IconHome2,
    IconBook,
    IconLanguage,
    IconVocabulary,
    IconChecklist,
    IconBriefcase,
    IconGitBranch,
    IconTools,
    IconSettings,
    IconCrane,
    IconBulb,
    IconCode,
} from '@tabler/icons-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import styles from './Layout.module.css';

// Navigation items configuration
const navItems = [
    { icon: IconHome2, label: 'nav_home', path: '/' },
    { icon: IconBook, label: 'nav_docs', path: '/docs' },
    { icon: IconLanguage, label: 'page_title_translation', path: '/translation' },
    { icon: IconVocabulary, label: 'page_title_glossary_manager', path: '/glossary-manager' },
    { icon: IconChecklist, label: 'page_title_proofreading', path: '/proofreading' },
    { icon: IconBriefcase, label: 'page_title_project_management', path: '/project-management' },
    { icon: IconGitBranch, label: 'page_title_cicd', path: '/cicd' },
    { icon: IconTools, label: 'page_title_tools', path: '/tools' },
    { icon: IconSettings, label: 'page_title_settings', path: '/settings' },
];

const developmentItems = [
    { icon: IconCode, label: 'page_title_under_development', path: '/under-development' },
    { icon: IconCrane, label: 'page_title_under_construction', path: '/under-construction' },
    { icon: IconBulb, label: 'page_title_in_conception', path: '/in-conception' },
];

function NavbarLink({ icon: Icon, label, active, onClick, expanded }) {
    const { t } = useTranslation();

    return (
        <Tooltip label={t(label)} position="right" transitionProps={{ duration: 0 }} disabled={expanded}>
            <UnstyledButton
                onClick={onClick}
                data-active={active || undefined}
                className={styles.navLink}
                style={{
                    width: '100%',
                    padding: '10px', /* equivalent to theme.spacing.xs approximately */
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: expanded ? 'flex-start' : 'center',
                }}
            >
                <Icon className={styles.icon} style={{ width: rem(22), height: rem(22) }} stroke={1.5} />
                {expanded && (
                    <Text size="sm" ml="md" style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', fontFamily: 'var(--font-body)' }}>
                        {t(label)}
                    </Text>
                )}
            </UnstyledButton>
        </Tooltip>
    );
}

export function AppSider() {
    const navigate = useNavigate();
    const location = useLocation();
    const [expanded, setExpanded] = useState(false);

    const links = navItems.map((link) => (
        <NavbarLink
            {...link}
            key={link.label}
            active={location.pathname === link.path}
            onClick={() => navigate(link.path)}
            expanded={expanded}
        />
    ));

    const devLinks = developmentItems.map((link) => (
        <NavbarLink
            {...link}
            key={link.label}
            active={location.pathname === link.path}
            onClick={() => navigate(link.path)}
            expanded={expanded}
        />
    ));

    return (
        <Box
            className={styles.sidebarLeft}
            onMouseEnter={() => setExpanded(true)}
            onMouseLeave={() => setExpanded(false)}
            style={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                width: expanded ? 240 : 80,
                transition: 'width 300ms ease',
                padding: '16px', /* theme.spacing.md */
                overflowX: 'hidden',
            }}
        >
            <Stack justify="center" gap={0} mb="md" align="center" style={{ height: 60, flexShrink: 0 }}>
                <Text className={styles.sidebarHeader} fw={700} size={expanded ? "lg" : "xl"} style={{ transition: 'font-size 200ms', color: 'var(--color-primary)' }}>
                    {expanded ? "Remis" : "R"}
                </Text>
            </Stack>

            <Stack gap="xs" style={{ flex: 1 }}>
                {links}
            </Stack>

            <Stack gap="xs" mt="md" pt="md" style={{ borderTop: '1px solid var(--glass-border)' }}>
                {devLinks}
            </Stack>
        </Box>
    );
}
