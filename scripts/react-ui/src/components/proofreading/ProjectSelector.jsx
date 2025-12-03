import React from 'react';
import { useTranslation } from 'react-i18next';
import {
    Paper,
    Title,
    Button,
    Group,
    Select,
    Collapse
} from '@mantine/core';
import {
    IconChevronDown,
    IconChevronUp
} from '@tabler/icons-react';

/**
 * 项目选择器组件
 * 负责项目列表展示和项目选择交互
 */
const ProjectSelector = ({
    projects,
    selectedProject,
    isHeaderOpen,
    onToggleHeader,
    onProjectSelect
}) => {
    const { t } = useTranslation();

    return (
        <>
            <Button
                variant="subtle"
                size="xs"
                onClick={onToggleHeader}
                rightSection={isHeaderOpen ? <IconChevronUp size={14} /> : <IconChevronDown size={14} />}
            >
                {selectedProject ? selectedProject.name : "Select Project"}
            </Button>

            <Collapse in={isHeaderOpen}>
                <Paper withBorder p="sm" mb="sm" style={{ background: 'rgba(0,0,0,0.2)' }}>
                    <Group>
                        <Select
                            label="Select Project"
                            placeholder="Search projects..."
                            data={projects.map(p => ({ value: p.project_id, label: `${p.name} (${p.game_id})` }))}
                            value={selectedProject?.project_id}
                            onChange={onProjectSelect}
                            searchable
                            style={{ flex: 1 }}
                        />
                    </Group>
                </Paper>
            </Collapse>
        </>
    );
};

export default ProjectSelector;
