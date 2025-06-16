from django.urls import path
from .views import roleSuggestionView

urlpatterns = [
    path('role-suggestion/', roleSuggestionView.as_view({'post': 'create'}), name='role-suggestion'),
]