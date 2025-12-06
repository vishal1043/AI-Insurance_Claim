import requests
import sys
import json
import os
from datetime import datetime
from pathlib import Path

class InsuranceClaimAPITester:
    def __init__(self, base_url="https://smartclaims-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.user_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_claim_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if headers:
            test_headers.update(headers)
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers)
            elif method == 'POST':
                if files:
                    # Remove Content-Type for multipart/form-data
                    test_headers.pop('Content-Type', None)
                    response = requests.post(url, data=data, files=files, headers=test_headers)
                else:
                    response = requests.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 500:
                        print(f"   Response: {response_data}")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test API health check"""
        return self.run_test("Health Check", "GET", "api/", 200)

    def test_user_registration(self):
        """Test user registration"""
        test_user_data = {
            "name": "Test User",
            "email": f"testuser_{datetime.now().strftime('%H%M%S')}@example.com",
            "mobile_no": "9876543210",
            "dob": "1990-01-01",
            "password": "TestPass123!"
        }
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "api/auth/register",
            200,
            data=test_user_data
        )
        
        if success and 'access_token' in response:
            self.user_token = response['access_token']
            print(f"   User token obtained: {self.user_token[:20]}...")
            return True
        return False

    def test_user_login(self):
        """Test user login with existing credentials"""
        login_data = {
            "email": "user1@example.com",
            "password": "password123"
        }
        
        success, response = self.run_test(
            "User Login",
            "POST",
            "api/auth/login",
            200,
            data=login_data
        )
        
        if success and 'access_token' in response:
            self.user_token = response['access_token']
            print(f"   User token obtained: {self.user_token[:20]}...")
            return True
        return False

    def test_admin_login(self):
        """Test admin login"""
        admin_data = {
            "email": "admin@insurance.com",
            "password": "admin123"
        }
        
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "api/auth/login",
            200,
            data=admin_data
        )
        
        if success and 'access_token' in response:
            self.admin_token = response['access_token']
            print(f"   Admin token obtained: {self.admin_token[:20]}...")
            return True
        return False

    def test_get_user_claims(self):
        """Test getting user claims"""
        if not self.user_token:
            print("❌ No user token available")
            return False
            
        headers = {'Authorization': f'Bearer {self.user_token}'}
        return self.run_test(
            "Get User Claims",
            "GET",
            "api/claims",
            200,
            headers=headers
        )[0]

    def test_create_claim(self):
        """Test creating a new claim with file upload"""
        if not self.user_token:
            print("❌ No user token available")
            return False

        # Create a simple test file
        test_file_path = "/tmp/test_bill.txt"
        with open(test_file_path, "w") as f:
            f.write("Test Medical Bill\nHospital: Test Hospital\nAmount: Rs. 5000\nDate: 2024-01-15")

        claim_data = {
            "name": "Test User",
            "insurance_id": "POL001",
            "aadhar_no": "1234567890123",
            "hospital_name": "Test Hospital",
            "date_of_admission": "2024-01-15",
            "disease_description": "Test medical condition for API testing",
            "expenses": [
                {"expense_name": "Consultation Fee", "amount": 2000},
                {"expense_name": "Medicine", "amount": 3000}
            ]
        }

        headers = {'Authorization': f'Bearer {self.user_token}'}
        
        try:
            with open(test_file_path, 'rb') as f:
                files = {'bills': ('test_bill.txt', f, 'text/plain')}
                data = {'claim_data': json.dumps(claim_data)}
                
                success, response = self.run_test(
                    "Create Claim",
                    "POST",
                    "api/claims",
                    200,
                    data=data,
                    files=files,
                    headers=headers
                )
                
                if success and 'id' in response:
                    self.created_claim_id = response['id']
                    print(f"   Created claim ID: {self.created_claim_id}")
                    return True
                    
        except Exception as e:
            print(f"❌ Error creating claim: {str(e)}")
        finally:
            # Clean up test file
            if os.path.exists(test_file_path):
                os.remove(test_file_path)
                
        return False

    def test_get_claim_detail(self):
        """Test getting claim details"""
        if not self.user_token or not self.created_claim_id:
            print("❌ No user token or claim ID available")
            return False
            
        headers = {'Authorization': f'Bearer {self.user_token}'}
        return self.run_test(
            "Get Claim Detail",
            "GET",
            f"api/claims/{self.created_claim_id}",
            200,
            headers=headers
        )[0]

    def test_admin_get_all_claims(self):
        """Test admin getting all claims"""
        if not self.admin_token:
            print("❌ No admin token available")
            return False
            
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        return self.run_test(
            "Admin Get All Claims",
            "GET",
            "api/admin/claims",
            200,
            headers=headers
        )[0]

    def test_admin_get_claim_detail(self):
        """Test admin getting claim detail for review"""
        if not self.admin_token or not self.created_claim_id:
            print("❌ No admin token or claim ID available")
            return False
            
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        return self.run_test(
            "Admin Get Claim Detail",
            "GET",
            f"api/admin/claims/{self.created_claim_id}",
            200,
            headers=headers
        )[0]

    def test_admin_approve_claim(self):
        """Test admin approving a claim"""
        if not self.admin_token or not self.created_claim_id:
            print("❌ No admin token or claim ID available")
            return False
            
        action_data = {
            "status": "Approved",
            "reimbursement_amount": 4500,
            "remarks": "Claim approved after review - API test"
        }
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        return self.run_test(
            "Admin Approve Claim",
            "PUT",
            f"api/admin/claims/{self.created_claim_id}/action",
            200,
            data=action_data,
            headers=headers
        )[0]

def main():
    print("🏥 Starting Insurance Claim System API Tests")
    print("=" * 60)
    
    tester = InsuranceClaimAPITester()
    
    # Test sequence
    tests = [
        ("Health Check", tester.test_health_check),
        ("User Registration", tester.test_user_registration),
        ("User Login", tester.test_user_login),
        ("Admin Login", tester.test_admin_login),
        ("Get User Claims", tester.test_get_user_claims),
        ("Create Claim", tester.test_create_claim),
        ("Get Claim Detail", tester.test_get_claim_detail),
        ("Admin Get All Claims", tester.test_admin_get_all_claims),
        ("Admin Get Claim Detail", tester.test_admin_get_claim_detail),
        ("Admin Approve Claim", tester.test_admin_approve_claim),
    ]
    
    failed_tests = []
    
    for test_name, test_func in tests:
        try:
            if not test_func():
                failed_tests.append(test_name)
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            failed_tests.append(test_name)
    
    # Print results
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if failed_tests:
        print(f"\n❌ Failed Tests:")
        for test in failed_tests:
            print(f"   - {test}")
    else:
        print("\n✅ All tests passed!")
    
    success_rate = (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0
    print(f"\n📈 Success Rate: {success_rate:.1f}%")
    
    return 0 if len(failed_tests) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())