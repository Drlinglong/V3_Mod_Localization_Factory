import React, { useState, useEffect } from 'react';
import {
  Radio,
  Select,
  Input,
  Button,
  Spin,
  Typography,
  Space,
  Alert,
  message,
  AutoComplete
} from 'antd';
import { CopyOutlined } from '@ant-design/icons';
import axios from 'axios';
import { useTranslation } from 'react-i18next';

const { TextArea } = Input;
const { Title, Paragraph } = Typography;

const WorkshopGenerator = () => {
  const { t } = useTranslation();

  // --- State Management ---
  const [projects, setProjects] = useState([]);
  const [languages, setLanguages] = useState([]);
  const [apiProviders, setApiProviders] = useState([]); // State for API providers
  const [selectedProjectId, setSelectedProjectId] = useState(null);
  const [selectedProvider, setSelectedProvider] = useState(null); // State for selected provider
  const [manualItemId, setManualItemId] = useState('');
  const [inputMode, setInputMode] = useState('project');
  const [userTemplate, setUserTemplate] = useState(
    `<!-- Chinese Title -->\n[h1]在此输入您的中文标题[/h1]\n\n<!-- Chinese Description -->\n[b]在此输入您的中文简介和描述。[/b]\n\n`
  );
  const [targetLanguage, setTargetLanguage] = useState('zh');
  const [customLanguage, setCustomLanguage] = useState('');
  const [generatedBbcode, setGeneratedBbcode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');

  // --- Data Fetching ---
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [projectsResponse, configResponse] = await Promise.all([
          axios.get('/api/projects'),
          axios.get('/api/config')
        ]);

        const projectData = projectsResponse.data;
        setProjects(projectData);
        if (projectData.length > 0) {
          setSelectedProjectId(projectData[0].id);
        }

        const configData = configResponse.data;
        if (configData.languages) {
          const langArray = Object.values(configData.languages);
          setLanguages(langArray);
        }
        if (configData.api_providers) {
          setApiProviders(configData.api_providers);
          if (configData.api_providers.length > 0) {
            setSelectedProvider(configData.api_providers[0]); // Set default provider
          }
        }

      } catch (err) {
        const fetchError = t('workshop_generator.errors.fetch_config_failed');
        setError(fetchError);
        message.error(fetchError);
      }
    };
    fetchData();
  }, [t]);

  // --- Helper Functions ---
  const extractWorkshopId = (value) => {
    if (!value) return '';
    const match = value.match(/(?:steamcommunity\.com\/sharedfiles\/filedetails\/\?id=)(\d+)/);
    return match ? match[1] : value;
  };

  const handleManualIdChange = (value) => {
    const extractedId = extractWorkshopId(value);
    setManualItemId(extractedId);
  };

  const handleCopyToClipboard = () => {
    if (generatedBbcode) {
      navigator.clipboard.writeText(generatedBbcode);
      message.success(t('workshop_generator.messages.copied_to_clipboard'));
    }
  };

  // --- Core Logic Handler ---
  const handleGenerate = async () => {
    setError(null);
    setSuccessMessage('');
    setIsLoading(true);
    setGeneratedBbcode('');

    let finalItemId = '';
    let finalProjectId = '';

    if (inputMode === 'project') {
      const selectedProject = projects.find(p => p.id === selectedProjectId);
      if (!selectedProject) {
        setError(t('workshop_generator.errors.project_not_selected'));
        setIsLoading(false);
        return;
      }
       if (!selectedProject.workshop_id) {
        setError(t('workshop_generator.errors.project_id_missing'));
        setIsLoading(false);
        return;
      }
      finalItemId = selectedProject.workshop_id;
      finalProjectId = selectedProject.id;
    } else {
      finalItemId = manualItemId;
    }

    if (!finalItemId || !selectedProvider) {
      setError(t('workshop_generator.errors.workshop_id_or_provider_required'));
      setIsLoading(false);
      return;
    }

    try {
      const response = await axios.post('/api/tools/generate_workshop_description', {
        item_id: finalItemId,
        project_id: finalProjectId,
        user_template: userTemplate,
        target_language: targetLanguage,
        custom_language: customLanguage,
        api_provider: selectedProvider
      });
      setGeneratedBbcode(response.data.bbcode);
      if (response.data.saved_path) {
        setSuccessMessage(`${t('workshop_generator.messages.generation_successful')} ${response.data.saved_path}`);
      } else {
         setSuccessMessage(response.data.message || t('workshop_generator.messages.generation_successful_no_save'));
      }
    } catch (err) {
      const errorMessage = err.response?.data?.detail || t('workshop_generator.errors.generation_failed');
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // --- Render ---
  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '24px' }}>
      <Title level={3}>{t('workshop_generator.title')}</Title>
      <Paragraph>{t('workshop_generator.description')}</Paragraph>

      <Spin spinning={isLoading} tip={t('workshop_generator.loading_tip')}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>

          {/* Input Mode */}
          <Radio.Group value={inputMode} onChange={(e) => setInputMode(e.target.value)}>
            <Radio.Button value="project">{t('workshop_generator.input_mode.project')}</Radio.Button>
            <Radio.Button value="manual">{t('workshop_generator.input_mode.manual')}</Radio.Button>
          </Radio.Group>

          {/* Input Area */}
          {inputMode === 'project' ? (
            <Select
              style={{ width: '100%' }}
              value={selectedProjectId}
              onChange={setSelectedProjectId}
              options={projects.map(p => ({ label: p.name, value: p.id }))}
              placeholder={t('workshop_generator.placeholders.select_project')}
            />
          ) : (
            <AutoComplete
              style={{ width: '100%' }}
              value={manualItemId}
              onChange={handleManualIdChange}
              placeholder={t('workshop_generator.placeholders.manual_input')}
              options={[]}
            />
          )}

          {/* User Template */}
          <div>
            <Title level={5}>{t('workshop_generator.template_title')}</Title>
            <TextArea
              rows={10}
              value={userTemplate}
              onChange={(e) => setUserTemplate(e.target.value)}
              placeholder={t('workshop_generator.placeholders.template_input')}
            />
          </div>

          {/* Configuration */}
          <Space wrap>
            <Select
              value={targetLanguage}
              onChange={setTargetLanguage}
              style={{ width: 200 }}
              aria-label={t('workshop_generator.labels.target_language')}
            >
              {languages.map(lang => (
                <Select.Option key={lang.code} value={lang.code}>
                  {lang.name}
                </Select.Option>
              ))}
              <Select.Option value="custom">{t('workshop_generator.languages.custom')}</Select.Option>
            </Select>

            {targetLanguage === 'custom' && (
              <Input
                value={customLanguage}
                onChange={(e) => setCustomLanguage(e.target.value)}
                placeholder={t('workshop_generator.placeholders.custom_language')}
                style={{ width: 200 }}
              />
            )}

            <Select
              value={selectedProvider}
              onChange={setSelectedProvider}
              style={{ width: 200 }}
              aria-label={t('workshop_generator.labels.api_provider')}
              placeholder={t('workshop_generator.placeholders.select_provider')}
            >
              {apiProviders.map(provider => (
                <Select.Option key={provider} value={provider}>
                  {provider}
                </Select.Option>
              ))}
            </Select>
          </Space>

          {/* Controls */}
          <Button type="primary" onClick={handleGenerate} disabled={isLoading}>
            {t('workshop_generator.buttons.generate')}
          </Button>

          {/* Messages */}
          {error && <Alert message={error} type="error" showIcon />}
          {successMessage && <Alert message={successMessage} type="success" showIcon />}

          {/* Output Area */}
          {generatedBbcode && (
            <div>
              <Title level={5}>{t('workshop_generator.output_title')}</Title>
              <TextArea
                rows={15}
                value={generatedBbcode}
                readOnly
                style={{ fontFamily: 'monospace', backgroundColor: '#f0f2f5' }}
              />
              <Button
                icon={<CopyOutlined />}
                onClick={handleCopyToClipboard}
                style={{ marginTop: '10px' }}
              >
                {t('workshop_generator.buttons.copy')}
              </Button>
            </div>
          )}

        </Space>
      </Spin>
    </div>
  );
};

export default WorkshopGenerator;
