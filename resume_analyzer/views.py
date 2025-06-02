from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework import permissions
from drf_yasg.utils import swagger_auto_schema
from .serializers import ResumeAnalysisSerializer
from .logic import analyze_resume_with_genai
from core.utils import success_response,error_response
import tempfile
import os


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

