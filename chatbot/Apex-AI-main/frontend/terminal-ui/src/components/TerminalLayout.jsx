import React from 'react';

const TerminalLayout = ({ children }) => {
  return (
    <main className="terminal" role="main">
      <div className="terminal-effects"></div>
      {children}
    </main>
  );
};

export default TerminalLayout;
