from rest_framework import serializers

class JobSerchingSerializer(serializers.Serializer):
    cv = serializers.FileField()

    DATE_SINCE_POSTED_CHOICES = [
        ('past month', 'past month'),
        ('past week', 'past week'),
        ('24hr', '24hr'),
    ]

    JOB_TYPE_CHOICES = [
        ('full time', 'full time'),
        ('part time', 'part time'),
        ('contract', 'contract'),
        ('temporary', 'temporary'),
        ('volunteer', 'volunteer'),
        ('internship', 'internship'),
    ]

    REMOTE_FILTER_CHOICES = [
        ('On-site', 'On-site'),
        ('Remote', 'Remote'),
        ('Hybrid', 'Hybrid'),
    ]

    EXPERIENCE_LEVEL_CHOICES = [
        ('internship', 'internship'),
        ('entry level', 'entry level'),
        ('associate', 'associate'),
        ('senior', 'senior'),
        ('director', 'director'),
        ('executive', 'executive'),
    ]

    SALARY_RANGE_CHOICES = [
        ('40000', '40000'),
        ('60000', '60000'),
        ('80000', '80000'),
        ('100000', '100000'),
        ('120000', '120000'),
    ]
    dateSincePosted = serializers.ChoiceField(choices=DATE_SINCE_POSTED_CHOICES, required=False)
    jobType = serializers.ChoiceField(choices=JOB_TYPE_CHOICES, required=False)
    remoteFilter = serializers.ChoiceField(choices=REMOTE_FILTER_CHOICES, required=False)
    salary_range = serializers.ChoiceField(choices=SALARY_RANGE_CHOICES, required=False)
    experience_level = serializers.ChoiceField(choices=EXPERIENCE_LEVEL_CHOICES, required=False)

