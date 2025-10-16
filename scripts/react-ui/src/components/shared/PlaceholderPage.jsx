import React from 'react';
import { Title } from '@mantine/core';

const PlaceholderPage = ({ title }) => (
    <div style={{ padding: '24px' }}>
        <Title order={2}>{title}</Title>
        <p>This page is under migration to Mantine UI.</p>
    </div>
);

export default PlaceholderPage;
