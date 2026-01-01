import React, { useState, useEffect } from 'react';
import { Center, Stack, Title, Text, Button, Loader, Transition, Box, RingProgress, ThemeIcon, Group } from '@mantine/core';
import { IconRocket, IconCheck, IconServer2, IconDatabase, IconPlugConnected } from '@tabler/icons-react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';

const SplashScreen = ({ onReady }) => {
    const { t } = useTranslation();
    const [status, setStatus] = useState('connecting'); // connecting, ready, error
    const [progress, setProgress] = useState(0);
    const [logs, setLogs] = useState([]);

    // Poll backend
    useEffect(() => {
        let isMounted = true;
        const addLog = (msg) => setLogs(prev => [...prev.slice(-4), msg]);

        const checkHealth = async () => {
            try {
                addLog('Pinging Neural Link (API)...');
                const start = Date.now();
                // We ping the health endpoint
                await axios.get('/api/health');

                if (!isMounted) return;

                const latency = Date.now() - start;
                addLog(`Connection established. Latency: ${latency}ms`);
                setProgress(100);
                setStatus('ready');

            } catch (error) {
                if (!isMounted) return;
                addLog(`Connection failed... retrying in 500ms`);
                // Retry in 500ms (was 2000ms, too slow)
                setTimeout(checkHealth, 500);
            }
        };

        // Smooth progress animation
        const interval = setInterval(() => {
            setProgress(p => {
                // Asymptotic approach to 90%
                if (p >= 90) return p;
                // Move 1% closer to 90% each frame, minimum 0.5%
                const remaining = 90 - p;
                return p + (remaining * 0.05) + 0.1;
            });
        }, 30); // 30ms = ~33 FPS for smoother visual

        // Start checking
        checkHealth();

        return () => {
            isMounted = false;
            clearInterval(interval);
        };
    }, []);

    // "Matrix" rain or simple gradient background
    return (
        <Box style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100vw',
            height: '100vh',
            background: 'linear-gradient(135deg, #0b1c2b 0%, #1a2a3a 100%)',
            color: 'white',
            zIndex: 9999,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            overflow: 'hidden'
        }}>
            {/* Background decorative elements */}
            <div style={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                width: '600px',
                height: '600px',
                background: 'radial-gradient(circle, rgba(34,139,230,0.1) 0%, rgba(0,0,0,0) 70%)',
                zIndex: 0
            }} />

            <Stack align="center" style={{ zIndex: 1, position: 'relative' }}>
                <RingProgress
                    size={240}
                    thickness={4}
                    roundCaps
                    sections={[{ value: progress, color: status === 'ready' ? 'teal' : 'blue' }]}
                    label={
                        <Center>
                            {status === 'ready' ? (
                                <ThemeIcon color="teal" variant="light" radius="xl" size="xl">
                                    <IconCheck size={40} />
                                </ThemeIcon>
                            ) : (
                                <Text fw={700} size="xl" ta="center">
                                    {Math.round(progress)}%
                                </Text>
                            )}
                        </Center>
                    }
                />

                <Stack align="center" gap={4}>
                    <Title order={1} style={{ letterSpacing: '2px', fontWeight: 900 }}>
                        REMIS
                    </Title>
                    <Text size="sm" c="dimmed" style={{ letterSpacing: '4px', textTransform: 'uppercase' }}>
                        Localization Factory
                    </Text>
                </Stack>

                <Box h={60} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                    {status === 'connecting' && (
                        <Text size="xs" c="dimmed" className="fade-in">
                            {logs[logs.length - 1] || "Initializing..."}
                        </Text>
                    )}

                    {status === 'ready' && (
                        <Transition mounted={status === 'ready'} transition="pop" duration={400} timingFunction="ease">
                            {(styles) => (
                                <Button
                                    style={styles}
                                    size="lg"
                                    variant="gradient"
                                    gradient={{ from: 'blue', to: 'cyan' }}
                                    onClick={onReady}
                                    className="pulse-button" // CSS class defined in global or we assume styled here? Let's stick to inline for safety or standard mantine.
                                    leftSection={<IconRocket />}
                                >
                                    ENTER SYSTEM
                                </Button>
                            )}
                        </Transition>
                    )}
                </Box>

                <Group gap="xl" mt="xl" style={{ opacity: 0.5 }}>
                    <Group gap="xs">
                        <IconServer2 size={16} />
                        <Text size="xs">Backend</Text>
                    </Group>
                    <Group gap="xs">
                        <IconDatabase size={16} />
                        <Text size="xs">Database</Text>
                    </Group>
                    <Group gap="xs">
                        <IconPlugConnected size={16} />
                        <Text size="xs">API</Text>
                    </Group>
                </Group>
            </Stack>
        </Box>
    );
};

export default SplashScreen;
