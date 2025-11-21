import React, { createContext, useState, useContext } from 'react';

const SidebarContext = createContext();

export const SidebarProvider = ({ children }) => {
    const [sidebarContent, setSidebarContent] = useState(null);
    const [sidebarWidth, setSidebarWidth] = useState(300);

    return (
        <SidebarContext.Provider value={{ sidebarContent, setSidebarContent, sidebarWidth, setSidebarWidth }}>
            {children}
        </SidebarContext.Provider>
    );
};

export const useSidebar = () => useContext(SidebarContext);
