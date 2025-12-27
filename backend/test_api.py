"""
Simple test script to verify API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_login():
    """Test login endpoint"""
    print("Testing login...")
    
    # Test HR login
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={
            "email": "john.hr@company.com",
            "password": "password123"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ HR Login successful")
        print(f"Token: {data['access_token'][:50]}...")
        return data['access_token']
    else:
        print("❌ HR Login failed")
        print(response.text)
        return None

def test_dashboard(token):
    """Test dashboard endpoint"""
    print("\nTesting HR dashboard...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/john/hr/dashboard", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Dashboard access successful")
        print(f"Total employees: {data.get('total_employees', 0)}")
        print(f"Pending tasks: {data.get('pending_tasks', 0)}")
        print(f"Pending documents: {data.get('pending_documents', 0)}")
    else:
        print("❌ Dashboard access failed")
        print(response.text)

def test_employees(token):
    """Test employees endpoint"""
    print("\nTesting employees list...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/john/hr/employees", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Employees list successful")
        print(f"Found {len(data.get('employees', []))} employees")
        for emp in data.get('employees', [])[:2]:  # Show first 2
            print(f"  - {emp['name']} ({emp['email']})")
    else:
        print("❌ Employees list failed")
        print(response.text)

def test_employee_login():
    """Test employee login"""
    print("\nTesting employee login...")
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={
            "email": "jane.employee@company.com",
            "password": "password123"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Employee login successful")
        return data['access_token']
    else:
        print("❌ Employee login failed")
        print(response.text)
        return None

def test_employee_tasks(token):
    """Test employee tasks endpoint"""
    print("\nTesting employee tasks...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/jane/employee/tasks", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Employee tasks successful")
        print(f"Found {len(data.get('tasks', []))} tasks")
        for task in data.get('tasks', [])[:2]:  # Show first 2
            print(f"  - {task['title']} ({task['status']})")
    else:
        print("❌ Employee tasks failed")
        print(response.text)

def main():
    """Run all tests"""
    print("🚀 Starting API tests...\n")
    
    # Test HR functionality
    hr_token = test_login()
    if hr_token:
        test_dashboard(hr_token)
        test_employees(hr_token)
    
    # Test Employee functionality
    emp_token = test_employee_login()
    if emp_token:
        test_employee_tasks(emp_token)
    
    print("\n✨ Tests completed!")

if __name__ == "__main__":
    main()