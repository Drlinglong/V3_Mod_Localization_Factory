/**
 * Paradox Mapping Utility
 * Adapts between Standard ISO Codes (used in DB/Frontend State) and Paradox Legacy Codes (used in Files).
 */

export const LanguageMapping = {
    // ISO -> Paradox
    'en': 'english',
    'zh-cn': 'simp_chinese',
    'fr': 'french',
    'de': 'german',
    'es': 'spanish',
    'ja': 'japanese',
    'ko': 'korean',
    'pl': 'polish',
    'pt-br': 'braz_por',
    'ru': 'russian',
    'tr': 'turkish',
};

// Reverse Mapping: Paradox -> ISO
export const ReverseLanguageMapping = Object.entries(LanguageMapping).reduce((acc, [iso, paradox]) => {
    acc[paradox] = iso;
    return acc;
}, {});

export const GameMapping = {
    // Standard ID -> Label/Legacy
    'stellaris': 'Stellaris',
    'hoi4': 'Hearts of Iron IV',
    'vic3': 'Victoria 3',
    'ck3': 'Crusader Kings III',
    'eu4': 'Europa Universalis IV'
};

// Normalization Helper
export const normalizeGameId = (val) => {
    if (!val) return 'stellaris';
    val = val.toLowerCase();
    // Map full names to IDs
    const reverseMap = {
        'victoria 3': 'vic3',
        'victoria3': 'vic3',
        'hearts of iron iv': 'hoi4'
    };
    return reverseMap[val] || val;
};

export const toParadoxLang = (isoCode) => {
    if (!isoCode) return 'english';
    return LanguageMapping[isoCode.toLowerCase()] || isoCode.toLowerCase();
};

export const toIsoLang = (paradoxCode) => {
    if (!paradoxCode) return 'en';
    return ReverseLanguageMapping[paradoxCode.toLowerCase()] || paradoxCode.toLowerCase();
};
