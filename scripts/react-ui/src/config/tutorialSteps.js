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
                    side: "top",
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
                    align: 'start'
                }
            }
        ],
        'project-management': [ // Fallback
            {
                element: '#project-list-container',
                popover: {
                    title: t('tutorial.project_management.list.title', 'Project List'),
                    description: t('tutorial.project_management.list.desc', 'View and manage all your localization projects here.'),
                    side: "bottom",
                    align: 'center'
                }
            }
        ],
        'project-management-list': [
            {
                element: '#project-list-container',
                popover: {
                    title: t('tutorial.project_management.list.title', 'Project List'),
                    description: t('tutorial.project_management.list.desc', 'View and manage all your localization projects here.'),
                    side: "bottom",
                    align: 'center'
                }
            },
            {
                element: '#create-project-btn',
                popover: {
                    title: t('tutorial.project_management.create.title', 'Create Project'),
                    description: t('tutorial.project_management.create.desc', 'Click here to start a new localization project from a folder.'),
                    side: "right",
                    align: 'start'
                }
            }
        ],
        'project-management-dashboard': [
            {
                element: '#new-task-btn',
                popover: {
                    title: t('tutorial.project_management.new_task.title'),
                    description: t('tutorial.project_management.new_task.desc'),
                    side: "right",
                    align: 'start'
                }
            },
            {
                element: '#manage-paths-btn',
                popover: {
                    title: t('tutorial.project_management.paths.title'),
                    description: t('tutorial.project_management.paths.desc'),
                    side: "bottom",
                    align: 'end'
                }
            },
            {
                element: '#kanban-tab-control',
                popover: {
                    title: t('tutorial.project_management.tabs.title', 'Task Board'),
                    description: t('tutorial.project_management.tabs.desc', 'Switch to the Task Board tab to see your Kanban board.'),
                    side: "bottom",
                    align: 'center'
                }
            }
        ],
        'translation-step-0': [
            {
                element: '#translation-project-list',
                popover: {
                    title: t('tutorial.translation.select.title', 'Select Project'),
                    description: t('tutorial.translation.select.desc', 'Please select a project to begin the translation process.'),
                    side: "bottom",
                    align: 'center'
                }
            }
        ],
        'translation-step-1': [
            {
                element: '#translation-config-card',
                popover: {
                    title: t('tutorial.translation.config.title', 'Configure Translation'),
                    description: t('tutorial.translation.config.desc', 'Set up your source/target languages and choosing an AI model.'),
                    side: "right",
                    align: 'start'
                }
            },
            {
                element: '#translation-start-btn',
                popover: {
                    title: t('tutorial.translation.start.title', 'Start Batch'),
                    description: t('tutorial.translation.start.desc', 'Click this to begin the automated translation batch.'),
                    side: "top",
                    align: 'end'
                }
            }
        ],
        'translation-step-2': [
            {
                element: '#task-runner-container',
                popover: {
                    title: t('tutorial.translation.processing.title', 'Processing'),
                    description: t('tutorial.translation.processing.desc', 'The AI is now translating your files. You can watch the real-time logs here.'),
                    side: "top",
                    align: 'center'
                }
            }
        ],
        'glossary-manager': [
            {
                element: '#glossary-search',
                popover: {
                    title: t('tutorial.glossary.search.title'),
                    description: t('tutorial.glossary.search.desc'),
                    side: "bottom",
                    align: 'start'
                }
            },
            {
                element: '#glossary-file-list',
                popover: {
                    title: t('tutorial.glossary.files.title'),
                    description: t('tutorial.glossary.files.desc'),
                    side: "right",
                    align: 'start'
                }
            },
            {
                element: '#glossary-entries-table',
                popover: {
                    title: t('tutorial.glossary.table.title'),
                    description: t('tutorial.glossary.table.desc'),
                    side: "top",
                    align: 'center'
                }
            }
        ],
        'proofreading': [
            {
                element: '#proofreading-mod-select',
                popover: {
                    title: t('tutorial.proofreading.mod_select.title'),
                    description: t('tutorial.proofreading.mod_select.desc'),
                    side: "bottom",
                    align: 'start'
                }
            },
            {
                element: '#proofreading-main-content',
                popover: {
                    title: t('tutorial.proofreading.editor.title'),
                    description: t('tutorial.proofreading.editor.desc'),
                    side: "top",
                    align: 'center'
                }
            },
            {
                element: '#proofreading-validate-btn',
                popover: {
                    title: t('tutorial.proofreading.validate.title'),
                    description: t('tutorial.proofreading.validate.desc'),
                    side: "left",
                    align: 'start'
                }
            }
        ]
    };

    return steps[pageName] || [];
};
