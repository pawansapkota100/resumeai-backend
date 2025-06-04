from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework import permissions
from drf_yasg.utils import swagger_auto_schema
from .serializers import ResumeAnalysisSerializer,ResumeScreeningSerializer
from .logic import analyze_resume_with_genai
from core.utils import success_response,error_response
import tempfile
import os
from django.conf import settings



class ResumeAnalysisView(APIView):
    serializer_class = ResumeAnalysisSerializer
    parser_classes = [MultiPartParser]
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(request_body=ResumeAnalysisSerializer)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        uploaded_file = serializer.validated_data['pdf']

        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name

        try:
            analysis_result = analyze_resume_with_genai(request=request, pdf_path=temp_file_path)
        finally:
            # Optional: clean up temporary file
            os.remove(temp_file_path)

        return success_response(data=analysis_result)



from resume_analyzer.logic import GenAIVisualAnalyzer
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

class ResumeScreeningAPIView(APIView):
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(request_body=ResumeScreeningSerializer)
    def post(self, request, *args, **kwargs):
    
        serializer=ResumeScreeningSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Define folder path
        folder_path = os.path.join(settings.MEDIA_ROOT, 'resume_screening')

        # Create folder if it doesn't exist
        os.makedirs(folder_path, exist_ok=True)
        import random
        random_number = random.randint(1, 100000)
        # Define file path to save
        file_path = os.path.join(folder_path, f"{random_number}_resume.pdf")

        # Save the uploaded resume file
        with open(file_path, 'wb+') as destination:
            for chunk in serializer.validated_data['pdf'].chunks():
                destination.write(chunk)

        # Extract text from saved PDF
        resume_text = GenAIVisualAnalyzer.extract_text_from_pdf(self,file_path)

        if not resume_text.strip():
            return error_response(message={"error": "Could not extract text from the uploaded resume PDF."}, status_code=status.HTTP_400_BAD_REQUEST)

        api_key = os.getenv('GENAI_API_KEY')

        # Initialize analyzer and call screening
        analyzer  = GenAIVisualAnalyzer(api_key)
        response = analyzer.resume_screening(
    resume_text=resume_text,
    job_description=serializer.validated_data['job_description']
)


        return success_response(data=response, status_code=status.HTTP_200_OK)