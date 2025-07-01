from rest_framework import serializers
from .models import Product

class PaymentOrderSerializer(serializers.Serializer):
    # amount = serializers.IntegerField()
    # price = serializers.DecimalField(max_digits=10, decimal_places=2)
    product= serializers.IntegerField()


class PaymentIntregationSerializer(serializers.Serializer):
    transaction_id= serializers.CharField()
    # amount= serializers.FloatField()

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        exclude = [ 'created_at', 'updated_at','can_save_result','job_matching_limit']