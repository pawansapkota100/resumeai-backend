
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import BillingRecord, Dashboard, Notification, UserProfile, UserResume,SaveResult
import os
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

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    email= serializers.EmailField(source='user.email', read_only=True)
    class Meta:
        model = UserProfile
        fields= ['bio', 'location','first_name', 'last_name','email']

    def update(self, instance, validated_data):
        user_data= validated_data.pop('user', {})

        for attrs,item in validated_data.items():
            setattr(instance, attrs, item)
        
        for attrs, item in user_data.items():
            setattr(instance.user, attrs, item)
        
        instance.user.save()
        instance.save()
        return instance
        
class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def validate_old_password(self, old_password):
        user = self.context['request'].user
        if not user.check_password(old_password):
            raise serializers.ValidationError("Old password is incorrect")
        return old_password

class BillingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingRecord
        fields = ('id','amount','payment_status','payment_method','billing_date')

class ProfileNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('email_notification', 'job_match_notification', 'resume_improvement_notification')
    
class DashboardSerializer(serializers.ModelSerializer):
    credit_available= serializers.IntegerField(source='user.profile.credit_available', read_only=True)
    class Meta:
        model = Dashboard
        fields='__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields='__all__'

class UserResumeSerializer(serializers.ModelSerializer):
    file_name= serializers.SerializerMethodField(read_only=True)
    created_at= serializers.DateTimeField(read_only=True)
    class Meta:
        model = UserResume
        fields = ('id', 'resume_file', 'created_at','file_name')
    
    def get_file_name(self, obj):
        return os.path.basename(obj.resume_file.name)
    
class SavedResumeSerializer(serializers.ModelSerializer):
    user= serializers.PrimaryKeyRelatedField(default=serializers.CurrentUserDefault(),read_only=True)
    class Meta:
        model = SaveResult
        fields='__all__'
        read_only_fields = ['created_at']
    
    def to_representation(self, instance):
        """
        Customize fields returned based on action (list/retrieve).
        """
        rep = super().to_representation(instance)
        request = self.context.get("request", None)

        # Determine view action
        if request and hasattr(self.context.get("view"), "action"):
            action = self.context["view"].action
            if action == "list":
                # Only include specific fields for list view
                return {
                    "id": rep.get("id"),
                    "title": rep.get("title"),
                    "feature_type": rep.get("feature_type"),
                    "created_at": rep.get("created_at"),
                }
        return rep