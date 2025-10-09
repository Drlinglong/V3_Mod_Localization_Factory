// scripts/react-ui/src/config/themes.js

/**
 * A centralized configuration for all available themes in the application.
 * This array is used to dynamically generate the theme selection UI.
 *
 * To add a new theme:
 * 1. Create a new CSS file in `src/themes/`.
 * 2. Add an `@import` statement for the new CSS file in `src/themes/index.css`.
 * 3. Add a new translation key for the theme's display name in the i18n locale files.
 * 4. Add a new object to this array with the theme's details.
 */
export const AVAILABLE_THEMES = [
  {
    id: 'light',
    nameKey: 'theme_light', // Corresponds to the key in translation.json
  },
  {
    id: 'dark',
    nameKey: 'theme_dark',
  },
  {
    id: 'theme-victorian',
    nameKey: 'theme_victorian',
  },
  {
    id: 'theme-byzantine',
    nameKey: 'theme_byzantine',
  },
];
