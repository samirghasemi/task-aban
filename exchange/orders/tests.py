# orders/tests.py

from django.test import TestCase
from django.contrib.auth.models import User
from .models import UserProfile, Cryptocurrency, Order, OrderQueue
from rest_framework.test import APIClient
from decimal import Decimal
import time

class BuyOrderTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='user1', password='pass')
        self.user2 = User.objects.create_user(username='user2', password='pass')
        self.user3 = User.objects.create_user(username='user3', password='pass')

        UserProfile.objects.filter(user=self.user1).update(account_balance=100)
        UserProfile.objects.filter(user=self.user2).update(account_balance=100)
        UserProfile.objects.filter(user=self.user3).update(account_balance=100)

        Cryptocurrency.objects.create(name='ABAN', price=4)

    def test_large_order_queue(self):
        self.client.login(username='user1', password='pass')
        response = self.client.post('/orders/buy/', {'cryptocurrency': 'ABAN', 'amount': 15})
        self.assertEqual(response.status_code, 201)

        # Wait for the task to process
        time.sleep(2)

        order = Order.objects.get(user=self.user1)
        self.assertEqual(order.status, 'SETTLED')

    def test_small_order_queue(self):
        self.client.login(username='user1', password='pass')
        response = self.client.post('/orders/buy/', {'cryptocurrency': 'ABAN', 'amount': 1})
        self.assertEqual(response.status_code, 201)

        self.client.login(username='user2', password='pass')
        response = self.client.post('/orders/buy/', {'cryptocurrency': 'ABAN', 'amount': 1})
        self.assertEqual(response.status_code, 201)

        self.client.login(username='user3', password='pass')
        response = self.client.post('/orders/buy/', {'cryptocurrency': 'ABAN', 'amount': 1})
        self.assertEqual(response.status_code, 201)

        # Wait for the task to process
        time.sleep(6)

        orders = Order.objects.filter(status='SETTLED')
        self.assertEqual(orders.count(), 3)

    def test_insufficient_balance(self):
        self.client.login(username='user1', password='pass')
        response = self.client.post('/orders/buy/', {'cryptocurrency': 'ABAN', 'amount': 1000})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)

    def test_refund_on_failure(self):
        # Modify buy_from_exchange to raise an exception
        from orders.tasks import buy_from_exchange

        def failing_buy_from_exchange(cryptocurrency_name, amount):
            raise Exception("Simulated exchange failure")

        # Replace the original function with the failing one
        original_function = buy_from_exchange
        from orders import tasks
        tasks.buy_from_exchange = failing_buy_from_exchange

        self.client.login(username='user1', password='pass')
        response = self.client.post('/orders/buy/', {'cryptocurrency': 'ABAN', 'amount': 3})
        self.assertEqual(response.status_code, 201)

        time.sleep(2)

        order = Order.objects.get(user=self.user1)
        self.assertEqual(order.status, 'FAILED')
        user_profile = UserProfile.objects.get(user=self.user1)
        self.assertEqual(user_profile.account_balance, Decimal('100'))

        # Restore the original function
        tasks.buy_from_exchange = original_function
