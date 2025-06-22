from rest_framework.permissions import BasePermission
from django.http import JsonResponse
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

class CreditCheckPermission(BasePermission):
    message = "Not enough credits to access this API."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            logger.debug("User not authenticated.")
            return False

        logger.debug(f"User: {request.user.email}")

        api_cost = getattr(view, 'api_credit_cost', None)
        logger.debug(f"View: {view.__class__.__name__}, API Cost: {api_cost}")

        if request.user.is_superuser:
            logger.debug("Superuser detected. Skipping credit deduction.")
            return True

        if api_cost is None:
            logger.debug("API cost is None. Skipping credit check.")
            return True

        try:
            api_cost = int(api_cost)
        except Exception as e:
            logger.error(f"Failed to convert API cost to int: {e}")
            return True  # Let it pass in case of error

        with transaction.atomic():
            user_profile = request.user.profile
            user_profile.refresh_from_db()
            logger.debug(f"User current credit: {user_profile.credit_available}, Cost: {api_cost}")

            if user_profile.credit_available < api_cost:
                logger.warning("Not enough credits.")
                self.message = "Not enough credit to access this API."
                return False

            user_profile.credit_available -= api_cost
            user_profile.save()
            logger.debug(f"Credit deducted. New balance: {user_profile.credit_available}")

        return True
