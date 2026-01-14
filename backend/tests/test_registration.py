"""
Test script for registration endpoint
"""
import requests
import json

# API endpoint
BASE_URL = "http://localhost:8000"
REGISTER_URL = f"{BASE_URL}/api/auth/register"

def test_registration():
    """Test user registration"""

    # Test data
    test_user = {
        "username": "testuser123",
        "email": "testuser123@example.com",
        "password": "TestPassword123!",
        "role": "student"
    }

    print("=" * 60)
    print("Testing Registration Endpoint")
    print("=" * 60)
    print(f"\nEndpoint: {REGISTER_URL}")
    print(f"\nTest Data:")
    print(json.dumps(test_user, indent=2))
    print("\n" + "-" * 60)

    try:
        # Send POST request
        response = requests.post(REGISTER_URL, json=test_user)

        print(f"\nResponse Status Code: {response.status_code}")
        print(f"\nResponse Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")

        print(f"\nResponse Body:")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print(response.text)

        # Check if successful
        if response.status_code == 201:
            print("\n" + "=" * 60)
            print("✓ Registration SUCCESSFUL!")
            print("=" * 60)
            return True
        else:
            print("\n" + "=" * 60)
            print("✗ Registration FAILED!")
            print("=" * 60)
            return False

    except requests.exceptions.ConnectionError:
        print("\n" + "=" * 60)
        print("✗ ERROR: Could not connect to backend server!")
        print(f"Make sure the backend is running at {BASE_URL}")
        print("=" * 60)
        return False
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"✗ ERROR: {str(e)}")
        print("=" * 60)
        return False

def test_duplicate_registration():
    """Test duplicate user registration (should fail)"""

    test_user = {
        "username": "testuser123",
        "email": "testuser123@example.com",
        "password": "TestPassword123!",
        "role": "student"
    }

    print("\n\n" + "=" * 60)
    print("Testing Duplicate Registration (should fail)")
    print("=" * 60)

    try:
        response = requests.post(REGISTER_URL, json=test_user)

        print(f"\nResponse Status Code: {response.status_code}")
        print(f"\nResponse Body:")
        print(json.dumps(response.json(), indent=2))

        if response.status_code == 400:
            print("\n" + "=" * 60)
            print("✓ Duplicate check working correctly!")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("✗ Duplicate check NOT working!")
            print("=" * 60)

    except Exception as e:
        print(f"Error: {str(e)}")

def test_teacher_registration():
    """Test teacher registration"""

    test_teacher = {
        "username": "testteacher456",
        "email": "testteacher456@example.com",
        "password": "TeacherPass123!",
        "role": "teacher"
    }

    print("\n\n" + "=" * 60)
    print("Testing Teacher Registration")
    print("=" * 60)

    try:
        response = requests.post(REGISTER_URL, json=test_teacher)

        print(f"\nResponse Status Code: {response.status_code}")
        print(f"\nResponse Body:")
        print(json.dumps(response.json(), indent=2))

        if response.status_code == 201:
            print("\n" + "=" * 60)
            print("✓ Teacher Registration SUCCESSFUL!")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("✗ Teacher Registration FAILED!")
            print("=" * 60)

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    # Test 1: New user registration
    success = test_registration()

    if success:
        # Test 2: Duplicate registration (should fail)
        test_duplicate_registration()

        # Test 3: Teacher registration
        test_teacher_registration()

    print("\n\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
