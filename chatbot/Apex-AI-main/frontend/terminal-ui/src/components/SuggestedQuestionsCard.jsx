import React from 'react';
import { useUserContext } from '../context/UserContext';

const SuggestedQuestionsCard = () => {
  const { profile } = useUserContext();

  return (
    <section className="whats-new-panel">
      <div className="panel-header">Suggested Questions</div>
      <ul className="whats-new-list">
        {profile.dashboard.dynamic_questions.map((q, index) => (
          <li key={index}>{q}</li>
        ))}
      </ul>
    </section>
  );
};

export default SuggestedQuestionsCard;
