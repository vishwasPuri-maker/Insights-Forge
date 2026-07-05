import React from 'react';
import { useUserContext } from '../context/UserContext';

const LogoSVG = () => (
  <svg width="200" height="150" viewBox="0 0 200 150" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M100 120 L50 120 L100 70 L110 80 L130 60 L150 120 L100 120 Z" stroke="var(--orange)" strokeWidth="3" fill="none"/>
    <path d="M90 120 L60 120 L95 85 L105 95 L115 85 L140 120 L90 120 Z" stroke="var(--orange)" strokeWidth="1.5" fill="none"/>
    
    <path d="M100 70 L100 30" stroke="var(--orange)" strokeWidth="3" />
    <circle cx="100" cy="20" r="4" fill="var(--orange)" />
    
    <path d="M100 50 L75 35" stroke="var(--orange)" strokeWidth="3" />
    <circle cx="70" cy="30" r="4" fill="var(--orange)" />
    
    <path d="M100 50 L125 35" stroke="var(--orange)" strokeWidth="3" />
    <circle cx="130" cy="30" r="4" fill="var(--orange)" />
    
    <path d="M100 60 L135 60" stroke="var(--orange)" strokeWidth="3" />
    <circle cx="145" cy="60" r="4" fill="var(--orange)" />
    
    <path d="M100 60 L65 60" stroke="var(--orange)" strokeWidth="3" />
    <circle cx="55" cy="60" r="4" fill="var(--orange)" />
  </svg>
);

const WelcomeCard = () => {
  const { profile } = useUserContext();
  const userName = profile.user.firstName || profile.user.nickname || profile.user.fullName;

  return (
    <section className="welcome-panel">
      <div className="divider">Apex AI v2.0.0</div>
      <h2>Welcome back, {userName}.</h2>
      <div className="logo-container glow-text">
        <LogoSVG />
      </div>
      <p>{profile.session.last_analytics}</p>
      <p>{profile.session.decision_gravity}</p>
    </section>
  );
};

export default WelcomeCard;
