import fitz  # PyMuPDF
import cv2
import numpy as np
import base64
import json
from collections import Counter
from PIL import Image
import io
from typing import Dict, List, Tuple
import google.generativeai as genai
import os 
from django.conf import settings




class GenAIVisualAnalyzer:
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-exp"):
        """
        Initialize with Gemini API credentials
        """
        self.api_key = api_key
        self.model_name = model_name
        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        
    def analyze_resume_comprehensively(self, pdf_path: str) -> Dict:
        """
        Comprehensive analysis combining traditional CV and GenAI
        """
        # Step 1: Traditional computer vision analysis
        cv_results = self._traditional_analysis(pdf_path)
        
        # Step 2: Convert PDF to high-quality image for GenAI
        image_base64 = self._pdf_to_base64_image(pdf_path)
        
        # Step 3: GenAI visual analysis
        genai_results = self._genai_visual_analysis(image_base64, cv_results)
        
        # Step 4: GenAI layout and design critique
        design_critique = self._genai_design_critique(image_base64)
        
        # Step 5: GenAI professional assessment
        professional_assessment = self._genai_professional_assessment(image_base64)
        
        # Step 6: Combine all analyses
        combined_results = self._combine_analyses(
            cv_results, genai_results, design_critique, professional_assessment
        )
        
        return combined_results
    
    def _pdf_to_base64_image(self, pdf_path: str) -> str:
        """Convert PDF first page to high-quality base64 image"""
        doc = fitz.open(pdf_path)
        page = doc[0]
        
        # High resolution for better GenAI analysis
        pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))
        img_data = pix.tobytes("png")
        
        doc.close()
        
        # Convert to base64
        img_base64 = base64.b64encode(img_data).decode('utf-8')
        return img_base64
    
    def _traditional_analysis(self, pdf_path: str) -> Dict:
        """Traditional computer vision analysis (from previous example)"""
        doc = fitz.open(pdf_path)
        page = doc[0]
        
        # Font analysis
        font_data = self._extract_font_metrics(page)
        
        # Color analysis
        color_data = self._extract_color_metrics(page)
        
        # Layout analysis
        layout_data = self._extract_layout_metrics(pdf_path)
        
        doc.close()
        
        return {
            'fonts': font_data,
            'colors': color_data,
            'layout': layout_data,
            'technical_score': self._calculate_technical_score(font_data, color_data, layout_data)
        }
    
    def _extract_font_metrics(self, page) -> Dict:
        """Extract detailed font metrics"""
        blocks = page.get_text("dict")
        fonts, sizes = [], []
        
        for block in blocks["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        fonts.append(span["font"])
                        sizes.append(span["size"])
        
        return {
            'unique_fonts': len(set(fonts)),
            'font_list': list(set(fonts)),
            'size_range': (min(sizes), max(sizes)) if sizes else (0, 0),
            'avg_size': np.mean(sizes) if sizes else 0,
            'size_distribution': Counter(sizes)
        }
    
    def _extract_color_metrics(self, page) -> Dict:
        """Extract color usage metrics"""
        blocks = page.get_text("dict")
        colors = []
        
        for block in blocks["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        colors.append(span["color"])
        
        color_counter = Counter(colors)
        return {
            'unique_colors': len(color_counter),
            'color_distribution': dict(color_counter),
            'dominant_color': color_counter.most_common(1)[0] if colors else None,
            'professional_ratio': color_counter.get(0, 0) / len(colors) if colors else 0
        }
    
    def _extract_layout_metrics(self, pdf_path: str) -> Dict:
        """Extract layout and spacing metrics"""
        doc = fitz.open(pdf_path)
        page = doc[0]
        
        # Convert to image
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img_data = pix.tobytes("ppm")
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
        
        height, width = gray.shape
        text_pixels = np.sum(binary == 0)
        white_space_ratio = 1 - (text_pixels / (height * width))
        
        doc.close()
        
        return {
            'white_space_ratio': white_space_ratio,
            'text_density': 1 - white_space_ratio,
            'dimensions': (width, height)
        }
    
    def _calculate_technical_score(self, fonts: Dict, colors: Dict, layout: Dict) -> float:
        """Calculate technical score from traditional metrics"""
        score = 0
        
        # Font score
        if 2 <= fonts['unique_fonts'] <= 3:
            score += 25
        elif fonts['unique_fonts'] == 1:
            score += 15
        
        if 10 <= fonts['avg_size'] <= 12:
            score += 25
        
        # Color score
        if colors['professional_ratio'] > 0.8:
            score += 25
        
        # Layout score
        if 0.3 <= layout['white_space_ratio'] <= 0.7:
            score += 25
        
        return score
    
    def _genai_visual_analysis(self, image_base64: str, cv_data: Dict) -> Dict:
        """GenAI-powered visual analysis with context from CV analysis"""
        
        prompt = f"""
            As a professional resume design expert and HR consultant, analyze the attached resume image for visual design quality.

            I have some technical data from computer vision analysis:
            - Fonts used: {cv_data['fonts']['unique_fonts']} different fonts
            - Average font size: {cv_data['fonts']['avg_size']:.1f}pt
            - White space ratio: {cv_data['layout']['white_space_ratio']:.2f}
            - Color professionalism ratio: {cv_data['colors']['professional_ratio']:.2f}

            Please provide a detailed analysis on:

            1. **Visual Hierarchy**: How well does the design guide the reader’s eye? Are headings, subheadings, and body text clearly distinguished?

            2. **Typography Assessment**: 
            - Are the fonts professional and appropriate?
            - Is there sufficient contrast and readability?
            - Are font sizes appropriate for different elements?

            3. **Layout Quality**:
            - Is the layout balanced and well-organized?
            - Are margins and spacing consistent?
            - Is related information grouped logically?

            4. **Professional Appearance**:
            - Does this look professional for the target industry?
            - Are there any visual distractions?
            - How does this compare to typical industry standards?

            5. **Specific Issues**: Identify any specific visual design problems. 
            If possible, include the exact bounding box on the image in the format:
            {{
                "description": "...",
                "page": 0,
                "bbox": [x0, y0, x1, y1]
            }}
            This will be used to visually mark the issue on the original PDF.

            6. **ATS Compatibility**: Assess whether this resume design will work well with Applicant Tracking Systems (ATS). Highlight any red flags.

            Please assign scores from 1 (poor) to 10 (excellent) for each of the above categories, and provide at least 3 specific, actionable recommendations for improvement.

            ⚠️ IMPORTANT: Return ONLY a valid JSON in the exact format below:
            {{
            "visual_hierarchy": {{"score": X, "analysis": "text"}},
            "typography": {{"score": X, "analysis": "text"}},
            "layout": {{"score": X, "analysis": "text"}},
            "professional_appearance": {{"score": X, "analysis": "text"}},
            "specific_issues": [
                {{
                "description": "text",
                "page": page_number,
                "bbox": [x0, y0, x1, y1]
                }}
            ],
            "ats_compatibility": {{"score": X, "analysis": "text"}},
            "overall_visual_score": X,
            "recommendations": ["rec1", "rec2", "rec3"]
            }}
            """
        
        try:
            # Convert base64 to PIL Image
            image_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_data))
            
            # Generate content with Gemini
            response = self.model.generate_content([prompt, image])
            
            # Clean response text
            response_text = response.text.strip()
            print(f"Raw response: {response_text[:200]}...")  # Debug print
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Parse JSON
            return json.loads(response_text)
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Response text: {response.text}")
            # Return fallback structure
            return {
                "visual_hierarchy": {"score": 5, "analysis": "Unable to analyze due to response format issue"},
                "typography": {"score": 5, "analysis": "Unable to analyze due to response format issue"},
                "layout": {"score": 5, "analysis": "Unable to analyze due to response format issue"},
                "professional_appearance": {"score": 5, "analysis": "Unable to analyze due to response format issue"},
                "specific_issues": ["Response parsing error"],
                "ats_compatibility": {"score": 5, "analysis": "Unable to analyze due to response format issue"},
                "overall_visual_score": 5,
                "recommendations": ["Please retry analysis"],
                "error": f"JSON parsing failed: {str(e)}"
            }
        except Exception as e:
            print(f"GenAI analysis error: {e}")
            return {"error": str(e)}
    
    def _genai_design_critique(self, image_base64: str) -> Dict:
        """Get detailed design critique from GenAI"""
        
        prompt = """
        As a graphic designer specializing in professional documents, provide a detailed design critique of this resume.
        
        Focus on:
        1. **Design Principles**: How well does it follow design principles (contrast, alignment, repetition, proximity)?
        2. **Color Psychology**: Are colors used effectively and appropriately?
        3. **White Space Usage**: Is white space used effectively to create breathing room?
        4. **Visual Flow**: Does the design guide the reader's eye naturally?
        5. **Modern vs Traditional**: How modern/contemporary is the design approach?
        6. **Industry Appropriateness**: What industries would this design work well for?
        
        Provide specific suggestions for improvement and rate each aspect 1-10.
        
        IMPORTANT: Return ONLY valid JSON with this exact structure (no markdown, no extra text):
        {
            "design_principles": {"score": X, "critique": "detailed critique"},
            "color_usage": {"score": X, "critique": "detailed critique"},
            "white_space": {"score": X, "critique": "detailed critique"},
            "visual_flow": {"score": X, "critique": "detailed critique"},
            "modernity": {"score": X, "critique": "detailed critique"},
            "industry_fit": ["industry1", "industry2"],
            "improvement_suggestions": ["suggestion1", "suggestion2"]
        }
        """
        
        try:
            # Convert base64 to PIL Image
            image_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_data))
            
            # Generate content with Gemini
            response = self.model.generate_content([prompt, image])
            
            # Clean response text
            response_text = response.text.strip()
            print(f"Design critique raw response: {response_text[:200]}...")  # Debug print
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            return json.loads(response_text)
            
        except json.JSONDecodeError as e:
            print(f"Design critique JSON decode error: {e}")
            print(f"Response text: {response.text}")
            # Return fallback structure
            return {
                "design_principles": {"score": 5, "critique": "Unable to analyze due to response format issue"},
                "color_usage": {"score": 5, "critique": "Unable to analyze due to response format issue"},
                "white_space": {"score": 5, "critique": "Unable to analyze due to response format issue"},
                "visual_flow": {"score": 5, "critique": "Unable to analyze due to response format issue"},
                "modernity": {"score": 5, "critique": "Unable to analyze due to response format issue"},
                "industry_fit": ["General"],
                "improvement_suggestions": ["Please retry analysis"],
                "error": f"JSON parsing failed: {str(e)}"
            }
        except Exception as e:
            print(f"Design critique error: {e}")
            return {"error": str(e)}
    
    def _genai_professional_assessment(self, image_base64: str) -> Dict:
        """Get professional/HR perspective from GenAI"""
        
        prompt = """
        As an experienced HR professional and hiring manager, assess this resume's visual presentation from a hiring perspective.
        
        Consider:
        1. **First Impression**: What's your immediate reaction? Professional? Modern? Conservative?
        2. **Readability**: How easy is it to quickly scan for key information?
        3. **Attention to Detail**: Does the visual presentation suggest attention to detail?
        4. **Cultural Fit**: What type of company culture would this design fit?
        5. **Role Suitability**: What types of roles would this design be appropriate for?
        6. **Red Flags**: Any visual elements that might hurt the candidate's chances?
        7. **Competitive Edge**: Does the design help the candidate stand out positively?
        
        Rate each aspect 1-10 and provide actionable feedback.
        
        IMPORTANT: Return ONLY valid JSON with this exact structure (no markdown, no extra text):
        {
            "first_impression": {"score": X, "feedback": "detailed feedback"},
            "readability": {"score": X, "feedback": "detailed feedback"},
            "attention_to_detail": {"score": X, "feedback": "detailed feedback"},
            "cultural_fit": ["culture_type1", "culture_type2"],
            "suitable_roles": ["role_type1", "role_type2"],
            "red_flags": ["flag1", "flag2"],
            "competitive_advantages": ["advantage1", "advantage2"],
            "hr_recommendation": "overall recommendation"
        }
        """
        
        try:
            # Convert base64 to PIL Image
            image_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_data))
            
            # Generate content with Gemini
            response = self.model.generate_content([prompt, image])
            
            # Clean response text
            response_text = response.text.strip()
            print(f"Professional assessment raw response: {response_text[:200]}...")  # Debug print
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            return json.loads(response_text)
            
        except json.JSONDecodeError as e:
            print(f"Professional assessment JSON decode error: {e}")
            print(f"Response text: {response.text}")
            # Return fallback structure
            return {
                "first_impression": {"score": 5, "feedback": "Unable to analyze due to response format issue"},
                "readability": {"score": 5, "feedback": "Unable to analyze due to response format issue"},
                "attention_to_detail": {"score": 5, "feedback": "Unable to analyze due to response format issue"},
                "cultural_fit": ["General"],
                "suitable_roles": ["Various"],
                "red_flags": ["Response parsing error"],
                "competitive_advantages": ["Please retry analysis"],
                "hr_recommendation": "Unable to provide recommendation due to response format issue",
                "error": f"JSON parsing failed: {str(e)}"
            }
            
        except Exception as e:
            print(f"Professional assessment error: {e}")
            return {"error": str(e)}
    
    def _combine_analyses(self, cv_results: Dict, genai_results: Dict, 
                         design_critique: Dict, professional_assessment: Dict) -> Dict:
        """Combine all analyses into comprehensive report"""
        
        # Calculate combined scores
        technical_score = cv_results['technical_score']
        visual_score = genai_results.get('overall_visual_score', 0) * 10
        design_score = np.mean([
            design_critique.get('design_principles', {}).get('score', 0),
            design_critique.get('color_usage', {}).get('score', 0),
            design_critique.get('white_space', {}).get('score', 0),
            design_critique.get('visual_flow', {}).get('score', 0)
        ]) * 10
        
        hr_score = np.mean([
            professional_assessment.get('first_impression', {}).get('score', 0),
            professional_assessment.get('readability', {}).get('score', 0),
            professional_assessment.get('attention_to_detail', {}).get('score', 0)
        ]) * 10
        
        # Weighted final score
        final_score = (
            technical_score * 0.25 +
            visual_score * 0.25 +
            design_score * 0.25 +
            hr_score * 0.25
        )
        
        return {
            'final_score': round(final_score, 1),
            'category_scores': {
                'technical': technical_score,
                'visual_design': visual_score,
                'design_principles': design_score,
                'hr_perspective': hr_score
            },
            'detailed_analysis': {
                'computer_vision': cv_results,
                'genai_visual': genai_results,
                'design_critique': design_critique,
                'professional_assessment': professional_assessment
            },
            'summary_recommendations': self._generate_summary_recommendations(
                genai_results, design_critique, professional_assessment
            )
        }
    
    def _generate_summary_recommendations(self, genai_results: Dict, 
                                        design_critique: Dict, professional_assessment: Dict) -> List[str]:
        """Generate prioritized recommendations"""
        recommendations = []
        
        # Collect all recommendations
        if 'recommendations' in genai_results:
            recommendations.extend(genai_results['recommendations'])
        
        if 'improvement_suggestions' in design_critique:
            recommendations.extend(design_critique['improvement_suggestions'])
        
        # Add critical issues
        if 'red_flags' in professional_assessment:
            for flag in professional_assessment['red_flags']:
                recommendations.append(f"🚩 CRITICAL: {flag}")
        
        return recommendations[:10]  # Top 10 recommendations
    
    def generate_detailed_report(self, analysis_results: Dict) -> str:
        """Generate human-readable detailed report"""
        report = f"""
                    === COMPREHENSIVE RESUME VISUAL ANALYSIS REPORT ===

                    OVERALL SCORE: {analysis_results['final_score']}/100

                    CATEGORY BREAKDOWN:
                    ├── Technical Quality: {analysis_results['category_scores']['technical']}/100
                    ├── Visual Design: {analysis_results['category_scores']['visual_design']}/100  
                    ├── Design Principles: {analysis_results['category_scores']['design_principles']}/100
                    └── HR Perspective: {analysis_results['category_scores']['hr_perspective']}/100

                    === KEY INSIGHTS === """
        
        # Add GenAI insights
        genai_data = analysis_results['detailed_analysis']['genai_visual']
        if 'visual_hierarchy' in genai_data:
            report += f"\n📊 Visual Hierarchy: {genai_data['visual_hierarchy']['score']}/10"
            report += f"\n   {genai_data['visual_hierarchy']['analysis']}"
        
        # Add design critique
        design_data = analysis_results['detailed_analysis']['design_critique']
        if 'visual_flow' in design_data:
            report += f"\n\n🎨 Visual Flow: {design_data['visual_flow']['score']}/10"
            report += f"\n   {design_data['visual_flow']['critique']}"
        
        # Add HR perspective
        hr_data = analysis_results['detailed_analysis']['professional_assessment']
        if 'first_impression' in hr_data:
            report += f"\n\n👔 HR First Impression: {hr_data['first_impression']['score']}/10"
            report += f"\n   {hr_data['first_impression']['feedback']}"
        
        # Add recommendations
        report += "\n\n=== TOP RECOMMENDATIONS ===\n"
        for i, rec in enumerate(analysis_results['summary_recommendations'], 1):
            report += f"{i}. {rec}\n"
        
        return report
    
    import fitz  # PyMuPDF

def annotate_pdf_with_comments(pdf_path, output_path, issues):
    doc = fitz.open(pdf_path)
    print("#################")
    print(issues)

    for issue in issues:
        page_number = issue.get("page")
        bbox = issue.get("bbox")
        description = issue.get("description", "No description")

        if page_number is None or bbox is None:
            continue

        try:
            page = doc[page_number]
            rect = fitz.Rect(bbox)

            # Draw yellow filled rectangle (background)
            page.draw_rect(rect, color=(1, 0, 0), width=2.5)  # red border, yellow fill

            # Text settings
            fontsize = 10
            fontname = "helv"
            line_height = fontsize + 2
            approx_char_width = fontsize * 0.6
            max_chars_per_line = int(rect.width / approx_char_width)

            # Word wrapping
            words = description.split()
            lines = []
            current_line = ""
            for word in words:
                test_line = (current_line + " " + word).strip()
                if len(test_line) <= max_chars_per_line:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)

            total_text_height = line_height * len(lines)
            text = "🔍 " + "\n".join(lines)

            if total_text_height <= rect.height:
                target_rect = rect
            else:
                target_rect = fitz.Rect(
                    rect.x0,
                    rect.y1 + 5,
                    rect.x1,
                    rect.y1 + 5 + total_text_height
                )

                # Draw yellow background for below text
                page.draw_rect(target_rect, color=(1, 0, 0), width=2.5)

            # Insert red text on yellow background
            page.insert_textbox(
                target_rect,
                text,
                fontsize=fontsize,
                fontname=fontname,
                color=(1, 0, 0),
                align=fitz.TEXT_ALIGN_LEFT,
                # overlay=True
            )

        except Exception as e:
            print(f"Error annotating page {page_number}: {e}")

    doc.save(output_path)
    doc.close()
    return output_path


# Usage Example
import random
def analyze_resume_with_genai(pdf_path: str, request):
    """Complete resume analysis using GenAI + Computer Vision"""
    
    analyzer = GenAIVisualAnalyzer('AIzaSyBuZYhHtZUJmwkQMzkPtHBBsTqudgzVClg')
    
    print("🔍 Starting comprehensive visual analysis...")
    print("1/4 Traditional computer vision analysis...")
    print("2/4 GenAI visual assessment...")
    print("3/4 Design critique...")
    print("4/4 Professional evaluation...")
    
    results = analyzer.analyze_resume_comprehensively(pdf_path)

    # Generate and display report
    report = analyzer.generate_detailed_report(results)
    print("############################")
    print(results)

    specific_issues = results["detailed_analysis"]["genai_visual"]["specific_issues"]

    result_pdf_url = None
    try:
        filename = f"{random.randint(1, 100000)}_annotated_resume.pdf"
        
        # Use your actual static folder path (filesystem) to save
        save_dir = os.path.join(settings.MEDIA_ROOT, 'result_resume')
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, filename)

        # Annotate and save PDF
        annotate_pdf_with_comments(pdf_path, save_path, specific_issues)

        # Build the URL to access the annotated PDF
        base_url = f"{request.scheme}://{request.get_host()}"
        result_pdf_url = f"{base_url}/media/result_resume/{filename}"

    except Exception as e:
        print(f"Error during PDF annotation: {e}")
        # fallback - no annotated PDF

    # Add the report and annotated PDF URL to results
    results['detailed_report'] = report
    results['annotated_pdf_url'] = result_pdf_url

    return results


# Example usage:
# results = analyze_resume_with_genai("Pawan Sapkota CV-Python.pdf")