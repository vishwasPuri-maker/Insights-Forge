import os
import json
import re

BASE_DIR = r"c:\Users\LENOVO\OneDrive\Attachments\Desktop\Apex AI"
OPENAPI_PATH = os.path.join(BASE_DIR, "insight_forge_backend_code", "docs", "openapi.json")

def load_openapi():
    with open(OPENAPI_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_pydantic_models(openapi):
    schemas = openapi.get("components", {}).get("schemas", {})
    output_lines = [
        "from pydantic import BaseModel, Field",
        "from typing import List, Optional, Any, Dict, Union",
        "",
        "class DynamicBaseModel(BaseModel):",
        "    class Config:",
        "        extra = 'allow'",
        ""
    ]
    
    # Map OpenAPI types to Python types
    type_mapping = {
        "string": "str",
        "integer": "int",
        "number": "float",
        "boolean": "bool",
        "array": "List[Any]",
        "object": "Dict[str, Any]"
    }
    
    for schema_name, schema_details in schemas.items():
        # Sanitize schema_name
        safe_name = schema_name.replace(" ", "").replace("-", "")
        output_lines.append(f"class {safe_name}(DynamicBaseModel):")
        properties = schema_details.get("properties", {})
        required = schema_details.get("required", [])
        
        if not properties:
            output_lines.append("    pass")
        
        for prop_name, prop_details in properties.items():
            prop_type_oa = prop_details.get("type", "Any")
            py_type = type_mapping.get(prop_type_oa, "Any")
            
            # Format handling for UUID
            if prop_details.get("format") == "uuid":
                py_type = "str"
                
            if "anyOf" in prop_details:
                py_type = "Any"
                
            is_optional = prop_name not in required
            if is_optional:
                py_type = f"Optional[{py_type}]"
                output_lines.append(f"    {prop_name}: {py_type} = None")
            else:
                output_lines.append(f"    {prop_name}: {py_type}")
        
        output_lines.append("")
    
    with open(os.path.join(BASE_DIR, "ai", "models", "api_models.py"), "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
        
def generate_openai_tools(openapi):
    tools = []
    paths = openapi.get("paths", {})
    schemas = openapi.get("components", {}).get("schemas", {})
    
    for path, methods in paths.items():
        for method, details in methods.items():
            tool_name = details.get("operationId", f"{method}_{path.replace('/', '_')}").replace('-', '_')
            description = details.get("summary", f"Executes {method.upper()} on {path}")
            
            # Parse parameters
            properties = {}
            required = []
            
            for param in details.get("parameters", []):
                name = param.get("name")
                prop_schema = param.get("schema", {})
                properties[name] = prop_schema
                if param.get("required"):
                    required.append(name)
                    
            # Parse request body ref
            if "requestBody" in details:
                content = details["requestBody"].get("content", {})
                json_content = content.get("application/json", {})
                ref = json_content.get("schema", {}).get("$ref", "")
                if ref:
                    ref_name = ref.split("/")[-1]
                    ref_schema = schemas.get(ref_name, {})
                    body_props = ref_schema.get("properties", {})
                    properties.update(body_props)
                    required.extend(ref_schema.get("required", []))
                    
            tools.append({
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": description,
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required
                    }
                }
            })
            
    with open(os.path.join(BASE_DIR, "ai", "functions", "tools.json"), "w", encoding="utf-8") as f:
        json.dump(tools, f, indent=2)

def generate_orchestrator():
    content = """import json
import importlib
from typing import Dict, Any

class OrchestratorEngine:
    def __init__(self):
        self.tools = self._load_tools()
        
    def _load_tools(self):
        try:
            with open(r"c:\\Users\\LENOVO\\OneDrive\\Attachments\\Desktop\\Apex AI\\ai\\functions\\tools.json", "r") as f:
                return json.load(f)
        except Exception:
            return []
            
    def route_intent(self, intent: str, context: Dict[str, Any]) -> str:
        # Core routing logic
        if "data" in intent.lower():
            return "DatasetAgent"
        elif "decision" in intent.lower():
            return "DecisionAgent"
        elif "sector" in intent.lower():
            return "SectorAnalysisAgent"
        else:
            return "CoordinatorAgent"
            
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        # Validate arguments using Pydantic models dynamically
        try:
            models_module = importlib.import_module("ai.models.api_models")
            # Map tool to model (this is a simplified dynamic lookup)
            model_class_name = "".join([part.capitalize() for part in tool_name.split("_")]) + "Request"
            if hasattr(models_module, model_class_name):
                model_class = getattr(models_module, model_class_name)
                validated_data = model_class(**arguments)
                return {"status": "success", "data": validated_data.dict()}
            return {"status": "success", "message": f"Tool {tool_name} executed (no strict model applied)."}
        except Exception as e:
            return {"status": "error", "error": str(e)}
"""
    with open(os.path.join(BASE_DIR, "ai", "orchestrator", "engine.py"), "w", encoding="utf-8") as f:
        f.write(content)

def generate_guardrails():
    sql_prevention = """import re

def detect_sql_injection(input_str: str) -> bool:
    sql_keywords = r'\\b(DROP|DELETE|UPDATE|INSERT|ALTER|TRUNCATE)\\b'
    if re.search(sql_keywords, input_str, re.IGNORECASE):
        return True
    return False
"""
    with open(os.path.join(BASE_DIR, "ai", "guardrails", "sql_prevention.py"), "w", encoding="utf-8") as f:
        f.write(sql_prevention)
        
    hallucination_detection = """def verify_factuality(output: str, context: str) -> bool:
    # Strict heuristic: Ensure numeric values in output exist in context
    import re
    numbers_in_output = set(re.findall(r'\\b\\d+\\b', output))
    numbers_in_context = set(re.findall(r'\\b\\d+\\b', context))
    # If output has numbers not in context, flag hallucination
    if not numbers_in_output.issubset(numbers_in_context):
        return False
    return True
"""
    with open(os.path.join(BASE_DIR, "ai", "guardrails", "hallucination_detection.py"), "w", encoding="utf-8") as f:
        f.write(hallucination_detection)
        
    pii_detection = """import re

def detect_pii(input_str: str) -> bool:
    # Detects basic SSN or credit card patterns
    ssn_pattern = r'\\b\\d{3}-\\d{2}-\\d{4}\\b'
    cc_pattern = r'\\b\\d{4}[- ]?\\d{4}[- ]?\\d{4}[- ]?\\d{4}\\b'
    if re.search(ssn_pattern, input_str) or re.search(cc_pattern, input_str):
        return True
    return False
"""
    with open(os.path.join(BASE_DIR, "ai", "guardrails", "pii_detection.py"), "w", encoding="utf-8") as f:
        f.write(pii_detection)

if __name__ == "__main__":
    openapi = load_openapi()
    generate_pydantic_models(openapi)
    generate_openai_tools(openapi)
    generate_orchestrator()
    generate_guardrails()
    print("Deep integration completed.")
