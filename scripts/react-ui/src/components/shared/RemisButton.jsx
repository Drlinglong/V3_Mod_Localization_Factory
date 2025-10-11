import React from 'react';

const RemisButton = ({ children, onClick, ...props }) => {
  return (
    <button className="remis-button" onClick={onClick} {...props}>
      {children}
    </button>
  );
};

export default RemisButton;
