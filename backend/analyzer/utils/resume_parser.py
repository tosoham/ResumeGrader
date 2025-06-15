import os
import json
import httpx
import asyncio
from typing import Dict, Any, List, Optional
import PyPDF2
import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ResumeData:
    """Data class to structure parsed resume information"""
    personal_info: Dict[str, str]
    experience: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    skills: List[str]
    projects: List[Dict[str, Any]]
    raw_text: str

@dataclass
class GradingResult:
    """Data class for resume grading results"""
    overall_score: float
    section_scores: Dict[str, float]
    strengths: List[str]
    improvements: List[str]
    tips: List[str]
    detailed_feedback: str

class ResumeParser:
    """Resume parser using Sarvam AI for intelligent extraction and grading"""
    
    def __init__(self):
        self.sarvam_api_key = os.getenv("SARVAM_API_KEY")
        if not self.sarvam_api_key:
            logger.warning("SARVAM_API_KEY not found in environment variables")
        
        self.base_url = "https://api.sarvam.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.sarvam_api_key}",
            "Content-Type": "application/json"
        }
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text content from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
                
                return text.strip()
        
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    async def call_sarvam_api(self, prompt: str, max_tokens: int = 1000) -> str:
        """Make API call to Sarvam AI"""
        try:
            if not self.sarvam_api_key:
                logger.warning("No Sarvam API key provided, using enhanced fallback parsing")
                return await self._enhanced_fallback_parsing(prompt)
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                payload = {
                    "model": "sarvam-m",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a professional resume parser. Extract information accurately and return only valid JSON."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.1,
                    "response_format": {"type": "json_object"}
                }
                
                logger.info(f"Making Sarvam API call with model: {payload['model']}")
                
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    logger.error(f"Sarvam API error: {response.status_code} - {response.text}")
                    return await self._enhanced_fallback_parsing(prompt)
                
                result = response.json()
                api_response = result["choices"][0]["message"]["content"]
                logger.info("Successfully received Sarvam API response")
                return api_response
        
        except Exception as e:
            logger.error(f"Error calling Sarvam API: {str(e)}")
            return await self._enhanced_fallback_parsing(prompt)
    
    async def _enhanced_fallback_parsing(self, prompt: str) -> str:
        """Enhanced fallback parsing when API is not available"""
        logger.info("Using enhanced fallback parsing")
        
        text_start = prompt.find("Resume text:")
        if text_start != -1:
            resume_text = prompt[text_start + len("Resume text:"):].strip()
        else:
            resume_text = prompt
        
        if "extract personal information" in prompt.lower():
            return self._extract_personal_info_fallback(resume_text)
        elif "extract experience" in prompt.lower():
            return self._extract_experience_fallback(resume_text)
        elif "extract education" in prompt.lower():
            return self._extract_education_fallback(resume_text)
        elif "extract skills" in prompt.lower():
            return self._extract_skills_fallback(resume_text)
        elif "extract projects" in prompt.lower():
            return self._extract_projects_fallback(resume_text)
        else:
            return "Enhanced parsing not available for this prompt type"
    
    def _extract_personal_info_fallback(self, text: str) -> str:
        """Fallback personal info extraction using regex patterns"""
        import re
        
        personal_info = {}
        lines = text.split('\n')
        for line in lines[:5]:
            line = line.strip()
            if line and not any(keyword in line.lower() for keyword in ['email', 'phone', 'linkedin', 'github', 'address']):
                words = line.split()
                if 2 <= len(words) <= 4 and all(word.isalpha() or word.replace('.', '').isalpha() for word in words):
                    personal_info['name'] = line
                    break
        
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            personal_info['email'] = email_match.group()
        
        phone_pattern = r'[\+]?[1-9]?[0-9]{7,15}'
        phone_matches = re.findall(phone_pattern, text.replace('-', '').replace(' ', ''))
        if phone_matches:
            for phone in phone_matches:
                if 10 <= len(phone) <= 15:
                    personal_info['phone'] = phone
                    break
        
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin_match = re.search(linkedin_pattern, text.lower())
        if linkedin_match:
            personal_info['linkedin'] = linkedin_match.group()
        
        github_pattern = r'github\.com/[\w-]+'
        github_match = re.search(github_pattern, text.lower())
        if github_match:
            personal_info['github'] = github_match.group()
        
        location_keywords = ['kolkata', 'mumbai', 'delhi', 'bangalore', 'india', 'usa', 'city', 'state']
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in location_keywords):
                personal_info['address'] = line.strip()
                break
        
        return json.dumps(personal_info)
    
    def _extract_experience_fallback(self, text: str) -> str:
        """Fallback experience extraction"""
        import re
        
        experience = []
        lines = text.split('\n')
        
        current_exp = {}
        in_experience_section = False
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            if 'experience' in line.lower() and len(line) < 50:
                in_experience_section = True
                continue
            
            if in_experience_section and any(section in line.lower() for section in ['education', 'skills', 'projects', 'certifications']):
                if current_exp:
                    experience.append(current_exp)
                break
            
            if in_experience_section and line:
                if not line.startswith('◦') and not line.startswith('•') and len(line.split()) <= 8:
                    if current_exp:
                        experience.append(current_exp)
                    current_exp = {
                        'company': line,
                        'position': '',
                        'duration': '',
                        'description': '',
                        'key_achievements': []
                    }
                elif '–' in line or '-' in line:
                    parts = line.split('–') if '–' in line else line.split('-')
                    if len(parts) >= 2:
                        current_exp['duration'] = line
                elif line.startswith('◦') or line.startswith('•'):
                    current_exp['key_achievements'].append(line[1:].strip())
        
        if current_exp:
            experience.append(current_exp)
        
        return json.dumps(experience)
    
    def _extract_education_fallback(self, text: str) -> str:
        """Fallback education extraction"""
        education = []
        lines = text.split('\n')
        
        current_edu = {}
        in_education_section = False
        
        for line in lines:
            line = line.strip()
            
            if 'education' in line.lower() and len(line) < 50:
                in_education_section = True
                continue
            
            if in_education_section and any(section in line.lower() for section in ['experience', 'skills', 'projects', 'certifications']):
                if current_edu:
                    education.append(current_edu)
                break
            
            if in_education_section and line:
                if not line.startswith('◦') and not line.startswith('•') and 'gpa' not in line.lower():
                    if current_edu:
                        education.append(current_edu)
                    current_edu = {
                        'institution': line,
                        'degree': '',
                        'field_of_study': '',
                        'year': '',
                        'gpa': ''
                    }
                elif 'b.tech' in line.lower() or 'bachelor' in line.lower() or 'master' in line.lower():
                    current_edu['degree'] = line
                elif 'gpa' in line.lower():
                    current_edu['gpa'] = line
        
        if current_edu:
            education.append(current_edu)
        
        return json.dumps(education)
    
    def _extract_skills_fallback(self, text: str) -> str:
        """Fallback skills extraction"""
        skills = []
        
        tech_keywords = [
            'python', 'javascript', 'java', 'c++', 'react', 'node.js', 'django', 'flask',
            'html', 'css', 'sql', 'mongodb', 'postgresql', 'mysql', 'git', 'docker',
            'kubernetes', 'aws', 'azure', 'gcp', 'tensorflow', 'pytorch', 'pandas',
            'numpy', 'scikit-learn', 'machine learning', 'deep learning', 'data science',
            'fastapi', 'express', 'vue.js', 'angular', 'spring', 'hibernate'
        ]
        
        text_lower = text.lower()
        lines = text.split('\n')
        in_skills_section = False
        
        for line in lines:
            line_lower = line.lower().strip()
            
            if 'skills' in line_lower and len(line) < 50:
                in_skills_section = True
                continue
            
            if in_skills_section and any(section in line_lower for section in ['experience', 'education', 'projects', 'certifications']):
                break
            
            if in_skills_section:
                if line.startswith('◦') or line.startswith('•'):
                    skill_line = line[1:].strip()
                    for separator in [',', '•', '|', ';']:
                        skill_line = skill_line.replace(separator, ',')
                    extracted_skills = [s.strip() for s in skill_line.split(',') if s.strip()]
                    skills.extend(extracted_skills)
        
        for keyword in tech_keywords:
            if keyword in text_lower and keyword not in [s.lower() for s in skills]:
                skills.append(keyword.title())
        
        return json.dumps(list(set(skills)))  
    
    def _extract_projects_fallback(self, text: str) -> str:
        """Fallback projects extraction"""
        projects = []
        lines = text.split('\n')
        
        current_project = {}
        in_projects_section = False
        
        for line in lines:
            line = line.strip()
            
            if 'projects' in line.lower() and len(line) < 50:
                in_projects_section = True
                continue
            
            if in_projects_section and any(section in line.lower() for section in ['experience', 'education', 'skills', 'certifications']):
                if current_project:
                    projects.append(current_project)
                break
            
            if in_projects_section and line:
                if not line.startswith('◦') and not line.startswith('•'):
                    if current_project:
                        projects.append(current_project)
                    current_project = {
                        'name': line,
                        'description': '',
                        'technologies': [],
                        'duration': '',
                        'url': ''
                    }
                elif line.startswith('◦') or line.startswith('•'):
                    current_project['description'] += line[1:].strip() + ' '
        
        if current_project:
            projects.append(current_project)
        
        return json.dumps(projects)
    
    async def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """Parse resume and extract structured information"""
        try:
            raw_text = self.extract_text_from_pdf(file_path)
            
            if not raw_text.strip():
                raise Exception("No text content found in PDF")
            
            tasks = [
                self._extract_personal_info(raw_text),
                self._extract_experience(raw_text),
                self._extract_education(raw_text),
                self._extract_skills(raw_text),
                self._extract_projects(raw_text)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            personal_info, experience, education, skills, projects = results

            if isinstance(personal_info, Exception):
                personal_info = {}
            if isinstance(experience, Exception):
                experience = []
            if isinstance(education, Exception):
                education = []
            if isinstance(skills, Exception):
                skills = []
            if isinstance(projects, Exception):
                projects = []
            
            return {
                "personal_info": personal_info,
                "experience": experience,
                "education": education,
                "skills": skills,
                "projects": projects,
                "raw_text": raw_text[:1000] + "..." if len(raw_text) > 1000 else raw_text,
                "parsed_at": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}")
            raise Exception(f"Failed to parse resume: {str(e)}")
    
    async def _extract_personal_info(self, text: str) -> Dict[str, str]:
        """Extract personal information from resume text"""
        prompt = f"""
        Extract personal information from the following resume text and return it as a JSON object with these fields:
        - name
        - email
        - phone
        - address
        - linkedin
        - github
        
        Resume text:
        {text[:2000]}
        
        Return only valid JSON, no additional text.
        """
        
        try:
            response = await self.call_sarvam_api(prompt)
            return json.loads(response)
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Error parsing personal info: {str(e)}")
            return {}
    
    async def _extract_experience(self, text: str) -> List[Dict[str, Any]]:
        """Extract work experience from resume text"""
        prompt = f"""
        Extract work experience from the following resume text and return it as a JSON array with objects containing:
        - company
        - position
        - duration
        - description
        - key_achievements (array)
        
        Resume text:
        {text[:2000]}
        
        Return only valid JSON array, no additional text.
        """
        
        try:
            response = await self.call_sarvam_api(prompt)
            return json.loads(response)
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Error parsing experience: {str(e)}")
            return []
    
    async def _extract_education(self, text: str) -> List[Dict[str, Any]]:
        """Extract education information from resume text"""
        prompt = f"""
        Extract education information from the following resume text and return it as a JSON array with objects containing:
        - institution
        - degree
        - field_of_study
        - year
        - gpa (if available)
        
        Resume text:
        {text[:2000]}
        
        Return only valid JSON array, no additional text.
        """
        
        try:
            response = await self.call_sarvam_api(prompt)
            return json.loads(response)
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Error parsing education: {str(e)}")
            return []
    
    async def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text"""
        prompt = f"""
        Extract technical skills, programming languages, tools, and technologies from the following resume text.
        Return them as a JSON array of strings.
        
        Resume text:
        {text[:2000]}
        
        Return only valid JSON array, no additional text.
        """
        
        try:
            response = await self.call_sarvam_api(prompt)
            return json.loads(response)
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Error parsing skills: {str(e)}")
            return []
    
    async def _extract_projects(self, text: str) -> List[Dict[str, Any]]:
        """Extract projects from resume text"""
        prompt = f"""
        Extract projects from the following resume text and return it as a JSON array with objects containing:
        - name
        - description
        - technologies (array)
        - duration
        - url (if available)
        
        Resume text:
        {text[:2000]}
        
        Return only valid JSON array, no additional text.
        """
        
        try:
            response = await self.call_sarvam_api(prompt)
            return json.loads(response)
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Error parsing projects: {str(e)}")
            return []
    
    async def grade_resume(self, file_path: str) -> Dict[str, Any]:
        """Grade the resume and provide detailed feedback"""
        try:
            parsed_data = await self.parse_resume(file_path)
            scores = self._calculate_scores(parsed_data)
            feedback = self._generate_detailed_feedback(parsed_data, scores)
            if self.sarvam_api_key:
                try:
                    ai_feedback = await self._get_ai_feedback(parsed_data)
                    if ai_feedback and ai_feedback != "Enhanced parsing not available for this prompt type":
                        feedback['ai_feedback'] = ai_feedback
                except Exception as e:
                    logger.warning(f"AI feedback generation failed: {e}")
            
            grading_result = {
                "overall_score": scores['overall'],
                "section_scores": scores['sections'],
                "strengths": feedback['strengths'],
                "improvements": feedback['improvements'],
                "tips": feedback['tips'],
                "detailed_feedback": feedback['detailed'],
                "parsing_method": "enhanced_fallback" if not self.sarvam_api_key else "ai_assisted"
            }
            
            grading_result['parsed_data'] = parsed_data
            return grading_result
        
        except Exception as e:
            logger.error(f"Error grading resume: {str(e)}")
            raise Exception(f"Failed to grade resume: {str(e)}")
    
    def _calculate_scores(self, parsed_data: Dict) -> Dict[str, Any]:
        """Calculate scores based on parsed data quality"""
        scores = {
            'personal_info': 0,
            'experience': 0,
            'education': 0,
            'skills': 0,
            'projects': 0
        }

        personal = parsed_data.get('personal_info', {})
        if personal.get('name') and personal['name'] != 'Not available':
            scores['personal_info'] += 30
        if personal.get('email') and personal['email'] != 'Not available':
            scores['personal_info'] += 25
        if personal.get('phone') and personal['phone'] != 'Not available':
            scores['personal_info'] += 25
        if personal.get('linkedin') or personal.get('github'):
            scores['personal_info'] += 20
        
        experience = parsed_data.get('experience', [])
        if experience:
            scores['experience'] = min(100, len(experience) * 40)
            for exp in experience:
                if exp.get('key_achievements') and len(exp['key_achievements']) > 0:
                    scores['experience'] = min(100, scores['experience'] + 10)
        
        education = parsed_data.get('education', [])
        if education:
            scores['education'] = min(100, len(education) * 50)
            for edu in education:
                if edu.get('gpa'):
                    scores['education'] = min(100, scores['education'] + 15)
        
        skills = parsed_data.get('skills', [])
        if skills:
            scores['skills'] = min(100, len(skills) * 10)
        
        projects = parsed_data.get('projects', [])
        if projects:
            scores['projects'] = min(100, len(projects) * 33)
        
        overall = sum(scores.values()) / len(scores)
        
        return {
            'overall': round(overall, 1),
            'sections': scores
        }
    
    def _generate_detailed_feedback(self, parsed_data: Dict, scores: Dict) -> Dict[str, Any]:
        """Generate detailed feedback based on parsed data"""
        strengths = []
        improvements = []
        detailed_feedback = []
        tips = []
        
        personal = parsed_data.get('personal_info', {})
        if personal.get('name') and personal['name'] != 'Not available':
            strengths.append(f"Clear identification with name: {personal['name']}")
        if personal.get('email'):
            strengths.append("Professional contact information provided")
        if not personal.get('email') or personal.get('email') == 'Not available':
            improvements.append("Add professional email address")
            tips.append("Use a professional email format like firstname.lastname@domain.com instead of casual handles")
        if not personal.get('phone') or personal.get('phone') == 'Not available':
            improvements.append("Include phone number for contact")
            tips.append("Add your phone number in a consistent format (e.g., +91-XXXXX-XXXXX for Indian numbers)")
        if not personal.get('linkedin'):
            tips.append("Add your LinkedIn profile URL to increase professional visibility")
        if not personal.get('github') and len(parsed_data.get('skills', [])) > 0:
            tips.append("Include your GitHub profile to showcase coding projects and contributions")
        
        experience = parsed_data.get('experience', [])
        if experience:
            strengths.append(f"Has {len(experience)} work experience entries")
            detailed_feedback.append(f"Experience section shows {len(experience)} positions, demonstrating career progression.")
            has_quantified = False
            for exp in experience:
                achievements = exp.get('key_achievements', [])
                for achievement in achievements:
                    if any(char.isdigit() for char in str(achievement)):
                        has_quantified = True
                        break
                if has_quantified:
                    break
            
            if has_quantified:
                strengths.append("Experience includes quantified achievements")
            else:
                tips.append("Quantify your achievements with numbers, percentages, or specific outcomes (e.g., 'Increased efficiency by 30%' instead of 'Improved efficiency')")
            short_descriptions = 0
            for exp in experience:
                achievements = exp.get('key_achievements', [])
                if len(achievements) < 2:
                    short_descriptions += 1
            
            if short_descriptions > 0:
                tips.append("Add 2-3 bullet points for each role highlighting key responsibilities and achievements")
        else:
            improvements.append("Add work experience or internships to strengthen profile")
            tips.append("Include internships, part-time jobs, freelance work, or volunteer positions to show practical experience")
        
        education = parsed_data.get('education', [])
        if education:
            strengths.append("Educational background clearly presented")
            has_gpa = False
            for edu in education:
                if 'gpa' in str(edu).lower():
                    strengths.append("Academic performance (GPA) included")
                    has_gpa = True
                    break
            
            if not has_gpa:
                tips.append("Consider adding GPA if it's 3.5 or above, or relevant coursework if applicable")
        else:
            improvements.append("Include educational qualifications")
            tips.append("Add your degree, institution, graduation year, and relevant coursework or academic achievements")
        
        skills = parsed_data.get('skills', [])
        if len(skills) > 10:
            strengths.append(f"Comprehensive skills list with {len(skills)} technical skills")
            tips.append("Consider grouping skills by category (e.g., Programming Languages, Frameworks, Tools) for better organization")
        elif len(skills) > 5:
            strengths.append(f"Good technical skills coverage with {len(skills)} skills listed")
        elif len(skills) > 0:
            improvements.append("Expand technical skills section with more relevant technologies")
            tips.append("Add more skills relevant to your target role - include programming languages, frameworks, tools, and soft skills")
        else:
            improvements.append("Add technical skills relevant to your field")
            tips.append("Create a skills section with technical abilities like programming languages, software tools, and relevant certifications")
        
        soft_skill_keywords = ['leadership', 'communication', 'teamwork', 'problem-solving', 'analytical']
        has_soft_skills = any(skill.lower() in soft_skill_keywords for skill in skills)
        if not has_soft_skills:
            tips.append("Consider adding soft skills like leadership, communication, or problem-solving alongside technical skills")
        
        
        projects = parsed_data.get('projects', [])
        if projects:
            strengths.append(f"Showcases {len(projects)} projects demonstrating practical experience")
            
            
            projects_with_tech = sum(1 for p in projects if p.get('technologies'))
            projects_with_urls = sum(1 for p in projects if p.get('url'))
            
            if projects_with_tech < len(projects):
                tips.append("Add technology stack details for each project to highlight technical expertise")
            
            if projects_with_urls == 0:
                tips.append("Include GitHub links or live demo URLs for your projects to allow recruiters to see your work")
            
            if len(projects) < 3:
                tips.append("Consider adding 2-3 significant projects that showcase different skills and technologies")
        else:
            improvements.append("Add personal or academic projects to demonstrate practical skills")
            tips.append("Create 2-3 projects showcasing your skills - include project name, description, technologies used, and GitHub/demo links")
        
    
        overall_score = scores['overall']
        if overall_score >= 80:
            detailed_feedback.append("Excellent resume with comprehensive information across all sections.")
            tips.append("Fine-tune formatting and ensure consistent styling throughout the document")
        elif overall_score >= 60:
            detailed_feedback.append("Good resume foundation with room for enhancement in specific areas.")
            tips.append("Focus on adding more specific details and quantified achievements to stand out")
        else:
            detailed_feedback.append("Resume needs significant improvement in multiple sections.")
            tips.append("Start by ensuring all basic sections (contact info, experience, education, skills) are complete and well-detailed")
        
        if len(tips) < 3:
            tips.extend([
                "Use action verbs to start bullet points (e.g., 'Developed', 'Implemented', 'Managed')",
                "Keep your resume to 1-2 pages and use consistent formatting throughout",
                "Tailor your resume for each job application by highlighting relevant skills and experience"
            ])
        
        tips = tips[:8] 
        
        return {
            'strengths': strengths,
            'improvements': improvements,
            'detailed': ' '.join(detailed_feedback),
            'tips': tips
        }
    
    async def _get_ai_feedback(self, parsed_data: Dict) -> str:
        """Get AI-powered feedback using Sarvam API"""
        prompt = f"""
        Analyze this resume data and provide professional feedback in 2-3 sentences:
        
        Personal Info: {json.dumps(parsed_data.get('personal_info', {}))}
        Experience: {len(parsed_data.get('experience', []))} entries
        Education: {len(parsed_data.get('education', []))} entries  
        Skills: {len(parsed_data.get('skills', []))} skills listed
        Projects: {len(parsed_data.get('projects', []))} projects
        
        Provide specific, actionable feedback for improvement.
        """
        
        try:
            return await self.call_sarvam_api(prompt, max_tokens=200)
        except Exception as e:
            logger.error(f"AI feedback generation failed: {e}")
            return "AI feedback not available"
        