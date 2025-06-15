from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser
from .serializer import JobSerchingSerializer
from .scrape import Query,query
import json
from rolesuggestion.utils import with_temp_file
from resume_analyzer.logic import GenAIVisualAnalyzer
import os
from core.utils import success_response
analyser=GenAIVisualAnalyzer(api_key=os.getenv('GENAI_API_KEY'))
class ScrapeJobViewset(viewsets.ModelViewSet):
    parser_classes = [MultiPartParser]
    serializer_class=JobSerchingSerializer
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with with_temp_file(serializer.validated_data['cv']) as temp_path:
            extracted_text = analyser.extract_text_from_pdf(temp_path)
            result = analyser.analyse_resume_for_job_search(extracted_text)
        serializer.validated_data.pop('cv')
        json_query=serializer.validated_data
        combine_query= {**result, **json_query}
        request_query= json.dumps(combine_query)
        request_query=json.loads(request_query)
        request_query['limit']=20
        print(request_query)
        result= query(request_query)
        return success_response(data=result)






        # dateSincePosted = serializers.ChoiceField(choices=DATE_SINCE_POSTED_CHOICES, required=False)
    # jobType = serializers.ChoiceField(choices=JOB_TYPE_CHOICES, required=False)
    # remoteFilter = serializers.ChoiceField(choices=REMOTE_FILTER_CHOICES, required=False)
    # salary_range = serializers.ChoiceField(choices=SALARY_RANGE_CHOICES, required=False)
    # experience_level = serializers.ChoiceField(choices=EXPERIENCE_LEVEL_CHOICES, required=False)
