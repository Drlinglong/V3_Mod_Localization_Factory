import React, { createContext, useState, useContext, useEffect } from 'react';

const NotificationContext = createContext();

export const NotificationProvider = ({ children }) => {
  const [notificationStyle, setNotificationStyle] = useState(
    () => localStorage.getItem('notificationStyle') || 'minimal'
  );

  useEffect(() => {
    localStorage.setItem('notificationStyle', notificationStyle);
  }, [notificationStyle]);

  const value = {
    notificationStyle,
    setNotificationStyle,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
};

export const useNotification = () => {
  const context = useContext(NotificationContext);
  if (context === undefined) {
    throw new Error('useNotification must be used within a NotificationProvider');
  }
  return context;
};
