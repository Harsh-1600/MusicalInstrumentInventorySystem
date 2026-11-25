"""
Automated Verification Suite for Customer Ordering & Checkout System
Tests:
1. Access guards: Checkout requires Customer authentication.
2. Single instrument instant 'Order Now' flow.
3. Stock auto-decrement & Admin Sales KPI synchronization.
4. Order receipt and invoice rendering.
5. 'My Orders' history view for logged-in customer.
6. Shopping cart addition, quantity updates, and multi-item cart checkout.
7. Out-of-stock and over-capacity purchase rejection.
"""

import unittest
from app import app
from database import (
    get_instrument_by_id,
    get_sales_history,
    get_customer_orders,
    get_order_details
)

class TestCustomerOrderSuite(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

        # Ensure test instruments have adequate stock
        import sqlite3
        conn = sqlite3.connect('musical_inventory.db')
        c = conn.cursor()
        c.execute("UPDATE instruments SET quantity = 10 WHERE instrument_id IN ('INS001', 'INS002', 'INS003');")
        conn.commit()
        conn.close()

    def test_01_checkout_requires_login(self):
        """Unauthenticated visitor trying to checkout should be redirected to customer login"""
        response = self.client.get('/customer/checkout/INS001', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/customer/login', response.location)

    def test_02_direct_order_placement_and_stock_deduction(self):
        """Test direct single-item order placement, stock deduction and sales sync"""
        # 1. Login as customer
        login_res = self.client.post('/customer/login', data={
            'username': 'customer',
            'password': 'Customer@123'
        }, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)

        # 2. Get initial stock of INS001
        inst_before = get_instrument_by_id('INS001')
        self.assertIsNotNone(inst_before)
        initial_qty = int(inst_before['quantity'])
        self.assertGreater(initial_qty, 2, "Insufficient stock on INS001 for test")

        sales_before_count = len(get_sales_history())

        # 3. Place order for 2 units
        order_res = self.client.post('/customer/checkout/INS001', data={
            'quantity': 2,
            'customer_name': 'Priya Sharma',
            'customer_email': 'priya@example.com',
            'phone_number': '9876543210',
            'shipping_address': '123 Anna Salai, T. Nagar',
            'city': 'Chennai',
            'pincode': '600017',
            'payment_method': 'Cash on Delivery'
        }, follow_redirects=False)

        self.assertEqual(order_res.status_code, 302)
        self.assertIn('/customer/order/', order_res.location)

        # Extract order_id from redirect location
        order_id = int(order_res.location.rstrip('/').split('/')[-1])

        # 4. Verify stock was atomically decremented by 2
        inst_after = get_instrument_by_id('INS001')
        self.assertEqual(int(inst_after['quantity']), initial_qty - 2)

        # 5. Verify Sales table was updated (Admin sync)
        sales_after = get_sales_history()
        self.assertEqual(len(sales_after), sales_before_count + 1)
        latest_sale = sales_after[0]
        self.assertEqual(str(latest_sale['instrument_id']), 'INS001')
        self.assertEqual(int(latest_sale['quantity_sold']), 2)

        # 6. Verify order details and receipt view
        order = get_order_details(order_id)
        self.assertIsNotNone(order)
        self.assertEqual(order['customer_name'], 'Priya Sharma')
        self.assertEqual(order['order_status'], 'Confirmed')
        self.assertEqual(len(order['items']), 1)
        self.assertEqual(order['items'][0]['quantity'], 2)

        receipt_res = self.client.get(f'/customer/order/{order_id}')
        self.assertEqual(receipt_res.status_code, 200)
        self.assertIn(b"Order Confirmed!", receipt_res.data)
        self.assertIn(order['order_number'].encode('utf-8'), receipt_res.data)

    def test_03_customer_my_orders_view(self):
        """Test /customer/orders lists past orders for logged in customer"""
        self.client.post('/customer/login', data={
            'username': 'customer',
            'password': 'Customer@123'
        })

        orders_res = self.client.get('/customer/orders')
        self.assertEqual(orders_res.status_code, 200)
        self.assertIn(b"My Orders", orders_res.data)
        self.assertIn(b"View &amp; Print Invoice", orders_res.data)

    def test_04_cart_addition_and_multi_item_checkout(self):
        """Test adding items to session cart and executing multi-item checkout"""
        # Login
        self.client.post('/customer/login', data={
            'username': 'customer',
            'password': 'Customer@123'
        })

        # Add INS002 to cart
        add_res1 = self.client.post('/customer/cart/add/INS002', data={'quantity': 1}, follow_redirects=True)
        self.assertEqual(add_res1.status_code, 200)
        self.assertIn(b"Shopping Cart", add_res1.data)
        self.assertIn(b"Piano", add_res1.data)

        # Add INS003 (Bass Guitar) to cart
        add_res2 = self.client.post('/customer/cart/add/INS003', data={'quantity': 1}, follow_redirects=True)
        self.assertEqual(add_res2.status_code, 200)

        # Check stock of both items before
        inst2_before = int(get_instrument_by_id('INS002')['quantity'])
        inst3_before = int(get_instrument_by_id('INS003')['quantity'])

        # Checkout entire cart
        cart_checkout_res = self.client.post('/customer/cart/checkout', data={
            'customer_name': 'Priya Sharma',
            'customer_email': 'priya@example.com',
            'phone_number': '9876543210',
            'shipping_address': '45 Gandhi Road',
            'city': 'Coimbatore',
            'pincode': '641001',
            'payment_method': 'UPI / GPay / PhonePe (Simulated)'
        }, follow_redirects=False)

        self.assertEqual(cart_checkout_res.status_code, 302)
        self.assertIn('/customer/order/', cart_checkout_res.location)

        # Verify stock decremented for both items
        inst2_after = int(get_instrument_by_id('INS002')['quantity'])
        inst3_after = int(get_instrument_by_id('INS003')['quantity'])
        self.assertEqual(inst2_after, inst2_before - 1)
        self.assertEqual(inst3_after, inst3_before - 1)

        # Verify cart was cleared after purchase
        cart_view_res = self.client.get('/customer/cart')
        self.assertIn(b"Your Cart is Currently Empty", cart_view_res.data)

    def test_05_out_of_stock_order_protection(self):
        """Test that out of stock or excessive quantities are safely rejected"""
        self.client.post('/customer/login', data={
            'username': 'customer',
            'password': 'Customer@123'
        })

        # Yamaha P-45 Digital Piano (#104) has quantity = 0 (Out of stock)
        p45 = get_instrument_by_id('104')
        if p45 and int(p45['quantity']) == 0:
            res = self.client.get('/customer/checkout/104', follow_redirects=True)
            self.assertIn(b"out of stock", res.data.lower())

        # Exceeding quantity beyond stock should be rejected
        inst = get_instrument_by_id('INS005')
        avail = int(inst['quantity'])
        res = self.client.post('/customer/checkout/INS005', data={
            'quantity': avail + 9999,
            'customer_name': 'Priya Sharma',
            'customer_email': 'priya@example.com',
            'phone_number': '9876543210',
            'shipping_address': '123 Test St',
            'city': 'Chennai',
            'pincode': '600001'
        }, follow_redirects=True)
        # Should not crash and should reject excessive quantity
        inst_after = int(get_instrument_by_id('INS005')['quantity'])
        self.assertEqual(inst_after, avail)

    def test_06_admin_can_place_order_without_signout(self):
        """Test that Admin logged in can also place customer orders and view receipt without being kicked out"""
        # 1. Login as Admin
        login_res = self.client.post('/customer/login', data={
            'username': 'admin',
            'password': 'Admin@123'
        }, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)

        # 2. Checkout INS001 as admin
        order_res = self.client.post('/customer/checkout/INS001', data={
            'quantity': 1,
            'customer_name': 'Store Admin',
            'customer_email': 'admin@soundcraft.com',
            'phone_number': '9876500000',
            'shipping_address': 'Admin Test Suite HQ',
            'city': 'Chennai',
            'pincode': '600001',
            'payment_method': 'Cash on Delivery'
        }, follow_redirects=False)

        # Must NOT redirect to login (302 should be to receipt)
        self.assertEqual(order_res.status_code, 302)
        self.assertIn('/customer/order/', order_res.location)

        # 3. Access receipt successfully
        receipt_res = self.client.get(order_res.location)
        self.assertEqual(receipt_res.status_code, 200)
        self.assertIn(b"Order Confirmed!", receipt_res.data)


if __name__ == '__main__':
    unittest.main()

