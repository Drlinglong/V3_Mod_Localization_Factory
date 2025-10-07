import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import {
  Layout,
  Steps,
  Button,
  Upload,
  Form,
  Select,
  message,
  Typography,
  Space,
  Spin,
  Result,
} from 'antd';
import {
  InboxOutlined,
  ToolOutlined,
  CloudUploadOutlined,
  SettingOutlined,
  SyncOutlined,
  DownloadOutlined,
} from '@ant-design/icons';
import './App.css';

const { Header, Content, Footer } = Layout;
const { Title, Paragraph, Text } = Typography;
const { Dragger } = Upload;
const { Option } = Select;

const App = () => {
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
  const [isPolling, setIsPolling] = useState(false);
  const pollingRef = useRef(null);

  useEffect(() => {
    // Fetch config from backend
    axios.get('/api/config')
      .then(response => {
        setConfig(response.data);
      })
      .catch(error => {
        message.error('Failed to load configuration from server.');
        console.error('Config fetch error:', error);
      });
  }, []);

  useEffect(() => {
    if (!taskId) {
      return; // Do nothing if there is no task ID
    }

    // Start polling when a new taskId is set
    setIsPolling(true);
    const intervalId = setInterval(() => {
      axios.get(`/api/status/${taskId}`)
        .then(response => {
          const { status: newStatus, log: newLogs } = response.data;
          setLogs(newLogs); // Update logs on each poll

          if (newStatus === 'completed' || newStatus === 'failed') {
            // Stop polling
            clearInterval(intervalId);

            // **CRITICAL FIX**: Set final status first, then stop polling, then change page.
            // This ensures the Result component receives the correct status prop.
            setStatus(newStatus);
            setIsPolling(false);
            setCurrent(3);

            // Show appropriate messages
            if (newStatus === 'completed') {
              message.success('Translation completed successfully!');
              setResultUrl(`/api/result/${taskId}`);
            } else {
              message.error('Translation task failed. Please check the logs.');
            }
          } else {
            // Keep updating status while polling (e.g., 'processing')
            setStatus(newStatus);
          }
        })
        .catch(error => {
          // Handle polling network errors
          message.error('Failed to get task status.');
          console.error('Polling error:', error);
          clearInterval(intervalId);

          // Go to result page with a failed status
          setStatus('failed');
          setIsPolling(false);
          setCurrent(3);
        });
    }, 2000);

    // Cleanup function to run when taskId changes or component unmounts
    return () => {
      clearInterval(intervalId);
    };
  }, [taskId]); // This effect re-runs ONLY when taskId changes

  const handleUploadChange = (info) => {
    let newFileList = [...info.fileList];
    newFileList = newFileList.slice(-1); // Only allow one file
    setFileList(newFileList);

    // The beforeUpload prop prevents the status from ever becoming 'done'.
    // Instead, we'll advance to the next step as soon as a file is selected.
    if (newFileList.length > 0 && info.file.status !== 'removed') {
        message.info(`File ${info.file.name} is ready for processing.`);
        setCurrent(1);
    } else if (info.file.status === 'removed') {
        setCurrent(0); // Go back to upload step if file is removed
    }
  };

  const onFinish = (values) => {
    if (fileList.length === 0) {
      message.error('Please upload a mod file first!');
      return;
    }

    const formData = new FormData();
    formData.append('file', fileList[0].originFileObj);
    formData.append('game_profile_id', values.game_profile_id);
    formData.append('source_lang_code', values.source_lang_code);
    formData.append('target_lang_codes', values.target_lang_codes.join(','));
    formData.append('api_provider', values.api_provider);

    // Reset state for new job
    setTaskId(null);
    setLogs(['Starting translation...']);
    setStatus('pending');
    setResultUrl(null);
    setCurrent(2);

    axios.post('/api/translate', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    .then(response => {
      const { task_id } = response.data;
      setTaskId(task_id);
      message.success('Translation task started!');
    })
    .catch(error => {
      message.error('Failed to start translation task.');
      console.error('Translate API error:', error);
      setCurrent(1); // Go back to config step on failure
    });
  };

  const steps = [
    {
      title: 'Upload Mod',
      icon: <CloudUploadOutlined />,
      content: (
        <Dragger
          name="file"
          fileList={fileList}
          onChange={handleUploadChange}
          beforeUpload={() => false} // Prevent automatic upload
          maxCount={1}
        >
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">Click or drag a .zip mod file to this area to upload</p>
          <p className="ant-upload-hint">
            Support for a single .zip file containing your mod's localization files.
          </p>
        </Dragger>
      ),
    },
    {
      title: 'Configure',
      icon: <SettingOutlined />,
      content: (
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
            <Button type="primary" htmlType="submit">
              Start Translation
            </Button>
          </Form.Item>
        </Form>
      ),
    },
    {
      title: 'Translate',
      icon: <SyncOutlined spin={isPolling} />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }}>
            <Title level={4}>Translation in Progress...</Title>
            <div className="log-container">
              {logs.map((log, index) => (
                <div key={index}>{log}</div>
              ))}
            </div>
            <Spin size="large" spinning={isPolling} />
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
                status === 'completed' && resultUrl ? (
                    <Button type="primary" href={resultUrl} icon={<DownloadOutlined />}>
                        Download Translated Mod
                    </Button>
                ) : null
            }
        />
      ),
    },
  ];

  return (
    <Layout className="layout">
      <Header>
        <div className="logo" />
        <Title style={{ color: 'white', lineHeight: '64px', float: 'left' }} level={3}>
            <ToolOutlined /> Paradox Mod Localization Factory
        </Title>
      </Header>
      <Content style={{ padding: '0 50px', marginTop: '24px' }}>
        <div className="site-layout-content" style={{ background: '#fff', padding: 24 }}>
          <Steps current={current} items={steps.map(s => ({title: s.title, icon: s.icon}))}/>
          <div className="steps-content">
            {steps[current].content}
          </div>
        </div>
      </Content>
      <Footer style={{ textAlign: 'center' }}>
        Paradox Mod Localization Factory ©2025 Created by Jules
      </Footer>
    </Layout>
  );
};

export default App;