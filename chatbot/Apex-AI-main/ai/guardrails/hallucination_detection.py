def verify_factuality(output: str, context: str) -> bool:
    # Strict heuristic: Ensure numeric values in output exist in context
    import re
    numbers_in_output = set(re.findall(r'\b\d+\b', output))
    numbers_in_context = set(re.findall(r'\b\d+\b', context))
    # If output has numbers not in context, flag hallucination
    if not numbers_in_output.issubset(numbers_in_context):
        return False
    return True
