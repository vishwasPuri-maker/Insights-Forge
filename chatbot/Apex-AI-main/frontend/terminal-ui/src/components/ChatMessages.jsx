import React from 'react';

const ChatMessages = ({ messages }) => {
  return (
    <div className="messages" role="log" aria-live="polite">
      {messages.map((msg, idx) => (
        <div key={idx} className={`message ${msg.role}`}>
          {msg.role === 'user' ? '> ' : ''}{msg.content}
        </div>
      ))}
    </div>
  );
};

export default ChatMessages;
