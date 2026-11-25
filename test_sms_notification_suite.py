"""
Automated Test Suite for SMS & WhatsApp Order Notification Service
Tests:
1. Phone number normalization (+91, leading 0, 10-digit extraction).
2. Message text generation with order details.
3. WhatsApp 1-Click direct URL construction with URL encoding.
4. Database audit logging into sms_notifications table.
5. End-to-end checkout with notification generation.
6. API endpoint /api/order/<order_id>/send-sms re-triggering.
"""

import unittest
import sqlite3
from app import app
from database import init_db, log_sms_notification, get_latest_order_notification
from services.sms_service import (
    clean_phone_number,
    format_display_phone,
    construct_order_message,
    send_order_notification
)

class TestSmsNotificationSuite(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

        # Ensure database is initialized
        init_db()

        # Ensure stock for test instrument
        conn = sqlite3.connect('musical_inventory.db')
        c = conn.cursor()
        c.execute("UPDATE instruments SET quantity = 10 WHERE instrument_id = 'INS001';")
        conn.commit()
        conn.close()

    def test_01_phone_normalization(self):
        """Test cleansing and standardizing phone numbers"""
        self.assertEqual(clean_phone_number("9876543210"), "9876543210")
        self.assertEqual(clean_phone_number("+91 98765 43210"), "9876543210")
        self.assertEqual(clean_phone_number("09876543210"), "9876543210")
        self.assertEqual(clean_phone_number("919876543210"), "9876543210")
        self.assertEqual(clean_phone_number("98765-43210"), "9876543210")
        self.assertEqual(format_display_phone("9876543210"), "+91 98765 43210")

    def test_02_message_construction(self):
        """Test generating structured order confirmation SMS message"""
        dummy_order = {
            "order_number": "ORD-TEST-1234",
            "customer_name": "Ravi Kumar",
            "total_amount": 12500.0,
            "city": "Chennai",
            "order_items": [
                {"instrument_name": "Acoustic Guitar", "quantity": 1}
            ]
        }
        msg = construct_order_message(dummy_order)
        self.assertIn("SoundCraft Musical Store: Order Confirmed!", msg)
        self.assertIn("ORD-TEST-1234", msg)
        self.assertIn("Ravi Kumar", msg)
        self.assertIn("12,500.00", msg)
        self.assertIn("Acoustic Guitar", msg)

    def test_03_whatsapp_url_generation(self):
        """Test generating direct WhatsApp message URL"""
        dummy_order = {
            "order_number": "ORD-WA-001",
            "customer_name": "Deepa",
            "total_amount": 4500.0,
            "city": "Madurai",
            "phone_number": "9876543210"
        }
        notif = send_order_notification(dummy_order)
        self.assertTrue(notif["success"])
        self.assertEqual(notif["clean_phone"], "9876543210")
        self.assertIn("https://api.whatsapp.com/send?phone=919876543210", notif["whatsapp_url"])
        self.assertIn("ORD-WA-001", notif["whatsapp_url"])

    def test_04_database_notification_logging(self):
        """Test logging SMS dispatch events into database"""
        conn = sqlite3.connect('musical_inventory.db')
        c = conn.cursor()
        c.execute("SELECT order_id FROM orders ORDER BY order_id DESC LIMIT 1;")
        row = c.fetchone()
        conn.close()
        test_order_id = row[0] if row else None

        log_res = log_sms_notification(
            test_order_id,
            "9876543210",
            "Test SMS message content",
            gateway="WhatsApp & Push",
            status="Dispatched"
        )
        self.assertTrue(log_res)

        fetched = get_latest_order_notification(test_order_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["phone_number"], "9876543210")
        self.assertEqual(fetched["status"], "Dispatched")

    def test_05_checkout_triggers_notification_and_renders_card(self):
        """Test that placing an order triggers notification and displays it on receipt"""
        # Login
        self.client.post('/customer/login', data={
            'username': 'customer',
            'password': 'Customer@123'
        }, follow_redirects=True)

        # Place single item order
        res = self.client.post('/customer/checkout/INS001', data={
            'quantity': 1,
            'customer_name': 'Sanjay Music',
            'customer_email': 'sanjay@example.com',
            'phone_number': '9876501234',
            'shipping_address': '88 Anna Salai',
            'city': 'Chennai',
            'pincode': '600002',
            'payment_method': 'Cash on Delivery'
        }, follow_redirects=True)

        self.assertEqual(res.status_code, 200)
        # Check that receipt displays the verified mobile notification card and registered phone
        self.assertIn(b"+91 98765 01234", res.data)
        self.assertIn(b"Store Administrator", res.data)
        self.assertIn(b"Order Status:", res.data)

    def test_06_api_resend_sms_endpoint(self):
        """Test /api/order/<id>/send-sms endpoint"""
        # Login
        self.client.post('/customer/login', data={
            'username': 'customer',
            'password': 'Customer@123'
        }, follow_redirects=True)

        # Get existing order ID or place one
        conn = sqlite3.connect('musical_inventory.db')
        c = conn.cursor()
        c.execute("SELECT order_id FROM orders ORDER BY order_id DESC LIMIT 1;")
        row = c.fetchone()
        conn.close()

        if row:
            order_id = row[0]
            api_res = self.client.post(f'/api/order/{order_id}/send-sms', data={
                'phone_number': '9123456789'
            })
            self.assertEqual(api_res.status_code, 200)
            data = api_res.get_json()
            self.assertTrue(data['success'])
            self.assertIn("91234", data['message'])
            self.assertEqual(data['notification']['clean_phone'], "9123456789")


if __name__ == '__main__':
    unittest.main()
