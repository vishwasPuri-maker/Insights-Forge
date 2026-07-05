import pytest
from ai.guardrails.sql_prevention import detect_sql_injection
from ai.guardrails.pii_detection import detect_pii
from ai.guardrails.hallucination_detection import verify_factuality

def test_sql_injection_detection():
    # True positives
    assert detect_sql_injection("DROP TABLE users;") == True
    assert detect_sql_injection("SELECT * FROM data; DELETE FROM users;") == True
    # False positives
    assert detect_sql_injection("Please update the dataset parameters.") == False

def test_pii_detection():
    assert detect_pii("My SSN is 123-45-6789.") == True
    assert detect_pii("Card: 1234-5678-9012-3456") == True
    assert detect_pii("The sector code is 1234.") == False

def test_hallucination_detection():
    context = "The revenue is 5000 and profit is 200."
    # Valid
    assert verify_factuality("Revenue hit 5000.", context) == True
    # Hallucinated number
    assert verify_factuality("Revenue hit 6000.", context) == False
