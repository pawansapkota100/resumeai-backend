from . import views
from django.urls import path

urlpatterns = [
    path('stripe/payment-order/', views.CreateOrderView.as_view(), name='payment-order'),
    path('stripe/payment-init/', views.CreateStripeCheckoutSession.as_view(), name='payment-integration'),
    path('stripe/stripe-success/session_id=<str:session_id>', views.StripePaymentSuccess.as_view(), name='stripe-success'),
    path('product-details-list/', views.ProductDetailsListView.as_view(), name='product-details-list'),
]
