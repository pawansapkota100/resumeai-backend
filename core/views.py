from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import UserProfile, ResumeAnalysis
from .serializers import UserProfileSerializer, UserRegistrationSerializer, UserSerializer
from firebase_admin import credentials, auth, firestore
import firebase_admin
import firebase_admin.exceptions
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from core.utils import error_response, success_response



User = get_user_model()
from .utils import error_response,success_response
credentials = credentials.Certificate(settings.GOOGLE_APPLICATION_CREDENTIALS) 

firebase_app = firebase_admin.initialize_app(credentials)


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



def generate_jwt(user):
    # Create the refresh token for the user
    refresh = RefreshToken.for_user(user)
    
    # Generate the access token from the refresh token
    access_token = str(refresh.access_token)  # Convert access token to string

    # Create the JWT payload (you can include the refresh token as well if needed)
    payload = {
        'refresh': str(refresh),  # Include the refresh token string
        'access': access_token,   # Include the access token string
        'exp': datetime.utcnow() + timedelta(days=1),  # Token expires in 1 day
        'iat': datetime.utcnow(),  # Issued at time
    }
    
    # Return the access token and refresh token as a response
    return {
        'access': access_token,
        'refresh': str(refresh),  # Include refresh token if needed
    }

# API view for verifying Firebase ID token
class FirebaseAuthView(APIView):
    def post(self, request):
        firebase_token = request.data.get('token')

        if not firebase_token:
            return Response({"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Step 1: Verify Firebase ID token
            decoded_token = auth.verify_id_token(firebase_token)
            uid = decoded_token['uid']  # The Firebase UID of the user
            email=decoded_token.get('email')
            picture = decoded_token.get('picture')

            
            # Step 2: Fetch or create user in the database
            user, created = User.objects.get_or_create(email=email)

            if created:
                # Optionally, populate the user fields from Firebase data
                user.first_name = decoded_token.get('name', '')
                user.email = decoded_token.get('email', '')
                user.is_active=True
                user.is_social_login=True
                user.firebase_uid= uid
                user.save()

                UserProfile.objects.create(user=user, bio='', location='', image='',created_at=datetime.now(),updated_at=datetime.now())

            if user.is_social_login != True:
                return error_response(message="You already have account from this email")


            jwt_token = generate_jwt(user)

            # Step 4: Return the JWT token to the client
            return Response({"token": jwt_token}, status=status.HTTP_200_OK)

        except firebase_admin.exceptions.FirebaseError:
            return Response({"error": "Invalid Firebase token"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)