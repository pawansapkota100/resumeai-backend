from .views import ResumeAnalysisView

from django.urls import path, include

urlpatterns = [
        path('resume-analysis/', ResumeAnalysisView.as_view(), name='resume-analysis'),

]
