import React from 'react';
import { NavLink } from 'react-router-dom';
import useBreadcrumbs from 'use-react-router-breadcrumbs';
import { Breadcrumb } from 'antd';
import { routes } from '../../App'; // Import the routes from App.jsx

const Breadcrumbs = () => {
    const breadcrumbs = useBreadcrumbs(routes);

    const items = breadcrumbs.map(({ match, breadcrumb }, index) => {
        const isLast = index === breadcrumbs.length - 1;
        return {
            key: match.pathname,
            title: isLast ? (
                <span>{breadcrumb}</span>
            ) : (
                <NavLink to={match.pathname}>{breadcrumb}</NavLink>
            ),
        };
    });

    return (
        <Breadcrumb style={{ margin: '16px 0' }} items={items} />
    );
};

export default Breadcrumbs;
