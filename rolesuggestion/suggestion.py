import google.generativeai as genai
import json
from typing import Dict, List
from dataclasses import dataclass
import re

@dataclass
class RoleRecommendation:
    """Data class for role recommendations"""
    title: str
    match_score: int
    skills: List[str]
    description: str
    demand: str

class ResumeRoleAnalyzer:
    """
    A class to analyze resume text and provide role suggestions using Gemini LLM
    """
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-exp"):
        """
        Initialize with Gemini API credentials
        """
        self.api_key = api_key
        self.model_name = model_name
        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
    
    
    def analyze_resume(self, resume_text: str) :
        """
        Analyze resume text and return role recommendations in JSON format.
        Strips markdown-style formatting if present.
        """
        analysis_prompt = self._create_analysis_prompt(resume_text)

        try:
            # Get response from Gemini
            response = self.model.generate_content(analysis_prompt)
            response_text = response.text.strip()

            # Remove Markdown code block (```json ... ```)
            if response_text.startswith("```json"):
                response_text = re.sub(r"^```json\s*|\s*```$", "", response_text.strip(), flags=re.DOTALL)

            # Try parsing the cleaned response text as JSON
            role_recommendations = json.loads(response_text)
            return role_recommendations

        except json.JSONDecodeError as je:
            raise ValueError(f"Failed to parse JSON from model response: {je}\nRaw response: {response.text}")
        except Exception as e:
            raise Exception(f"Error analyzing resume: {str(e)}")
    
    def _create_analysis_prompt(self, resume_text: str) -> str:
        """
        Create the analysis prompt using the specified format
        """
        prompt = f"""You are a role suggestion engine analyzing a candidate's resume.

            Your task is to:
            1. Extract and suggest the top relevant job roles based on the candidate's experience, skills, and background.
            2. Provide suggestions on how the candidate can improve their profile to better match more roles or increase match scores.

            Output the results in the following structured JSON format:

            [
            {{
                "title": "<Job Title>",
                "matchScore": <Integer 0-100>, 
                "skills": ["<Skill1>", "<Skill2>", ...],
                "description": "<Short description of what this role typically does, based on the candidate's resume>",
                "demand": "<Low | Medium | High>",
                "suggestions": ["<Skill to learn>", "<Certifications to consider>", "<Experience to gain>", ...]
            }},
            ...
            ]

            Instructions:
            - Only include roles that are clearly supported by the resume content.
            - Limit to 3–5 most relevant roles.
            - Use matchScore to reflect how closely the resume fits the role.
            - Estimate demand based on common industry trends.
            - For each role, give actionable suggestions the candidate can follow to improve fit. This can include missing skills, tools, frameworks, certifications, or types of projects to work on.
            - Format the output as a JSON list with each role as a structured object.
            

            Resume:
            \"\"\"
            {resume_text}
            \"\"\"
            """
        return prompt
    
    def _parse_gemini_response(self, response_text: str) -> List[RoleRecommendation]:
        """
        Parse the Gemini response and extract role recommendations
        """
        try:
            # Clean the response text
            cleaned_response = response_text.strip()
            
            # Remove any markdown code blocks if present
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]
            
            # Parse JSON
            roles_data = json.loads(cleaned_response.strip())
            
            # Convert to RoleRecommendation objects
            recommendations = []
            for role_data in roles_data:
                role_rec = RoleRecommendation(
                    title=role_data.get('title', ''),
                    match_score=int(role_data.get('matchScore', 0)),
                    skills=role_data.get('skills', []),
                    description=role_data.get('description', ''),
                    demand=role_data.get('demand', 'Medium')
                )
                recommendations.append(role_rec)
            
            return recommendations
            
        except json.JSONDecodeError as e:
            raise Exception(f"Error parsing JSON response: {str(e)}")
        except Exception as e:
            raise Exception(f"Error parsing Gemini response: {str(e)}")
    
    def get_role_suggestions_dict(self, resume_text: str) -> List[Dict]:
        """
        Get role suggestions as a list of dictionaries
        """
        recommendations = self.analyze_resume(resume_text)
        return [
            {
                "title": rec.title,
                "matchScore": rec.match_score,
                "skills": rec.skills,
                "description": rec.description,
                "demand": rec.demand
            }
            for rec in recommendations
        ]
    
    def get_role_titles(self, resume_text: str) -> List[str]:
        """
        Get simple role titles as a list of strings
        """
        recommendations = self.analyze_resume(resume_text)
        return [rec.title for rec in recommendations]

# Example usage
if __name__ == "__main__":
    # Example usage of the ResumeRoleAnalyzer class
    
    # Initialize the analyzer
    # analyzer = ResumeRoleAnalyzer(api_key="your-gemini-api-key")
    
    # Sample resume text
    sample_resume = """
    John Doe
    Software Developer
    john.doe@email.com | (555) 123-4567
    
    EXPERIENCE:
    - 3 years of experience in full-stack web development
    - Proficient in Python, JavaScript, React, and Node.js
    - Experience with AWS cloud services and Docker
    - Led a team of 2 developers on e-commerce project
    
    EDUCATION:
    Bachelor of Science in Computer Science, 2021
    
    SKILLS:
    Python, JavaScript, React, Node.js, AWS, Docker, Git, SQL
    """
    
    # Analyze resume and get role recommendations
    # recommendations = analyzer.analyze_resume(sample_resume)
    # for rec in recommendations:
    #     print(f"Role: {rec.title} (Match: {rec.match_score}%)")
    #     print(f"Skills: {rec.skills}")
    #     print(f"Description: {rec.description}")
    #     print(f"Demand: {rec.demand}")
    #     print("---")
    
    # Get role suggestions as dictionary list
    # role_dicts = analyzer.get_role_suggestions_dict(sample_resume)
    # print(role_dicts)
    
    # Get simple role titles
    # titles = analyzer.get_role_titles(sample_resume)
    # print(f"Role titles: {titles}")