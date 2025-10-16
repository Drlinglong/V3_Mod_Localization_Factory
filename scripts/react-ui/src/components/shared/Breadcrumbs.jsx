import React from 'react';
import { NavLink } from 'react-router-dom';
import useBreadcrumbs from 'use-react-router-breadcrumbs';
import { Breadcrumbs as MantineBreadcrumbs, Anchor } from '@mantine/core';
import { routes } from '../../App'; // Import the routes from App.jsx

const Breadcrumbs = () => {
    const breadcrumbs = useBreadcrumbs(routes);

    const items = breadcrumbs.map(({ match, breadcrumb }, index) => {
        const isLast = index === breadcrumbs.length - 1;
        return isLast ? (
            <span key={match.pathname}>{breadcrumb}</span>
        ) : (
            <Anchor component={NavLink} to={match.pathname} key={match.pathname}>
                {breadcrumb}
            </Anchor>
        );
    });

    return (
        <MantineBreadcrumbs style={{ margin: '16px 0' }}>{items}</MantineBreadcrumbs>
    );
};

export default Breadcrumbs;
