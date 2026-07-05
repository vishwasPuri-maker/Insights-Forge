from typing import Dict, Any
from agents.retrieval import RAGPipeline
from security.guardrails import SecurityGuardrail
from security.audit import AuditLogger
from security.privacy import PrivacyFilter
from agents.formatter import ResponseFormatter
from agents.prompt_engine import PromptTemplateEngine
from agents.llama3_runtime import Llama3Runtime

class MultiAgentRouter:
    def __init__(self):
        self.rag = RAGPipeline()
        self.guardrail = SecurityGuardrail()
        self.auditor = AuditLogger()
        self.privacy = PrivacyFilter()
        self.formatter = ResponseFormatter()
        self.prompt_engine = PromptTemplateEngine()
        self.llama3 = Llama3Runtime()
    
    def route_query(self, user_query: str, tenant_id: str, response_mode: str = "MODE_BUSINESS") -> Dict[str, Any]:
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
        context = self.rag.retrieve_context(clean_query)
        
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
        
        # Feature 8: Construct the Llama 3 Instruct prompt for vLLM inference
        system_prompt = f"You are Apex AI. Analysis type: {analysis_type}. Agent: {agent}."
        llama3_prompt = self.llama3.build_prompt(
            system_prompt=system_prompt,
            user_query=clean_query,
            rag_context=context,
            conversation_history=""
        )
        
        # Validate token budget before inference
        budget_check = self.llama3.check_context_budget(llama3_prompt)
        
        formatted_response = self.formatter.format_response(context, confidence, response_mode)
            
        return {
            "role": agent,
            "analysis_type": analysis_type,
            "response": formatted_response,
            "confidence": confidence,
            "token_budget": budget_check
        }
