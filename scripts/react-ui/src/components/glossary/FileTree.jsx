import React from 'react';
import { NavLink } from '@mantine/core';
import { IconFolder, IconFileText } from '@tabler/icons-react';

/**
 * 文件树组件
 * 递归渲染词典文件树结构
 */
const FileTree = ({ nodes, onSelect, selectedKey }) => (
    <>
        {nodes.map(node =>
            node.isLeaf ? (
                <NavLink
                    key={node.key}
                    label={node.title}
                    leftSection={<IconFileText size="1rem" />}
                    active={node.key === selectedKey}
                    onClick={() => onSelect(node.key, node)}
                    variant="light"
                />
            ) : (
                <NavLink
                    key={node.key}
                    label={node.title}
                    leftSection={<IconFolder size="1rem" />}
                    childrenOffset={28}
                    defaultOpened
                >
                    {node.children && <FileTree nodes={node.children} onSelect={onSelect} selectedKey={selectedKey} />}
                </NavLink>
            )
        )}
    </>
);

export default FileTree;
