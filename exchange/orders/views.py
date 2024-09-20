# orders/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import UserProfile, Order, OrderQueue
from .serializers import OrderSerializer
from decimal import Decimal

class BuyOrderView(APIView):

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            user_profile = UserProfile.objects.get(user=user)
            cryptocurrency = serializer.validated_data['cryptocurrency_obj']
            amount = serializer.validated_data['amount']
            total_price = amount * cryptocurrency.price

            if user_profile.account_balance < total_price:
                return Response({'error': 'Insufficient balance.'}, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                user_profile.account_balance -= total_price
                user_profile.save()

                order = Order.objects.create(
                    user=user,
                    cryptocurrency=cryptocurrency,
                    amount=amount,
                    total_price=total_price,
                    status='PENDING'
                )

                order_type = 'LARGE' if total_price >= Decimal('10') else 'SMALL'

                queue, created = OrderQueue.objects.get_or_create(
                    cryptocurrency=cryptocurrency,
                    order_type=order_type
                )
                queue.orders.add(order)
                queue.total_amount += amount
                queue.total_value += total_price
                queue.save()

                return Response({'message': 'Order placed successfully.'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
