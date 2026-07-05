import React, { useState, useRef, useEffect } from 'react';

const CommandPrompt = ({ onCommand }) => {
  const [input, setInput] = useState('');
  const inputRef = useRef(null);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && input.trim() !== '') {
      onCommand(input);
      setInput('');
    }
  };

  useEffect(() => {
    // Auto focus terminal input on mount
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  return (
    <div className="terminal-input">
      <span className="prompt">{'>'}</span>
      <input
        ref={inputRef}
        type="text"
        id="apex-input"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder='Try "edit <filepath>" to ...'
        aria-label="Chat input"
        role="textbox"
        autoComplete="off"
        spellCheck="false"
      />
      <span className="cursor"></span>
    </div>
  );
};

export default CommandPrompt;
