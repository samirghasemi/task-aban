from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username}'s profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


class CryptoCurrency(models.Model):
    name = models.CharField(max_length=10, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)


    def __str__(self):
        return self.name
# Create your models here.

class Order(models.Model):
    STATUS_CHOICES = [
        ('FAILED', 'Failed'),
        ('PASSED', 'Passed'),
        ('PENDING', 'Pending'),
        ('SETTLED', 'Settled')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    crypto_currency = models.ForeignKey(CryptoCurrency, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=4)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class PendingBatch(models.Model):
    cryptocurrency = models.ForeignKey(Cryptocurrency, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    total_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"PendingBatch for {self.cryptocurrency.name}"
