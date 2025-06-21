from rest_framework import viewsets
from .serializers import RoleSuggestionSerializer
from rest_framework.parsers import MultiPartParser
from resume_analyzer.logic import GenAIVisualAnalyzer
import os
from core.utils import success_response
from .suggestion import ResumeRoleAnalyzer
from .utils import with_temp_file
api_key=os.getenv('GENAI_API_KEY')

analyser=GenAIVisualAnalyzer(api_key='d')

class roleSuggestionView(viewsets.ModelViewSet):
    parser_classes = [MultiPartParser]
    serializer_class = RoleSuggestionSerializer
    api_credit_cost= os.getenv('API_COST')


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        analyzer = ResumeRoleAnalyzer(api_key=api_key)
        with with_temp_file(serializer.validated_data['resume']) as temp_path:
            extracted_text = analyser.extract_text_from_pdf(temp_path)
            result = analyzer.analyze_resume(extracted_text)
        return success_response(data=result)


