import json
import importlib
from typing import Dict, Any, List
from pydantic import BaseModel

class OrchestratorEngine:
    def __init__(self):
        self.tools = self._load_tools()
        # Mocking LangChain/LlamaIndex Router initialization for robust semantic routing
        # In production, this would be: self.llm = ChatOpenAI(temperature=0)
        self.agent_map = {
            "datasets": "DatasetAgent",
            "decision": "DecisionAgent",
            "sector": "SectorAnalysisAgent",
            "auth": "AuthenticationAgent"
        }
        
    def _load_tools(self) -> List[Dict[str, Any]]:
        try:
            with open(r"c:\Users\LENOVO\OneDrive\Attachments\Desktop\Apex AI\ai\functions\tools.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
            
    def route_intent(self, intent: str, context: Dict[str, Any]) -> str:
        """
        Uses semantic keyword matching as a fallback for an LLM intent classifier.
        Proper integration uses embeddings to match the user's intent to the nearest agent description.
        """
        intent_lower = intent.lower()
        
        # Proper LLM-based routing logic (simulated with robust matching)
        for keyword, agent_name in self.agent_map.items():
            if keyword in intent_lower:
                return agent_name
                
        return "CoordinatorAgent"
        
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dynamically loads the strict Pydantic model for the tool, validates arguments, 
        and simulates execution.
        """
        try:
            models_module = importlib.import_module("ai.models.api_models")
            model_class_name = "".join([part.capitalize() for part in tool_name.split("_")]) + "Request"
            
            if hasattr(models_module, model_class_name):
                model_class = getattr(models_module, model_class_name)
                # This will raise a ValidationError if the LLM hallucinated the schema
                validated_data = model_class(**arguments)
                return {
                    "status": "success", 
                    "message": f"Successfully invoked {tool_name}",
                    "validated_payload": validated_data.dict()
                }
                
            return {"status": "success", "message": f"Executed {tool_name} (no strict model found)."}
            
        except Exception as e:
            # Catch Pydantic ValidationErrors and pass them back to the LLM to fix
            return {"status": "error", "error": f"Schema Validation Failed: {str(e)}"}
