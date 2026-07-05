"""Quick smoke test of all key API endpoints the frontend uses."""
import requests, json, sys

BASE = 'http://127.0.0.1:8000/api/v1'
results = {}

# 1. Health
r = requests.get(f'{BASE}/health')
results['1_health'] = r.status_code
print(f"[{'OK' if r.status_code == 200 else 'FAIL'}] GET /health -> {r.status_code}")

# 2. Login
r = requests.post(f'{BASE}/auth/login', json={'email':'test@example.com','password':'password123'})
results['2_login'] = r.status_code
print(f"[{'OK' if r.status_code == 200 else 'FAIL'}] POST /auth/login -> {r.status_code}")
tokens = r.json()
access = tokens['access_token']
headers = {'Authorization': f'Bearer {access}'}

# 3. Get OpenAPI routes
r = requests.get('http://127.0.0.1:8000/openapi.json')
openapi = r.json()
paths = sorted(openapi['paths'].keys())
print(f"\n=== ALL {len(paths)} API ROUTES ===")
for p in paths:
    methods = [m.upper() for m in openapi['paths'][p].keys()]
    print(f"  {', '.join(methods):20s} {p}")

# 4. Test key endpoints
print("\n=== TESTING KEY FRONTEND ENDPOINTS ===")

test_endpoints = [
    ('GET', '/auth/me'),
    ('GET', '/datasets'),
    ('GET', '/sectors/retail/scorecard'),
    ('GET', '/sectors/retail/timeseries'),
    ('GET', '/sectors/retail/geo'),
    ('GET', '/decision-cards'),
    ('GET', '/reports'),
    ('GET', '/users'),
    ('GET', '/thresholds'),
    ('GET', '/notifications'),
]

for method, path in test_endpoints:
    try:
        if method == 'GET':
            r = requests.get(f'{BASE}{path}', headers=headers, timeout=10)
        status = r.status_code
        body_preview = r.text[:100] if status >= 400 else ''
        tag = 'OK' if status < 400 else 'WARN' if status < 500 else 'FAIL'
        print(f"[{tag:4s}] {method} {path} -> {status} {body_preview}")
        results[path] = status
    except Exception as e:
        print(f"[ERR ] {method} {path} -> {e}")
        results[path] = str(e)

# 5. Test dataset upload
print("\n=== TESTING DATASET UPLOAD ===")
import io
csv_data = "id,name,revenue\n1,A,100\n2,B,200\n3,C,300\n"
files = {'file': ('test_verify.csv', io.BytesIO(csv_data.encode()), 'text/csv')}
r = requests.post(f'{BASE}/datasets/upload', headers=headers, files=files)
print(f"[{'OK' if r.status_code in (200, 201) else 'WARN'}] POST /datasets/upload -> {r.status_code}")
if r.status_code in (200, 201):
    ds = r.json()
    ds_id = ds.get('id', ds.get('dataset_id', 'unknown'))
    print(f"  Dataset ID: {ds_id}")
    print(f"  Name: {ds.get('name', 'N/A')}")
    print(f"  Status: {ds.get('processing_status', ds.get('status', 'N/A'))}")
else:
    print(f"  Response: {r.text[:300]}")

# 6. Test chatbot
print("\n=== TESTING CHATBOT / AI ===")
r = requests.get(f'{BASE}/ai/conversations', headers=headers)
print(f"[{'OK' if r.status_code < 400 else 'WARN'}] GET /ai/conversations -> {r.status_code}")

# Try to create a conversation and send a message
chat_body = {'title': 'Test conversation', 'model_name': 'gemini-2.5-flash'}
r = requests.post(f'{BASE}/ai/conversations', headers=headers, json=chat_body)
print(f"[{'OK' if r.status_code in (200, 201) else 'WARN'}] POST /ai/conversations -> {r.status_code}")
if r.status_code in (200, 201):
    conv = r.json()
    conv_id = conv.get('id', 'unknown')
    # Send a message
    msg_body = {'message': 'How many records are in this dataset?'}
    r = requests.post(f'{BASE}/ai/conversations/{conv_id}/messages', headers=headers, json=msg_body)
    print(f"[{'OK' if r.status_code in (200, 201) else 'WARN'}] POST message -> {r.status_code}")
    if r.status_code in (200, 201):
        resp = r.json()
        ai_reply = resp.get('message', resp.get('response', str(resp)[:200]))
        print(f"  AI Reply: {str(ai_reply)[:200]}")

# Summary
print("\n=== SUMMARY ===")
ok_count = sum(1 for v in results.values() if isinstance(v, int) and v < 400)
warn_count = sum(1 for v in results.values() if isinstance(v, int) and 400 <= v < 500)
fail_count = sum(1 for v in results.values() if isinstance(v, int) and v >= 500)
err_count = sum(1 for v in results.values() if isinstance(v, str))
print(f"OK: {ok_count}  WARN: {warn_count}  FAIL: {fail_count}  ERR: {err_count}")
