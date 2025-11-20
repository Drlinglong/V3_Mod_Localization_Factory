import React from 'react';
import { Paper, Text, Group, Avatar, Stack, Badge, ActionIcon, ScrollArea } from '@mantine/core';
import { IconDotsVertical, IconFileText } from '@tabler/icons-react';

const mockActivities = [
    { id: 1, project: 'Victoria 3: Divergences', action: 'Translated 50 keys', time: '2 hours ago', game: 'Vic3' },
    { id: 2, project: 'Stellaris: Gigastructures', action: 'Proofread 12 files', time: '5 hours ago', game: 'Stellaris' },
    { id: 3, project: 'HOI4: Kaiserreich', action: 'Exported mod', time: '1 day ago', game: 'HOI4' },
    { id: 4, project: 'CK3: Godherja', action: 'Created new glossary', time: '2 days ago', game: 'CK3' },
    { id: 5, project: 'EU4: Anbennar', action: 'Updated source files', time: '3 days ago', game: 'EU4' },
];

const RecentActivityList = () => {
    return (
        <Paper withBorder radius="md" p="md" bg="dark.7">
            <Group justify="space-between" mb="md">
                <Text fw={700}>Recent Activity</Text>
                <ActionIcon variant="subtle" color="gray">
                    <IconDotsVertical size={16} />
                </ActionIcon>
            </Group>

            <ScrollArea h={300} offsetScrollbars>
                <Stack gap="md">
                    {mockActivities.map((activity) => (
                        <Group key={activity.id} wrap="nowrap">
                            <Avatar color="blue" radius="xl">
                                {activity.game.substring(0, 2)}
                            </Avatar>
                            <div style={{ flex: 1 }}>
                                <Text size="sm" fw={500}>
                                    {activity.project}
                                </Text>
                                <Text c="dimmed" size="xs">
                                    {activity.action} • {activity.time}
                                </Text>
                            </div>
                            <Badge variant="light" size="xs">{activity.game}</Badge>
                        </Group>
                    ))}
                </Stack>
            </ScrollArea>
        </Paper>
    );
};

export default RecentActivityList;
