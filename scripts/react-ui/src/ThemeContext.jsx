import React, { createContext, useState, useEffect, useMemo } from 'react';
import { MantineProvider } from '@mantine/core';
import { theme as customTheme } from './theme';

// 1. Create the context
const ThemeContext = createContext();

// 2. Create the provider component
export const ThemeProvider = ({ children }) => {
  // State to hold the current theme
  const [theme, setTheme] = useState(() => {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    return savedTheme;
  });

  // Effect to apply the theme class to the html element
  useEffect(() => {
    const root = window.document.documentElement;
    root.classList.remove('light', 'dark', 'theme-victorian', 'theme-byzantine', 'victorian', 'byzantine', 'scifi', 'wwii', 'medieval');
    root.classList.add(theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  // The function to change the theme
  const toggleTheme = (newTheme) => {
    if (newTheme) {
      setTheme(newTheme);
    }
  };

  const value = useMemo(() => ({
    theme,
    toggleTheme,
  }), [theme]);

  return (
    <ThemeContext.Provider value={value}>
      <MantineProvider theme={customTheme} defaultColorScheme="dark">
        {children}
      </MantineProvider>
    </ThemeContext.Provider>
  );
};

export default ThemeContext;
