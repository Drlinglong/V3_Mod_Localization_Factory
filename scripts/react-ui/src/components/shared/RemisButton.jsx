import React from 'react';
import './RemisButton.css';

const RemisButton = ({ children, onClick, ...props }) => {
  return (
    <button className="remis-button" onClick={onClick} {...props}>
      {children}
    </button>
  );
};

export default RemisButton;
