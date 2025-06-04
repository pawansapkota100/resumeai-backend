from .views import ResumeAnalysisView,ResumeScreeningAPIView

from django.urls import path, include

urlpatterns = [
        path('resume-analysis/', ResumeAnalysisView.as_view(), name='resume-analysis'),
        path('resume-screening/', ResumeScreeningAPIView.as_view(), name='resume-screening'),

]
