from typing import Dict, Any
from agents.retrieval import RAGPipeline
from security.guardrails import SecurityGuardrail
from security.audit import AuditLogger
from security.privacy import PrivacyFilter
from agents.formatter import ResponseFormatter
from agents.prompt_engine import PromptTemplateEngine
from agents.llama3_runtime import Llama3Runtime
import json
import time

class MultiAgentRouter:
    def __init__(self):
        self.rag = RAGPipeline()
        self.guardrail = SecurityGuardrail()
        self.auditor = AuditLogger()
        self.privacy = PrivacyFilter()
        self.formatter = ResponseFormatter()
        self.prompt_engine = PromptTemplateEngine()
        self.llama3 = Llama3Runtime()
    
    def route_query(self, user_query: str, tenant_id: str, response_mode: str = "MODE_BUSINESS", db = None, workspace_id = None, organization_id = None) -> Dict[str, Any]:
        """
        Determines query intent and routes to the appropriate virtual sub-agent.
        Enforces read-only boundaries and privacy rules for Apex AI.
        """
        # Privacy Scrubbing (Feature 5)
        clean_query = self.privacy.scrub(user_query)

        # Guardrail check
        is_safe, refusal_msg, severity = self.guardrail.check_query(clean_query)
        
        if not is_safe:
            self.auditor.log_violation(tenant_id, clean_query, severity, refusal_msg)
            return {
                "role": "SecurityAgent",
                "response": refusal_msg,
                "confidence": "HIGH"
            }
            
        query_lower = clean_query.lower()
        context = self.rag.retrieve_context(clean_query, db, workspace_id, organization_id)
        
        # Feature 5: Hallucination Prevention & Confidence Scoring
        if not context or context.strip() == "":
            return {
                "role": "FactCheckAgent",
                "response": "There is insufficient evidence to provide a reliable answer. I cannot verify this data.",
                "confidence": "UNKNOWN"
            }
        
        # Feature 7: Intent Classification & Prompt Template Selection
        analysis_type = self.prompt_engine.classify_query_intent(clean_query)
        
        agent_map = {
            "kpi_analysis": "KPIAnalysisAgent",
            "trend_analysis": "TrendAnalysisAgent",
            "forecasting": "PredictiveAnalyticsAgent",
            "anomaly_detection": "AnomalyDetectionAgent",
            "executive_summary": "ExecutiveSummaryAgent",
            "dashboard_explanation": "DashboardExplanationAgent",
            "recommendation": "RecommendationAgent",
            "comparative_analysis": "ComparativeAnalysisAgent"
        }
        
        confidence_map = {
            "kpi_analysis": "VERY_HIGH",
            "trend_analysis": "HIGH",
            "forecasting": "LOW",
            "anomaly_detection": "MEDIUM",
            "executive_summary": "VERY_HIGH",
            "dashboard_explanation": "HIGH",
            "recommendation": "MEDIUM",
            "comparative_analysis": "HIGH"
        }
        
        agent = agent_map.get(analysis_type, "DescriptiveAnalyticsAgent")
        confidence = confidence_map.get(analysis_type, "MEDIUM")
            
        return {
            "role": agent,
            "analysis_type": analysis_type,
            "context": context,
            "confidence": confidence
        }

    def route_sector_command(self, user_query: str, sector: str, tenant_id: str, user_id: str) -> Dict[str, Any]:
        """
        Executes a sector command, gathering multi-domain intelligence,
        constructing context for the LLM, and returning structured JSON.
        """
        from api.data_orchestrator import data_orchestrator
        
        # 1. Guardrail check
        clean_query = self.privacy.scrub(user_query)
        is_safe, refusal_msg, severity = self.guardrail.check_query(clean_query)
        
        if not is_safe:
            self.auditor.log_violation(tenant_id, clean_query, severity, refusal_msg)
            return {"status": "error", "message": refusal_msg}

        # 2. Gather data
        start_time = time.time()
        sector_data = data_orchestrator.get_sector_data(sector, tenant_id, clean_query)
        
        # 3. Simulate LLM Structured Generation
        # (In reality, we would pass sector_data to self.llama3.build_prompt and parse JSON)
        # We will mock the structured JSON output as requested by the prompt.
        
        response = {
            "status": "success",
            "executive_summary": {
                "title": f"Executive Intelligence: {sector.capitalize()}",
                "overview": f"Analysis complete for command '{user_query}'. Projected growth metrics are positive."
            },
            "key_findings": [
                "Primary metrics align with historical Q2 performance.",
                "Sentiment indicators suggest market optimism."
            ],
            "trend_analysis": {
                "current_trend": "Upward trajectory",
                "forecast": "Continued growth expected through next quarter."
            },
            "sentiment": sector_data.get("sentiment", {"score": 50, "label": "Neutral"}),
            "financial_metrics": {
                "revenue": sector_data.get("historical_metrics", {}).get("q2_revenue", "N/A"),
                "eps": sector_data.get("eps_metrics", {}).get("eps", "N/A"),
                "dps": sector_data.get("dps_metrics", {}).get("dps", "N/A")
            },
            "risk_analysis": {
                "risk_score": "24",
                "risk_level": "LOW"
            },
            "recommendations": [
                "Proceed with planned allocations.",
                "Monitor supply chain anomalies closely."
            ],
            "anomalies": sector_data.get("anomalies", []),
            "charts": [
                {
                    "title": {"text": "Performance Trend"},
                    "tooltip": {"trigger": "axis"},
                    "xAxis": {"type": "category", "data": ["Jan", "Feb", "Mar", "Apr", "May"]},
                    "yAxis": {"type": "value"},
                    "series": [{"data": [120, 132, 101, 134, 90], "type": "line", "smooth": True}]
                }
            ],
            "confidence": 0.96
        }
        
        latency = time.time() - start_time
        
        # 4. Audit Log
        self.auditor.log_execution(
            user_id=user_id,
            tenant_id=tenant_id,
            sector=sector,
            command=user_query,
            apis_called=["data_orchestrator.get_sector_data"],
            prompt_used="sector_intelligence.prompt",
            confidence=0.96,
            latency=latency,
            charts_generated=len(response.get("charts", []))
        )
        
        return response
