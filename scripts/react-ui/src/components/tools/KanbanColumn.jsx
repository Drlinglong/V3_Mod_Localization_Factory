import React from 'react';
import { useDroppable } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { Paper, Title, Badge, Button, Group } from '@mantine/core';
import { IconPlus } from '@tabler/icons-react';
import { TaskCard } from './TaskCard';
import styles from '../../pages/ProjectManagement.module.css';

// Helper to map status codes to display titles and colors
const COLUMN_CONFIG = {
    todo: { title: '待办', color: 'gray' },
    in_progress: { title: '翻译中', color: 'blue' },
    proofreading: { title: '校对中', color: 'yellow' },
    paused: { title: '挂起', color: 'orange' },
    done: { title: '已完工', color: 'green' }
};

export const KanbanColumn = ({ id, tasks, onCardClick, onAddNote }) => {
    const { setNodeRef } = useDroppable({ id });
    const config = COLUMN_CONFIG[id] || { title: id, color: 'gray' };

    return (
        <div className={styles.column}>
            {/* Header */}
            <div className={styles.columnHeader}>
                <Group gap="xs">
                    <Title order={5} style={{ color: 'var(--text-main)' }}>{config.title}</Title>
                    <Badge color={config.color} variant="light" size="sm" circle>
                        {tasks.length}
                    </Badge>
                </Group>
                <Button
                    variant="subtle"
                    size="xs"
                    compact
                    onClick={() => onAddNote(id)}
                    title="Add Note Task"
                >
                    <IconPlus size={16} />
                </Button>
            </div>

            {/* Task List Area */}
            <div ref={setNodeRef} className={styles.taskList}>
                <SortableContext
                    id={id}
                    items={tasks.map(t => t.id)}
                    strategy={verticalListSortingStrategy}
                >
                    {tasks.map((task) => (
                        <TaskCard
                            key={task.id}
                            task={task}
                            onClick={onCardClick}
                        />
                    ))}
                </SortableContext>

                {/* Empty State / Drop Target hint could go here if needed */}
                {tasks.length === 0 && (
                    <div style={{ height: '50px', border: '1px dashed rgba(255,255,255,0.1)', borderRadius: '8px' }} />
                )}
            </div>
        </div>
    );
};
