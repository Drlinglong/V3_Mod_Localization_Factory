import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { driver } from "driver.js";
import "driver.js/dist/driver.css";
import { useTranslation } from 'react-i18next';
import { getTutorialSteps } from '../config/tutorialSteps';

const TutorialContext = createContext();

export const TutorialProvider = ({ children }) => {
    const { t, i18n } = useTranslation();
    const [isTourActive, setIsTourActive] = useState(false);

    const startTour = useCallback((pageName = 'home') => {
        const steps = getTutorialSteps(t, pageName);

        if (!steps || steps.length === 0) return;

        const driverObj = driver({
            showProgress: true,
            animate: true,
            overlayOpacity: 0.7,
            stagePadding: 4,
            nextBtnText: t('tutorial.next'),
            prevBtnText: t('tutorial.prev'),
            doneBtnText: t('tutorial.done'),
            onDeselected: () => {
                setIsTourActive(false);
            },
            onDestroyed: () => {
                setIsTourActive(false);
            },
            steps: steps
        });

        setIsTourActive(true);
        driverObj.drive();
    }, [t]);

    // Optional: Check for first-time user
    useEffect(() => {
        const hasSeenWelcome = localStorage.getItem('remis_has_seen_welcome');
        if (!hasSeenWelcome) {
            // We can trigger a gentle prompt here or wait for the home page to mount
            // For now, we'll just set the flag when they actually start a tour or manually.
        }
    }, []);

    return (
        <TutorialContext.Provider value={{ startTour, isTourActive }}>
            {children}
        </TutorialContext.Provider>
    );
};

export const useTutorial = () => {
    const context = useContext(TutorialContext);
    if (!context) {
        throw new Error('useTutorial must be used within a TutorialProvider');
    }
    return context;
};
