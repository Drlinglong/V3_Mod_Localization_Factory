import React, { useState, useEffect } from 'react';
import axios from 'axios';
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

const { Title, Text } = Typography;
const { Dragger } = Upload;
const { Option } = Select;

const InitialTranslation = () => {
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
        message.error('Failed to load configuration from server.');
        console.error('Config fetch error:', error);
      });
  }, []);

  useEffect(() => {
    if (!taskId || !isProcessing) return;

    const poll = setInterval(() => {
      axios.get(`/api/status/${taskId}`)
        .then(response => {
          const { status: newStatus, log: newLogs } = response.data;
          // Simulate new log format
          const formattedLogs = newLogs.map(l => (typeof l === 'string' ? { level: 'INFO', message: l } : l));
          setLogs(formattedLogs);

          if (newStatus === 'completed' || newStatus === 'failed') {
            clearInterval(poll);
            setStatus(newStatus);
            setIsProcessing(false);
            setCurrent(3);
            if (newStatus === 'completed') {
              message.success('Translation completed successfully!');
              setResultUrl(`/api/result/${taskId}`);
            } else {
              message.error('Translation task failed. Please check the logs.');
            }
          } else {
            setStatus(newStatus);
          }
        })
        .catch(error => {
          clearInterval(poll);
          message.error('Failed to get task status.');
          console.error('Polling error:', error);
          setStatus('failed');
          setIsProcessing(false);
          setCurrent(3);
        });
    }, 2000);

    return () => clearInterval(poll);
  }, [taskId, isProcessing]);

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
      // Mock API call
      // In a real scenario: await axios.post(`/api/tasks/${taskId}/abort`);
      console.log(`Aborting task ${taskId}`);
      message.warn('Translation has been aborted by the user.');
      setIsProcessing(false);
      setStatus('failed');
      setLogs(prev => [...prev, { level: 'WARN', message: 'Task aborted by user.' }]);
    } catch (error) {
      message.error('Failed to abort the translation task.');
      console.error('Abort error:', error);
    }
  };

  const onFinish = (values) => {
    if (fileList.length === 0) {
      message.error('Please upload a mod file first!');
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
    setLogs([{ level: 'INFO', message: 'Starting translation...' }]);
    setStatus('pending');
    setResultUrl(null);
    setCurrent(2);
    setIsProcessing(true);

    axios.post('/api/translate', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    .then(response => {
      setTaskId(response.data.task_id);
      message.success('Translation task started!');
    })
    .catch(error => {
      message.error('Failed to start translation task.');
      console.error('Translate API error:', error);
      setIsProcessing(false);
      setStatus('failed');
      setCurrent(1);
    });
  };

  const renderBackButton = () => (
    <Button onClick={handleBack} icon={<ArrowLeftOutlined />} style={{ marginRight: 8 }}>
      Back
    </Button>
  );

  const steps = [
    {
      title: 'Upload Mod',
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
          <p className="ant-upload-text">Click or drag a .zip mod file to this area to upload</p>
          <p className="ant-upload-hint">Support for a single .zip file containing your mod's localization files.</p>
        </Dragger>
      ),
    },
    {
      title: 'Configure',
      icon: <SettingOutlined />,
      content: (
        <>
          <Form form={form} layout="vertical" onFinish={onFinish}>
            <Form.Item name="game_profile_id" label="Game" rules={[{ required: true }]}>
              <Select placeholder="Select a game">
                {Object.entries(config.game_profiles).map(([id, profile]) => (
                  <Option key={id} value={id}>{profile.name}</Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item name="source_lang_code" label="Source Language" rules={[{ required: true }]}>
              <Select placeholder="Select source language">
                {Object.values(config.languages).map(lang => (
                  <Option key={lang.code} value={lang.code}>{lang.name}</Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item name="target_lang_codes" label="Target Language(s)" rules={[{ required: true }]}>
              <Select mode="multiple" placeholder="Select target language(s)">
                {Object.values(config.languages).map(lang => (
                  <Option key={lang.code} value={lang.code}>{lang.name}</Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item name="api_provider" label="API Provider" rules={[{ required: true }]}>
              <Select placeholder="Select an API provider">
                {config.api_providers.map(provider => (
                  <Option key={provider} value={provider}>{provider}</Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item>
              <Space>
                {renderBackButton()}
                <Button type="primary" htmlType="submit">Start Translation</Button>
              </Space>
            </Form.Item>
          </Form>
        </>
      ),
    },
    {
      title: 'Translate',
      icon: <SyncOutlined spin={isProcessing} />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }}>
          {translationDetails && (
             <Card>
                <Descriptions title="Translation Job Details" bordered column={1} size="small">
                    <Descriptions.Item label="Mod Name">{translationDetails.modName}</Descriptions.Item>
                    <Descriptions.Item label="Game">{translationDetails.game}</Descriptions.Item>
                    <Descriptions.Item label="Source Language">{translationDetails.source}</Descriptions.Item>
                    <Descriptions.Item label="Target Language(s)">{translationDetails.targets}</Descriptions.Item>
                    <Descriptions.Item label="API Provider">{translationDetails.provider}</Descriptions.Item>
                </Descriptions>
            </Card>
          )}
          <LogViewer logs={logs} />
          <Space>
            {renderBackButton()}
            {isProcessing && (
              <Button onClick={handleAbort} icon={<StopOutlined />} danger>
                Abort Translation
              </Button>
            )}
          </Space>
        </Space>
      ),
    },
    {
      title: 'Download',
      icon: <DownloadOutlined />,
      content: (
        <Result
          status={status === 'completed' ? 'success' : 'error'}
          title={status === 'completed' ? "Translation Successful!" : "Translation Failed"}
          subTitle={status === 'completed' ? "Your translated mod is ready for download." : "Something went wrong. Please check the logs and try again."}
          extra={
            <Space>
              {renderBackButton()}
              {status === 'completed' && resultUrl && (
                <Button type="primary" href={resultUrl} icon={<DownloadOutlined />}>
                  Download Translated Mod
                </Button>
              )}
            </Space>
          }
        />
      ),
    },
  ];

  return (
    <div>
      <Steps current={current} items={steps.map(s => ({ title: s.title, icon: s.icon }))} />
      <div className="steps-content" style={{ marginTop: '24px' }}>
        {steps[current].content}
      </div>
    </div>
  );
};

export default InitialTranslation;
