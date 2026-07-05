import React from 'react';
import ChartRenderer from './ChartRenderer';

const IntelligenceDashboard = ({ responseData }) => {
  if (!responseData) return null;

  const {
    executive_summary,
    key_findings,
    trend_analysis,
    sentiment,
    financial_metrics,
    risk_analysis,
    recommendations,
    anomalies,
    charts,
    confidence
  } = responseData;

  const confidencePercentage = confidence ? Math.round(confidence * 100) : 0;
  
  return (
    <div className="intelligence-dashboard fade-in">
      <div className="dashboard-header">
        <h2 className="dashboard-title">Apex AI Intelligence Report</h2>
        <div className="confidence-meter">
          <span className="confidence-label">DECISION CONFIDENCE:</span>
          <span className={`confidence-value ${confidencePercentage > 90 ? 'high' : 'medium'}`}>
            {confidencePercentage}%
          </span>
        </div>
      </div>

      <div className="dashboard-grid">
        {/* Executive Summary Panel */}
        <div className="dashboard-panel exec-summary">
          <h3>EXECUTIVE SUMMARY</h3>
          <h4>{executive_summary?.title}</h4>
          <p>{executive_summary?.overview}</p>
        </div>

        {/* Sentiment and Risk */}
        <div className="dashboard-panel side-panel">
          <div className="metric-box">
            <h3>MARKET SENTIMENT</h3>
            <div className={`sentiment-score ${sentiment?.label?.toLowerCase()}`}>
              <span className="score">{sentiment?.score}</span>
              <span className="label">{sentiment?.label}</span>
            </div>
          </div>
          
          <div className="metric-box">
            <h3>RISK ANALYSIS</h3>
            <div className={`risk-score ${risk_analysis?.risk_level?.toLowerCase()}`}>
              <span className="score">{risk_analysis?.risk_score}</span>
              <span className="label">{risk_analysis?.risk_level}</span>
            </div>
          </div>
        </div>

        {/* Financial Metrics */}
        {financial_metrics && (
          <div className="dashboard-panel metrics-panel full-width">
            <h3>FINANCIAL METRICS</h3>
            <div className="metrics-grid">
              {Object.entries(financial_metrics).map(([key, value]) => (
                <div key={key} className="metric-item">
                  <span className="metric-label">{key.replace('_', ' ').toUpperCase()}</span>
                  <span className="metric-value">{value}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Charts */}
        {charts && charts.length > 0 && (
          <div className="dashboard-panel full-width chart-panel">
            <h3>TREND VISUALIZATION</h3>
            {charts.map((chartConfig, idx) => (
              <ChartRenderer key={idx} chartConfig={chartConfig} />
            ))}
          </div>
        )}

        {/* Key Findings and Recommendations */}
        <div className="dashboard-panel full-width text-lists">
          <div className="list-container">
            <h3>KEY FINDINGS</h3>
            <ul>
              {key_findings?.map((finding, idx) => (
                <li key={idx}>
                  {typeof finding === 'object' ? JSON.stringify(finding) : finding}
                </li>
              ))}
            </ul>
          </div>
          
          <div className="list-container">
            <h3>RECOMMENDATIONS</h3>
            <ul>
              {recommendations?.map((rec, idx) => (
                <li key={idx}>
                  {typeof rec === 'object' ? JSON.stringify(rec) : rec}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Anomalies */}
        {anomalies && anomalies.length > 0 && (
          <div className="dashboard-panel anomalies-panel full-width anomaly-highlight">
            <h3>DETECTED ANOMALIES</h3>
            <ul>
              {anomalies.map((anomaly, idx) => (
                <li key={idx}>
                  {typeof anomaly === 'object' ? JSON.stringify(anomaly) : anomaly}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default IntelligenceDashboard;
