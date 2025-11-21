import { useState, useEffect, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';

// --- Mock Data Generators ---
const MOCK_FILES = [
    { name: 'events_l_english.yml', path: 'localization/english/events_l_english.yml', lines: 150 },
    { name: 'modifiers_l_english.yml', path: 'localization/english/modifiers_l_english.yml', lines: 45 },
    { name: 'decisions_l_english.yml', path: 'localization/english/decisions_l_english.yml', lines: 200 },
    { name: 'diplomacy_l_english.yml', path: 'localization/english/diplomacy_l_english.yml', lines: 80 },
    { name: 'gui_l_english.yml', path: 'localization/english/gui_l_english.yml', lines: 320 },
];

const INITIAL_MOCK_STORED_DATA = {
    // Tasks that have been modified or are notes
    'task-note-1': {
        id: 'task-note-1',
        type: 'note',
        title: 'Fix typo in intro',
        status: 'todo',
        comments: 'Line 42 has a typo.',
        priority: 'high'
    },
    // Example of a file task that has moved
    'events_l_english.yml': {
        status: 'in_progress',
        comments: 'Working on the naval events.'
    }
};

export const COLUMNS = ['todo', 'in_progress', 'proofreading', 'paused', 'done'];

export const useKanban = () => {
    const [tasks, setTasks] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    // --- Simulation: Load Data ---
    useEffect(() => {
        const loadData = async () => {
            setIsLoading(true);
            // In a real app, this would fetch the file list and the JSON sidecar
            // await api.getProjectStatus();

            // 1. Generate File Tasks
            const fileTasks = MOCK_FILES.map(file => {
                const storedInfo = INITIAL_MOCK_STORED_DATA[file.name];
                return {
                    id: file.name, // Using filename as ID for simplicity in this mock
                    type: 'file',
                    title: file.name,
                    filePath: file.path,
                    // Default to 'todo' if not stored, or use stored status
                    status: storedInfo?.status || 'todo',
                    comments: storedInfo?.comments || '',
                    priority: 'medium',
                    meta: { lines: file.lines }
                };
            });

            // 2. Load Note Tasks
            const noteTasks = Object.values(INITIAL_MOCK_STORED_DATA)
                .filter(item => item.type === 'note');

            setTasks([...fileTasks, ...noteTasks]);
            setIsLoading(false);
        };

        loadData();
    }, []);

    // --- Actions ---

    const moveTask = useCallback((taskId, newStatus) => {
        setTasks((prev) => prev.map(t =>
            t.id === taskId ? { ...t, status: newStatus } : t
        ));
        // TODO: Trigger "Save" to backend
        console.log(`[Sync] Moved ${taskId} to ${newStatus}`);
    }, []);

    const addNoteTask = useCallback((status = 'todo') => {
        const newTask = {
            id: uuidv4(),
            type: 'note',
            title: 'New Task',
            status,
            comments: '',
            priority: 'medium'
        };
        setTasks(prev => [newTask, ...prev]);
        console.log(`[Sync] Created note ${newTask.id}`);
        return newTask;
    }, []);

    const updateTask = useCallback((taskId, updates) => {
        setTasks(prev => prev.map(t =>
            t.id === taskId ? { ...t, ...updates } : t
        ));
        console.log(`[Sync] Updated ${taskId}`, updates);
    }, []);

    const deleteTask = useCallback((taskId) => {
        setTasks(prev => prev.filter(t => t.id !== taskId));
        console.log(`[Sync] Deleted ${taskId}`);
    }, []);

    return {
        tasks,
        isLoading,
        moveTask,
        addNoteTask,
        updateTask,
        deleteTask,
        columns: COLUMNS
    };
};
