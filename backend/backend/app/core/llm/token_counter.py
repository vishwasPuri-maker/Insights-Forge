"""
Token Counter
-------------
Abstraction for estimating and counting prompt and completion tokens.
"""


class TokenCounter:
    """
    Utility to count or estimate token counts for prompts and completions.
    """

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """
        Estimates the number of tokens in a text block using character heuristic (chars / 4).
        """
        if not text:
            return 0
        return len(text) // 4
