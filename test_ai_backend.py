# Test Script for AI Backend

import requests
import json
import time

BASE_URL = "http://localhost:5000/api/ai"

def test_health():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"Health Check: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return True
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_chat():
    """Test the chat endpoint"""
    try:
        data = {
            "message": "I have a headache and feel dizzy",
            "patient_id": "test123",
            "session_id": "session456"
        }
        response = requests.post(f"{BASE_URL}/chat", json=data, timeout=15)
        print(f"Chat Test: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return True
    except Exception as e:
        print(f"Chat test failed: {e}")
        return False

def test_vitals():
    """Test the vitals analysis endpoint"""
    try:
        data = {
            "vitals": {
                "bp_systolic": 140,
                "bp_diastolic": 90,
                "heart_rate": 85,
                "oxygen_saturation": 97,
                "temperature": 99.2
            },
            "patient_id": "test123"
        }
        response = requests.post(f"{BASE_URL}/analyze-vitals", json=data, timeout=15)
        print(f"Vitals Test: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return True
    except Exception as e:
        print(f"Vitals test failed: {e}")
        return False

def test_tts():
    """Test the text-to-speech endpoint"""
    try:
        data = {
            "text": "Hello, this is a test of the text-to-speech functionality.",
            "voice_id": "default"
        }
        response = requests.post(f"{BASE_URL}/generate-tts", json=data, timeout=15)
        print(f"TTS Test: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return True
    except Exception as e:
        print(f"TTS test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing VirtuDoc AI Backend...")
    print("=" * 50)
    
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(3)
    
    tests = [
        ("Health Check", test_health),
        ("Chat Endpoint", test_chat),
        ("Vitals Analysis", test_vitals),
        ("Text-to-Speech", test_tts)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        success = test_func()
        results.append((test_name, success))
        print()
    
    print("=" * 50)
    print("Test Results:")
    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{test_name}: {status}")

