/**
 * Tutorial steps configuration
 */
export const getTutorialSteps = (t, pageName) => {
    const steps = {
        home: [
            {
                element: '#welcome-banner',
                popover: {
                    title: t('tutorial.home.welcome.title'),
                    description: t('tutorial.home.welcome.desc'),
                    side: "bottom",
                    align: 'start'
                }
            },
            {
                element: '#stat-cards',
                popover: {
                    title: t('tutorial.home.stats.title'),
                    description: t('tutorial.home.stats.desc'),
                    side: "bottom",
                    align: 'center'
                }
            },
            {
                element: '#recent-activity',
                popover: {
                    title: t('tutorial.home.activity.title'),
                    description: t('tutorial.home.activity.desc'),
                    side: "left",
                    align: 'start'
                }
            },
            {
                element: '#quick-links',
                popover: {
                    title: t('tutorial.home.quick_links.title'),
                    description: t('tutorial.home.quick_links.desc'),
                    side: "left",
                    align: 'start'
                }
            },
            {
                element: '#sidebar-nav',
                popover: {
                    title: t('tutorial.home.navigation.title'),
                    description: t('tutorial.home.navigation.desc'),
                    side: "right",
                    align: 'center'
                }
            }
        ],
        // Additional pages can be added here...
        'glossary-manager': [
            {
                element: '#glossary-search',
                popover: {
                    title: t('tutorial.glossary.search.title'),
                    description: t('tutorial.glossary.search.desc'),
                    side: "bottom",
                    align: 'start'
                }
            }
        ]
    };

    return steps[pageName] || [];
};
