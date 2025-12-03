import React from 'react';
import { useTranslation } from 'react-i18next';
import { Box, Tabs } from '@mantine/core';
import { IconCpu, IconGavel } from '@tabler/icons-react';
import MiningDashboard from '../components/neologism/MiningDashboard';
import JudgmentCourt from '../components/neologism/JudgmentCourt';

/**
 * 新词审核页面
 * 轻量级容器，仅负责 Tab 切换和布局
 */
const NeologismReviewPage = () => {
    const { t } = useTranslation();

    return (
        <Box h="100%" style={{ overflow: 'hidden' }}>
            <Tabs defaultValue="dashboard" h="100%" variant="pills" radius="md">
                <Box p="md" pb={0}>
                    <Tabs.List>
                        <Tabs.Tab value="dashboard" leftSection={<IconCpu size={16} />}>
                            {t('neologism_review.tab_mining')}
                        </Tabs.Tab>
                        <Tabs.Tab value="court" leftSection={<IconGavel size={16} />}>
                            {t('neologism_review.tab_court')}
                        </Tabs.Tab>
                    </Tabs.List>
                </Box>

                <Tabs.Panel value="dashboard" h="calc(100% - 60px)">
                    <MiningDashboard />
                </Tabs.Panel>

                <Tabs.Panel value="court" h="calc(100% - 60px)">
                    <JudgmentCourt />
                </Tabs.Panel>
            </Tabs>
        </Box>
    );
};

export default NeologismReviewPage;
