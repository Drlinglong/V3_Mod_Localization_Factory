import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Row, Col, Typography, Card } from 'antd';
import ActionCard from '../components/ActionCard';
import ProjectStatusPieChart from '../components/ProjectStatusPieChart';
import GlossaryAnalysisBarChart from '../components/GlossaryAnalysisBarChart';
import RemisButton from '../components/shared/RemisButton';

const { Title, Paragraph } = Typography;

const HomePage = () => {
  const { t } = useTranslation();
  const [slogan, setSlogan] = useState('');

  useEffect(() => {
    const slogans = t('homepage_slogans', { returnObjects: true });
    if (Array.isArray(slogans) && slogans.length > 0) {
      const randomIndex = Math.floor(Math.random() * slogans.length);
      setSlogan(slogans[randomIndex]);
    }
  }, [t]);

  return (
    <div style={{ padding: '24px' }}>
      <Card style={{ marginBottom: '24px', textAlign: 'center' }}>
        <Title level={3}>{t('homepage_title')}</Title>
        <Paragraph>"{slogan}"</Paragraph>
        <RemisButton onClick={() => alert('RemisButton Clicked!')}>
          {t('homepage_test_button')}
        </RemisButton>
      </Card>

      <Row gutter={[24, 24]}>
        <Col xs={24} sm={12}>
          <ActionCard
            icon={t('homepage_action_card_new_project_icon')}
            title={t('homepage_action_card_new_project')}
            linkTo="/translation"
          />
        </Col>
        <Col xs={24} sm={12}>
          <ActionCard
            icon={t('homepage_action_card_update_project_icon')}
            title={t('homepage_action_card_update_project')}
            linkTo="/translation"
          />
        </Col>
      </Row>

      <Row gutter={[24, 24]} style={{ marginTop: '24px' }}>
        <Col xs={24} lg={12}>
          <Card title={t('homepage_chart_pie_title')}>
            <ProjectStatusPieChart />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title={t('homepage_chart_bar_title')}>
            <GlossaryAnalysisBarChart />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default HomePage;
