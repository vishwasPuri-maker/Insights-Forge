"""
PAX 2.0 — Comprehensive End-to-End Backend Verification Script
Tests: Health, Auth (login), Ingestion (upload sample.csv), Chat, Simulate, Datasets
"""
import requests
import json
import os
import sys
import time

BASE = "http://127.0.0.1:8000/api/v1"
CSV_PATH = r"c:\Users\shlok\OneDrive\Desktop\IsightFordge_v1\sample.csv"
EMAIL = "test@example.com"
PASSWORD = "password123"

results = []

def report(name, passed, detail=""):
    status = "PASS" if passed else "FAIL"
    results.append((name, status, detail))
    print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))


print("=" * 60)
print("PAX 2.0 — E2E BACKEND VERIFICATION")
print("=" * 60)

# ─── TEST 1: Health ───
print("\n--- Phase 1: Health ---")
try:
    r = requests.get(f"{BASE}/health", timeout=10)
    report("GET /health", r.status_code == 200, f"status={r.status_code} body={r.text.strip()}")
except Exception as e:
    report("GET /health", False, str(e))

# ─── TEST 2: Auth — Login ───
print("\n--- Phase 2: Auth (Login) ---")
token = None
refresh_token = None
try:
    r = requests.post(f"{BASE}/auth/login", json={"email": EMAIL, "password": PASSWORD}, timeout=10)
    data = r.json()
    token = data.get("access_token")
    refresh_token = data.get("refresh_token")
    report("POST /auth/login", r.status_code == 200 and token is not None, f"status={r.status_code}")
except Exception as e:
    report("POST /auth/login", False, str(e))

if not token:
    print("\nFATAL: Cannot continue without auth token.")
    sys.exit(1)

headers = {"Authorization": f"Bearer {token}"}

# ─── TEST 3: Auth — Token Refresh ───
print("\n--- Phase 3: Auth (Refresh) ---")
try:
    r = requests.post(f"{BASE}/auth/refresh", json={"refresh_token": refresh_token}, timeout=10)
    new_data = r.json()
    new_token = new_data.get("access_token")
    report("POST /auth/refresh", r.status_code == 200 and new_token is not None, f"status={r.status_code}")
    # Update token
    if new_token:
        token = new_token
        headers = {"Authorization": f"Bearer {token}"}
except Exception as e:
    report("POST /auth/refresh", False, str(e))

# ─── TEST 4: Ingestion — Upload sample.csv ───
print("\n--- Phase 4: Ingestion (Upload sample.csv) ---")
dataset_id = None
try:
    with open(CSV_PATH, "rb") as f:
        r = requests.post(
            f"{BASE}/ingestion/stream",
            headers=headers,
            data={"sector": "retail"},
            files={"file": ("sample.csv", f, "text/csv")},
            timeout=60,
        )
    if r.status_code in (200, 201, 202):
        data = r.json()
        dataset_id = data.get("dataset_id")
        report("POST /ingestion/stream", True, f"status={r.status_code} dataset_id={dataset_id}")
    else:
        report("POST /ingestion/stream", False, f"status={r.status_code} body={r.text[:200]}")
except Exception as e:
    report("POST /ingestion/stream", False, str(e))

# ─── TEST 5: Chat Completions ───
print("\n--- Phase 5: Chat (Completions) ---")
try:
    chat_body = {
        "query": "How many records are in this dataset?",
        "response_mode": "concise",
        "stream": False,
    }
    r = requests.post(f"{BASE}/chat/completions", headers=headers, json=chat_body, timeout=60)
    if r.status_code == 200:
        data = r.json()
        msg = data.get("message", "")[:120]
        report("POST /chat/completions", True, f"response={msg}")
    else:
        report("POST /chat/completions", False, f"status={r.status_code} body={r.text[:200]}")
except Exception as e:
    report("POST /chat/completions", False, str(e))

# ─── TEST 6: Chat — data grounding question ───
print("\n--- Phase 6: Chat (Data Grounding) ---")
try:
    chat_body = {
        "query": "What is the total revenue from all sales in the dataset?",
        "response_mode": "detailed",
        "stream": False,
    }
    r = requests.post(f"{BASE}/chat/completions", headers=headers, json=chat_body, timeout=60)
    if r.status_code == 200:
        data = r.json()
        msg = data.get("message", "")[:200]
        report("POST /chat/completions (grounding)", True, f"response={msg}")
    else:
        report("POST /chat/completions (grounding)", False, f"status={r.status_code} body={r.text[:200]}")
except Exception as e:
    report("POST /chat/completions (grounding)", False, str(e))

# ─── TEST 7: Simulate ───
print("\n--- Phase 7: Simulate ---")
try:
    sim_body = {
        "metrics": [
            {"key": "revenue", "current": 10000, "change_pct": 5},
            {"key": "units", "current": 500, "change_pct": -2},
        ]
    }
    r = requests.post(f"{BASE}/simulate", headers=headers, json=sim_body, timeout=15)
    if r.status_code == 200:
        data = r.json()
        report("POST /simulate", True, f"sector={data.get('sector')} total_projected={data.get('total_projected')}")
    else:
        report("POST /simulate", False, f"status={r.status_code} body={r.text[:200]}")
except Exception as e:
    report("POST /simulate", False, str(e))

# ─── TEST 8: Auth — Logout ───
print("\n--- Phase 8: Auth (Logout) ---")
try:
    r = requests.post(f"{BASE}/auth/logout", headers=headers, json={"refresh_token": refresh_token}, timeout=10)
    report("POST /auth/logout", r.status_code in (200, 204), f"status={r.status_code}")
except Exception as e:
    report("POST /auth/logout", False, str(e))

# ─── SUMMARY ───
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
passed = sum(1 for _, s, _ in results if s == "PASS")
failed = sum(1 for _, s, _ in results if s == "FAIL")
for name, status, detail in results:
    print(f"  [{status}] {name}")
print(f"\nTotal: {passed} passed, {failed} failed out of {len(results)} tests")
print("=" * 60)
