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
                style={(theme) => ({
                    width: '100%',
                    padding: theme.spacing.xs,
                    borderRadius: theme.radius.md,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: expanded ? 'flex-start' : 'center',
                    color: active ? theme.colors.brand[3] : theme.colors.dark[0],
                    backgroundColor: active ? 'rgba(137, 180, 250, 0.15)' : 'transparent',
                    transition: 'all 200ms ease',
                    '&:hover': {
                        backgroundColor: active ? 'rgba(137, 180, 250, 0.25)' : theme.colors.dark[5],
                        color: active ? theme.colors.brand[2] : theme.colors.white,
                    },
                })}
            >
                <Icon style={{ width: rem(22), height: rem(22) }} stroke={1.5} />
                {expanded && (
                    <Text size="sm" ml="md" style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
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
            onMouseEnter={() => setExpanded(true)}
            onMouseLeave={() => setExpanded(false)}
            style={(theme) => ({
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                borderRight: `1px solid ${theme.colors.dark[6]}`, // Subtle border
                backgroundColor: 'rgba(26, 27, 30, 0.7)', // Semi-transparent surface
                backdropFilter: 'blur(10px)',
                width: expanded ? 240 : 80, // Expand width
                transition: 'width 300ms ease',
                padding: theme.spacing.md,
                overflowX: 'hidden',
                zIndex: 100, // Ensure it stays on top
            })}
        >
            <Stack justify="center" gap={0} mb="md" align="center" style={{ height: 60, flexShrink: 0 }}>
                {/* Logo placeholder or App Title */}
                <Text fw={700} size={expanded ? "lg" : "xl"} c="brand.3" style={{ transition: 'font-size 200ms' }}>
                    {expanded ? "Remis" : "R"}
                </Text>
            </Stack>

            <Stack gap="xs" style={{ flex: 1 }}>
                {links}
            </Stack>

            <Stack gap="xs" mt="md" pt="md" style={(theme) => ({ borderTop: `1px solid ${theme.colors.dark[4]}` })}>
                {devLinks}
            </Stack>
        </Box>
    );
}
