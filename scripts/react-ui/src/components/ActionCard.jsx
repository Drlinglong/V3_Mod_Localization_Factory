import React from 'react';
import { Link } from 'react-router-dom';
import { Card } from 'antd';

const ActionCard = ({ icon, title, linkTo }) => {
  return (
    <Link to={linkTo}>
      <Card hoverable style={{ textAlign: 'center' }}>
        <div style={{ fontSize: '48px' }}>{icon}</div>
        <h2>{title}</h2>
      </Card>
    </Link>
  );
};

export default ActionCard;
