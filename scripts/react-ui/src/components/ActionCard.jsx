import React from 'react';
import { Link } from 'react-router-dom';
import { Card, Text } from '@mantine/core';

const ActionCard = ({ icon, title, linkTo }) => {
  return (
    <Link to={linkTo} style={{ textDecoration: 'none' }}>
      <Card shadow="sm" padding="lg" radius="md" withBorder style={{ textAlign: 'center' }}>
        <Text size="xl" style={{ fontSize: '48px' }}>{icon}</Text>
        <Text weight={500} size="lg" mt="md">{title}</Text>
      </Card>
    </Link>
  );
};

export default ActionCard;
