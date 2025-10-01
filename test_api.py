#!/usr/bin/env python3
"""
Simple test script to verify API functionality
"""
import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    print("---")

def test_root_endpoint():
    """Test root endpoint"""
    print("Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    print("---")

def test_register_user():
    """Test user registration"""
    print("Testing user registration...")
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Access Token: {result['access_token'][:20]}...")
            return result['access_token']
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    print("---")

def test_login_user():
    """Test user login"""
    print("Testing user login...")
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Access Token: {result['access_token'][:20]}...")
            return result['access_token']
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    print("---")

def test_create_quiz(token):
    """Test quiz creation"""
    if not token:
        print("No token available for quiz creation test")
        return None
        
    print("Testing quiz creation...")
    
    headers = {"Authorization": f"Bearer {token}"}
    quiz_data = {
        "title": "Test Quiz",
        "prompt": "A simple test quiz about general knowledge",
        "category": "General",
        "difficulty": "medium",
        "question_count": 3
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/quizzes/", json=quiz_data, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Created Quiz ID: {result['id']}")
            print(f"Questions Count: {len(result['questions'])}")
            return result['id']
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    print("---")

def test_get_quizzes(token):
    """Test getting user quizzes"""
    if not token:
        print("No token available for get quizzes test")
        return
        
    print("Testing get user quizzes...")
    
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{BASE_URL}/api/quizzes/", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Total Quizzes: {result['total']}")
            print(f"Quizzes in Response: {len(result['quizzes'])}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    print("---")

if __name__ == "__main__":
    print("=== AI Quiz Builder API Test ===\n")
    
    # Test basic endpoints
    test_health_check()
    test_root_endpoint()
    
    # Test authentication
    token = test_register_user()
    if not token:  # If registration fails (user exists), try login
        token = test_login_user()
    
    # Test quiz operations
    if token:
        quiz_id = test_create_quiz(token)
        test_get_quizzes(token)
    
    print("Test completed!") 