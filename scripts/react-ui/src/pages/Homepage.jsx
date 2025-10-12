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

      {/* --- Scrollbar Test Container --- */}
      <Card style={{ marginTop: '24px' }}>
        <Title level={4}>Scrollbar Test Container</Title>
        <div
          style={{
            height: '200px',
            overflowY: 'scroll',
            border: '1px solid #ccc',
            padding: '10px',
            marginTop: '10px'
          }}
        >
          <Paragraph>This is a test container to demonstrate the custom scrollbar.</Paragraph>
          <Paragraph>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</Paragraph>
          <Paragraph>Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</Paragraph>
          <Paragraph>Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</Paragraph>
          <Paragraph>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.</Paragraph>
          <Paragraph>Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</Paragraph>
          <Paragraph>This is the end of the content. Scroll up and down to see the custom scrollbar in action.</Paragraph>
        </div>
      </Card>
      {/* --- End of Scrollbar Test Container --- */}

    </div>
  );
};

export default HomePage;
