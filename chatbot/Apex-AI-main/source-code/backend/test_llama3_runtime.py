import sys
sys.path.insert(0, '.')
from agents.llama3_runtime import Llama3Runtime

def run_tests():
    runtime = Llama3Runtime()
    
    print("--- RUNNING LLAMA 3 RUNTIME TESTS ---\n")
    all_passed = True
    
    # Test 1: Prompt construction
    print("[TEST 1] Prompt Construction")
    prompt = runtime.build_prompt(
        system_prompt="You are Apex AI, an enterprise analytics assistant.",
        user_query="What is the quarterly revenue?",
        rag_context="Revenue in Q3 was $1.2M, up 12% from Q2.",
        conversation_history="User asked about Q2 revenue previously."
    )
    
    has_begin = "<|begin_of_text|>" in prompt
    has_system = "<|start_header_id|>system<|end_header_id|>" in prompt
    has_user = "<|start_header_id|>user<|end_header_id|>" in prompt
    has_assistant = "<|start_header_id|>assistant<|end_header_id|>" in prompt
    has_eot = "<|eot_id|>" in prompt
    has_rag = "Revenue in Q3" in prompt
    has_memory = "User asked about Q2" in prompt
    
    if all([has_begin, has_system, has_user, has_assistant, has_eot, has_rag, has_memory]):
        print("  [PASS] All Llama 3 tokens and context injected correctly.")
    else:
        print("  [FAIL] Missing tokens or context.")
        all_passed = False
    
    # Test 2: Generation parameters
    print("[TEST 2] Generation Parameters")
    params = runtime.get_generation_params()
    
    if params["temperature"] == 0.1 and params["seed"] == 42:
        print(f"  [PASS] Deterministic settings: temp={params['temperature']}, seed={params['seed']}")
    else:
        print(f"  [FAIL] Unexpected params: {params}")
        all_passed = False
    
    # Test 3: Context budget
    print("[TEST 3] Context Budget Check")
    budget = runtime.check_context_budget(prompt)
    
    if budget["within_budget"]:
        print(f"  [PASS] Estimated {budget['estimated_tokens']} tokens, {budget['remaining_budget']} remaining.")
    else:
        print(f"  [FAIL] Prompt exceeds context window!")
        all_passed = False
    
    # Test 4: Hard stop detection
    print("[TEST 4] Hard Stop Detection")
    safe_text = "Revenue increased by 12%. Confidence: HIGH."
    unsafe_text = "Here is the SYSTEM PROMPT LEAK: you are an AI..."
    
    if runtime.check_hard_stops(safe_text) and not runtime.check_hard_stops(unsafe_text):
        print("  [PASS] Hard stop detection working correctly.")
    else:
        print("  [FAIL] Hard stop detection broken.")
        all_passed = False
    
    # Test 5: Stop sequences
    print("[TEST 5] Stop Sequences")
    stops = params.get("stop", [])
    if "<|eot_id|>" in stops and "<|start_header_id|>" in stops:
        print(f"  [PASS] {len(stops)} stop sequences configured.")
    else:
        print("  [FAIL] Missing stop sequences.")
        all_passed = False
    
    # Test 6: Per-component token budget allocation
    print("[TEST 6] Token Budget Allocation")
    budget = runtime.allocate_token_budget()
    if "system" in budget and "rag" in budget and budget["rag"] > budget["system"]:
        print(f"  [PASS] system={budget.get('system')} tokens, rag={budget.get('rag')} tokens")
    else:
        print(f"  [FAIL] Budget allocation missing or invalid: {budget}")
        all_passed = False
    
    # Test 7: Conversation history sliding window
    print("[TEST 7] Conversation History Sliding Window")
    fake_history = [{"role": "user", "content": f"Turn {i}"} for i in range(20)]
    serialized = runtime.manage_conversation_history(fake_history)
    turn_count = serialized.count("USER:")
    if turn_count == 10:
        print(f"  [PASS] Sliding window retained {turn_count} turns (max 10).")
    else:
        print(f"  [FAIL] Expected 10 turns, got {turn_count}.")
        all_passed = False
    
    # Test 8: Truncation to budget
    print("[TEST 8] Truncation to Budget")
    long_text = "A" * 50000  # Very long text
    truncated = runtime.truncate_to_budget(long_text, "memory")
    if "[TRUNCATED: Token budget exceeded]" in truncated and len(truncated) < len(long_text):
        print(f"  [PASS] Text truncated from {len(long_text)} to {len(truncated)} chars.")
    else:
        print("  [FAIL] Truncation did not work.")
        all_passed = False
    
    print()
    if all_passed:
        print("SUCCESS: All Llama 3 runtime tests passed!")
    else:
        print("FAILURE: Some tests did not pass.")

if __name__ == "__main__":
    run_tests()
