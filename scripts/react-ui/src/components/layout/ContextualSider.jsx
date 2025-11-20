import React, { useState, useEffect } from 'react';
import { Box, Text, ScrollArea, SegmentedControl, Stack, Group, ActionIcon, Tooltip } from '@mantine/core';
import { IconInfoCircle, IconHistory, IconX, IconLayoutSidebarRightCollapse, IconLayoutSidebarRightExpand } from '@tabler/icons-react';
import { useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

export function ContextualSider() {
    const location = useLocation();
    const { t } = useTranslation();
    const [activeTab, setActiveTab] = useState('info');
    const [collapsed, setCollapsed] = useState(false);
    const [content, setContent] = useState(null);

    // Determine content based on route
    useEffect(() => {
        const path = location.pathname;

        if (path.startsWith('/translation')) {
            setContent({
                title: 'Translation Context',
                info: 'Select a mod to see details here.',
                history: 'Translation logs will appear here.'
            });
        } else if (path.startsWith('/project-management')) {
            setContent({
                title: 'Project Details',
                info: 'Select a project task to view properties.',
                history: 'Recent project activity.'
            });
        } else if (path.startsWith('/glossary-manager')) {
            setContent({
                title: 'Glossary Term',
                info: 'Select a term to view definitions and variants.',
                history: 'Term edit history.'
            });
        } else {
            setContent(null); // Hide for pages without context
        }
    }, [location.pathname]);

    if (!content) return null;

    if (collapsed) {
        return (
            <Box
                style={(theme) => ({
                    width: 50,
                    height: '100%',
                    borderLeft: `1px solid ${theme.colors.dark[6]}`,
                    backgroundColor: theme.colors.dark[6],
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    paddingTop: theme.spacing.md,
                })}
            >
                <Tooltip label="Expand Context" position="left">
                    <ActionIcon variant="subtle" onClick={() => setCollapsed(false)}>
                        <IconLayoutSidebarRightExpand size={20} />
                    </ActionIcon>
                </Tooltip>
            </Box>
        );
    }

    return (
        <Box
            style={(theme) => ({
                width: 300,
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                borderLeft: `1px solid ${theme.colors.dark[6]}`,
                backgroundColor: theme.colors.dark[6],
            })}
        >
            {/* Header */}
            <Group justify="space-between" p="md" style={(theme) => ({ borderBottom: `1px solid ${theme.colors.dark[4]}` })}>
                <Text fw={600} size="sm">{content.title}</Text>
                <Tooltip label="Collapse" position="left">
                    <ActionIcon variant="subtle" size="sm" onClick={() => setCollapsed(true)}>
                        <IconLayoutSidebarRightCollapse size={16} />
                    </ActionIcon>
                </Tooltip>
            </Group>

            {/* Tabs */}
            <Box p="xs">
                <SegmentedControl
                    fullWidth
                    size="xs"
                    value={activeTab}
                    onChange={setActiveTab}
                    data={[
                        { label: 'Info', value: 'info', icon: <IconInfoCircle size={14} /> },
                        { label: 'History', value: 'history', icon: <IconHistory size={14} /> },
                    ]}
                />
            </Box>

            {/* Content Area */}
            <ScrollArea style={{ flex: 1 }} p="md">
                {activeTab === 'info' ? (
                    <Text size="sm" c="dimmed">
                        {content.info}
                    </Text>
                ) : (
                    <Text size="sm" c="dimmed">
                        {content.history}
                    </Text>
                )}
            </ScrollArea>
        </Box>
    );
}
