import { toParadoxLang } from './paradoxMapping';

/**
 * Groups files into sources and targets based on Paradox naming conventions.
 * 
 * @param {Array} files - Flat list of files from the database.
 * @param {Object} selectedProject - The current project object.
 * @returns {Object} { sources: Array, targetsMap: Object }
 */
export const groupFiles = (files, selectedProject) => {
    if (!selectedProject || !files) return { sources: [], targetsMap: {} };

    // Strict Source Identification based on Project Settings
    const dbLang = selectedProject.source_language || 'english';
    const paradoxLang = toParadoxLang(dbLang);
    const sourceSuffix = `_l_${paradoxLang}.yml`;

    const sources = [];
    const targetsMap = {};
    const sourceBaseMap = {};

    const getFileName = (path) => path.replace(/\\/g, '/').split('/').pop();

    // Pass 1: Identify REAL Sources based on filename pattern
    files.forEach(f => {
        const fileName = getFileName(f.file_path);
        if (fileName.toLowerCase().endsWith(sourceSuffix.toLowerCase())) {
            sources.push(f);
            const baseName = fileName.slice(0, -sourceSuffix.length);
            sourceBaseMap[baseName.toLowerCase()] = f;
            targetsMap[f.file_id] = [];
        }
    });

    // Pass 2: Identify Targets (everything that is NOT a source)
    files.forEach(f => {
        // Skip if it was already identified as source
        if (sources.includes(f)) return;

        const fileName = getFileName(f.file_path);

        // Try to match against known source bases
        for (const baseLower in sourceBaseMap) {
            // Check if it looks like a translation: {base}_l_{otherLang}.yml
            if (fileName.toLowerCase().startsWith(baseLower) && fileName.toLowerCase().includes('_l_')) {
                // Ensure it belongs to THIS source file's group
                targetsMap[sourceBaseMap[baseLower].file_id].push(f);
                break; // One file belongs to one source
            }
        }
    });

    return { sources, targetsMap };
};
