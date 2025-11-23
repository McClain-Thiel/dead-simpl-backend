import requests
import time
import pandas as pd
import os

BASE_URL = "http://localhost:8000/api/eval"

def test_eval_flow():
    print("Starting Eval Flow Verification...")

    # 1. Create a Scorer (Builtin)
    print("\n1. Creating Builtin Scorer...")
    scorer_payload = {
        "name": "Readability Check",
        "scorer_type": "builtin",
        "configuration": {"metric_name": "flesch_kincaid_grade_level"}
    }
    response = requests.post(f"{BASE_URL}/scorers", json=scorer_payload)
    if response.status_code != 200:
        print(f"Failed to create scorer: {response.text}")
        return
    scorer_id = response.json()["id"]
    print(f"Created Scorer ID: {scorer_id}")

    # 2. Create a Profile
    print("\n2. Creating Profile...")
    profile_payload = {
        "name": "Readability Suite",
        "scorer_ids": [scorer_id]
    }
    response = requests.post(f"{BASE_URL}/profiles", json=profile_payload)
    if response.status_code != 200:
        print(f"Failed to create profile: {response.text}")
        return
    profile_id = response.json()["id"]
    print(f"Created Profile ID: {profile_id}")

    # 3. Upload Dataset
    print("\n3. Uploading Dataset...")
    # Create a dummy CSV
    df = pd.DataFrame({
        "inputs": ["How do I return a package?", "What is the weather?"],
        "outputs": ["You can return it within 30 days.", "It is sunny."],
        "context": ["Return policy is 30 days.", "Weather is sunny."],
        "ground_truth": ["valid", "valid"]
    })
    csv_path = "test_dataset.csv"
    df.to_csv(csv_path, index=False)
    
    with open(csv_path, "rb") as f:
        files = {"file": (csv_path, f, "text/csv")}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    if response.status_code != 200:
        print(f"Failed to upload dataset: {response.text}")
        return
    dataset_id = response.json()["dataset_id"]
    print(f"Uploaded Dataset ID: {dataset_id}")
    
    # 4. Trigger Run
    print("\n4. Triggering Run...")
    run_payload = {
        "profile_id": profile_id,
        "dataset_id": dataset_id,
        "eval_type": "chatbot"
    }
    response = requests.post(f"{BASE_URL}/runs", json=run_payload)
    if response.status_code != 200:
        print(f"Failed to trigger run: {response.text}")
        return
    run_id = response.json()["run_id"]
    print(f"Started Run ID: {run_id}")

    # 5. Poll Status
    print("\n5. Polling Status...")
    for _ in range(10):
        response = requests.get(f"{BASE_URL}/runs/{run_id}")
        status = response.json()["status"]
        print(f"Status: {status}")
        if status in ["COMPLETED", "FAILED"]:
            break
        time.sleep(2)
        
    if status == "COMPLETED":
        print("\nRun Completed Successfully!")
        print("Summary Results:", response.json().get("summary_results"))
        
        # 6. Fetch Report Rows
        print("\n6. Fetching Report Rows...")
        response = requests.get(f"{BASE_URL}/reports/{run_id}/rows")
        if response.status_code == 200:
            print(f"Rows fetched: {len(response.json()['items'])}")
        else:
            print(f"Failed to fetch rows: {response.text}")
            
    else:
        print(f"\nRun Failed: {response.json().get('error_message')}")

    # Cleanup
    if os.path.exists(csv_path):
        os.remove(csv_path)

if __name__ == "__main__":
    test_eval_flow()
