"""
Comprehensive Verification Suite for Customer Authentication & Account Management
Tests:
1. Root Route (/) smart redirection to /store for guests/customers, and /dashboard for admins.
2. Customer Login (/customer/login) with credentials validation and 'next' parameter redirection.
3. Customer Registration (/customer/register) with uniqueness checks.
4. Customer Profile (/customer/profile) GET, POST updates, and access protection.
5. Customer Password Change (/customer/change-password) with verification and re-login check.
6. Customer Forgot Password (/customer/forgot-password) & Reset (/customer/reset-password/<token>).
7. Admin Portal & Catalog Integrity Regression Check.
"""

import sys
import unittest
from app import app
from database import (
    get_db_connection,
    get_user_by_username,
    get_all_instruments,
    get_sales_history
)

class TestCustomerAuthSuite(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    def test_01_root_route_redirection(self):
        """Verify root / redirects guests directly to /store"""
        response = self.client.get('/', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith('/store'))

        # When logged in as Customer, / redirects to /store
        with self.client.session_transaction() as sess:
            sess['user_id'] = 2
            sess['role'] = 'Customer'
            sess['username'] = 'customer'
        response = self.client.get('/', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith('/store'))

        # When logged in as Admin, / redirects to /dashboard
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['role'] = 'Admin'
            sess['username'] = 'admin'
        response = self.client.get('/', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith('/dashboard'))

    def test_02_customer_login_flow(self):
        """Test Customer login with valid, invalid credentials and next redirect"""
        # GET login page
        response = self.client.get('/customer/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Customer Sign In", response.data)
        self.assertIn(b"Forgot Password?", response.data)

        # Invalid login
        response = self.client.post('/customer/login', data={
            'username': 'customer',
            'password': 'WrongPassword999'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Invalid customer username or password", response.data)

        # Valid login
        response = self.client.post('/customer/login', data={
            'username': 'customer',
            'password': 'Customer@123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome to SoundCraft", response.data)
        self.assertIn(b"Customer Account", response.data)
        self.assertIn(b"My Profile", response.data)

    def test_03_customer_registration_and_uniqueness(self):
        """Test customer registration and duplicate prevention"""
        import time
        uniq_id = int(time.time())
        new_username = f"testuser_{uniq_id}"
        new_email = f"test_{uniq_id}@soundcraft-store.com"

        # Successful registration
        response = self.client.post('/customer/register', data={
            'full_name': 'Test Runner User',
            'username': new_username,
            'email': new_email,
            'password': 'TestPassword@123',
            'confirm_password': 'TestPassword@123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Customer account created successfully", response.data)

        # Duplicate registration with same username
        response = self.client.post('/customer/register', data={
            'full_name': 'Another Person',
            'username': new_username,
            'email': f"diff_{uniq_id}@soundcraft-store.com",
            'password': 'TestPassword@123',
            'confirm_password': 'TestPassword@123'
        }, follow_redirects=True)
        self.assertIn(b"already taken", response.data)

        # Duplicate registration with same email
        response = self.client.post('/customer/register', data={
            'full_name': 'Another Person',
            'username': f"diffuser_{uniq_id}",
            'email': new_email,
            'password': 'TestPassword@123',
            'confirm_password': 'TestPassword@123'
        }, follow_redirects=True)
        self.assertIn(b"already registered", response.data)

    def test_04_customer_profile_access_and_update(self):
        """Test /customer/profile access guards, GET display and POST updates"""
        # Unauthenticated access redirects to /customer/login
        response = self.client.get('/customer/profile', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/customer/login', response.location)

        # Login as customer
        self.client.post('/customer/login', data={
            'username': 'customer',
            'password': 'Customer@123'
        })

        # GET profile page
        response = self.client.get('/customer/profile')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Customer Account Profile", response.data)
        self.assertIn(b"customer", response.data)

        # POST update profile
        response = self.client.post('/customer/profile', data={
            'full_name': 'Priya Sharma Updated',
            'email': 'priya.updated@example.com'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"profile has been updated successfully", response.data)
        self.assertIn(b"Priya Sharma Updated", response.data)

        # Restore original info
        self.client.post('/customer/profile', data={
            'full_name': 'Priya Sharma',
            'email': 'priya@example.com'
        })

    def test_05_customer_change_password_and_relogin(self):
        """Test customer password change and verify with new password"""
        import time
        uniq_id = int(time.time())
        temp_user = f"pwuser_{uniq_id}"
        temp_email = f"pw_{uniq_id}@example.com"
        initial_pw = "Initial@123"
        new_pw = "NewSecret@456"

        # Register temp customer
        self.client.post('/customer/register', data={
            'full_name': 'PW Test User',
            'username': temp_user,
            'email': temp_email,
            'password': initial_pw,
            'confirm_password': initial_pw
        })

        # Login with initial password
        self.client.post('/customer/login', data={
            'username': temp_user,
            'password': initial_pw
        })

        # Test wrong current password
        response = self.client.post('/customer/change-password', data={
            'current_password': 'WrongCurrentPassword',
            'new_password': new_pw,
            'confirm_password': new_pw
        }, follow_redirects=True)
        self.assertIn(b"Incorrect current password", response.data)

        # Test valid password change
        response = self.client.post('/customer/change-password', data={
            'current_password': initial_pw,
            'new_password': new_pw,
            'confirm_password': new_pw
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Password changed successfully", response.data)

        # Logout
        self.client.get('/customer/logout')

        # Old password should now fail
        response = self.client.post('/customer/login', data={
            'username': temp_user,
            'password': initial_pw
        }, follow_redirects=True)
        self.assertIn(b"Invalid customer username or password", response.data)

        # New password should succeed
        response = self.client.post('/customer/login', data={
            'username': temp_user,
            'password': new_pw
        }, follow_redirects=True)
        self.assertIn(b"Welcome to SoundCraft", response.data)

    def test_06_customer_forgot_password_flow(self):
        """Test customer forgot password token generation and password reset"""
        # GET forgot password page
        response = self.client.get('/customer/forgot-password')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Reset Customer Password", response.data)

        # POST with registered customer email
        response = self.client.post('/customer/forgot-password', data={
            'email': 'priya@example.com'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Password reset link generated", response.data)
        self.assertIn(b"customer/reset-password/", response.data)

        # Extract token from response
        import re
        match = re.search(r'/customer/reset-password/([A-Za-z0-9_-]+)', response.data.decode('utf-8'))
        self.assertIsNotNone(match, "Reset token link was not found in response")
        token = match.group(1)

        # GET reset page with token
        response = self.client.get(f'/customer/reset-password/{token}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Set New Password", response.data)

        # POST new password
        reset_pw = "Customer@123" # Reset back to default
        response = self.client.post(f'/customer/reset-password/{token}', data={
            'new_password': reset_pw,
            'confirm_password': reset_pw
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"password has been successfully reset", response.data)

        # Trying to use token again should fail
        response = self.client.get(f'/customer/reset-password/{token}', follow_redirects=True)
        self.assertIn(b"already been used", response.data)

    def test_07_regression_admin_and_catalog(self):
        """Ensure Admin portal and catalog data (35 items, 10 sales) remain untouched"""
        # Admin Login
        response = self.client.post('/login', data={
            'username': 'admin',
            'password': 'Admin@123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Store Administrator", response.data)

        # Admin Dashboard
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)

        # Verify catalog integrity
        instruments = get_all_instruments()
        self.assertGreaterEqual(len(instruments), 30, f"Expected at least 30 instruments, found {len(instruments)}")

        sales = get_sales_history()
        self.assertGreaterEqual(len(sales), 10, f"Expected at least 10 sales, found {len(sales)}")

if __name__ == '__main__':
    unittest.main()
