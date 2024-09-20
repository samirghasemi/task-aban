from django.urls import path
from .views import BuyOrderView

urlpatterns = [
    path('buy/', BuyOrderView.as_view(), name='buy-order'),
]