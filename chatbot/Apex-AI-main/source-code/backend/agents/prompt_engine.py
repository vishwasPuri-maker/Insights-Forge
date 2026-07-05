import os
from typing import Dict, Optional

class PromptTemplateEngine:
    """
    Loads and manages Llama 3 Instruct prompt templates from the /prompts/ directory.
    Supports all 8 analytical reasoning workflows for Apex AI.
    """
    
    TEMPLATE_MAP = {
        "kpi_analysis": "kpi_analysis.prompt",
        "trend_analysis": "trend_analysis.prompt",
        "forecasting": "forecasting.prompt",
        "anomaly_detection": "anomaly_detection.prompt",
        "executive_summary": "executive_summary.prompt",
        "dashboard_explanation": "dashboard_explanation.prompt",
        "recommendation": "recommendation.prompt",
        "comparative_analysis": "comparative_analysis.prompt"
    }
    
    def __init__(self, prompts_dir: str = "../../prompts"):
        self.prompts_dir = prompts_dir
        self._cache: Dict[str, str] = {}
    
    def load_template(self, analysis_type: str) -> Optional[str]:
        """
        Load a prompt template by analysis type. Returns the raw Llama 3 Instruct string.
        """
        if analysis_type in self._cache:
            return self._cache[analysis_type]
            
        filename = self.TEMPLATE_MAP.get(analysis_type)
        if not filename:
            return None
            
        filepath = os.path.join(self.prompts_dir, filename)
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                template = f.read()
            self._cache[analysis_type] = template
            return template
        except FileNotFoundError:
            print(f"PROMPT ENGINE WARNING: Template '{filename}' not found at {filepath}")
            return None
    
    def render_prompt(self, analysis_type: str, input_data: str, **kwargs) -> Optional[str]:
        """
        Loads the template and injects the user's input data into the {input_data} placeholder.
        Additional kwargs (e.g., forecast_horizon) are also substituted.
        """
        template = self.load_template(analysis_type)
        if not template:
            return None
        
        rendered = template.replace("{input_data}", input_data)
        for key, value in kwargs.items():
            rendered = rendered.replace("{" + key + "}", str(value))
        
        return rendered
    
    def classify_query_intent(self, query: str) -> str:
        """
        Deterministic intent classifier to route natural language queries to the correct template.
        """
        query_lower = query.lower()
        
        # Check more specific intents first before falling back to general ones
        if any(kw in query_lower for kw in ["forecast", "predict", "projection", "next quarter"]):
            return "forecasting"
        elif any(kw in query_lower for kw in ["anomaly", "unexpected", "spike", "outlier", "deviat"]):
            return "anomaly_detection"
        elif any(kw in query_lower for kw in ["recommend", "improve", "optimize", "strategy"]):
            return "recommendation"
        elif any(kw in query_lower for kw in ["compare", "versus", "vs", "difference", "benchmark"]):
            return "comparative_analysis"
        elif any(kw in query_lower for kw in ["trend", "growth", "momentum", "pattern"]):
            return "trend_analysis"
        elif any(kw in query_lower for kw in ["dashboard", "visual", "chart", "widget"]):
            return "dashboard_explanation"
        elif any(kw in query_lower for kw in ["summary", "summarize", "overview", "report"]):
            return "executive_summary"
        elif any(kw in query_lower for kw in ["kpi", "metric", "revenue", "churn", "retention", "conversion"]):
            return "kpi_analysis"
        
        return "kpi_analysis"  # Default fallback
    
    def list_available_templates(self):
        """Returns all registered analysis types."""
        return list(self.TEMPLATE_MAP.keys())
