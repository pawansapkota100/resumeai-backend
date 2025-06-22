# from django.utils.deprecation import MiddlewareMixin
# from django.db import transaction
# from django.http import JsonResponse
# from django.conf import settings


# import logging
# logger = logging.getLogger(__name__)

# class CreditCheckMiddleware(MiddlewareMixin):
#     def process_view(self, request, view_func, view_args, view_kwargs):

#         if not request.user.is_authenticated:
#             logger.debug("User not authenticated.")
#             return None  # Let auth middleware handle it

#         logger.debug(f"User: {request.user.email}")

#         # Determine the credit cost based on view type
#         api_cost = None

#         # Class-based view
#         view_class = getattr(view_func, 'view_class', None)
#         if view_class:
#             api_cost = getattr(view_class, 'api_credit_cost', None)
#             logger.debug(f"View Class: {view_class.__name__}, API Cost: {api_cost}")
#         else:
#             api_cost = getattr(view_func, 'api_credit_cost', None)
#             logger.debug(f"Function View, API Cost: {api_cost}")

#         if request.user.is_superuser:
#             logger.debug("Superuser detected. Skipping credit deduction.")
#             api_cost = 0

#         if api_cost is None:
#             logger.debug("API cost is None. Skipping middleware.")
#             return None

#         try:
#             api_cost = int(api_cost)
#         except Exception as e:
#             logger.error(f"Failed to convert API cost to int: {e}")
#             return None

#         with transaction.atomic():
#             user_profile = request.user.profile
#             user_profile.refresh_from_db()
#             logger.debug(f"User current credit: {user_profile.credit_available}, Cost: {api_cost}")

#             if user_profile.credit_available < api_cost:
#                 logger.warning("Not enough credits.")
#                 return JsonResponse(
#                     {"detail": "Not enough credit to access this API."},
#                     status=402
#                 )

#             user_profile.credit_available -= api_cost
#             user_profile.save()
#             logger.debug(f"Credit deducted. New balance: {user_profile.credit_available}")

#         return None  # Allow request to continue
