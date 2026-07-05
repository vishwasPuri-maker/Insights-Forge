import React from 'react';

const SECTORS = {
  RETAIL: [
    "/forecast revenue next quarter",
    "/analyze inventory turnover",
    "/compare q1 q2 sales",
    "/customer segmentation",
    "/detect sales anomalies"
  ],
  SERVICE: [
    "/forecast service demand",
    "/analyze utilization",
    "/compare sla performance",
    "/customer satisfaction trends",
    "/detect operational anomalies"
  ],
  EDUCATION: [
    "/analyze student performance",
    "/predict dropout risk",
    "/attendance trends",
    "/compare academic years",
    "/generate institutional insights"
  ],
  MANUFACTURING: [
    "/forecast production demand",
    "/analyze supply chain risk",
    "/equipment efficiency",
    "/detect production anomalies",
    "/generate factory report"
  ]
};

const SectorCommandCards = ({ onCommandSelect }) => {
  return (
    <div className="sector-command-cards">
      <h3 className="section-title">SECTOR INTELLIGENCE COMMANDS</h3>
      <div className="sector-grid">
        {Object.entries(SECTORS).map(([sectorName, commands]) => (
          <div key={sectorName} className="sector-card">
            <h4 className="sector-name">{sectorName}</h4>
            <ul className="command-list">
              {commands.map((cmd, idx) => (
                <li 
                  key={idx} 
                  className="command-item"
                  onClick={() => onCommandSelect(sectorName, cmd)}
                >
                  <span className="command-text">{cmd}</span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SectorCommandCards;
