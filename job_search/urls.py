# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ScrapeJobViewset

router = DefaultRouter()
router.register(r'job-scraper', ScrapeJobViewset, basename='job-scraper')

urlpatterns = [
    path('', include(router.urls)),
]