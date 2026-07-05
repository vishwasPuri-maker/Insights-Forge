import os
import yaml
from typing import Dict, List, Optional

class Llama3Runtime:
    """
    Production runtime engine for constructing, serializing, and managing
    Llama 3 Instruct prompts for Apex AI vLLM inference.
    """
    
    # Llama 3 Instruct special tokens
    BEGIN_OF_TEXT = "<|begin_of_text|>"
    SYSTEM_HEADER = "<|start_header_id|>system<|end_header_id|>"
    USER_HEADER = "<|start_header_id|>user<|end_header_id|>"
    ASSISTANT_HEADER = "<|start_header_id|>assistant<|end_header_id|>"
    END_OF_TURN = "<|eot_id|>"
    
    # Separators
    SEP_SYSTEM = "=== SYSTEM ==="
    SEP_GOVERNANCE = "=== GOVERNANCE ==="
    SEP_CONTEXT = "=== CONTEXT ==="
    SEP_MEMORY = "=== MEMORY ==="
    SEP_USER = "=== USER ==="
    SEP_RESPONSE = "=== RESPONSE ==="
    
    # Stop sequences
    STOP_SEQUENCES = [
        "<|eot_id|>",
        "<|start_header_id|>",
        "USER:",
        "SYSTEM:",
        "ASSISTANT:"
    ]
    
    # Hard stops (emergency termination triggers)
    HARD_STOPS = [
        "SYSTEM PROMPT LEAK",
        "CHAIN OF THOUGHT",
        "SQL EXECUTION",
        "ROLE OVERRIDE"
    ]
    
    def __init__(self, config_path: str = "../../llama3_runtime_config.yaml"):
        self.config = self._load_config(config_path)
        self.generation_params = self._build_generation_params()
    
    def _load_config(self, path: str) -> Dict:
        """Load the YAML runtime configuration."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # Fallback to hardcoded defaults
            return {
                "generation": {
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "top_k": 40,
                    "max_tokens": 2048,
                    "repeat_penalty": 1.1,
                    "do_sample": False,
                    "seed": 42,
                    "stream": True
                },
                "context": {
                    "max_context_length": 8192
                }
            }
    
    def _build_generation_params(self) -> Dict:
        """Extract vLLM-compatible generation parameters."""
        gen = self.config.get("generation", {})
        return {
            "temperature": gen.get("temperature", 0.1),
            "top_p": gen.get("top_p", 0.9),
            "top_k": gen.get("top_k", 40),
            "max_tokens": gen.get("max_tokens", 2048),
            "repetition_penalty": gen.get("repeat_penalty", 1.1),
            "seed": gen.get("seed", 42),
            "stop": self.STOP_SEQUENCES
        }
    
    def build_prompt(
        self,
        system_prompt: str,
        user_query: str,
        rag_context: str = "",
        conversation_history: str = ""
    ) -> str:
        """
        Constructs a fully serialized Llama 3 Instruct prompt string
        ready for vLLM inference.
        """
        # Inject RAG context and memory into system prompt
        full_system = system_prompt
        if conversation_history:
            full_system += f"\n\n{self.SEP_MEMORY}\n{conversation_history}"
        if rag_context:
            full_system += f"\n\n{self.SEP_CONTEXT}\n{rag_context}"
        
        # Assemble Llama 3 Instruct format
        prompt = (
            f"{self.BEGIN_OF_TEXT}\n\n"
            f"{self.SYSTEM_HEADER}\n\n"
            f"{full_system}\n\n"
            f"{self.END_OF_TURN}\n\n"
            f"{self.USER_HEADER}\n\n"
            f"{self.SEP_USER}\n\n"
            f"{user_query}\n\n"
            f"{self.END_OF_TURN}\n\n"
            f"{self.ASSISTANT_HEADER}\n\n"
            f"{self.SEP_RESPONSE}\n"
        )
        
        return prompt
    
    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation (~4 chars per token for English text)."""
        return len(text) // 4
    
    def check_context_budget(self, prompt: str) -> Dict:
        """Validates whether the constructed prompt fits within the context window."""
        max_ctx = self.config.get("context", {}).get("max_context_length", 8192)
        estimated = self.estimate_tokens(prompt)
        remaining = max_ctx - estimated
        
        return {
            "estimated_tokens": estimated,
            "max_context_length": max_ctx,
            "remaining_budget": remaining,
            "within_budget": remaining > 0
        }
    
    def check_hard_stops(self, generated_text: str) -> bool:
        """
        Post-generation safety check. Returns True if the output is safe.
        Returns False if a hard stop condition is detected.
        """
        text_upper = generated_text.upper()
        for stop in self.HARD_STOPS:
            if stop in text_upper:
                return False
        return True
    
    def get_generation_params(self) -> Dict:
        """Returns the vLLM-compatible generation parameter dictionary."""
        return self.generation_params
    
    def allocate_token_budget(self) -> Dict[str, int]:
        """
        Returns per-component token budget based on the YAML allocation percentages.
        Enforces the hierarchical context window management from Task 6.
        """
        max_ctx = self.config.get("context", {}).get("max_context_length", 8192)
        allocation = self.config.get("context", {}).get("allocation", {})
        
        budget = {}
        for component, pct in allocation.items():
            budget[component] = int(max_ctx * pct)
        
        return budget
    
    def manage_conversation_history(self, history: list, max_turns: int = 10) -> str:
        """
        Implements the sliding window memory strategy from Task 6.
        Retains only the last `max_turns` conversation entries and serializes them.
        """
        window_size = self.config.get("memory", {}).get("conversation_window", max_turns)
        truncated = history[-window_size:] if len(history) > window_size else history
        
        serialized = ""
        for turn in truncated:
            role = turn.get("role", "user")
            content = turn.get("content", "")
            serialized += f"{role.upper()}: {content}\n"
        
        return serialized.strip()
    
    def truncate_to_budget(self, text: str, component: str) -> str:
        """
        Truncates a text block to fit within its allocated token budget.
        Uses the per-component allocation from allocate_token_budget().
        """
        budget = self.allocate_token_budget()
        max_tokens = budget.get(component, 1024)
        max_chars = max_tokens * 4  # Reverse of estimate_tokens
        
        if len(text) > max_chars:
            return text[:max_chars] + "\n[TRUNCATED: Token budget exceeded]"
        return text

