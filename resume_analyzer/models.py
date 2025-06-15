import json 
import os
from django.utils.timezone import now
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone



User = get_user_model()
import numpy as np
from collections import Counter
import json

class ResumeAnalysisManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class ResumeAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_analyses')
    resume_file = models.CharField(max_length=255)
    analysis_result = models.JSONField(blank=True, null=True)
    file_hash = models.CharField(max_length=64)
    uploaded_at = models.DateTimeField(default=timezone.now)

    deleted_at = models.DateTimeField(null=True, blank=True)

    # Managers
    objects = ResumeAnalysisManager()  # Default manager hides deleted
    all_objects = models.Manager()     # Use this to access all records, even deleted

    @staticmethod
    def custom_to_serializable(obj):
        if isinstance(obj, (np.float32, np.float64)):
            return float(obj)
        if isinstance(obj, (np.int32, np.int64, np.integer)):
            return int(obj)
        if isinstance(obj, Counter):
            return dict(obj)
        if isinstance(obj, tuple):
            return [ResumeAnalysis.custom_to_serializable(item) for item in obj]
        if isinstance(obj, dict):
            return {key: ResumeAnalysis.custom_to_serializable(value) for key, value in obj.items()}
        if isinstance(obj, list):
            return [ResumeAnalysis.custom_to_serializable(item) for item in obj]
        return obj

    def get_analysis_result_json(self):
        if not self.analysis_result:
            return None
        try:
            # Load string to Python dict
            data = json.dumps(self.analysis_result)
        except json.JSONDecodeError:
            # If it's not valid JSON, just return the raw string
            pass
        
        # Convert non-serializable objects inside data
        # serializable_data = self.custom_to_serializable(data)
        # # Return pretty JSON string
        # return json.dumps(serializable_data, indent=2)
        return self.analysis_result
        
    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self):
        super().delete()

    def __str__(self):
        return f"{self.user} - {self.resume_file.name}"
    def save(self, *args, **kwargs):
        if self.resume_file and not self.pk:
            # Extract extension and rename
            ext = os.path.splitext(self.resume_file)[1]
            new_name = f"{self.user.id}_resume_{ext}"
            self.resume_file = new_name
        super().save(*args, **kwargs)


