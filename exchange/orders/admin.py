# orders/admin.py

from django.contrib import admin
from .models import UserProfile, Cryptocurrency, Order, OrderQueue

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_balance')
    search_fields = ('user__username',)

@admin.register(Cryptocurrency)
class CryptocurrencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'cryptocurrency', 'amount', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'cryptocurrency')
    search_fields = ('user__username', 'cryptocurrency__name')

@admin.register(OrderQueue)
class OrderQueueAdmin(admin.ModelAdmin):
    list_display = ('cryptocurrency', 'order_type', 'total_amount', 'total_value', 'last_processed')
    list_filter = ('order_type', 'cryptocurrency')
