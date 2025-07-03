import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_prompt_improvement():
    """Test the main prompt improvement functionality"""
    
    # Test data
    test_request = {
        "prompt": "Write a story",
        "criteria": ["relevance", "coherence", "simplicity", "depth"],
        "max_iterations": 3,
        "min_consecutive_improvements": 1
    }
    
    print("\n=== Starting Prompt Improvement Test ===")
    
    # Start the job
    response = requests.post(f"{BASE_URL}/improve-prompt", json=test_request)
    print(f"Start job response: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Error: {response.text}")
        return False
    
    job_data = response.json()
    job_id = job_data["job_id"]
    print(f"Job ID: {job_id}")
    
    # Poll for status
    max_polls = 30  # 30 seconds max wait
    poll_count = 0
    
    while poll_count < max_polls:
        time.sleep(1)
        status_response = requests.get(f"{BASE_URL}/job/{job_id}")
        
        if status_response.status_code != 200:
            print(f"Error getting status: {status_response.text}")
            return False
            
        status_data = status_response.json()
        print(f"Poll {poll_count + 1}: Status = {status_data['status']}, Progress = {status_data['progress']}/{status_data['total_iterations']}")
        
        if status_data["status"] in ["completed", "failed"]:
            print(f"\nFinal Status: {status_data['status']}")
            if status_data["status"] == "completed":
                print(f"Final Prompt: {status_data['final_prompt']}")
                if status_data["current_iteration"]:
                    print(f"Final Scores: {status_data['current_iteration']['scores']}")
            else:
                print(f"Error: {status_data.get('error', 'Unknown error')}")
            break
            
        poll_count += 1
    
    if poll_count >= max_polls:
        print("Test timed out!")
        return False
    
    return status_data["status"] == "completed"

def test_job_management():
    """Test job listing and deletion"""
    print("\n=== Testing Job Management ===")
    
    # List jobs
    response = requests.get(f"{BASE_URL}/jobs")
    print(f"List jobs: {response.json()}")
    
    # Test with invalid job ID
    response = requests.get(f"{BASE_URL}/job/invalid-id")
    print(f"Invalid job ID response: {response.status_code}")
    
    return True

def run_all_tests():
    """Run all tests"""
    print("Starting API Tests...")
    
    tests = [
        ("Health Check", test_health),
        ("Prompt Improvement", test_prompt_improvement),
        ("Job Management", test_job_management)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"✅ {test_name}: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            results.append((test_name, False))
            print(f"❌ {test_name}: FAILED with error: {e}")
    
    print(f"\n=== Test Summary ===")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")

if __name__ == "__main__":
    run_all_tests()