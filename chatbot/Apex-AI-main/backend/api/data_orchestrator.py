class DataOrchestrator:
    def get_sector_data(self, sector: str, tenant_id: str, command: str) -> dict:
        """
        Mocks the fetching of enterprise data based on the sector.
        """
        # Baseline mock data
        data = {
            "historical_metrics": {},
            "eps_metrics": {},
            "dps_metrics": {},
            "sentiment": {"score": 85, "label": "Positive"},
            "executive_reports": [],
            "anomalies": [],
            "kpis": {}
        }
        
        if sector == "retail":
            data["historical_metrics"] = {
                "q1_revenue": "100 Cr",
                "q2_revenue": "110 Cr",
                "yoy_growth": "12%"
            }
            data["eps_metrics"] = {"eps": "12.48"}
            data["dps_metrics"] = {"dps": "3.12"}
            data["anomalies"] = ["Unusual spike in inventory turnover for Q2", "Footfall dropped by 5% in Western region"]
            data["kpis"] = {"gmroi": "1.45", "inventory_turnover": "4.2"}
            
        elif sector == "service":
            data["historical_metrics"] = {
                "q1_utilization": "82%",
                "q2_utilization": "85%"
            }
            data["sentiment"] = {"score": 92, "label": "Very Positive"}
            data["anomalies"] = ["SLA breach in support tier 1 on Friday"]
            data["kpis"] = {"csat": "4.8/5", "nps": "65"}
            
        elif sector == "education":
            data["historical_metrics"] = {
                "enrollment_2024": "12,500",
                "enrollment_2025": "13,200"
            }
            data["sentiment"] = {"score": 75, "label": "Neutral"}
            data["anomalies"] = ["Dropout risk increased by 2% in Engineering department"]
            data["kpis"] = {"retention_rate": "92%", "average_attendance": "88%"}
            
        elif sector == "manufacturing":
            data["historical_metrics"] = {
                "q1_production": "50,000 units",
                "q2_production": "55,000 units"
            }
            data["sentiment"] = {"score": 60, "label": "Concerned"}
            data["anomalies"] = ["Equipment failure in line 4 caused 12 hours downtime", "Supply chain delay in raw material X"]
            data["kpis"] = {"oee": "78%", "yield_rate": "95%"}
            
        return data

data_orchestrator = DataOrchestrator()
