import React from 'react';

const TranslationIcon = (props) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    {...props}
  >
    <path d="M5 12h14M12 5l7 7-7 7"></path>
    <path d="M2 12a10 10 0 0 1 10-10v0a10 10 0 0 1 10 10v0a10 10 0 0 1-10 10v0a10 10 0 0 1-10-10z"></path>
    <path d="M12 2L14.39 5.39L18 6.34L15.5 9.27L16.2 13.1L12 11.25L7.8 13.1L8.5 9.27L6 6.34L9.61 5.39z"></path>
  </svg>
);

export default TranslationIcon;
