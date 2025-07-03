#!/usr/bin/env python3
"""
Test script to verify backend API functionality
"""
import requests
import json

BACKEND_URL = "http://localhost:8000"

def test_health_endpoint():
    """Test if backend health endpoint is working"""
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False

def test_root_endpoint():
    """Test root endpoint"""
    try:
        response = requests.get(f"{BACKEND_URL}/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False

def test_openai_connection():
    """Test OpenAI API connection through backend"""
    import os
    import sys
    sys.path.append('./backend')
    
    try:
        from g_chain import RAGChain
        rag = RAGChain()
        if rag.test_connection():
            print("✅ OpenAI API connection working")
            return True
        else:
            print("❌ OpenAI API connection failed")
            return False
    except Exception as e:
        print(f"❌ Error testing OpenAI connection: {e}")
        return False

def main():
    print("🔍 Testing Backend API...")
    print("=" * 50)
    
    # Test endpoints
    health_ok = test_health_endpoint()
    root_ok = test_root_endpoint()
    openai_ok = test_openai_connection()
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"Health endpoint: {'✅' if health_ok else '❌'}")
    print(f"Root endpoint: {'✅' if root_ok else '❌'}")
    print(f"OpenAI connection: {'✅' if openai_ok else '❌'}")
    
    if health_ok and root_ok and openai_ok:
        print("\n🎉 All tests passed! Backend is ready.")
        return True
    else:
        print("\n⚠️ Some tests failed. Check the backend configuration.")
        return False

if __name__ == "__main__":
    main()
