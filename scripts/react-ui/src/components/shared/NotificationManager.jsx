import React from 'react';
import { useTranslation } from 'react-i18next';
import { useNotification } from '../../context/NotificationContext';
import { useToasterStore, toast } from 'react-hot-toast';
import { Drawer, Card, Button, Text, Group, Badge, Tooltip } from '@mantine/core';
import { IconX, IconMinus, IconSquare, IconLayoutSidebar, IconBell } from '@tabler/icons-react';

// --- 1. The Always-Visible Control Panel ---
const NotificationControls = () => {
  const { t } = useTranslation();
  const { notificationStyle, setNotificationStyle } = useNotification();

  return (
    <Card
      shadow="md"
      padding="xs"
      radius="md"
      withBorder
      style={{
        position: 'fixed',
        bottom: 16,
        right: 16,
        zIndex: 10000,
        backdropFilter: 'blur(5px)',
      }}
    >
      <Group>
        <Tooltip label={t('notification_tooltip_minimal')}>
          <Button
            variant={notificationStyle === 'minimal' ? 'filled' : 'light'}
            size="sm"
            isIcon
            onClick={() => setNotificationStyle('minimal')}
          >
            <IconMinus />
          </Button>
        </Tooltip>
        <Tooltip label={t('notification_tooltip_windowed')}>
          <Button
            variant={notificationStyle === 'bottom-right' ? 'filled' : 'light'}
            size="sm"
            isIcon
            onClick={() => setNotificationStyle('bottom-right')}
          >
            <IconSquare />
          </Button>
        </Tooltip>
        <Tooltip label={t('notification_tooltip_sidebar')}>
          <Button
            variant={notificationStyle === 'sidebar' ? 'filled' : 'light'}
            size="sm"
            isIcon
            onClick={() => setNotificationStyle('sidebar')}
          >
            <IconLayoutSidebar />
          </Button>
        </Tooltip>
      </Group>
    </Card>
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
          <Card withBorder radius="md" shadow="sm" style={{ width: 320 }} p="xs">
            <Text c="dimmed">No new notifications.</Text>
          </Card>
        )}
        {toasts.filter(t => t.visible).map(t => (
          <Card key={t.id} withBorder radius="md" shadow="sm" style={{ width: 320 }} p="xs">
            <Group justify="space-between">
              <Text color={t.type === 'error' ? 'red' : 'green'}>{t.message}</Text>
              <Button variant="light" size="xs" isIcon onClick={() => toast.dismiss(t.id)}>
                <IconX size={14} />
              </Button>
            </Group>
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
        position="right"
        onClose={() => setNotificationStyle('minimal')}
        opened={true}
        size="md"
        zIndex={9999}
      >
        <Group direction="vertical" style={{ width: '100%' }}>
          {toasts.length === 0 && (
            <div style={{ textAlign: 'center', marginTop: '20px' }}>
              <IconBell size={24} style={{ color: '#ccc' }} />
              <p><Text c="dimmed">The notification log is empty.</Text></p>
            </div>
          )}
          {toasts.map(t => (
            <Card key={t.id} withBorder radius="md" style={{ width: '100%' }}>
               <Badge color={t.type === 'error' ? 'red' : 'green'} variant="light" >{t.type.toUpperCase()}</Badge>
               <Text>{t.message}</Text>
            </Card>
          ))}
        </Group>
      </Drawer>
    );
  }

  // Render Minimized Bar (Default)
  return (
    <Card
      withBorder
      radius={0}
      style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        width: '100%',
        zIndex: 9990,
        paddingRight: '200px', // Offset for the controls
      }}
    >
      {latestToast ? (
        <Text color={latestToast.type === 'error' ? 'red' : 'green'}>{latestToast.message}</Text>
      ) : (
        <Text c="dimmed">Ready.</Text>
      )}
    </Card>
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
