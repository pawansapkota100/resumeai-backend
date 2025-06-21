
# resume_parser.py
import fitz
import google.generativeai as genai
import json
import re


class ResumeParser:
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-exp"):
        """
        Initialize with Gemini API credentials
        """
        self.api_key = api_key
        self.model_name = model_name
        # Configure Gemini  
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF using PyMuPDF"""
        doc = fitz.open(pdf_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        doc.close()
        return full_text
    
    def parse_resume_with_gemini(self, resume_text):
        """Parse resume text using Gemini AI"""
        prompt = f"""
        Extract the following information from this resume text and return it as a JSON object:
        
        Required fields:
        - name: Full name
        - email: Email address
        - phone: Phone number
        - location: Current location/address
        - skills: Array of technical skills
        - experience: Array of work experience objects with (company, position, duration, description)
        - education: Array of education objects with (institution, degree, field, year)
        - summary: Brief professional summary
        - preferred_job_types: Array of preferred job types (full-time, part-time, contract, remote, internship)
        - preferred_locations: Array of preferred work locations
        - expected_salary_range: Expected salary range if mentioned
        - years_of_experience: Total years of professional experience (as integer)
        - job_level: Career level (entry, mid, senior, lead, executive)
        
        Resume text:
        {resume_text}
        
        Return only valid JSON format. If any field is not found, use null or empty array as appropriate.
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Clean and parse the response
            json_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if json_text.startswith('```json'):
                json_text = json_text[7:]
            if json_text.endswith('```'):
                json_text = json_text[:-3]
            
            parsed_data = json.loads(json_text)
            return parsed_data
            
        except Exception as e:
            print(f"Error parsing resume with Gemini: {str(e)}")
            return self._fallback_parsing(resume_text)
    
    def _fallback_parsing(self, resume_text):
        """Fallback parsing using regex patterns"""
        data = {
            "name": None,
            "email": None,
            "phone": None,
            "location": None,
            "skills": [],
            "experience": [],
            "education": [],
            "summary": None,
            "preferred_job_types": [],
            "preferred_locations": [],
            "expected_salary_range": None,
            "years_of_experience": 0,
            "job_level": "entry"
        }
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, resume_text)
        if email_match:
            data["email"] = email_match.group()
        
        # Extract phone
        phone_pattern = r'[\+]?[1-9]?[\-\.\s]?\(?[0-9]{3}\)?[\-\.\s]?[0-9]{3}[\-\.\s]?[0-9]{4}'
        phone_match = re.search(phone_pattern, resume_text)
        if phone_match:
            data["phone"] = phone_match.group()
        
        return data
    
    def process_resume(self, pdf_path):
        """Main method to process resume"""
        try:
            # Extract text from PDF
            resume_text = self.extract_text_from_pdf(pdf_path)
            
            # Parse with Gemini AI
            parsed_data = self.parse_resume_with_gemini(resume_text)
            
            return {
                "success": True,
                "extracted_text": resume_text,
                "parsed_data": parsed_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "extracted_text": "",
                "parsed_data": {}
            }