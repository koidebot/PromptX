#!/usr/bin/env python3
"""
Docker testing script for the Prompt API
"""
import subprocess
import time
import requests
import sys
import os

def run_command(cmd, check=True):
    """Run a shell command and return the result"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    return result

def test_docker_build():
    """Test if Docker image builds successfully"""
    print("\n=== Testing Docker Build ===")
    
    # Build the image
    result = run_command("docker build -t prompt-api .")
    if not result:
        print("❌ Docker build failed")
        return False
    
    # Check if image exists
    result = run_command("docker images prompt-api")
    if "prompt-api" not in result.stdout:
        print("❌ Docker image not found")
        return False
    
    print("✅ Docker build successful")
    return True

def test_docker_run():
    """Test if Docker container runs successfully"""
    print("\n=== Testing Docker Run ===")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found. Create it from .env.example")
        return False
    
    # Stop any existing container
    run_command("docker stop prompt-api-test", check=False)
    run_command("docker rm prompt-api-test", check=False)
    
    # Run the container in background
    result = run_command(
        "docker run -d --name prompt-api-test -p 8001:8000 --env-file .env prompt-api"
    )
    if not result:
        print("❌ Failed to start Docker container")
        return False
    
    # Wait for container to start
    print("Waiting for container to start...")
    time.sleep(5)
    
    # Check if container is running
    result = run_command("docker ps | grep prompt-api-test")
    if not result.stdout:
        print("❌ Container not running")
        # Show logs for debugging
        run_command("docker logs prompt-api-test", check=False)
        return False
    
    print("✅ Docker container started successfully")
    return True

def test_api_endpoints():
    """Test API endpoints in the Docker container"""
    print("\n=== Testing API Endpoints ===")
    
    base_url = "http://localhost:8001"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ Health endpoint error: {e}")
        return False
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("✅ Root endpoint working")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ Root endpoint error: {e}")
        return False
    
    # Test prompt improvement endpoint (just structure, not full test)
    try:
        test_payload = {
            "prompt": "Test prompt",
            "max_iterations": 1,
            "min_consecutive_improvements": 1
        }
        response = requests.post(f"{base_url}/improve-prompt", json=test_payload, timeout=10)
        if response.status_code == 200:
            print("✅ Prompt improvement endpoint accepting requests")
        else:
            print(f"❌ Prompt improvement endpoint failed: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ Prompt improvement endpoint error: {e}")
        return False
    
    return True

def test_container_logs():
    """Check container logs for errors"""
    print("\n=== Checking Container Logs ===")
    
    result = run_command("docker logs prompt-api-test", check=False)
    if result:
        print("Container logs:")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
    
    return True

def cleanup():
    """Clean up test resources"""
    print("\n=== Cleaning Up ===")
    run_command("docker stop prompt-api-test", check=False)
    run_command("docker rm prompt-api-test", check=False)
    print("✅ Cleanup completed")

def main():
    """Main test function"""
    print("🚀 Starting Docker tests for Prompt API")
    
    tests = [
        ("Docker Build", test_docker_build),
        ("Docker Run", test_docker_run),
        ("API Endpoints", test_api_endpoints),
        ("Container Logs", test_container_logs)
    ]
    
    passed = 0
    total = len(tests)
    
    try:
        for test_name, test_func in tests:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
                break
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
    finally:
        cleanup()
    
    print(f"\n=== Test Summary ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All Docker tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)