from rest_framework.serializers import Serializer
from rest_framework import serializers


class ResumeAnalysisSerializer(Serializer):
    pdf= serializers.FileField()


class ResumeScreeningSerializer(Serializer):
    pdf= serializers.FileField()
    job_description = serializers.CharField()