import React from 'react';
import { useUserContext } from '../context/UserContext';

const ActivityCard = () => {
  const { profile } = useUserContext();

  return (
    <section className="activity-panel" aria-label="Recent activity">
      <div className="panel-header">Recent activity</div>
      <ul className="activity-list">
        {profile.session.last_activity.map((activity, index) => (
          <li key={index} className="activity-item">
            <span className="activity-time">{activity.time}</span>
            <span className="activity-desc">{activity.desc}</span>
          </li>
        ))}
      </ul>
      <a href="#" className="more-link">... /resume for more</a>
    </section>
  );
};

export default ActivityCard;
