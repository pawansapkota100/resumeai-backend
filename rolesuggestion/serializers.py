from rest_framework import serializers


class RoleSuggestionSerializer(serializers.Serializer):
    resume = serializers.FileField()