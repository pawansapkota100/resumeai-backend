from django.contrib import admin

# Register your models here.
from .models import CreditPurchaseOrder,Product

admin.site.register(CreditPurchaseOrder)
admin.site.register(Product)