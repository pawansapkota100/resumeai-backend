from .suggestion import ResumeRoleAnalyzer
from resume_analyzer.logic import GenAIVisualAnalyzer
import os

analyser=GenAIVisualAnalyzer(api_key='d')
api_key=os.getenv('GENAI_API_KEY')

resume_text=analyser.extract_text_from_pdf("result_resume/61009_annotated_resume.pdf")
# Initialize
analyzer = ResumeRoleAnalyzer(api_key=api_key)

# Get structured recommendations
recommendations = analyzer.analyze_resume(resume_text)
for rec in recommendations:
    print(f"Role: {rec.title} (Match: {rec.match_score}%)")
    print(f"Skills: {rec.skills}")
    print(f"Demand: {rec.demand}")

# Get as dictionaries (JSON format)
role_dicts = analyzer.get_role_suggestions_dict(resume_text)

# Get simple titles list
titles = analyzer.get_role_titles(resume_text)
