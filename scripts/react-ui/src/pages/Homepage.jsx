import React from 'react';
import { Typography, Button, Space } from 'antd';
import { RocketOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;

const Homepage = ({ onStart }) => {
    return (
        <div style={{ textAlign: 'center', padding: '50px' }}>
            <Title level={1}>欢迎使用智能本地化工作台 v2.0</Title>
            <Paragraph style={{ fontSize: '18px', marginBottom: '40px' }}>
                AI驱动的P社游戏本地化一站式解决方案
            </Paragraph>
            <Space>
                <Button type="primary" size="large" icon={<RocketOutlined />} onClick={onStart}>
                    🚀 开始新的翻译项目
                </Button>
            </Space>
        </div>
    );
};

export default Homepage;
