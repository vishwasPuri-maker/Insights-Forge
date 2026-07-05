import time
from typing import Dict, Any
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from security.guardrails import SecurityGuardrail

class SQLBlockValidator:
    """Validates DML, DDL, and administrative command blocking."""
    
    def __init__(self):
        self.guardrail = SecurityGuardrail()
        
    def run_tests(self) -> list[Dict[str, Any]]:
        results = []
        
        # Test 1: DML Blocking
        dml_payloads = [
            "DELETE FROM users;",
            "UPDATE sales SET revenue=0;",
            "INSERT INTO config VALUES (1);",
            "MERGE INTO analytics USING temp_data ON id;"
        ]
        
        for payload in dml_payloads:
            start_time = time.time()
            is_safe, refusal_msg, severity = self.guardrail.check_query(payload)
            latency = int((time.time() - start_time) * 1000)
            
            status = "success" if not is_safe and severity == "CRITICAL" else "error"
            results.append({
                "test_name": f"DML Block: {payload[:20]}",
                "category": "sql_safety",
                "status": status,
                "score": 100 if status == "success" else 0,
                "confidence": 1.0,
                "latency_ms": latency,
                "violations": [] if status == "success" else ["DML statement bypassed guardrail"],
                "recommendations": [] if status == "success" else ["Update regex to catch advanced DML patterns"]
            })
            
        # Test 2: DDL Blocking
        ddl_payloads = [
            "DROP DATABASE analytics;",
            "ALTER TABLE metrics ADD COLUMN hack;",
            "CREATE USER admin;",
            "TRUNCATE TABLE logs;"
        ]
        
        for payload in ddl_payloads:
            start_time = time.time()
            is_safe, refusal_msg, severity = self.guardrail.check_query(payload)
            latency = int((time.time() - start_time) * 1000)
            
            status = "success" if not is_safe and severity == "CRITICAL" else "error"
            results.append({
                "test_name": f"DDL Block: {payload[:20]}",
                "category": "sql_safety",
                "status": status,
                "score": 100 if status == "success" else 0,
                "confidence": 1.0,
                "latency_ms": latency,
                "violations": [] if status == "success" else ["DDL statement bypassed guardrail"],
                "recommendations": [] if status == "success" else ["Update regex to catch advanced DDL patterns"]
            })
            
        # Test 3: Admin & Infrastructure Blocking
        admin_payloads = [
            "GRANT ALL PRIVILEGES ON *.* TO user;",
            "REVOKE SELECT ON analytics FROM user;",
            "EXECUTE sp_dropserver;"
        ]
        
        for payload in admin_payloads:
            start_time = time.time()
            is_safe, refusal_msg, severity = self.guardrail.check_query(payload)
            latency = int((time.time() - start_time) * 1000)
            
            status = "success" if not is_safe and severity == "CRITICAL" else "error"
            results.append({
                "test_name": f"Admin Block: {payload[:20]}",
                "category": "sql_safety",
                "status": status,
                "score": 100 if status == "success" else 0,
                "confidence": 1.0,
                "latency_ms": latency,
                "violations": [] if status == "success" else ["Admin statement bypassed guardrail"],
                "recommendations": [] if status == "success" else ["Update regex for admin privileges"]
            })
            
        return results

if __name__ == "__main__":
    import json
    validator = SQLBlockValidator()
    print(json.dumps(validator.run_tests(), indent=2))
