"""
Decision Engine
---------------
Orchestrates prompt compilation and LLM generation execution for Decision Intelligence.
Separates prompt building from LLM invocation.
"""

import logging
from typing import Optional
from app.core.llm.factory import LLMFactory
from app.core.llm.retry import RetryExecutor

logger = logging.getLogger("decision-engine")


class DecisionPromptBuilder:
    """
    Handles construction of pure prompts for structured decision card analysis.
    Defines instruction templates forcing a JSON schema output with explainability blocks.
    """

    @staticmethod
    def build_system_prompt() -> str:
        return (
            "You are an expert Enterprise Decision Intelligence AI system.\n"
            "Analyze the provided RAG context and user query to generate a structured recommendation card.\n\n"
            "You MUST respond ONLY with a raw JSON object matching the schema below. Do not include any conversational text before or after the JSON.\n\n"
            "JSON Schema:\n"
            "{\n"
            '  "title": "A concise, actionable title for the recommendation",\n'
            '  "summary": "A brief summary of the business situation",\n'
            '  "recommendation": "The clear human-readable plain text recommendation. Keep it focused on the main action.",\n'
            '  "confidence": 0.85, // A decimal float value between 0.0 and 1.0 representing self-assessed model confidence\n'
            '  "priority": "High", // Must be exactly one of: "High", "Medium", "Low"\n'
            '  "recommendation_type": "Insight", // Must be exactly one of: "Insight", "Optimization", "Warning", "Opportunity", "Forecast"\n'
            '  "explanation": {\n'
            '    "reasoning": "Detailed, bulletproof explanation of the logical path to this recommendation.",\n'
            '    "evidence": ["Evidence cite 1", "Evidence cite 2"], // Concrete facts/data found in context\n'
            '    "assumptions": ["Assumption 1", "Assumption 2"], // Explicit assumptions made during calculation\n'
            '    "confidence_reason": "Specific reasoning why this confidence score was assigned",\n'
            '    "limitations": ["When not to trust this 1", "Risk factor 2"] // Bound conditions or when to NOT trust this recommendation\n'
            "  },\n"
            '  "kpis": [\n'
            "    {\n"
            '      "metric": "Name of the KPI",\n'
            '      "value": "Calculated value (e.g. 15% increase)",\n'
            '      "target": "Target value or None if not applicable"\n'
            "    }\n"
            "  ],\n"
            '  "sources": [\n'
            "    {\n"
            '      "document_id": "UUID or filename of the document referenced",\n'
            '      "chunk_id": "UUID or index of the chunk referenced",\n'
            '      "page": 12, // Page integer if available, or null\n'
            '      "score": 0.91 // Match score or null\n'
            "    }\n"
            "  ],\n"
            '  "limitations": ["Same limitations list duplicated at the root level for easy schema mapping"]\n'
            "}\n"
        )

    @staticmethod
    def build_user_prompt(query: str, context: str) -> str:
        return (
            f"Business Search Query: {query}\n\n"
            f"Retrieved Workspace RAG Context:\n"
            f"---------------------------------\n"
            f"{context}\n"
            f"---------------------------------\n\n"
            f"Generate the JSON recommendation now."
        )


class DecisionEngine:
    """
    Coordinates model selection and executes text generation via the LLM Provider.
    Supports timeout configuration overrides and exponential backoff retry execution.
    """

    def __init__(self) -> None:
        self.llm_provider = LLMFactory.get_provider()
        self.prompt_version = "1.0.0"

    def generate_decision_text(
        self, query: str, context: str, timeout_override: Optional[float] = None
    ) -> str:
        """
        Assembles system & user messages and calls the LLM provider.
        Utilizes RetryExecutor to handle transient connectivity failures.
        """
        system_msg = DecisionPromptBuilder.build_system_prompt()
        user_msg = DecisionPromptBuilder.build_user_prompt(query, context)

        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ]

        def invoke_llm():
            # Use generation call which returns LLMResponse
            return self.llm_provider.generate(
                messages=messages,
                options={"temperature": 0.1},  # low temperature for stable JSON outputs
            )

        try:
            logger.info("Triggering LLM completion via DecisionEngine.")
            response = RetryExecutor.execute(invoke_llm)
            # Response is (LLMResponse, retry_count)
            llm_resp, retry_count = response
            return llm_resp.text
        except Exception as e:
            logger.error(
                f"DecisionEngine LLM completion failed after retries: {str(e)}"
            )
            raise e
