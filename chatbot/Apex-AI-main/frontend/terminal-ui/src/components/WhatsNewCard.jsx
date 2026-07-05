import React from 'react';

const WhatsNewCard = () => {
  return (
    <section className="whats-new-panel">
      <div className="panel-header">What's new</div>
      <ul className="whats-new-list">
        <li><b>/forecast</b> to project trends</li>
        <li><b>/anomaly-detect</b> for review</li>
        <li><b>ctrl+b</b> to create reports</li>
      </ul>
      <a href="#" className="more-link">... /help for more</a>
    </section>
  );
};

export default WhatsNewCard;
