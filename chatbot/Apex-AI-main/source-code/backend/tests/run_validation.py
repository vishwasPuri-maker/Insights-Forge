import json
import os
import sys

from safety_tests import SafetyValidator
from hallucination_tests import HallucinationValidator
from sql_block_tests import SQLBlockValidator
from prompt_regression_tests import RegressionValidator

def run_all_tests():
    print("Executing Apex AI Enterprise Validation Framework...\n")
    
    all_results = []
    
    # 1. Safety Tests
    safety = SafetyValidator()
    all_results.extend(safety.run_tests())
    
    # 2. Hallucination Tests
    hallucination = HallucinationValidator()
    all_results.extend(hallucination.run_tests())
    
    # 3. SQL Blocking Tests
    sql = SQLBlockValidator()
    all_results.extend(sql.run_tests())
    
    # 4. Regression & Determinism Tests
    regression = RegressionValidator()
    all_results.extend(regression.run_tests())
    
    # Compute Metrics
    total = len(all_results)
    passed = sum(1 for r in all_results if r["status"] == "success")
    security_tests = [r for r in all_results if r["category"] in ["security", "sql_safety"]]
    sec_passed = sum(1 for r in security_tests if r["status"] == "success")
    
    overall_pass_rate = (passed / total) * 100 if total > 0 else 0
    sec_pass_rate = (sec_passed / len(security_tests)) * 100 if security_tests else 0
    
    # Output Results as JSON Array
    output_file = "validation_report.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)
        
    print(f"Validation complete. Wrote {total} test results to {output_file}.")
    print(f"Overall Pass Rate:  {overall_pass_rate:.1f}%")
    print(f"Security Pass Rate: {sec_pass_rate:.1f}%\n")
    
    if passed < total:
        print("WARNING: Some tests failed. Check validation_report.json for details.")
        sys.exit(1)
    else:
        print("SUCCESS: Apex AI is ready for production deployment.")
        sys.exit(0)

if __name__ == "__main__":
    run_all_tests()
