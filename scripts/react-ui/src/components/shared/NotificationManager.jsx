import React, { useState, useEffect } from 'react';
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

const NotificationManager = () => {
    const { notificationStyle, setNotificationStyle } = useNotification();
    const { toasts } = useToasterStore();
    const [sidebarVisible, setSidebarVisible] = useState(false);

    const latestToast = toasts.filter(t => t.visible).slice(-1)[0];

    useEffect(() => {
        if (notificationStyle === 'sidebar' && toasts.some(t => t.visible)) {
            setSidebarVisible(true);
        }
    }, [toasts, notificationStyle]);

    const renderStyleSwitchControls = () => (
        <Space>
            <Tooltip title="Minimized View">
                <Button
                    shape="circle"
                    icon={<LineOutlined />}
                    type={notificationStyle === 'minimal' ? 'primary' : 'default'}
                    onClick={() => setNotificationStyle('minimal')}
                />
            </Tooltip>
            <Tooltip title="Bottom-Right Window View">
                <Button
                    shape="circle"
                    icon={<BlockOutlined />}
                    type={notificationStyle === 'bottom-right' ? 'primary' : 'default'}
                    onClick={() => setNotificationStyle('bottom-right')}
                />
            </Tooltip>
            <Tooltip title="Sidebar Log View">
                <Button
                    shape="circle"
                    icon={<LayoutOutlined />}
                    type={notificationStyle === 'sidebar' ? 'primary' : 'default'}
                    onClick={() => setNotificationStyle('sidebar')}
                />
            </Tooltip>
        </Space>
    );

    // --- Bottom-Right Window Style ---
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
                }}
            >
                <Card bodyStyle={{ padding: '8px 12px' }} size="small">
                    {renderStyleSwitchControls()}
                </Card>
                {toasts
                    .filter(t => t.visible)
                    .map(t => (
                        <Card
                            key={t.id}
                            style={{ width: 320, boxShadow: '0 4px 12px rgba(0,0,0,0.15)' }}
                            bodyStyle={{ padding: '12px' }}
                            size="small"
                        >
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <Text type={t.type === 'error' ? 'danger' : 'success'}>
                                    {t.message}
                                </Text>
                                <Button
                                    type="text"
                                    shape="circle"
                                    icon={<CloseOutlined />}
                                    size="small"
                                    onClick={() => toast.dismiss(t.id)}
                                />
                            </div>
                        </Card>
                    ))
                }
            </div>
        );
    }

    // --- Sidebar Log Style ---
    if (notificationStyle === 'sidebar') {
        return (
            <Drawer
                title="Notification Log"
                placement="right"
                onClose={() => setSidebarVisible(false)}
                open={sidebarVisible}
                width={400}
                extra={renderStyleSwitchControls()}
            >
                <Space direction="vertical" style={{ width: '100%' }}>
                    {toasts.map(t => (
                         <Badge.Ribbon
                            key={t.id}
                            text={t.type.toUpperCase()}
                            color={t.type === 'error' ? 'red' : 'green'}
                        >
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

    // --- Minimized Bar (Default) ---
    return (
        <div
            style={{
                position: 'fixed',
                bottom: 0,
                left: 0,
                width: '100%',
                zIndex: 9999,
                background: '#fff',
                borderTop: '1px solid #f0f0f0',
                padding: '8px 24px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                boxShadow: '0 -2px 8px rgba(0,0,0,0.06)'
            }}
        >
            {latestToast ? (
                <Text type={latestToast.type === 'error' ? 'danger' : 'success'}>
                    {latestToast.message}
                </Text>
            ) : (
                <Text type="secondary">Ready.</Text>
            )}
            {renderStyleSwitchControls()}
        </div>
    );
};

export default NotificationManager;
