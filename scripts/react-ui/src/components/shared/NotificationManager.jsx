import React from 'react';
import { useNotification } from '../../context/NotificationContext';
import { useToasterStore, toast } from 'react-hot-toast';
import { Drawer, Card, Button, Typography, Space, Badge, Tooltip } from 'antd';
import {
  CloseOutlined,
  LineOutlined,
  BlockOutlined,
  LayoutOutlined,
} from '@ant-design/icons';

const { Text } = Typography;

// --- 1. The Always-Visible Control Panel ---
const NotificationControls = () => {
  const { notificationStyle, setNotificationStyle } = useNotification();

  return (
    <div
      style={{
        position: 'fixed',
        bottom: 16,
        right: 16,
        zIndex: 10000, // Extremely high z-index to stay on top of everything
        background: 'rgba(255, 255, 255, 0.9)',
        padding: '8px',
        borderRadius: '8px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        backdropFilter: 'blur(5px)',
      }}
    >
      <Space>
        <Tooltip title="Minimized Log">
          <Button
            shape="circle"
            icon={<LineOutlined />}
            type={notificationStyle === 'minimal' ? 'primary' : 'default'}
            onClick={() => setNotificationStyle('minimal')}
          />
        </Tooltip>
        <Tooltip title="Windowed Log">
          <Button
            shape="circle"
            icon={<BlockOutlined />}
            type={notificationStyle === 'bottom-right' ? 'primary' : 'default'}
            onClick={() => setNotificationStyle('bottom-right')}
          />
        </Tooltip>
        <Tooltip title="Sidebar Log">
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
  const { notificationStyle, setNotificationStyle } = useNotification(); // Get setter for closing sidebar
  const { toasts } = useToasterStore();

  const latestToast = toasts.filter(t => t.visible).slice(-1)[0];

  // Render Bottom-Right Windows
  if (notificationStyle === 'bottom-right') {
    return (
      <div
        style={{
          position: 'fixed',
          bottom: 16,
          right: 16,
          zIndex: 9998,
          display: 'flex',
          flexDirection: 'column',
          gap: '8px',
          // Move the stack above the controls
          bottom: '80px',
        }}
      >
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
        // FIX: Closing the drawer now switches the style back to minimal
        onClose={() => setNotificationStyle('minimal')}
        // FIX: The drawer is open simply if the style is 'sidebar'
        open={true}
        width={400}
        zIndex={9999}
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          {toasts.map(t => (
            <Badge.Ribbon key={t.id} text={t.type.toUpperCase()} color={t.type === 'error' ? 'red' : 'green'}>
              <Card size="small" style={{ width: '100%' }}>
                <Text>{t.message}</Text>
              </Card>
            </Badge.Ribbon>
          ))}
          {toasts.length === 0 && <Text type="secondary">No notifications yet.</Text>}
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
        paddingRight: '200px', // Offset for the controls on the right
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
