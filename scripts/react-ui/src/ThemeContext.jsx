import React, { createContext, useState, useEffect, useMemo } from 'react';
import './themes/theme-victorian.css';
import './themes/theme-byzantine.css';

// 1. Create the context
const ThemeContext = createContext();

// 2. Create the provider component
export const ThemeProvider = ({ children }) => {
  // State to hold the current theme
  // Initialize state with the theme from localStorage or default to 'light'
  const [theme, setTheme] = useState(() => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    return savedTheme;
  });

  // Effect to apply the theme class to the html element
  useEffect(() => {
    const root = window.document.documentElement;
    // Remove previous theme classes
    root.classList.remove('theme-victorian', 'theme-byzantine', 'light', 'dark');
    // Add the new theme class
    root.classList.add(theme);
    // Persist the theme to localStorage
    localStorage.setItem('theme', theme);
  }, [theme]);

  // The function to change the theme
  const toggleTheme = (newTheme) => {
    if (newTheme) {
        setTheme(newTheme);
    }
  };

  // useMemo to prevent unnecessary re-renders of consumers
  const value = useMemo(() => ({
    theme,
    toggleTheme,
  }), [theme]);

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};

export default ThemeContext;
