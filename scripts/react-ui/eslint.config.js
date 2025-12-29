import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import { defineConfig, globalIgnores } from 'eslint/config'

export default defineConfig([
  globalIgnores(['dist', 'src-tauri']),
  {
    files: ['**/*.{js,jsx}'],
    extends: [
      js.configs.recommended,
      reactHooks.configs['recommended-latest'],
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      ecmaVersion: 2020,
      globals: {
        ...globals.browser,
        ...globals.node, // Add node globals for process, etc.
      },
      parserOptions: {
        ecmaVersion: 'latest',
        ecmaFeatures: { jsx: true },
        sourceType: 'module',
      },
    },
    rules: {
      // === 放宽 "未使用变量" 规则 ===
      // 允许以 _ 开头的未使用变量（常见约定）
      // 允许以大写字母开头的未使用变量（组件名、常量）
      'no-unused-vars': ['warn', {
        varsIgnorePattern: '^_|^[A-Z]',
        argsIgnorePattern: '^_',
      }],

      // === 放宽 React Hooks 依赖检查 ===
      // 将错误降级为警告，避免阻塞开发
      'react-hooks/exhaustive-deps': 'warn',

      // === 允许 Context 导出非组件 ===
      // Fast Refresh 限制过于严格，改为警告
      'react-refresh/only-export-components': ['warn', {
        allowConstantExport: true,
      }],

      // === 其他优化 ===
      // 允许不必要的转义（正则表达式中常见）
      'no-useless-escape': 'warn',
    },
  },
])
