import re

def detect_sql_injection(input_str: str) -> bool:
    sql_keywords = r'\b(DROP|DELETE|UPDATE|INSERT|ALTER|TRUNCATE)\b'
    if re.search(sql_keywords, input_str, re.IGNORECASE):
        return True
    return False
