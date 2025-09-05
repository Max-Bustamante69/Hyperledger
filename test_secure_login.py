#!/usr/bin/env python3
"""
Secure Login Testing Script
Tests all login scenarios to ensure proper functionality
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

class LoginTester:
    def __init__(self):
        self.test_results = []
        
    def test_result(self, test_name, success, message=""):
        """Record test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append((test_name, success, message))
        print(f"{status}: {test_name}")
        if not success and message:
            print(f"    └── {message}")
    
    def test_new_user_registration(self):
        """Test new user registration"""
        print("\n🆕 Testing New User Registration")
        
        # Test 1: Valid registration
        data = {
            'user_id': 'test-prof-1',
            'name': 'Test Professor One',
            'user_type': 'professor',
            'email': 'testprof@university.edu',
            'password': 'securepass123',
            'block': '33'
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/login", json=data)
            result = response.json()
            
            self.test_result(
                "New professor registration",
                result.get('success', False) and result.get('new_user', False),
                result.get('error', '')
            )
        except Exception as e:
            self.test_result("New professor registration", False, str(e))
        
        # Test 2: Short password
        data['password'] = '123'  # Too short
        data['user_id'] = 'test-prof-2'
        
        try:
            response = requests.post(f"{BASE_URL}/api/login", json=data)
            result = response.json()
            
            self.test_result(
                "Short password rejection",
                not result.get('success', True),
                "Should reject passwords < 6 characters"
            )
        except Exception as e:
            self.test_result("Short password rejection", False, str(e))
    
    def test_duplicate_prevention(self):
        """Test duplicate prevention"""
        print("\n🚫 Testing Duplicate Prevention")
        
        # Test 1: Duplicate User ID
        data = {
            'user_id': 'test-prof-1',  # Same as registered above
            'name': 'Different Professor',
            'user_type': 'professor',
            'password': 'differentpass123',
            'block': '34'
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/login", json=data)
            result = response.json()
            
            self.test_result(
                "Duplicate User ID rejection",
                not result.get('success', True),
                "Should reject duplicate User IDs"
            )
        except Exception as e:
            self.test_result("Duplicate User ID rejection", False, str(e))
        
        # Test 2: Duplicate Name
        data = {
            'user_id': 'test-prof-different',
            'name': 'Test Professor One',  # Same name as above
            'user_type': 'professor',
            'password': 'anotherpass123',
            'block': '35'
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/login", json=data)
            result = response.json()
            
            self.test_result(
                "Duplicate name rejection",
                not result.get('success', True),
                "Should reject duplicate names"
            )
        except Exception as e:
            self.test_result("Duplicate name rejection", False, str(e))
    
    def test_existing_user_login(self):
        """Test existing user login"""
        print("\n🔑 Testing Existing User Login")
        
        # Test 1: Correct password
        data = {
            'user_id': 'test-prof-1',
            'name': 'Test Professor One',
            'user_type': 'professor',
            'password': 'securepass123',  # Correct password
            'block': '33'
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/login", json=data)
            result = response.json()
            
            self.test_result(
                "Correct password login",
                result.get('success', False) and result.get('returning_user', False),
                result.get('error', '')
            )
        except Exception as e:
            self.test_result("Correct password login", False, str(e))
        
        # Test 2: Wrong password
        data['password'] = 'wrongpassword'
        
        try:
            response = requests.post(f"{BASE_URL}/api/login", json=data)
            result = response.json()
            
            self.test_result(
                "Wrong password rejection",
                not result.get('success', True),
                "Should reject wrong passwords"
            )
        except Exception as e:
            self.test_result("Wrong password rejection", False, str(e))
        
        # Test 3: Wrong role
        data['password'] = 'securepass123'  # Correct password
        data['user_type'] = 'student'  # Wrong role
        
        try:
            response = requests.post(f"{BASE_URL}/api/login", json=data)
            result = response.json()
            
            self.test_result(
                "Wrong role rejection",
                not result.get('success', True),
                "Should reject wrong roles for existing users"
            )
        except Exception as e:
            self.test_result("Wrong role rejection", False, str(e))
    
    def test_user_checking_api(self):
        """Test user checking API"""
        print("\n🔍 Testing User Checking API")
        
        # Test existing user check
        try:
            response = requests.get(f"{BASE_URL}/api/check-user/test-prof-1")
            result = response.json()
            
            self.test_result(
                "Existing user check API",
                result.get('success', False) and result.get('user_exists', False),
                result.get('error', '')
            )
        except Exception as e:
            self.test_result("Existing user check API", False, str(e))
        
        # Test non-existing user check
        try:
            response = requests.get(f"{BASE_URL}/api/check-user/nonexistent-user")
            result = response.json()
            
            self.test_result(
                "Non-existing user check API",
                result.get('success', False) and not result.get('user_exists', True),
                result.get('error', '')
            )
        except Exception as e:
            self.test_result("Non-existing user check API", False, str(e))
    
    def run_all_tests(self):
        """Run all login tests"""
        print("🧪 SECURE LOGIN SYSTEM TESTING")
        print("=" * 50)
        
        # Check if app is running
        try:
            response = requests.get(f"{BASE_URL}/api/session-status", timeout=5)
            if response.status_code != 200:
                print("❌ Flask app not responding. Please start it first:")
                print("   cd client && python app.py")
                return False
        except Exception as e:
            print("❌ Cannot connect to Flask app. Please start it first:")
            print("   cd client && python app.py")
            return False
        
        # Run tests
        self.test_new_user_registration()
        self.test_duplicate_prevention()
        self.test_existing_user_login()
        self.test_user_checking_api()
        
        # Print results
        print("\n" + "=" * 50)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for _, success, _ in self.test_results if success)
        total = len(self.test_results)
        
        print(f"✅ PASSED: {passed}/{total} tests")
        print(f"❌ FAILED: {total - passed}/{total} tests")
        
        if total - passed > 0:
            print("\n❌ FAILED TESTS:")
            for test_name, success, message in self.test_results:
                if not success:
                    print(f"  • {test_name}: {message}")
        
        success_rate = (passed / total) * 100
        print(f"\n🎯 SUCCESS RATE: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("\n🎉 ALL LOGIN TESTS PASSED!")
            print("   Your secure login system is working perfectly!")
        else:
            print(f"\n⚠️  Login system needs attention.")
        
        return success_rate == 100

if __name__ == "__main__":
    tester = LoginTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)
