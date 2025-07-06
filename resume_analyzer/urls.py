from .views import CoverletterGenerator, ResumeAnalysisView,ResumeScreeningAPIView,ResumeGenerator

from django.urls import path

urlpatterns = [
        path('resume-analysis/', ResumeAnalysisView.as_view(), name='resume-analysis'),
        path('resume-screening/', ResumeScreeningAPIView.as_view(), name='resume-screening'),
        path('cover-letter-generation/', CoverletterGenerator.as_view(), name='cover-letter-generation'),
        path('resume-json/', ResumeGenerator.as_view(), name='resume-json'),
]       
