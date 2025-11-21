import React from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { Paper, Text, Group, Badge, ActionIcon, Tooltip } from '@mantine/core';
import { IconFileText, IconNote } from '@tabler/icons-react';
import styles from '../../pages/ProjectManagement.module.css';

export const TaskCard = ({ task, onClick }) => {
    const {
        attributes,
        listeners,
        setNodeRef,
        transform,
        transition,
        isDragging,
    } = useSortable({ id: task.id });

    const style = {
        transform: CSS.Transform.toString(transform),
        transition,
    };

    return (
        <div
            ref={setNodeRef}
            style={style}
            {...attributes}
            {...listeners}
            onClick={() => onClick(task)}
            className={`${styles.taskCard} ${isDragging ? styles.taskCardDragging : ''} ${task.type === 'file' ? styles.fileTaskIndicator : styles.noteTaskIndicator}`}
        >
            <Group justify="space-between" align="flex-start" wrap="nowrap">
                <Group gap="xs" wrap="nowrap" style={{ flex: 1, overflow: 'hidden' }}>
                    {task.type === 'file' ? (
                        <IconFileText size={16} style={{ minWidth: 16 }} color="var(--color-info)" />
                    ) : (
                        <IconNote size={16} style={{ minWidth: 16 }} color="var(--color-warning)" />
                    )}
                    <Text size="sm" fw={500} truncate title={task.title}>
                        {task.title}
                    </Text>
                </Group>
                {task.priority === 'high' && (
                    <Badge size="xs" color="red" variant="dot" />
                )}
            </Group>

            {task.type === 'file' && task.meta && (
                <Text size="xs" c="dimmed" mt={4}>
                    Lines: {task.meta.lines}
                </Text>
            )}

            {task.comments && (
                <Text size="xs" c="dimmed" lineClamp={2} mt={4} style={{ fontStyle: 'italic' }}>
                    {task.comments}
                </Text>
            )}
        </div>
    );
};
