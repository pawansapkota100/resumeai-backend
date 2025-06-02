from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import UserProfile, ResumeAnalysis
from .serializers import UserProfileSerializer, UserRegistrationSerializer, UserSerializer

User = get_user_model()
from .utils import error_response,success_response
# Create your views here.

# class ResumeAnalyzeView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request):
#         serializer = ResumeAnalysisSerializer(data=request.data)
#         if serializer.is_valid():
#             # Here you would integrate with your GenAI service
#             # For now, we'll just save the file and return a mock analysis
#             analysis_result = {
#                 "skills": ["Python", "Django", "REST API"],
#                 "experience_level": "Intermediate",
#                 "suggestions": ["Add more project details", "Include certifications"]
#             }
            
#             serializer.save(
#                 user=request.user,
#                 analysis_result=analysis_result
#             )
#             return success_response(data=serializer.data, status_code=status.HTTP_201_CREATED)
#         return error_response(message=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

class ResumeSuggestionsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Here you would integrate with your GenAI service to get suggestions
        # For now, returning mock data
        suggestions = {
            "content_suggestions": [
                "Add more quantifiable achievements",
                "Include relevant certifications",
                "Highlight leadership experience"
            ],
            "format_suggestions": [
                "Use bullet points for better readability",
                "Keep consistent formatting throughout",
                "Use action verbs to start bullet points"
            ]
        }
        return Response(suggestions)

# class ResumeHistoryView(generics.ListAPIView):
#     serializer_class = ResumeAnalysisSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         return ResumeAnalysis.objects.filter(user=self.request.user).order_by('-created_at')

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return success_response(
                data= UserSerializer(user, context=self.get_serializer_context()).data,
                message= "User Created Successfully", status_code=status.HTTP_201_CREATED)
        return error_response(message=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
