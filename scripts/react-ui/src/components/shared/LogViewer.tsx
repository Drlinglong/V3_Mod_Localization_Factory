import React, { useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, Typography } from 'antd';
import './LogViewer.css';

const { Text } = Typography;

const LogViewer = ({ logs }) => {
  const { t } = useTranslation();
  const logContainerRef = useRef(null);

  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [logs]);

  const getLogColor = (level) => {
    switch (level) {
      case 'INFO':
        return 'white';
      case 'WARN':
        return 'yellow';
      case 'ERROR':
        return 'red';
      default:
        return 'white';
    }
  };

  const formatTimestamp = (date) => {
    return new Date(date).toLocaleTimeString();
  };

  return (
    <Card title={t('log_viewer_title')} bordered={false} style={{ backgroundColor: '#2c3e50', color: 'white' }}>
      <div className="log-container" ref={logContainerRef}>
        {logs.map((log, index) => (
          <div key={index} className="log-entry">
            <Text style={{ color: getLogColor(log.level), marginRight: '8px' }}>
              [{formatTimestamp(Date.now())}] [{log.level}]
            </Text>
            <Text style={{ color: 'white' }}>{log.message}</Text>
          </div>
        ))}
      </div>
    </Card>
  );
};

export default LogViewer;
