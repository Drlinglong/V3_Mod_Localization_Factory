import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import en from './locales/en/translation.json';
import zh from './locales/zh/translation.json';

const resources = {
  en: {
    translation: en,
  },
  zh: {
    translation: zh,
  },
};

i18n
  .use(LanguageDetector) // 探测浏览器语言
  .use(initReactI18next) // 将 i18n 实例传递给 react-i18next
  .init({
    resources,
    fallbackLng: 'en', // 如果当前语言没有对应的翻译，则使用英文
    interpolation: {
      escapeValue: false, // React已经可以防范XSS
    },
  });

export default i18n;