import React, { createContext, useContext, useState, useEffect } from 'react';

const UserContext = createContext();

const mockProfiles = {
  retail: {
    user: {
      firstName: "Sarah",
      nickname: "Sarah",
      fullName: "Sarah Connor",
      role: "Retail CEO",
      active_sector: "Retail"
    },
    session: {
      last_analytics: "Retail Revenue Forecast Analysis.",
      decision_gravity: "Decision gravity remains stable.",
      last_activity: [
        { time: "2m ago", desc: "Analyzed retail sales trends" },
        { time: "8m ago", desc: "Generated executive dashboard" },
        { time: "1h ago", desc: "Created forecasting model" },
        { time: "1d ago", desc: "Reviewed anomaly report" }
      ]
    },
    dashboard: {
      dynamic_questions: [
        "What factors contributed to the revenue spike shown in this chart?",
        "Compare the current trend with the previous reporting period.",
        "Identify anomalies present in this visualization.",
        "Generate executive insights from this dashboard.",
        "Predict the next trend trajectory using historical data."
      ]
    },
    commands: [
      "/forecast revenue next quarter",
      "/analyze inventory turnover",
      "/compare q1 q2 sales",
      "/customer-segmentation",
      "/detect-sales-anomalies"
    ]
  },
  service: {
    user: {
      firstName: "Michael",
      nickname: "Mike",
      fullName: "Michael Scott",
      role: "Service Operations Manager",
      active_sector: "Service"
    },
    session: {
      last_analytics: "Your service optimization workspace is ready.",
      decision_gravity: "Recent operational vectors have been synchronized.",
      last_activity: [
        { time: "5m ago", desc: "Analyzed service utilization" },
        { time: "15m ago", desc: "Generated SLA compliance report" },
        { time: "2h ago", desc: "Forecasted customer demand" },
        { time: "2d ago", desc: "Detected operational bottlenecks" }
      ]
    },
    dashboard: {
      dynamic_questions: [
        "What caused the drop in SLA compliance?",
        "Compare current ticket volume to last week.",
        "Identify potential bottlenecks in the support queue.",
        "Generate operational efficiency insights.",
        "Predict next week's peak support hours."
      ]
    },
    commands: [
      "/analyze service utilization",
      "/forecast customer demand",
      "/analyze sla compliance",
      "/detect operational bottlenecks",
      "/generate executive summary"
    ]
  },
  education: {
    user: {
      firstName: "Priya",
      nickname: "Priya",
      fullName: "Dr. Priya Sharma",
      role: "Education Director",
      active_sector: "Education"
    },
    session: {
      last_analytics: "Academic intelligence models have been restored.",
      decision_gravity: "Learning analytics remain available.",
      last_activity: [
        { time: "1m ago", desc: "Analyzed student performance" },
        { time: "30m ago", desc: "Predicted dropout risk" },
        { time: "3h ago", desc: "Analyzed attendance trends" },
        { time: "1d ago", desc: "Compared academic years" }
      ]
    },
    dashboard: {
      dynamic_questions: [
        "What factors contributed to the dropout risk spike?",
        "Compare current attendance trends with the previous semester.",
        "Identify anomalies in student performance data.",
        "Generate institutional insights from this dashboard.",
        "Predict next semester's academic performance."
      ]
    },
    commands: [
      "/analyze student performance",
      "/predict dropout risk",
      "/analyze attendance trends",
      "/compare academic years",
      "/generate institutional insights"
    ]
  },
  manufacturing: {
    user: {
      firstName: "Rajesh",
      nickname: "Rajesh",
      fullName: "Rajesh Kumar",
      role: "Manufacturing Executive",
      active_sector: "Manufacturing"
    },
    session: {
      last_analytics: "Production intelligence dashboards are active.",
      decision_gravity: "Supply chain signals have been refreshed.",
      last_activity: [
        { time: "2m ago", desc: "Forecasted production demand" },
        { time: "8m ago", desc: "Analyzed supply chain risk" },
        { time: "1h ago", desc: "Monitored equipment efficiency" },
        { time: "1d ago", desc: "Generated factory performance report" }
      ]
    },
    dashboard: {
      dynamic_questions: [
        "What factors contributed to the production bottleneck?",
        "Compare current equipment efficiency with the previous shift.",
        "Identify supply chain anomalies present in this visualization.",
        "Generate factory insights from this dashboard.",
        "Predict next week's production demand using historical data."
      ]
    },
    commands: [
      "/forecast production demand",
      "/analyze supply down risk",
      "/monitor equipment efficiency",
      "/detect production anomalies",
      "/generate factory performance report"
    ]
  }
};

const API_BASE_URL = 'http://localhost:8000/api/v1';

export const UserProvider = ({ children }) => {
  const [activeProfileId, setActiveProfileId] = useState('retail');
  const [profile, setProfile] = useState(mockProfiles['retail']);

  useEffect(() => {
    // We start with the mock profile, then try to fetch real dashboard metrics
    // to override or add to our context.
    const fetchDashboardContext = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/analytics/dashboard/${activeProfileId}?datetime_lower_bound=2024-01-01`, {
          headers: {
            'Authorization': 'Bearer mock-token'
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          if (data && !data.error) {
            setProfile(prev => ({
              ...prev,
              apiData: data // Store the fetched API data in the profile
            }));
          } else {
            setProfile(mockProfiles[activeProfileId]);
          }
        }
      } catch (err) {
        // Fallback to mock profile if backend is offline
        setProfile(mockProfiles[activeProfileId]);
      }
    };

    setProfile(mockProfiles[activeProfileId]); // Reset immediately on switch
    fetchDashboardContext();
  }, [activeProfileId]);

  const contextValue = {
    profile,
    switchProfile: setActiveProfileId,
    availableProfiles: Object.keys(mockProfiles)
  };

  return (
    <UserContext.Provider value={contextValue}>
      {children}
    </UserContext.Provider>
  );
};

export const useUserContext = () => useContext(UserContext);
