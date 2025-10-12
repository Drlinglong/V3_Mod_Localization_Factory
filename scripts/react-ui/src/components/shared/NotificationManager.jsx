import React from 'react';
import { useTranslation } from 'react-i18next';
import { useNotification } from '../../context/NotificationContext';
import { useToasterStore, toast } from 'react-hot-toast';
import { Drawer, Card, Button, Typography, Space, Badge, Tooltip } from 'antd';
import {
  CloseOutlined,
  LineOutlined,
  BlockOutlined,
  LayoutOutlined,
  NotificationOutlined,
} from '@ant-design/icons';

const { Text } = Typography;

// --- 1. The Always-Visible Control Panel ---
const NotificationControls = () => {
  const { t } = useTranslation();
  const { notificationStyle, setNotificationStyle } = useNotification();

  return (
    <div
      style={{
        position: 'fixed',
        bottom: 16,
        right: 16, // Corrected position
        zIndex: 10000,
        background: 'rgba(255, 255, 255, 0.9)',
        padding: '8px',
        borderRadius: '8px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        backdropFilter: 'blur(5px)',
      }}
    >
      <Space>
        <Tooltip title={t('notification_tooltip_minimal')}>
          <Button
            shape="circle"
            icon={<LineOutlined />}
            type={notificationStyle === 'minimal' ? 'primary' : 'default'}
            onClick={() => setNotificationStyle('minimal')}
          />
        </Tooltip>
        <Tooltip title={t('notification_tooltip_windowed')}>
          <Button
            shape="circle"
            icon={<BlockOutlined />}
            type={notificationStyle === 'bottom-right' ? 'primary' : 'default'}
            onClick={() => setNotificationStyle('bottom-right')}
          />
        </Tooltip>
        <Tooltip title={t('notification_tooltip_sidebar')}>
          <Button
            shape="circle"
            icon={<LayoutOutlined />}
            type={notificationStyle === 'sidebar' ? 'primary' : 'default'}
            onClick={() => setNotificationStyle('sidebar')}
          />
        </Tooltip>
      </Space>
    </div>
  );
};


// --- 2. The Notification Views ---
const NotificationViews = () => {
  const { notificationStyle, setNotificationStyle } = useNotification();
  const { toasts } = useToasterStore();

  const latestToast = toasts.filter(t => t.visible).slice(-1)[0];
  const hasVisibleToasts = toasts.some(t => t.visible);

  // Render Bottom-Right Windows
  if (notificationStyle === 'bottom-right') {
    return (
      <div
        style={{
          position: 'fixed',
          bottom: '80px', // Position above controls
          right: 16,
          zIndex: 9998,
          display: 'flex',
          flexDirection: 'column',
          gap: '8px',
        }}
      >
        {/* Empty State */}
        {!hasVisibleToasts && (
          <Card style={{ width: 320 }} bodyStyle={{ padding: '12px' }} size="small">
            <Text type="secondary">No new notifications.</Text>
          </Card>
        )}
        {toasts.filter(t => t.visible).map(t => (
          <Card key={t.id} style={{ width: 320, boxShadow: '0 4px 12px rgba(0,0,0,0.15)' }} bodyStyle={{ padding: '12px' }} size="small">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Text type={t.type === 'error' ? 'danger' : 'success'}>{t.message}</Text>
              <Button type="text" shape="circle" icon={<CloseOutlined />} size="small" onClick={() => toast.dismiss(t.id)} />
            </div>
          </Card>
        ))}
      </div>
    );
  }

  // Render Sidebar Log
  if (notificationStyle === 'sidebar') {
    return (
      <Drawer
        title="Notification Log"
        placement="right"
        onClose={() => setNotificationStyle('minimal')} // Close button switches back to minimal
        open={true} // Always open if style is 'sidebar'
        width={400}
        zIndex={9999}
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          {/* Empty State */}
          {toasts.length === 0 && (
            <div style={{ textAlign: 'center', marginTop: '20px' }}>
              <NotificationOutlined style={{ fontSize: '24px', color: '#ccc' }} />
              <p><Text type="secondary">The notification log is empty.</Text></p>
            </div>
          )}
          {toasts.map(t => (
            <Badge.Ribbon key={t.id} text={t.type.toUpperCase()} color={t.type === 'error' ? 'red' : 'green'}>
              <Card size="small" style={{ width: '100%' }}>
                <Text>{t.message}</Text>
              </Card>
            </Badge.Ribbon>
          ))}
        </Space>
      </Drawer>
    );
  }

  // Render Minimized Bar (Default)
  return (
    <div
      style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        width: '100%',
        zIndex: 9990,
        background: '#fff',
        borderTop: '1px solid #f0f0f0',
        padding: '8px 24px',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        boxShadow: '0 -2px 8px rgba(0,0,0,0.06)',
        paddingRight: '200px', // Offset for the controls
      }}
    >
      {latestToast ? (
        <Text type={latestToast.type === 'error' ? 'danger' : 'success'}>{latestToast.message}</Text>
      ) : (
        <Text type="secondary">Ready.</Text>
      )}
    </div>
  );
};


// --- 3. The Main Component ---
const NotificationManager = () => {
    return (
        <>
            <NotificationControls />
            <NotificationViews />
        </>
    );
};

export default NotificationManager;
