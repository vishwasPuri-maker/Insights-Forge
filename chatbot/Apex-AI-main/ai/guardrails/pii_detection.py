import re

def detect_pii(input_str: str) -> bool:
    # Detects basic SSN or credit card patterns
    ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
    cc_pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
    if re.search(ssn_pattern, input_str) or re.search(cc_pattern, input_str):
        return True
    return False
