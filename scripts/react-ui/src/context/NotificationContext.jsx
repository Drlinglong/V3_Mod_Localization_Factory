import React, { createContext, useState, useContext, useEffect } from 'react';
import { toast } from 'react-hot-toast';

const NotificationContext = createContext();

export const NotificationProvider = ({ children }) => {
  const [notificationStyle, setNotificationStyle] = useState(
    () => localStorage.getItem('notificationStyle') || 'minimal'
  );

  useEffect(() => {
    localStorage.setItem('notificationStyle', notificationStyle);
  }, [notificationStyle]);

  // Define the notification functions within the provider
  const notify = {
    success: (message) => {
      const options = notificationStyle === 'bottom-right' ? { duration: Infinity } : {};
      toast.success(message, options);
    },
    error: (message) => {
      const options = notificationStyle === 'bottom-right' ? { duration: Infinity } : {};
      toast.error(message, options);
    },
  };

  const value = {
    notificationStyle,
    setNotificationStyle,
    notify, // Expose the notify object through the context
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
