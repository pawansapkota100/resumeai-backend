from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User=get_user_model()
# Create your models here.
class CreditPurchaseOrder(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credit_orders')
    product= models.ForeignKey('Product', on_delete=models.CASCADE, related_name='product_orders',null=True,blank=True)
    credit_amount = models.PositiveIntegerField(help_text="How many credits user is buying")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total price for the credits")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    total_amount=models.DecimalField(max_digits=10, decimal_places=2, help_text="Total price for the credits",null=True,blank=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    currency=models.CharField(max_length=10, default='USD')
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"TXN-{uuid.uuid4().hex[:10].upper()}"
        if not self.price:
            self.price = self.calculate_price()
        super().save(*args, **kwargs)


class Product(models.Model):
    PLAN_CHOICES = [
        ('basic', 'Basic'),
        ('pro', 'Pro'),
        ('ultimate', 'Ultimate'),
    ]

    name = models.CharField(max_length=255)
    tag = models.CharField(max_length=255, choices=PLAN_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    credits = models.PositiveIntegerField()
    description = models.TextField()
    features = models.JSONField(help_text="JSON with feature flags like {'resume_analysis': True, ...}")
    job_matching_limit = models.PositiveIntegerField(null=True, blank=True, help_text="Set null for unlimited")
    can_save_result = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rank = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
    class Meta:
        ordering = ['rank']

class FAQ(models.Model):
    question=models.CharField(max_length=255)
    answer=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)