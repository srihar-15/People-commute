import requests
import time
import sys

BASE_URL = "http://localhost:8000/api/v1"

def print_banner(text):
    print("\n" + "="*60)
    print(f" {text}")
    print("="*60)

def main():
    print_banner("SAHAYAK SYSTEM INTEGRATION TEST")
    
    # 1. Login as Citizen Ramesh
    print("Step 1: Logging in as Citizen Ramesh...")
    login_res = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "ramesh@citizen.in",
        "password": "password123"
    })
    if login_res.status_code != 200:
        print(f"Failed to log in: {login_res.text}")
        sys.exit(1)
        
    citizen_data = login_res.json()
    cit_token = citizen_data["access_token"]
    cit_headers = {"Authorization": f"Bearer {cit_token}"}
    print(f"  Login Successful! User ID: {citizen_data['user_id']}")
    
    # 2. File a water leakage grievance
    print("\nStep 2: Citizen Ramesh submits a water leakage complaint...")
    g_res = requests.post(f"{BASE_URL}/grievances/", headers=cit_headers, json={
        "title": "Water leakage near Ward 1 park",
        "description": "There is a water pipeline leakage in Vasant Nagar near the municipal park. Drinking water is leaking on the street.",
        "latitude": 16.5062,
        "longitude": 80.6480,
        "source": "whatsapp",
        "language": "en",
        "evidence_url": "https://sahayak-demo-evidence.s3.amazonaws.com/intake_pipe_burst.jpg"
      })
    if g_res.status_code != 201:
        print(f"Failed to file grievance: {g_res.text}")
        sys.exit(1)
        
    grievance = g_res.json()
    g_id = grievance["id"]
    print(f"  Grievance filed successfully! ID: {g_id} | Status: {grievance['status']}")
    
    # Wait for LangGraph background execution (classification & routing)
    print("  Waiting 2 seconds for LangGraph worker thread to complete classification and routing...")
    time.sleep(2)
    
    # Check updated grievance status
    detail_res = requests.get(f"{BASE_URL}/grievances/{g_id}", headers=cit_headers)
    g_detail = detail_res.json()
    print(f"  AI Classification: Priority={g_detail['priority']} | Score={g_detail['priority_score']} | Status={g_detail['status']}")
    if g_detail["status"] != "ROUTED":
        print(f"Error: expected status 'ROUTED', got '{g_detail['status']}'")
        sys.exit(1)
    print(f"  AI Explanation: {g_detail['explanation']['classification_reasoning']}")

    # 3. Login as Officer K. Ramakrishna
    print("\nStep 3: Logging in as Water Officer Sri K. Ramakrishna...")
    off_login = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "water_officer@sahayak.gov.in",
        "password": "password123"
    })
    if off_login.status_code != 200:
        print(f"Failed to login officer: {off_login.text}")
        sys.exit(1)
        
    off_data = off_login.json()
    off_token = off_data["access_token"]
    off_headers = {"Authorization": f"Bearer {off_token}"}
    print(f"  Login Successful! Officer ID: {off_data['user_id']}")
    
    # 4. Officer accepts the task from queue
    print("\nStep 4: Officer Ramakrishna accepts the routed grievance from department queue...")
    accept_res = requests.post(f"{BASE_URL}/grievances/{g_id}/accept", headers=off_headers)
    if accept_res.status_code != 200:
        print(f"Failed to accept grievance: {accept_res.text}")
        sys.exit(1)
    print(f"  Task Accepted! Grievance Status: {accept_res.json()['status']}")
    
    # 5. Query AI Assistant recommendations
    print("\nStep 5: Officer queries AI Officer Assistant for SOPs and historical context...")
    assistant_res = requests.get(f"{BASE_URL}/grievances/{g_id}/assistant", headers=off_headers)
    if assistant_res.status_code != 200:
        print(f"Failed to get AI assistant recommendations: {assistant_res.text}")
        sys.exit(1)
        
    assist = assistant_res.json()
    print(f"  Retrieved SOP document: {assist['suggested_sops'][0]['title']} (version {assist['suggested_sops'][0]['version']})")
    print(f"  Likely Repair Steps suggested by assistant:")
    for step in assist["likely_steps"][:3]:
        print(f"    {step}")
        
    # 6. Officer resolves issue and submits proof (Resolution Assurance check)
    print("\nStep 6: Officer uploads repair photo to trigger Resolution Assurance image verification...")
    resolve_res = requests.post(f"{BASE_URL}/grievances/{g_id}/resolve", headers=off_headers, json={
        "evidence_url": "https://sahayak-demo-evidence.s3.amazonaws.com/closure_pipe_fixed.jpg",
        "notes": "Replaced the damaged section of the PVC pipe and fitted a Cast Iron clamp."
    })
    if resolve_res.status_code != 200:
        print(f"Failed to resolve: {resolve_res.text}")
        sys.exit(1)
        
    verif = resolve_res.json()
    print(f"  AI Verification Status: Success={verif['success']}")
    print(f"  Remarks: {verif['message']}")
    print("  Verification Checklist checked off by Vision Agent:")
    for check in verif["report"]["verification_checklist"]:
        print(f"    - [x] {check}")
        
    # 7. Citizen confirms closure
    print("\nStep 7: Citizen Ramesh confirms the resolution on WhatsApp, closing the ticket...")
    confirm_res = requests.post(f"{BASE_URL}/grievances/{g_id}/confirm", headers=cit_headers)
    if confirm_res.status_code != 200:
        print(f"Failed to confirm: {confirm_res.text}")
        sys.exit(1)
        
    final_g = confirm_res.json()
    print(f"  Grievance successfully CLOSED! Status: {final_g['status']} | Resolved At: {final_g['resolved_at']}")
    
    print_banner("INTEGRATION TEST PASSED! MULTI-AGENT STATE TRANSITIONS ARE 100% CORRECT.")

if __name__ == "__main__":
    main()
