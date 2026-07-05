import React from 'react';

const BrowserFrame = ({ children }) => {
  return (
    <div className="window">
      <div className="window-header">
        <div className="mac-buttons">
          <div className="mac-btn close"></div>
          <div className="mac-btn minimize"></div>
          <div className="mac-btn maximize"></div>
        </div>
      </div>
      {children}
    </div>
  );
};

export default BrowserFrame;
