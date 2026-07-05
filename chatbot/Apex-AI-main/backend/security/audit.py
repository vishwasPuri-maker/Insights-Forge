import json
import os
from datetime import datetime

class AuditLogger:
    def __init__(self, log_path: str = "audit_log.json"):
        self.log_path = log_path

    def log_violation(self, tenant_id: str, payload: str, severity_level: int, refusal_sent: str):
        """
        Records security violations to a local JSON file for enterprise compliance monitoring.
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "tenant_id": tenant_id,
            "severity_level": severity_level,
            "payload_snippet": payload[:100] + "..." if len(payload) > 100 else payload,
            "refusal_sent": refusal_sent,
            "action_taken": "BLOCKED"
        }
        
        # Append to log file
        try:
            logs = []
            if os.path.exists(self.log_path):
                with open(self.log_path, "r") as f:
                    logs = json.load(f)
            
            logs.append(entry)
            
            with open(self.log_path, "w") as f:
                json.dump(logs, f, indent=2)
                
            print(f"SECURITY AUDIT: Logged Level {severity_level} violation for tenant {tenant_id}.")
        except Exception as e:
            print(f"SECURITY AUDIT ERROR: Failed to write to audit log: {str(e)}")

    def log_execution(self, user_id: str, tenant_id: str, sector: str, command: str, apis_called: list, prompt_used: str, confidence: float, latency: float, charts_generated: int):
        """
        Logs successful execution of an intelligence command for audit and telemetry purposes.
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "tenant_id": tenant_id,
            "sector": sector,
            "command": command,
            "apis_called": apis_called,
            "prompt_used": prompt_used,
            "confidence": confidence,
            "latency_sec": latency,
            "charts_generated": charts_generated,
            "action_taken": "EXECUTED"
        }
        
        # Append to log file
        try:
            logs = []
            if os.path.exists(self.log_path):
                with open(self.log_path, "r") as f:
                    logs = json.load(f)
            
            logs.append(entry)
            
            with open(self.log_path, "w") as f:
                json.dump(logs, f, indent=2)
                
            print(f"EXECUTION AUDIT: Logged successful command for tenant {tenant_id}.")
        except Exception as e:
            print(f"EXECUTION AUDIT ERROR: Failed to write to audit log: {str(e)}")

