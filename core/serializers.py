from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile, ResumeAnalysis

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    full_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'password2', 'full_name')
        extra_kwargs = {
            'full_name': {'required': True},
            'email': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    def validate_full_name(self, full_name):
        if ' ' not in full_name:
            raise serializers.ValidationError("Please enter your full name")
        return full_name

    def create(self, validated_data):

        validated_data.pop('password2')
        full_name = validated_data['full_name'].split()
        validated_data.pop('full_name')
        user = User.objects.create_user(**validated_data)
        user.first_name=full_name[0]
        user.last_name=full_name[1:]
        user.save()
        # Create user profile   
        UserProfile.objects.create(user=user)
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name')
        read_only_fields = ('id',)

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ('id', 'user', 'bio', 'location', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

# class ResumeAnalysisSerializer(serializers.ModelSerializer):
#     user = UserSerializer(read_only=True)

#     class Meta:
#         model = ResumeAnalysis
#         fields = ('id', 'user', 'resume_file', 'analysis_result', 'created_at', 'updated_at')
#         read_only_fields = ('id', 'created_at', 'updated_at') 