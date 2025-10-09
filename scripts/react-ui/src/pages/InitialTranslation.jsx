import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import {
  Steps,
  Button,
  Upload,
  Form,
  Select,
  message,
  Typography,
  Space,
  Result,
  Card,
  Descriptions,
} from 'antd';
import {
  InboxOutlined,
  CloudUploadOutlined,
  SettingOutlined,
  SyncOutlined,
  DownloadOutlined,
  ArrowLeftOutlined,
  StopOutlined,
} from '@ant-design/icons';
import '../App.css';
import LogViewer from '../components/shared/LogViewer';

const { Dragger } = Upload;
const { Option } = Select;

const InitialTranslation = () => {
  const { t } = useTranslation();
  const [current, setCurrent] = useState(0);
  const [config, setConfig] = useState({
    game_profiles: {},
    languages: {},
    api_providers: [],
  });
  const [fileList, setFileList] = useState([]);
  const [form] = Form.useForm();
  const [taskId, setTaskId] = useState(null);
  const [logs, setLogs] = useState([]);
  const [status, setStatus] = useState(null);
  const [resultUrl, setResultUrl] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [translationDetails, setTranslationDetails] = useState(null);

  useEffect(() => {
    axios.get('/api/config')
      .then(response => setConfig(response.data))
      .catch(error => {
        message.error(t('message_error_load_config'));
        console.error('Config fetch error:', error);
      });
  }, [t]);

  useEffect(() => {
    if (!taskId || !isProcessing) return;

    const poll = setInterval(() => {
      axios.get(`/api/status/${taskId}`)
        .then(response => {
          const { status: newStatus, log: newLogs } = response.data;
          const formattedLogs = newLogs.map(l => (typeof l === 'string' ? { level: 'INFO', message: l } : l));
          setLogs(formattedLogs);

          if (newStatus === 'completed' || newStatus === 'failed') {
            clearInterval(poll);
            setStatus(newStatus);
            setIsProcessing(false);
            setCurrent(3);
            if (newStatus === 'completed') {
              message.success(t('message_success_translation_complete'));
              setResultUrl(`/api/result/${taskId}`);
            } else {
              message.error(t('message_error_translation_failed'));
            }
          } else {
            setStatus(newStatus);
          }
        })
        .catch(error => {
          clearInterval(poll);
          message.error(t('message_error_get_status'));
          console.error('Polling error:', error);
          setStatus('failed');
          setIsProcessing(false);
          setCurrent(3);
        });
    }, 2000);

    return () => clearInterval(poll);
  }, [taskId, isProcessing, t]);

  const handleUploadChange = ({ fileList: newFileList }) => {
    setFileList(newFileList.slice(-1));
    if (newFileList.length > 0) {
      setCurrent(1);
    }
  };

  const handleBack = () => {
    if (current > 0) {
      setCurrent(current - 1);
    }
  };

  const handleAbort = async () => {
    if (!taskId) return;
    try {
      console.log(`Aborting task ${taskId}`);
      message.warn(t('message_warn_aborted'));
      setIsProcessing(false);
      setStatus('failed');
      setLogs(prev => [...prev, { level: 'WARN', message: t('log_aborted') }]);
    } catch (error) {
      message.error(t('message_error_abort_failed'));
      console.error('Abort error:', error);
    }
  };

  const onFinish = (values) => {
    if (fileList.length === 0) {
      message.error(t('message_error_upload_first'));
      return;
    }

    const { game_profile_id, source_lang_code, target_lang_codes, api_provider } = values;
    const gameProfile = config.game_profiles[game_profile_id]?.name || 'Unknown Game';
    const sourceLang = config.languages[source_lang_code]?.name || source_lang_code;
    const targetLangs = target_lang_codes.map(code => config.languages[code]?.name || code).join(', ');

    setTranslationDetails({
      modName: fileList[0].name,
      game: gameProfile,
      source: sourceLang,
      targets: targetLangs,
      provider: api_provider,
    });

    const formData = new FormData();
    formData.append('file', fileList[0].originFileObj);
    Object.entries(values).forEach(([key, value]) => {
        if (Array.isArray(value)) {
            formData.append(key, value.join(','));
        } else {
            formData.append(key, value);
        }
    });

    setTaskId(null);
    setLogs([{ level: 'INFO', message: t('log_starting') }]);
    setStatus('pending');
    setResultUrl(null);
    setCurrent(2);
    setIsProcessing(true);

    axios.post('/api/translate', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    .then(response => {
      setTaskId(response.data.task_id);
      message.success(t('message_success_task_started'));
    })
    .catch(error => {
      message.error(t('message_error_task_start_failed'));
      console.error('Translate API error:', error);
      setIsProcessing(false);
      setStatus('failed');
      setCurrent(1);
    });
  };

  const renderBackButton = () => (
    <Button onClick={handleBack} icon={<ArrowLeftOutlined />} style={{ marginRight: 8 }}>
      {t('button_back')}
    </Button>
  );

  const steps = [
    {
      title: t('initial_translation_step_upload'),
      icon: <CloudUploadOutlined />,
      content: (
        <Dragger
          name="file"
          fileList={fileList}
          onChange={handleUploadChange}
          beforeUpload={() => false}
          maxCount={1}
        >
          <p className="ant-upload-drag-icon"><InboxOutlined /></p>
          <p className="ant-upload-text">{t('initial_translation_upload_text')}</p>
          <p className="ant-upload-hint">{t('initial_translation_upload_hint')}</p>
        </Dragger>
      ),
    },
    {
      title: t('initial_translation_step_configure'),
      icon: <SettingOutlined />,
      content: (
        <>
          <Form form={form} layout="vertical" onFinish={onFinish}>
            <Form.Item name="game_profile_id" label={t('form_label_game')} rules={[{ required: true }]}>
              <Select placeholder={t('form_placeholder_game')}>
                {Object.entries(config.game_profiles).map(([id, profile]) => (
                  <Option key={id} value={id}>{profile.name}</Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item name="source_lang_code" label={t('form_label_source_language')} rules={[{ required: true }]}>
              <Select placeholder={t('form_placeholder_source_language')}>
                {Object.values(config.languages).map(lang => (
                  <Option key={lang.code} value={lang.code}>{lang.name}</Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item name="target_lang_codes" label={t('form_label_target_languages')} rules={[{ required: true }]}>
              <Select mode="multiple" placeholder={t('form_placeholder_target_languages')}>
                {Object.values(config.languages).map(lang => (
                  <Option key={lang.code} value={lang.code}>{lang.name}</Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item name="api_provider" label={t('form_label_api_provider')} rules={[{ required: true }]}>
              <Select placeholder={t('form_placeholder_api_provider')}>
                {config.api_providers.map(provider => (
                  <Option key={provider} value={provider}>{provider}</Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item>
              <Space>
                {renderBackButton()}
                <Button type="primary" htmlType="submit">{t('button_start_translation')}</Button>
              </Space>
            </Form.Item>
          </Form>
        </>
      ),
    },
    {
      title: t('initial_translation_step_translate'),
      icon: <SyncOutlined spin={isProcessing} />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }}>
          {translationDetails && (
             <Card>
                <Descriptions title={t('job_details_title')} bordered column={1} size="small">
                    <Descriptions.Item label={t('job_details_mod_name')}>{translationDetails.modName}</Descriptions.Item>
                    <Descriptions.Item label={t('job_details_game')}>{translationDetails.game}</Descriptions.Item>
                    <Descriptions.Item label={t('job_details_source_language')}>{translationDetails.source}</Descriptions.Item>
                    <Descriptions.Item label={t('job_details_target_languages')}>{translationDetails.targets}</Descriptions.Item>
                    <Descriptions.Item label={t('job_details_api_provider')}>{translationDetails.provider}</Descriptions.Item>
                </Descriptions>
            </Card>
          )}
          <LogViewer logs={logs} />
          <Space>
            {renderBackButton()}
            {isProcessing && (
              <Button onClick={handleAbort} icon={<StopOutlined />} danger>
                {t('button_abort_translation')}
              </Button>
            )}
          </Space>
        </Space>
      ),
    },
    {
      title: t('initial_translation_step_download'),
      icon: <DownloadOutlined />,
      content: (
        <Result
          status={status === 'completed' ? 'success' : 'error'}
          title={status === 'completed' ? t('result_title_success') : t('result_title_failed')}
          subTitle={status === 'completed' ? t('result_subtitle_success') : t('result_subtitle_failed')}
          extra={
            <Space>
              {renderBackButton()}
              {status === 'completed' && resultUrl && (
                <Button type="primary" href={resultUrl} icon={<DownloadOutlined />}>
                  {t('button_download_mod')}
                </Button>
              )}
            </Space>
          }
        />
      ),
    },
  ];

  const translatedSteps = steps.map(step => ({ ...step, title: t(step.title) }));

  return (
    <div>
      <Steps current={current} items={translatedSteps.map(s => ({title: s.title, icon: s.icon}))} />
      <div className="steps-content" style={{ marginTop: '24px' }}>
        {steps[current].content}
      </div>
    </div>
  );
};

export default InitialTranslation;
