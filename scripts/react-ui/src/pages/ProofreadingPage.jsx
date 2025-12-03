import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Paper,
  Title,
  Button,
  Group,
  Select,
  Tabs
} from '@mantine/core';
import {
  IconFolder,
  IconFileText,
  IconEdit
} from '@tabler/icons-react';
import layoutStyles from '../components/layout/Layout.module.css';
import useProofreadingState from '../hooks/useProofreadingState';
import ProjectSelector from '../components/proofreading/ProjectSelector';
import { SourceFileSelector, AIFileSelector } from '../components/proofreading/ProofreadingFileList';
import ProofreadingWorkspace from '../components/proofreading/ProofreadingWorkspace';
import FreeLinterMode from '../components/proofreading/FreeLinterMode';

/**
 * 校对页面主组件
 * 轻量级容器，仅负责布局和组件组合
 */
const ProofreadingPage = () => {
  const { t } = useTranslation();
  const state = useProofreadingState();

  // 本地 UI 状态
  const [activeTab, setActiveTab] = useState('file');
  const [zoomLevel, setZoomLevel] = useState('1');

  // 源文件选择器组件
  const sourceFileSelector = (
    <SourceFileSelector
      sourceFiles={state.sourceFiles}
      currentSourceFile={state.currentSourceFile}
      onSourceFileChange={state.handleSourceFileChange}
    />
  );

  // AI 初稿选择器组件
  const aiFileSelector = (
    <AIFileSelector
      sourceFiles={state.sourceFiles}
      currentSourceFile={state.currentSourceFile}
      targetFilesMap={state.targetFilesMap}
      currentTargetFile={state.currentTargetFile}
      onTargetFileChange={state.handleTargetFileChange}
    />
  );

  return (
    <div style={{ height: 'calc(100vh - 20px)', display: 'flex', flexDirection: 'column', padding: '10px', width: '100%' }}>
      <Paper withBorder p="xs" radius="md" className={layoutStyles.glassCard} style={{ flex: 1, display: 'flex', flexDirection: 'column', width: '100%', overflow: 'hidden' }}>

        {/* Header */}
        <Group position="apart" mb="xs">
          <Group>
            <Title order={4}>{t('page_title_proofreading')}</Title>
            <ProjectSelector
              projects={state.projects}
              selectedProject={state.selectedProject}
              isHeaderOpen={state.isHeaderOpen}
              onToggleHeader={() => state.setIsHeaderOpen(!state.isHeaderOpen)}
              onProjectSelect={state.handleProjectSelect}
            />
          </Group>

          <Group>
            <Select
              value={zoomLevel}
              onChange={setZoomLevel}
              data={[
                { value: '1', label: '100%' },
                { value: '1.1', label: '110%' },
                { value: '1.25', label: '125%' },
                { value: '1.5', label: '150%' },
                { value: '1.75', label: '175%' },
                { value: '2', label: '200%' },
              ]}
              size="xs"
              style={{ width: 80 }}
            />
            <Button
              variant="default"
              size="xs"
              leftSection={<IconFolder size={14} />}
              onClick={state.handleOpenFolder}
            >
              {t('proofreading.open_folder')}
            </Button>
            <Tabs value={activeTab} onChange={setActiveTab} variant="pills" radius="md">
              <Tabs.List>
                <Tabs.Tab value="file" leftSection={<IconFileText size={14} />}>{t('proofreading.tab_file_mode')}</Tabs.Tab>
                <Tabs.Tab value="free" leftSection={<IconEdit size={14} />}>{t('proofreading.tab_free_mode')}</Tabs.Tab>
              </Tabs.List>
            </Tabs>
          </Group>
        </Group>

        {/* Main Content */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', zoom: zoomLevel }}>
          <Tabs value={activeTab} style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>

            {/* File Mode Tab */}
            <Tabs.Panel value="file" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
              <ProofreadingWorkspace
                originalContentStr={state.originalContentStr}
                aiContentStr={state.aiContentStr}
                finalContentStr={state.finalContentStr}
                onFinalContentChange={state.setFinalContentStr}
                originalEditorRef={state.originalEditorRef}
                aiEditorRef={state.aiEditorRef}
                finalEditorRef={state.finalEditorRef}
                validationResults={state.validationResults}
                stats={state.stats}
                loading={state.loading}
                saving={state.saving}
                keyChangeWarning={state.keyChangeWarning}
                saveModalOpen={state.saveModalOpen}
                onValidate={state.handleValidate}
                onSave={state.handleSaveClick}
                onConfirmSave={state.confirmSave}
                onCancelSave={() => state.setSaveModalOpen(false)}
                fileInfo={state.fileInfo}
                onOpenFolder={state.handleOpenFolder}
                sourceFileSelector={sourceFileSelector}
                aiFileSelector={aiFileSelector}
              />
            </Tabs.Panel>

            {/* Free Mode Tab */}
            <Tabs.Panel value="free" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
              <FreeLinterMode
                linterContent={state.linterContent}
                onLinterContentChange={state.setLinterContent}
                linterGameId={state.linterGameId}
                onGameIdChange={state.setLinterGameId}
                linterResults={state.linterResults}
                linterLoading={state.linterLoading}
                linterError={state.linterError}
                onValidate={state.handleLinterValidate}
              />
            </Tabs.Panel>

          </Tabs>
        </div>
      </Paper>
    </div>
  );
};

export default ProofreadingPage;
