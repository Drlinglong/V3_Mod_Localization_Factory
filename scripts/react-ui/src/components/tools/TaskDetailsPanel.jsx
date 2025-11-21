import React, { useState, useEffect } from 'react';
import { Stack, TextInput, Textarea, Select, Button, Text, Group, Badge, Divider } from '@mantine/core';
import { IconDeviceFloppy, IconTrash } from '@tabler/icons-react';
import { useDebouncedCallback } from '@mantine/hooks';

const STATUS_OPTIONS = [
    { value: 'todo', label: '待办' },
    { value: 'in_progress', label: '翻译中' },
    { value: 'proofreading', label: '校对中' },
    { value: 'paused', label: '挂起' },
    { value: 'done', label: '已完工' }
];

export const TaskDetailsPanel = ({ task, onUpdate, onDelete }) => {
    const [localComments, setLocalComments] = useState(task.comments || '');
    const [localTitle, setLocalTitle] = useState(task.title || '');

    // Sync local state when task prop changes
    useEffect(() => {
        setLocalComments(task.comments || '');
        setLocalTitle(task.title || '');
    }, [task.comments, task.title, task.id]);

    // Debounce updates to the parent/hook
    const debouncedUpdate = useDebouncedCallback((updates) => {
        onUpdate(task.id, updates);
    }, 500);

    const handleCommentChange = (e) => {
        const val = e.currentTarget.value;
        setLocalComments(val);
        debouncedUpdate({ comments: val });
    };

    const handleTitleChange = (e) => {
        const val = e.currentTarget.value;
        setLocalTitle(val);
        debouncedUpdate({ title: val });
    };

    const handleStatusChange = (val) => {
        onUpdate(task.id, { status: val });
    };

    if (!task) return <Text>No task selected</Text>;

    return (
        <Stack spacing="md" p="xs">
            <Group justify="space-between">
                <Badge
                    color={task.type === 'file' ? 'blue' : 'yellow'}
                    variant="light"
                >
                    {task.type === 'file' ? 'FILE TASK' : 'NOTE'}
                </Badge>
                <Text size="xs" c="dimmed">ID: {task.id}</Text>
            </Group>

            {/* Title */}
            {task.type === 'note' ? (
                <TextInput
                    label="Title"
                    value={localTitle}
                    onChange={handleTitleChange}
                />
            ) : (
                <div>
                    <Text size="sm" fw={500} c="dimmed" mb={4}>File Name</Text>
                    <Text fw={600} style={{ wordBreak: 'break-all' }}>{task.title}</Text>
                </div>
            )}

            {/* Status */}
            <Select
                label="Status"
                data={STATUS_OPTIONS}
                value={task.status}
                onChange={handleStatusChange}
            />

            {/* File Specific Info */}
            {task.type === 'file' && (
                <Stack spacing={4}>
                    <Text size="sm" fw={500} c="dimmed">File Path</Text>
                    <Text size="xs" c="dimmed" style={{ wordBreak: 'break-all' }}>
                        {task.filePath}
                    </Text>
                    {task.meta && (
                        <Text size="xs" c="dimmed">Lines: {task.meta.lines}</Text>
                    )}
                </Stack>
            )}

            <Divider my="xs" />

            {/* Comments */}
            <Textarea
                label="Comments & Notes"
                placeholder="Add your notes here..."
                minRows={4}
                autosize
                value={localComments}
                onChange={handleCommentChange}
            />
            <Text size="xs" c="dimmed" align="right">
                <IconDeviceFloppy size={12} style={{ marginRight: 4 }} />
                Auto-saving...
            </Text>

            <Divider my="xs" />

            {/* Actions */}
            {task.type === 'note' && (
                <Button
                    color="red"
                    variant="light"
                    leftSection={<IconTrash size={16} />}
                    onClick={() => onDelete(task.id)}
                    fullWidth
                >
                    Delete Task
                </Button>
            )}
        </Stack>
    );
};
