from django.utils.deprecation import MiddlewareMixin
from django.db import transaction
from django.http import JsonResponse
from django.conf import settings


class CreditCheckMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.user.is_authenticated:
            return None  # Let auth middleware handle it

        # Determine the credit cost based on view type
        api_cost = None

        # Class-based view
        view_class = getattr(view_func, 'view_class', None)
        if view_class:
            api_cost = getattr(view_class, 'api_credit_cost', None)
        else:
            # Function-based view: attach credit manually
            api_cost = getattr(view_func, 'api_credit_cost', None)

        if request.user.is_superuser:
            api_cost = 0
        if api_cost is None:
            return None  # Skip if no cost is defined
        with transaction.atomic():
            user = request.user.profile
            user.refresh_from_db()

            if user.credit_available < api_cost:
                return JsonResponse(
                    {"detail": "Not enough credit to access this API."},
                    status=402
                )

            user.credit_available -= api_cost
            user.save()

        return None  # Allow request to continue
