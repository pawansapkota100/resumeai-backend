from rest_framework.serializers import Serializer
from rest_framework import serializers


class ResumeAnalysisSerializer(Serializer):
    pdf= serializers.FileField()


class ResumeScreeningSerializer(Serializer):
    pdf= serializers.FileField()
    job_description = serializers.CharField()

class CoverLetterSerializer(serializers.Serializer):
    # Job Details
    company = serializers.CharField(
        max_length=200,
        required=True,
        help_text="Company name",
        error_messages={
            'required': 'Company name is required.',
            'blank': 'Company name cannot be blank.',
            'max_length': 'Company name cannot exceed 200 characters.'
        }
    )
    
    position = serializers.CharField(
        max_length=200,
        required=True,
        help_text="Job position/title",
        error_messages={
            'required': 'Position is required.',
            'blank': 'Position cannot be blank.',
            'max_length': 'Position cannot exceed 200 characters.'
        }
    )
    
    job_description = serializers.CharField(
        required=True,
        help_text="Complete job description",
        error_messages={
            'required': 'Job description is required.',
            'blank': 'Job description cannot be blank.'
        }
    )
    
    # Personal Information
    name = serializers.CharField(
        max_length=100,
        required=True,
        help_text="Full name of the applicant",
        error_messages={
            'required': 'Full name is required.',
            'blank': 'Full name cannot be blank.',
            'max_length': 'Name cannot exceed 100 characters.'
        }
    )
    
    email = serializers.EmailField(
        required=True,
        help_text="Email address",
        error_messages={
            'required': 'Email is required.',
            'invalid': 'Please enter a valid email address.'
        }
    )
    
    phone = serializers.CharField(
        max_length=20,
        required=False,
        help_text="Phone number",
        error_messages={
            'required': 'Phone number is required.',
            'blank': 'Phone number cannot be blank.',
            'max_length': 'Phone number cannot exceed 20 characters.'
        }
    )
    
    linkedin = serializers.URLField(
        required=False,
        allow_blank=True,
        help_text="LinkedIn profile URL (optional)",
        error_messages={
            'invalid': 'Please enter a valid LinkedIn URL.'
        }
    )
    
    portfolio = serializers.URLField(
        required=False,
        allow_blank=True,
        help_text="Portfolio or website URL (optional)",
        error_messages={
            'invalid': 'Please enter a valid portfolio/website URL.'
        }
    )
    
    # Skills and Experience
    skills = serializers.CharField(
        required=True,
        help_text="Relevant skills for the position",
        error_messages={
            'required': 'Skills are required.',
            'blank': 'Skills cannot be blank.'
        }
    )
    
    achievements = serializers.CharField(
        required=False,
        help_text="Key achievements (2-3 relevant ones)",
        error_messages={
            'required': 'Achievements are required.',
            'blank': 'Achievements cannot be blank.'
        }
    )
    
    why_interested = serializers.CharField(
        required=False,
        help_text="Why you're interested in this position and company",
        error_messages={
            'required': 'Interest explanation is required.',
            'blank': 'Please explain why you are interested in this position.'
        }
    )
