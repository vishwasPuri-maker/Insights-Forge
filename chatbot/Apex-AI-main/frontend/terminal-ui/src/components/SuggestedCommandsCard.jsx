import React from 'react';
import { useUserContext } from '../context/UserContext';

const SuggestedCommandsCard = () => {
  const { profile } = useUserContext();

  return (
    <section className="whats-new-panel">
      <div className="panel-header">Suggested Commands</div>
      <ul className="whats-new-list">
        {profile.commands.map((cmd, index) => (
          <li key={index}><b>{cmd}</b></li>
        ))}
      </ul>
      <a href="#" className="more-link">... /help for more</a>
    </section>
  );
};

export default SuggestedCommandsCard;
