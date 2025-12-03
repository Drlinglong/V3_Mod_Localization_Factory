import React from 'react';
import {
    Paper,
    Button,
    Group,
    Select,
    Table,
    Badge,
    Text
} from '@mantine/core';
import MonacoWrapper from '../common/MonacoWrapper';

/**
 * 自由 Linter 模式组件
 * 独立的验证模式，不依赖项目和文件
 */
const FreeLinterMode = ({
    linterContent,
    onLinterContentChange,
    linterGameId,
    onGameIdChange,
    linterResults,
    linterLoading,
    linterError,
    onValidate
}) => {
    const getLevelColor = (level) => {
        switch (level) {
            case 'error': return 'red';
            case 'warning': return 'yellow';
            default: return 'gray';
        }
    };

    return (
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', paddingTop: '10px' }}>
            <Group mb="xs">
                <Select
                    data={['1', '2', '3', '4', '5']}
                    value={linterGameId}
                    onChange={onGameIdChange}
                    placeholder="Game ID"
                    size="xs"
                />
                <Button onClick={onValidate} loading={linterLoading} size="xs">Validate</Button>
            </Group>

            <div style={{ flex: 1, minHeight: 0 }}>
                <MonacoWrapper
                    value={linterContent}
                    onChange={onLinterContentChange}
                    theme="vs-dark"
                    language="yaml"
                />
            </div>

            {linterError && <Text color="red" mt="xs">{linterError}</Text>}

            {linterResults.length > 0 && (
                <Paper withBorder p="xs" mt="xs" h={150} style={{ overflowY: 'auto' }}>
                    <Table striped highlightOnHover size="xs">
                        <Table.Tbody>
                            {linterResults.map((r, i) => (
                                <Table.Tr key={i}>
                                    <Table.Td><Badge color={getLevelColor(r.level)}>{r.level}</Badge></Table.Td>
                                    <Table.Td>{r.message}</Table.Td>
                                </Table.Tr>
                            ))}
                        </Table.Tbody>
                    </Table>
                </Paper>
            )}
        </div>
    );
};

export default FreeLinterMode;
