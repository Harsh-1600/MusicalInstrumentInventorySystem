"""
Test Suite: Admin Orders Management, Separate Logins & Direct Customer Messaging
SoundCraft Musical Instrument Inventory System
"""

import unittest
import json
from app import app
from database import (
    get_all_orders_for_admin,
    get_latest_orders_feed,
    get_orders_kpi_stats,
    update_order_status,
    get_latest_order_notification
)
from services.sms_service import send_custom_admin_message, clean_phone_number


class TestAdminOrdersAndMessaging(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False

    def test_01_database_order_queries(self):
        """Verify database functions for retrieving orders and KPI statistics."""
        kpis = get_orders_kpi_stats()
        self.assertIn('total_orders', kpis)
        self.assertIn('total_revenue', kpis)
        self.assertIn('pending_orders', kpis)
        self.assertIn('delivered_orders', kpis)

        orders = get_all_orders_for_admin(limit=10)
        self.assertIsInstance(orders, list)

        feed = get_latest_orders_feed(limit=5)
        self.assertIsInstance(feed, list)
        if feed:
            self.assertIn('order_number', feed[0])
            self.assertIn('phone_number', feed[0])
            self.assertIn('first_item_image', feed[0])

    def test_02_custom_admin_message_service(self):
        """Verify that custom admin message service standardizes phone numbers and generates WhatsApp URLs."""
        res = send_custom_admin_message(
            raw_phone="+91 98765 43210",
            customer_name="Karthik",
            custom_text="Your Acoustic Guitar is tested, tuned, and ready for pickup!",
            order_number="ORD-2026-TEST"
        )
        self.assertTrue(res['success'])
        self.assertEqual(res['clean_phone'], "9876543210")
        self.assertIn("+91 98765 43210", res['formatted_phone'])
        self.assertIn("https://api.whatsapp.com/send?phone=919876543210", res['whatsapp_url'])
        self.assertIn("Karthik", res['message_text'])
        self.assertIn("ORD-2026-TEST", res['message_text'])

    def test_03_separate_login_portals_rendering(self):
        """Verify dedicated Administrator Login and Customer Login pages render distinct portals."""
        # Admin Login
        resp_admin = self.client.get('/login')
        self.assertEqual(resp_admin.status_code, 200)
        self.assertIn(b"Administrator Login", resp_admin.data)
        self.assertIn(b"Live Customer Orders Station", resp_admin.data)
        self.assertIn(b"Admin Control Center", resp_admin.data)

        # /admin/login alias
        resp_admin_alias = self.client.get('/admin/login')
        self.assertEqual(resp_admin_alias.status_code, 200)
        self.assertIn(b"Administrator Login", resp_admin_alias.data)

        # Customer Login
        resp_cust = self.client.get('/customer/login')
        self.assertEqual(resp_cust.status_code, 200)
        self.assertIn(b"Customer Sign In", resp_cust.data)
        self.assertIn(b"Customer Store Login", resp_cust.data)
        self.assertIn(b"Administrator Portal", resp_cust.data)

    def test_04_live_orders_api_endpoint(self):
        """Verify /api/admin/live-orders returns JSON feed for 5-second asynchronous polling."""
        resp = self.client.get('/api/admin/live-orders?limit=5')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data['success'])
        self.assertIn('orders', data)
        self.assertIsInstance(data['orders'], list)

    def test_05_admin_orders_page_access_control(self):
        """Verify /admin/orders requires Admin authentication."""
        # Unauthenticated request -> redirect to /login
        resp = self.client.get('/admin/orders')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login', resp.headers['Location'])

        # Authenticated as Admin -> 200 OK
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'admin'
            sess['role'] = 'Admin'

        resp_auth = self.client.get('/admin/orders')
        self.assertEqual(resp_auth.status_code, 200)
        self.assertIn(b"Customer Orders &amp; Direct Messaging", resp_auth.data)
        self.assertIn(b"Customer Purchase Orders", resp_auth.data)
        self.assertIn(b"Direct Message", resp_auth.data)

    def test_06_api_admin_send_customer_message(self):
        """Verify that strictly only authenticated Administrators can send messages to customers."""
        orders = get_all_orders_for_admin(limit=1)
        target_order_id = orders[0]['order_id'] if orders else None
        target_phone = orders[0]['phone_number'] if orders else "9876543210"

        payload = {
            'order_id': target_order_id or '',
            'order_number': 'ORD-TEST-99',
            'customer_name': 'Test Musician',
            'phone_number': target_phone,
            'message_text': 'Your instrument has passed final acoustic inspection!'
        }

        # 1. Unauthenticated request MUST be blocked (redirected by @login_required)
        resp_unauth = self.client.post('/api/admin/send-customer-message', data=payload)
        self.assertIn(resp_unauth.status_code, [302, 401, 403])

        # 2. Customer role MUST be blocked
        with self.client.session_transaction() as sess:
            sess['user_id'] = 2
            sess['username'] = 'customer'
            sess['role'] = 'Customer'
        resp_cust = self.client.post('/api/admin/send-customer-message', data=payload)
        self.assertIn(resp_cust.status_code, [302, 401, 403])

        # 3. Administrator role MUST succeed (200 OK)
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'admin'
            sess['role'] = 'Admin'

        resp_admin = self.client.post('/api/admin/send-customer-message', data=payload)
        self.assertEqual(resp_admin.status_code, 200)
        data = json.loads(resp_admin.data)
        self.assertTrue(data['success'])
        self.assertIn('whatsapp_url', data['notification'])
        self.assertIn("91", data['notification']['whatsapp_url'])

        # Verify audit log if order_id was provided
        if target_order_id:
            log = get_latest_order_notification(target_order_id)
            self.assertIsNotNone(log)
            self.assertEqual(log['phone_number'], clean_phone_number(target_phone))

    def test_07_order_status_update(self):
        """Verify order status update through Admin endpoint."""
        orders = get_all_orders_for_admin(limit=1)
        if orders:
            order_id = orders[0]['order_id']
            with self.client.session_transaction() as sess:
                sess['user_id'] = 1
                sess['username'] = 'admin'
                sess['role'] = 'Admin'

            resp = self.client.post(f'/admin/orders/status/{order_id}', data={'order_status': 'Processing'})
            self.assertEqual(resp.status_code, 302)


if __name__ == '__main__':
    unittest.main()
