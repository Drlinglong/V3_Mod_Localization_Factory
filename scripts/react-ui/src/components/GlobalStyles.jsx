import React, { useContext } from 'react';
import ThemeContext from '../ThemeContext';
import './GlobalStyles.css';

const GlobalStyles = () => {
    const { theme } = useContext(ThemeContext);

    return (
        <div
            className={`global-background-layer ${theme}`}
            data-testid="global-background-layer"
        />
    );
};

export default GlobalStyles;
