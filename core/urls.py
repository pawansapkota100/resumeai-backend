from django.urls import path,include
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from .auth import EmailTokenObtainPairView
from rest_framework.routers import DefaultRouter

router=DefaultRouter()
router.register(r'update-profile', views.UserProfileViewset, basename='profile')

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', views.UserRegistrationView.as_view(), name='register'),
    path('auth/token/', EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Resume processing endpoints
    # path('resume/analyze/', views.ResumeAnalyzeView.as_view(), name='resume-analyze'),
    path('resume/suggestions/', views.ResumeSuggestionsView.as_view(), name='resume-suggestions'),
    path('signup/firebase/', views.FirebaseAuthView.as_view(), name='firebase-auth'),
    path('change-password/', views.ChangePaswwordView.as_view(), name='change-password'),
    path('billing-info/', views.BillingDetailsView.as_view(), name='billing-info'),
    path('profile-notification/', views.ProfileNotificationView.as_view(), name='profile-notification'),
    path('', include(router.urls)),

] 