"""
Decision Validator
------------------
Executes Pydantic schema validation and computes the multi-signal derived confidence score.
"""

import logging
from typing import Dict, Any
from pydantic import ValidationError
from app.core.config import settings
from app.core.errors import AppError
from app.schemas.decision import DecisionOutput

logger = logging.getLogger("decision-validator")


class DecisionValidator:
    """
    Validates LLM output against structured schemas.
    Applies configurable weight heuristics to derive the final confidence score.
    """

    @staticmethod
    def validate_and_enrich(
        parsed_data: Dict[str, Any],
        retrieval_score: float,
        parser_quality: float,
        retrieved_docs_count: int,
        model_name: str,
        provider_name: str,
        prompt_version: str,
    ) -> DecisionOutput:
        """
        Runs Pydantic validation on parsed decision dict and enrich with derived metadata.
        Calculates multi-signal derived confidence score.
        """
        # Inject metadata parameters if not present
        if "retrieval_score" not in parsed_data:
            parsed_data["retrieval_score"] = retrieval_score
        if "model_used" not in parsed_data:
            parsed_data["model_used"] = model_name
        if "provider" not in parsed_data:
            parsed_data["provider"] = provider_name
        if "embedding_model" not in parsed_data:
            parsed_data["embedding_model"] = getattr(
                settings, "EMBEDDING_MODEL", "all-MiniLM-L6-v2"
            )
        if "prompt_version" not in parsed_data:
            parsed_data["prompt_version"] = prompt_version
        if "retrieved_documents_count" not in parsed_data:
            parsed_data["retrieved_documents_count"] = retrieved_docs_count
        if "generated_at" not in parsed_data:
            from datetime import datetime, timezone

            parsed_data["generated_at"] = datetime.now(timezone.utc)
        if "version" not in parsed_data:
            parsed_data["version"] = "1.0.0"

        # Validate with Pydantic
        try:
            decision = DecisionOutput.model_validate(parsed_data)
        except ValidationError as val_err:
            logger.error(f"Schema validation failed: {str(val_err)}")
            raise AppError(
                status_code=422,
                code="validation_error",
                message=f"LLM decision output failed schema validation: {str(val_err)}",
            )

        # Enforce confidence range bounds
        llm_conf = max(0.0, min(float(decision.confidence), 1.0))

        # Calculate derived confidence weight heuristics
        w_retrieval = settings.DECISION_CONFIDENCE_WEIGHT_RETRIEVAL
        w_llm = settings.DECISION_CONFIDENCE_WEIGHT_LLM
        w_evidence = settings.DECISION_CONFIDENCE_WEIGHT_EVIDENCE
        w_parser = settings.DECISION_CONFIDENCE_WEIGHT_PARSER

        # Compute normalized evidence weight based on counts cited
        evidence_count = len(decision.explanation.evidence)
        evidence_weight = min(evidence_count / 5.0, 1.0)

        # Compute final derived confidence
        derived_confidence = (
            w_retrieval * retrieval_score
            + w_llm * llm_conf
            + w_evidence * evidence_weight
            + w_parser * parser_quality
        )
        # Bounded between 0.0 and 1.0
        decision.confidence = max(0.0, min(derived_confidence, 1.0))

        return decision
