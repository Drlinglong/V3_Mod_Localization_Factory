import React, { useState, useEffect } from 'react';
import { Row, Col, Typography, Card } from 'antd';
import ActionCard from '../components/ActionCard';
import ProjectStatusPieChart from '../components/ProjectStatusPieChart';
import GlossaryAnalysisBarChart from '../components/GlossaryAnalysisBarChart';
import slogans from '../data/slogans.json';

const { Title, Paragraph } = Typography;

const HomePage = () => {
  const [slogan, setSlogan] = useState('');

  useEffect(() => {
    const randomIndex = Math.floor(Math.random() * slogans.length);
    setSlogan(slogans[randomIndex]);
  }, []);

  return (
    <div style={{ padding: '24px' }}>
      <Card style={{ marginBottom: '24px', textAlign: 'center' }}>
        <Title level={3}>Smart Localization Workbench v2.0</Title>
        <Paragraph>"{slogan}"</Paragraph>
      </Card>

      <Row gutter={[24, 24]}>
        <Col xs={24} sm={12}>
          <ActionCard
            icon="🚀"
            title="开始新的翻译项目"
            linkTo="/translation"
          />
        </Col>
        <Col xs={24} sm={12}>
          <ActionCard
            icon="🔄"
            title="更新现有项目"
            linkTo="/translation"
          />
        </Col>
      </Row>

      <Row gutter={[24, 24]} style={{ marginTop: '24px' }}>
        <Col xs={24} lg={12}>
          <Card title="项目状态概览">
            <ProjectStatusPieChart />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="游戏术语库分析">
            <GlossaryAnalysisBarChart />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default HomePage;
