"""
Test script to verify add user functionality
Run this after starting the Flask server
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

# First login as admin to get JWT token
def test_add_user():
    # Step 1: Login as admin
    print("Step 1: Logging in as admin...")
    login_data = {
        "email": "admin@nirmauni.ac.in",  # Change to your admin email
        "password": "admin123"  # Change to your admin password
    }
    
    session = requests.Session()
    login_response = session.post(f"{BASE_URL}/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    print(f"✅ Login successful: {login_response.json()}")
    
    # Step 2: Add a faculty user
    print("\nStep 2: Adding faculty user...")
    faculty_data = {
        "name": "Test Faculty",
        "email": "testfaculty@nirmauni.ac.in",
        "password": "Test@123",
        "role": "faculty",
        "department": "CSE"
    }
    
    add_response = session.post(f"{BASE_URL}/admin/users/add", json=faculty_data)
    print(f"Status Code: {add_response.status_code}")
    print(f"Response: {add_response.json()}")
    
    if add_response.status_code == 201:
        print("✅ Faculty user created successfully!")
    else:
        print(f"❌ Failed to create user")
    
    # Step 3: Add a student user
    print("\nStep 3: Adding student user...")
    student_data = {
        "name": "Test Student",
        "email": "teststudent@nirmauni.ac.in",
        "password": "Test@123",
        "role": "student",
        "department": "CSE",
        "roll_no": "22BCE999",
        "sgpa": 8.5,
        "cgpa": 8.3,
        "attendance": 85
    }
    
    add_response = session.post(f"{BASE_URL}/admin/users/add", json=student_data)
    print(f"Status Code: {add_response.status_code}")
    print(f"Response: {add_response.json()}")
    
    if add_response.status_code == 201:
        print("✅ Student user created successfully!")
    else:
        print(f"❌ Failed to create user")

if __name__ == "__main__":
    test_add_user()
