from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework import permissions
from drf_yasg.utils import swagger_auto_schema
from .serializers import CoverLetterSerializer, ResumeAnalysisSerializer, ResumeScreeningSerializer
from .logic import analyze_resume_with_genai
from core.utils import success_response, error_response
import tempfile
import os
from django.conf import settings
from resume_analyzer.models import ResumeAnalysis
from .utils import calculate_file_hash
import json

# def get_pretty_json(data):
#     try:
#         data = json.loads(data)
#         return json.dumps(data, indent=4)
#     except json.JSONDecodeError:
#         return None
from django.db import transaction


class ResumeAnalysisView(APIView):
    serializer_class = ResumeAnalysisSerializer
    parser_classes = [MultiPartParser]
    permission_classes = [permissions.IsAuthenticated]
    api_credit_cost = None

    @swagger_auto_schema(request_body=ResumeAnalysisSerializer)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded_file = serializer.validated_data["pdf"]

        # Step 1: Calculate hash of uploaded file
        file_hash = calculate_file_hash(uploaded_file)

        # Step 2: Check if this resume has already been analyzed
        existing = ResumeAnalysis.objects.filter(
            file_hash=file_hash, deleted_at__isnull=True
        ).first()

        if existing:
            # Reuse previous result
            analysis_result = {
                "detailed_report": existing.get_analysis_result_json(),
                "annotated_pdf_url": existing.resume_file,  # Use .url to get the full URL
                "reused": True,
            }
        else:
            self.api_credit_cost = os.getenv("API_COST")
            if request.user.profile.credit_available < self.api_credit_cost:
                return error_response(
                    message={
                        "error": "You don't have enough credits to perform this action."
                    },
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            # Step 3: Save file temporarily for GenAI processing
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                for chunk in uploaded_file.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name

            try:
                # Step 4: Run GenAI analysis
                analysis_result = analyze_resume_with_genai(
                    pdf_path=temp_file_path, request=request
                )

                # Step 5: Save result in DB with the file
                resume_analysis = ResumeAnalysis.objects.create(
                    user=request.user,
                    resume_file=analysis_result[
                        "annotated_pdf_url"
                    ],  # Save the actual file
                    file_hash=file_hash,
                    analysis_result=analysis_result,
                )

                with transaction.atomic():
                    profile = request.user.profile
                    profile.refresh_from_db()
                    cost = getattr(self, "api_credit_cost", 10)
                    profile.credit_available -= cost
                    profile.save()

            finally:
                os.remove(temp_file_path)

        return success_response(data=analysis_result)


from resume_analyzer.logic import GenAIVisualAnalyzer
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema


class ResumeScreeningAPIView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [permissions.IsAuthenticated]
    api_credit_cost = os.getenv("API_COST")

    @swagger_auto_schema(request_body=ResumeScreeningSerializer)
    def post(self, request, *args, **kwargs):

        serializer = ResumeScreeningSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Define folder path
        folder_path = os.path.join(settings.MEDIA_ROOT, "resume_screening")

        # Create folder if it doesn't exist
        os.makedirs(folder_path, exist_ok=True)
        import random

        random_number = random.randint(1, 100000)
        # Define file path to save
        file_path = os.path.join(folder_path, f"{random_number}_resume.pdf")

        # Save the uploaded resume file
        with open(file_path, "wb+") as destination:
            for chunk in serializer.validated_data["pdf"].chunks():
                destination.write(chunk)

        # Extract text from saved PDF
        resume_text = GenAIVisualAnalyzer.extract_text_from_pdf(self, file_path)

        if not resume_text.strip():
            return error_response(
                message={
                    "error": "Could not extract text from the uploaded resume PDF."
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        api_key = os.getenv("GENAI_API_KEY")

        # Initialize analyzer and call screening
        analyzer = GenAIVisualAnalyzer(api_key)
        response = analyzer.resume_screening(
            resume_text=resume_text,
            job_description=serializer.validated_data["job_description"],
        )

        return success_response(data=response, status_code=status.HTTP_200_OK)

class CoverletterGenerator(APIView):
    serializer_class = CoverLetterSerializer
    permission_classes = [permissions.IsAuthenticated]
    api_credit_cost = os.getenv("API_COST")

    @swagger_auto_schema(request_body=CoverLetterSerializer)
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        api_key = os.getenv("GENAI_API_KEY")
        analyzer = GenAIVisualAnalyzer(api_key)
        response = analyzer.generate_cover_letter(data=data)

        return success_response(data=response, status_code=status.HTTP_200_OK)
