"""
Decision Parser
---------------
Resilient extraction and parsing of JSON objects from LLM text responses.
Handles fenced code blocks, conversational wraps, trailing commas, and truncated braces.
"""

import json
import re
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger("decision-parser")


class DecisionParser:
    """
    Parses raw LLM text outputs into Python dictionaries.
    Maintains parser quality metrics for confidence calculations.
    """

    @staticmethod
    def parse_raw_response(text: str) -> Tuple[Dict[str, Any], float]:
        """
        Extracts JSON from response text.
        Returns:
            Tuple[parsed_dict, parser_quality_score]
            where parser_quality_score is:
              - 1.0: Perfect parse without structural modifications.
              - 0.5: Recovered parse (stripped markdown, resolved truncated scopes, or fixed trailing commas).
              - 0.0: Failed parse.
        """
        if not text:
            return {}, 0.0

        cleaned = text.strip()
        quality = 1.0

        # 1. Attempt raw parsing first
        try:
            return json.loads(cleaned), quality
        except json.JSONDecodeError:
            pass

        # 2. Extract JSON using bracket bounding to handle conversational wraps (before/after text)
        # Fallback: search for first '{' and last '}'
        start_idx = cleaned.find("{")
        end_idx = cleaned.rfind("}")

        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            extracted = cleaned[start_idx : end_idx + 1]
            quality = 0.5
            try:
                return json.loads(extracted), quality
            except json.JSONDecodeError:
                cleaned = extracted
        elif start_idx != -1:
            # Missing closing brace entirely (truncated output)
            extracted = cleaned[start_idx:]
            cleaned = extracted
            quality = 0.5

        # 3. Clean up common structural syntax anomalies
        # Remove trailing commas before closing braces/brackets
        cleaned = re.sub(r",\s*([\]}])", r"\1", cleaned)

        # 4. Attempt to parse cleaned string
        try:
            return json.loads(cleaned), quality
        except json.JSONDecodeError:
            pass

        # 5. Recovery for truncated JSON payloads (auto-close open structures)
        try:
            recovered_text = DecisionParser._close_truncated_json(cleaned)
            return json.loads(recovered_text), 0.5
        except Exception:
            pass

        logger.warning("Failed to parse LLM response as JSON.")
        return {}, 0.0

    @staticmethod
    def _close_truncated_json(text: str) -> str:
        """
        Attempts to balance unclosed brackets and braces for truncated JSON streams.
        """
        open_braces = 0
        open_brackets = 0
        in_string = False
        escape = False

        for char in text:
            if char == '"' and not escape:
                in_string = not in_string
            elif char == "\\" and not escape:
                escape = True
                continue

            if not in_string:
                if char == "{":
                    open_braces += 1
                elif char == "}":
                    open_braces = max(0, open_braces - 1)
                elif char == "[":
                    open_brackets += 1
                elif char == "]":
                    open_brackets = max(0, open_brackets - 1)

            escape = False

        fixed_text = text
        # If string is open, close it
        if in_string:
            fixed_text += '"'

        # Close arrays first, then objects
        if open_brackets > 0:
            fixed_text += "]" * open_brackets
        if open_braces > 0:
            fixed_text += "}" * open_braces

        return fixed_text
