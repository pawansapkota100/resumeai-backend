from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import PaymentOrderSerializer,PaymentIntregationSerializer,ProductSerializer
from .models import CreditPurchaseOrder
from core.utils import success_response, error_response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import stripe
from .models import Product
from rest_framework.permissions import IsAuthenticated

from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')

class CreateOrderView(APIView):
    serializer_class =PaymentOrderSerializer
    permission_classes=[IsAuthenticated]

    @swagger_auto_schema(request_body=PaymentOrderSerializer)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        purchase=CreditPurchaseOrder()
        purchase.user=request.user
        product=serializer.validated_data['product']
        
        try:
            product_obj= Product.objects.get(id=product)
        except Product.DoesNotExist:
            return error_response(message="Product not found.", status_code=status.HTTP_404_NOT_FOUND)

        purchase.product=product_obj
        purchase.price=product_obj.price
        purchase.credit_amount= product_obj.credits

        purchase.save()

        return success_response(data=purchase.transaction_id, message="Order created successfully.", status_code=status.HTTP_201_CREATED)

import os 
frontend_url= os.getenv("FRONTEND_URL")
class CreateStripeCheckoutSession(APIView):
    permission_classes=[IsAuthenticated]

    @swagger_auto_schema(request_body=PaymentIntregationSerializer)
    def post(self, request):
        base_url = f"{request.scheme}://{request.get_host()}"
        serializer= PaymentIntregationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Extract amount and transaction_id from the request body
        # amount = serializer.validated_data.get("amount")
        transaction_id = serializer.validated_data.get("transaction_id")
        amount= CreditPurchaseOrder.objects.get(transaction_id=transaction_id).price
        
        try:
            session = stripe.checkout.Session.create(
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": " credit amount",  # Replace with your product name
                            "description": "credit amount"  # You can modify this dynamically
                        },
                        "unit_amount": int(amount * 100),  # Amount in cents
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url=f"{frontend_url}/pricing/success?session_id={{CHECKOUT_SESSION_ID}}",
                # success_url=request.build_absolute_uri(reverse('stripe_success_handler')) + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=f"{base_url}/stripe/cancel/",
                metadata={
                    "transaction_id": transaction_id,
                    "amount": amount
                }
            )
            print("#########",session.url)
            # Return the checkout session URL to frontend
            return success_response(data={"checkout_url": session.url}, status_code=status.HTTP_200_OK)
        except Exception as e:
            return error_response(message={"error": str(e)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StripePaymentSuccess(APIView):
    def get(self, request,session_id):
        try:
            
            session = stripe.checkout.Session.retrieve(session_id)
            metadata = session.metadata
            transaction_uuid = metadata.get("transaction_id")
            price= metadata.get("amount")
            base_url = request.scheme + '://' + request.get_host()


            if not session_id or not transaction_uuid:
                return error_response(message="Payment Failed. Please try again")


            # Retrieve session from Stripe
            try:
                total_amount = round(float(price),2)
            except ValueError:
                total_amount = 0

            ticket_order= CreditPurchaseOrder.objects.get(transaction_id=transaction_uuid)

            if ticket_order.status == "success":
                return success_response(data={"message": "Payment already successful"}, status_code=status.HTTP_200_OK)
            
            if float(ticket_order.price) != total_amount:
                return error_response(message="amount mismatch. Please try again") 
            

            ticket_order.status = "success"
            ticket_order.total_amount= total_amount
            ticket_order.payment_reference = session.payment_intent 
            ticket_order.save()
            user_profile=ticket_order.user.profile
            user_profile.credit_available += ticket_order.credit_amount
            user_profile.save()

            return success_response(data={"message": "Payment successful"}, status_code=status.HTTP_200_OK)

        except Exception as e:
            return error_response(message={"error": str(e)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            


class ProductDetailsListView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return success_response(data=serializer.data, status_code=status.HTTP_200_OK)