if (import.meta.env.DEV) {
  const showErrorOverlay = (err) => {
    const ErrorOverlay = customElements.get('vite-error-overlay');
    if (!ErrorOverlay) {
      return;
    }
    const overlay = new ErrorOverlay(err);
    document.body.appendChild(overlay);
  };

  window.addEventListener('error', (e) => showErrorOverlay(e.error));
  window.addEventListener('unhandledrejection', (e) => showErrorOverlay(e.reason));
}

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)