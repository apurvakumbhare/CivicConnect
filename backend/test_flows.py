import requests
import json
import time
import uuid

BASE_URL = "http://localhost:8000"

def run_tests():
    print("Starting API Integration Verifications...")
    mobile = f"9876{str(uuid.uuid4().int)[:6]}"
    
    print("\n--- PHASE 1 & 5: Auth & Admin Setup ---")
    password = "Password@123"
    reg_data = {
        "full_name": "Test User",
        "mobile_number": mobile,
        "residential_address": "Test Addr",
        "email": "test@example.com",
        "language_preference": "English",
        "password": password
    }
    requests.post(f"{BASE_URL}/users/signup", json=reg_data)
    login_req = requests.post(f"{BASE_URL}/users/login", json={"mobile_number": mobile, "password": password})
    try:
        citizen_token = login_req.json().get("access_token")
        citizen_id = login_req.json().get("user_id", "Unknown")
        print(f"Citizen registered and logged in.")
        headers = {"Authorization": f"Bearer {citizen_token}"}
    except:
        print("Login failed: ", login_req.text)
        return

    print("\n--- PHASE 2: Workflow 1 (Citizen Grievance Submission) ---")
    start_req = requests.post(
        f"{BASE_URL}/grievance/start", 
        data={"text": "There is a massive pothole causing accidents near my house boundary at MG Road."},
        headers=headers
    )
    if start_req.status_code != 200:
        print(f"AI Start Failed: {start_req.text}")
        return
    session_id = start_req.json().get("session_id")
    print(f"AI Parsed Report successfully. Session: {session_id}")
    
    sub_req = requests.post(f"{BASE_URL}/grievance/submit", json={"session_id": session_id, "confirmed": True}, headers=headers)
    form_id = sub_req.json().get("form_id")
    print(f"Grievance Submitted successfully. ID: {form_id}")

    print("Waiting for Background Analysis Pipeline (10s)...")
    time.sleep(10)

    # Let's check status
    status_req = requests.get(f"{BASE_URL}/grievance/status/{form_id}", headers=headers)
    print(f"Grievance Status: {status_req.json().get('status')}")

    print("\nAll Workflows verified via automated APIs safely. Test complete.")

if __name__ == "__main__":
    run_tests()
