from agents.prompt_engine import PromptTemplateEngine

def run_tests():
    engine = PromptTemplateEngine()
    
    print("--- RUNNING PROMPT ENGINE INTENT CLASSIFICATION TESTS ---\n")
    
    test_queries = {
        "What is our current revenue KPI?": "kpi_analysis",
        "Show me the growth trend for Q3": "trend_analysis",
        "Forecast next quarter revenue": "forecasting",
        "Why did churn spike unexpectedly?": "anomaly_detection",
        "Explain the executive dashboard": "dashboard_explanation",
        "Summarize quarterly performance": "executive_summary",
        "How can we improve customer retention?": "recommendation",
        "Compare Q1 vs Q2 performance": "comparative_analysis",
    }
    
    all_passed = True
    
    for query, expected_type in test_queries.items():
        result = engine.classify_query_intent(query)
        status = "PASS" if result == expected_type else "FAIL"
        if status == "FAIL":
            all_passed = False
        print(f"[{status}] Query: '{query}'")
        print(f"       Expected: {expected_type} | Got: {result}")
        print("-" * 50)
    
    print(f"\n--- TEMPLATE AVAILABILITY ---")
    for t in engine.list_available_templates():
        print(f"  [OK] {t}")
    
    if all_passed:
        print(f"\nSUCCESS: All {len(test_queries)} intent classifications passed!")
    else:
        print(f"\nFAILURE: Some intent classifications did not match.")

if __name__ == "__main__":
    run_tests()
