import requests
import time
import uuid

API_URL = "http://localhost:8000/api/v1/scanners/website"

def run_audit():
    print("=== ScamShield AI E2E Pipeline Audit ===")
    
    # 0. Login to get JWT
    print("\n[0] Authenticating...")
    login_resp = requests.post("http://localhost:8000/api/v1/auth/login", data={"username": "test@example.com", "password": "Password123!"})
    if login_resp.status_code != 200:
        # Try to register if test user doesn't exist
        print("    Test user not found, registering...")
        requests.post("http://localhost:8000/api/v1/auth/register", json={"email": "test@example.com", "password": "Password123!"})
        login_resp = requests.post("http://localhost:8000/api/v1/auth/login", data={"username": "test@example.com", "password": "Password123!"})
        
    if login_resp.status_code != 200:
        print("    [FAIL] Could not authenticate.")
        return
        
    token = login_resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Generate unique URL to force a cache miss (Cold Scan)
    unique_id = uuid.uuid4().hex[:8]
    test_url = f"http://test-audit-{unique_id}.com"
    
    print(f"\n[1] Initiating Cold Scan for {test_url}...")
    start_time = time.time()
    resp = requests.post(API_URL, json={"url": test_url}, headers=headers)
    cold_latency = time.time() - start_time
    print(f"    Cold Scan Latency: {cold_latency:.2f} seconds")
    
    if resp.status_code != 200:
        print(f"    Error: {resp.text}")
        return
        
    data = resp.json()
    print(f"    Risk Score: {data.get('risk_score')}")
    print(f"    Confidence: {data.get('confidence_score')}")
    print(f"    Severity: {data.get('severity')}")
    
    # 2. Re-scan the exact same URL to force a cache hit (Warm Scan)
    print(f"\n[2] Initiating Warm Scan for {test_url}...")
    start_time = time.time()
    resp2 = requests.post(API_URL, json={"url": test_url})
    warm_latency = time.time() - start_time
    print(f"    Warm Scan Latency: {warm_latency:.2f} seconds")
    
    if resp2.status_code != 200:
        print(f"    Error: {resp2.text}")
        return
        
    data2 = resp2.json()
    print(f"    Risk Score: {data2.get('risk_score')}")
    
    # Verify performance constraints
    print("\n[3] Validating Performance...")
    if warm_latency > 0.5:
        print(f"    [FAIL] Warm scan latency ({warm_latency:.2f}s) exceeded 500ms constraint.")
    else:
        print(f"    [PASS] Warm scan latency ({warm_latency:.2f}s) is acceptable.")
        
    if cold_latency > 15.0:
        print(f"    [FAIL] Cold scan latency ({cold_latency:.2f}s) exceeded 15s constraint.")
    else:
        print(f"    [PASS] Cold scan latency ({cold_latency:.2f}s) is acceptable.")

if __name__ == "__main__":
    run_audit()
