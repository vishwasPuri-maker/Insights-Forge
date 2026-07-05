import json
import os

class ResponseFormatter:
    def __init__(self, templates_path: str = "../../response_templates.json"):
        # We will mock the templates here for rapid execution since the json is in the root directory.
        self.templates = {
            "MODE_EXECUTIVE": "Executive Summary:\n{context}\n\nBusiness Impact:\nPositive growth trajectory.\n\nConfidence: {confidence}",
            "MODE_TECHNICAL": "Methodology:\nVector Similarity Search (RAG Pipeline)\n\nDataset:\nBusiness Telemetry DB\n\nAnalysis:\n{context}\n\nLimitations:\nMock environment constraints applied.\n\nConfidence: {confidence}",
            "MODE_CONCISE": "{context}\n\nConfidence: {confidence}",
            "MODE_ANALYST": "Observation: {context}\n\nInterpretation: The data aligns with projected targets.\n\nConfidence: {confidence}\nRecommendation: Monitor trailing metrics.",
            "MODE_BUSINESS": "Based on the analysis, I found the following:\n{context}\n\nConfidence: {confidence}"
        }

    def format_response(self, context: str, confidence: str, mode: str) -> str:
        """
        Takes raw context from the RAG pipeline and wraps it in the enterprise-compliant structural tone.
        """
        # Ensure we always default to a safe business tone if mode is unrecognized
        template = self.templates.get(mode, self.templates["MODE_BUSINESS"])
        return template.format(context=context, confidence=confidence)
