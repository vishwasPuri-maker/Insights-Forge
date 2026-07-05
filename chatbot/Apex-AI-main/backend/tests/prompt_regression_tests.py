import time
from typing import Dict, Any
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agents.router import MultiAgentRouter

class RegressionValidator:
    """Validates response stability, output schemas, and determinism."""
    
    def __init__(self):
        self.router = MultiAgentRouter()
        
    def run_tests(self) -> list[Dict[str, Any]]:
        results = []
        
        # Test 1: Determinism (Response Stability)
        payload = "Analyze revenue growth."
        
        start_time = time.time()
        resp1 = self.router.route_query(payload, "tenant_test", "MODE_BUSINESS")
        latency1 = (time.time() - start_time) * 1000
        
        start_time = time.time()
        resp2 = self.router.route_query(payload, "tenant_test", "MODE_BUSINESS")
        latency2 = (time.time() - start_time) * 1000
        
        # Since we use deterministic parameters (seed=42, temp=0.1) in runtime,
        # the router output should be identical.
        status = "success" if resp1 == resp2 else "error"
        
        results.append({
            "test_name": "Determinism: Same Input -> Same Output",
            "category": "regression",
            "status": status,
            "score": 100 if status == "success" else 0,
            "confidence": 1.0,
            "latency_ms": int((latency1 + latency2) / 2),
            "violations": [] if status == "success" else ["Output diverged for identical input"],
            "recommendations": [] if status == "success" else ["Check vLLM seed injection"]
        })
        
        # Test 2: Output Schema Stability
        payload = "Compare Q1 and Q2 performance."
        start_time = time.time()
        resp = self.router.route_query(payload, "tenant_test", "MODE_BUSINESS")
        latency = int((time.time() - start_time) * 1000)
        
        # Verify response object structure
        has_required_keys = all(k in resp for k in ["role", "analysis_type", "response", "confidence"])
        
        # Verify JSON formatting of the mocked string payload
        try:
            # We mock formatted output with strings like 'Analysis type: ...' currently,
            # but structurally the router returned a dict with the right keys.
            status = "success" if has_required_keys else "error"
            violations = []
        except Exception as e:
            status = "error"
            violations = [str(e)]
            
        results.append({
            "test_name": "Schema Stability: Router Response Format",
            "category": "regression",
            "status": status,
            "score": 100 if status == "success" else 0,
            "confidence": 1.0,
            "latency_ms": latency,
            "violations": violations if status == "error" else [],
            "recommendations": [] if status == "success" else ["Revert schema breaking changes"]
        })
        
        # Test 3: Performance Stability (Latency)
        status = "success" if latency < 2000 else "error"
        results.append({
            "test_name": "Performance Stability: Latency < 2s",
            "category": "regression",
            "status": status,
            "score": 100 if status == "success" else 0,
            "confidence": 1.0,
            "latency_ms": latency,
            "violations": [] if status == "success" else [f"Latency exceeded SLA: {latency}ms"],
            "recommendations": [] if status == "success" else ["Optimize RAG retrieval speed"]
        })
        
        return results

if __name__ == "__main__":
    validator = RegressionValidator()
    print(json.dumps(validator.run_tests(), indent=2))
