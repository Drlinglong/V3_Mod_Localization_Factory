import React, { useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, Text } from '@mantine/core';
import './LogViewer.css';

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
    <Card withBorder radius="md" style={{ backgroundColor: '#2c3e50', color: 'white' }}>
      <Card.Section withBorder inheritPadding py="xs">
        <Text fw={500}>{t('log_viewer_title')}</Text>
      </Card.Section>
      <div className="log-container" ref={logContainerRef} style={{paddingTop: "10px"}}>
        {logs.map((log, index) => (
          <div key={index} className="log-entry">
            <Text c={getLogColor(log.level)} style={{ marginRight: '8px' }}>
              [{formatTimestamp(Date.now())}] [{log.level}]
            </Text>
            <Text c="white">{log.message}</Text>
          </div>
        ))}
      </div>
    </Card>
  );
};

export default LogViewer;
