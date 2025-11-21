import React from 'react';
import { useTranslation } from 'react-i18next';
import { Title, Text, Box, ActionIcon, Group, Badge, Code } from '@mantine/core';
import { IconCode, IconEye, IconPlayerPlay, IconSettings } from '@tabler/icons-react';
import styles from './EventRenderer.module.css';

const EventRenderer = () => {
    const { t } = useTranslation();

    // Mock Code Content
    const mockCode = `namespace = "example_event"

country_event = {
    id = example_event.1
    title = "example_event.1.t"
    desc = "example_event.1.d"
    picture = GFX_evt_landing_page

    is_triggered_only = yes

    option = {
        name = "example_event.1.a"
        add_political_power = 50
    }
}`;

    return (
        <div className={styles.container}>
            <Group justify="space-between">
                <Title order={2} style={{ fontFamily: 'var(--font-header)', color: 'var(--text-highlight)' }}>
                    {t('page_title_event_renderer')}
                </Title>
                <Group>
                    <Badge variant="outline" color="blue">Paradox Script</Badge>
                    <ActionIcon variant="subtle" color="gray"><IconSettings size={20} /></ActionIcon>
                </Group>
            </Group>

            <div className={styles.editorLayout}>
                {/* Left Pane: Code Editor */}
                <div className={styles.codePane}>
                    <div className={styles.paneHeader}>
                        <Group gap="xs">
                            <IconCode size={16} color="var(--text-muted)" />
                            <Text className={styles.paneTitle}>Script Editor</Text>
                        </Group>
                    </div>
                    <div className={styles.paneContent}>
                        <Code block bg="transparent" c="var(--text-main)">
                            {mockCode}
                        </Code>
                    </div>
                </div>

                {/* Right Pane: Preview */}
                <div className={styles.previewPane}>
                    <div className={styles.paneHeader}>
                        <Group gap="xs">
                            <IconEye size={16} color="var(--text-muted)" />
                            <Text className={styles.paneTitle}>Live Preview</Text>
                        </Group>
                        <ActionIcon variant="light" color="green" size="xs" radius="xl">
                            <IconPlayerPlay size={12} />
                        </ActionIcon>
                    </div>
                    <div className={styles.previewContent}>
                        <Text c="dimmed" ta="center">
                            {t('placeholder_event_renderer_description')}
                        </Text>
                        <Box mt="xl" p="lg" style={{ border: '1px dashed var(--glass-border)', borderRadius: '8px' }}>
                            <Text size="sm" c="var(--text-muted)">Event Preview Area</Text>
                        </Box>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default EventRenderer;
