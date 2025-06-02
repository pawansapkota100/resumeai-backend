from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from .auth import EmailTokenObtainPairView

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', views.UserRegistrationView.as_view(), name='register'),
    path('auth/token/', EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Resume processing endpoints
    # path('resume/analyze/', views.ResumeAnalyzeView.as_view(), name='resume-analyze'),
    path('resume/suggestions/', views.ResumeSuggestionsView.as_view(), name='resume-suggestions'),
    # path('resume/history/', views.ResumeHistoryView.as_view(), name='resume-history'),
] 