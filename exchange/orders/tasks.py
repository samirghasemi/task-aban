# orders/tasks.py

from celery import shared_task
from django.utils import timezone
from django.db import transaction
from .models import OrderQueue, Order
from decimal import Decimal
from django.db.models import Sum

@shared_task
def process_large_orders():
    queues = OrderQueue.objects.filter(order_type='LARGE')
    for queue in queues:
        process_queue(queue)

@shared_task
def process_small_orders():
    queues = OrderQueue.objects.filter(order_type='SMALL')
    for queue in queues:
        if queue.total_value >= Decimal('10'):
            process_queue(queue)

def process_queue(queue):

    orders = queue.orders.filter(status='PENDING')
    if not orders.exists():
        return
    with transaction.atomic():
        orders.update(status='PROCESSING', updated_at=timezone.now())
        total_amount = orders.aggregate(total=Sum('amount'))['total']
        try:
            buy_from_exchange(queue.cryptocurrency.name, total_amount)
            orders.update(status='SETTLED', updated_at=timezone.now())
        except Exception as e:
            orders.update(status='FAILED', failure_reason=str(e), updated_at=timezone.now())
            refund_users(orders)
        queue.orders.clear()
        queue.total_amount = 0
        queue.total_value = 0
        queue.save()

def buy_from_exchange(cryptocurrency_name, amount):
    # Simulate buying from an international exchange
    # Raise exception if there's a failure
    # For demonstration purposes, we'll assume it always succeeds
    # To simulate a failure, you can raise an exception
    pass

def refund_users(orders):
    for order in orders:
        user_profile = order.user.userprofile
        user_profile.account_balance += order.total_price
        user_profile.save()

@shared_task
def requeue_stuck_orders():
    from django.utils import timezone
    stuck_orders = Order.objects.filter(
        status='PROCESSING',
        updated_at__lte=timezone.now() - timezone.timedelta(seconds=30)
    )
    for order in stuck_orders:
        order.status = 'PENDING'
        order.save()
