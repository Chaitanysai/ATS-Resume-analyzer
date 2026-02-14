"""
ATS Resume Analyzer - Core Module
Analyzes resumes for ATS compatibility and provides scoring/recommendations
"""

import re
import spacy
from typing import Dict, List, Tuple
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class ResumeScore:
    """Data class to hold resume analysis results"""
    total_score: float
    section_scores: Dict[str, float]
    recommendations: List[str]
    strengths: List[str]
    keyword_analysis: Dict[str, any]
    formatting_issues: List[str]


class ATSResumeAnalyzer:
    """Main class for analyzing resume ATS compatibility"""
    
    def __init__(self):
    # Load spaCy model - make it optional for deployment
    self.nlp = None
    try:
        import spacy
        self.nlp = spacy.load("en_core_web_sm")
    except:
        # Model not found, try to download
        try:
            import spacy.cli
            spacy.cli.download("en_core_web_sm")
            import spacy
            self.nlp = spacy.load("en_core_web_sm")
        except:
            # If download fails, continue without NLP (limited features)
            print("WARNING: spaCy model not available. Running with limited NLP features.")
            self.nlp = None
        
        # Define ATS-friendly section headers
        self.section_patterns = {
            'contact': [r'contact', r'personal\s+information', r'phone', r'email'],
            'summary': [r'summary', r'objective', r'profile', r'about\s+me'],
            'experience': [r'experience', r'work\s+history', r'employment', r'professional\s+experience'],
            'education': [r'education', r'academic', r'qualifications', r'degrees'],
            'skills': [r'skills', r'technical\s+skills', r'competencies', r'expertise'],
            'certifications': [r'certification', r'licenses', r'credentials'],
            'projects': [r'projects', r'portfolio'],
        }
        
        # Common ATS-unfriendly formatting
        self.formatting_issues_patterns = {
            'tables': r'[│┌┐└┘├┤┬┴┼─]',  # Table characters
            'images': r'\[image\]|\[photo\]',
            'headers_footers': r'page\s+\d+\s+of\s+\d+',
            'special_chars': r'[★☆●○■□▪▫◆◇]',  # Bullets that might cause issues
        }
        
        # Critical keywords for different fields (expandable)
        self.industry_keywords = {
            'software': ['python', 'java', 'javascript', 'react', 'sql', 'aws', 'docker', 
                        'kubernetes', 'agile', 'api', 'git', 'ci/cd'],
            'data_science': ['python', 'r', 'machine learning', 'deep learning', 'tensorflow',
                           'pytorch', 'sql', 'pandas', 'numpy', 'statistics'],
            'marketing': ['seo', 'sem', 'analytics', 'content marketing', 'social media',
                         'google analytics', 'campaign management', 'roi'],
            'finance': ['financial analysis', 'excel', 'accounting', 'budgeting', 'forecasting',
                       'gaap', 'financial modeling', 'quickbooks'],
        }
    
    def analyze_resume(self, resume_text: str, target_job: str = None) -> ResumeScore:
        """
        Main analysis function that orchestrates all checks
        
        Args:
            resume_text: Extracted text from resume
            target_job: Optional job description or field for targeted analysis
            
        Returns:
            ResumeScore object with detailed analysis
        """
        section_scores = {}
        recommendations = []
        strengths = []
        formatting_issues = []
        
        # 1. Analyze sections
        sections_found = self._detect_sections(resume_text)
        section_scores['sections'] = self._score_sections(sections_found, recommendations, strengths)
        
        # 2. Analyze formatting
        formatting_issues = self._check_formatting(resume_text)
        section_scores['formatting'] = self._score_formatting(formatting_issues, recommendations)
        
        # 3. Analyze content quality
        section_scores['content'] = self._score_content(resume_text, recommendations, strengths)
        
        # 4. Analyze keywords
        keyword_analysis = self._analyze_keywords(resume_text, target_job)
        section_scores['keywords'] = keyword_analysis['score']
        
        if keyword_analysis['missing_keywords']:
            recommendations.append(
                f"Add relevant keywords: {', '.join(keyword_analysis['missing_keywords'][:5])}"
            )
        
        # 5. Check contact information
        contact_score = self._check_contact_info(resume_text, recommendations)
        section_scores['contact'] = contact_score
        
        # 6. Analyze length
        length_score = self._analyze_length(resume_text, recommendations, strengths)
        section_scores['length'] = length_score
        
        # Calculate total score (weighted average)
        weights = {
            'sections': 0.25,
            'formatting': 0.20,
            'content': 0.20,
            'keywords': 0.20,
            'contact': 0.10,
            'length': 0.05
        }
        
        total_score = sum(section_scores[key] * weights[key] for key in weights.keys())
        total_score = round(total_score, 1)
        
        return ResumeScore(
            total_score=total_score,
            section_scores=section_scores,
            recommendations=recommendations,
            strengths=strengths,
            keyword_analysis=keyword_analysis,
            formatting_issues=formatting_issues
        )
    
    def _detect_sections(self, text: str) -> Dict[str, bool]:
        """Detect which standard resume sections are present"""
        text_lower = text.lower()
        sections_found = {}
        
        for section, patterns in self.section_patterns.items():
            found = any(re.search(pattern, text_lower) for pattern in patterns)
            sections_found[section] = found
        
        return sections_found
    
    def _score_sections(self, sections_found: Dict[str, bool], 
                       recommendations: List[str], strengths: List[str]) -> float:
        """Score based on presence of essential sections"""
        essential_sections = ['contact', 'experience', 'education', 'skills']
        recommended_sections = ['summary', 'certifications']
        
        score = 0.0
        found_count = sum(1 for section in essential_sections if sections_found.get(section))
        
        # Essential sections worth 80 points
        score += (found_count / len(essential_sections)) * 80
        
        # Recommended sections worth 20 points
        recommended_count = sum(1 for section in recommended_sections if sections_found.get(section))
        score += (recommended_count / len(recommended_sections)) * 20
        
        # Generate recommendations
        missing_essential = [s for s in essential_sections if not sections_found.get(s)]
        if missing_essential:
            recommendations.append(
                f"Add missing essential sections: {', '.join(missing_essential).title()}"
            )
        
        missing_recommended = [s for s in recommended_sections if not sections_found.get(s)]
        if missing_recommended:
            recommendations.append(
                f"Consider adding: {', '.join(missing_recommended).title()} section"
            )
        
        if found_count == len(essential_sections):
            strengths.append("All essential sections present")
        
        return score
    
    def _check_formatting(self, text: str) -> List[str]:
        """Check for ATS-unfriendly formatting"""
        issues = []
        
        for issue_type, pattern in self.formatting_issues_patterns.items():
            if re.search(pattern, text):
                issues.append(issue_type)
        
        # Check for excessive special characters
        special_char_count = len(re.findall(r'[^a-zA-Z0-9\s\.,;:\-\(\)\[\]\/]', text))
        if special_char_count > 50:
            issues.append('excessive_special_characters')
        
        return issues
    
    def _score_formatting(self, issues: List[str], recommendations: List[str]) -> float:
        """Score formatting ATS-compatibility"""
        if not issues:
            return 100.0
        
        # Each issue deducts points
        score = 100.0 - (len(issues) * 15)
        score = max(score, 0.0)
        
        if 'tables' in issues:
            recommendations.append("Remove tables - use simple bullet points instead")
        if 'images' in issues:
            recommendations.append("Remove images/photos - ATS cannot parse them")
        if 'special_chars' in issues:
            recommendations.append("Use standard bullet points (•, -, *) instead of special characters")
        if 'excessive_special_characters' in issues:
            recommendations.append("Reduce use of special characters and symbols")
        
        return score
    
    def _score_content(self, text: str, recommendations: List[str], 
                  strengths: List[str]) -> float:
    """Score content quality using NLP"""
    score = 50.0  # Base score
    
        if not self.nlp:
            return score
        
        doc = self.nlp(text)
        
        # Check for action verbs (stronger resumes use them)
        action_verbs = ['led', 'managed', 'developed', 'created', 'improved', 
                       'increased', 'decreased', 'designed', 'implemented', 'achieved']
        
        action_verb_count = sum(1 for token in doc if token.lemma_ in action_verbs)
        
        if action_verb_count > 10:
            score += 30
            strengths.append("Good use of action verbs")
        elif action_verb_count > 5:
            score += 15
        else:
            recommendations.append("Use more action verbs (e.g., 'Led', 'Managed', 'Developed')")
        
        # Check for quantifiable achievements (numbers)
        numbers = re.findall(r'\d+%|\$\d+|\d+\+', text)
        if len(numbers) > 5:
            score += 20
            strengths.append("Includes quantifiable achievements")
        elif len(numbers) > 0:
            score += 10
        else:
            recommendations.append("Add quantifiable achievements (e.g., 'Increased sales by 25%')")
        
        return min(score, 100.0)
    
    def _analyze_keywords(self, text: str, target_job: str = None) -> Dict:
        """Analyze keyword density and relevance"""
        text_lower = text.lower()
        
        # Auto-detect industry or use target job
        detected_keywords = {}
        
        for industry, keywords in self.industry_keywords.items():
            matches = [kw for kw in keywords if kw in text_lower]
            detected_keywords[industry] = matches
        
        # Find the best matching industry
        best_industry = max(detected_keywords.items(), key=lambda x: len(x[1]))
        
        if best_industry[1]:  # If any keywords found
            found_keywords = best_industry[1]
            all_keywords = self.industry_keywords[best_industry[0]]
            missing_keywords = [kw for kw in all_keywords if kw not in found_keywords]
            
            score = (len(found_keywords) / len(all_keywords)) * 100
        else:
            found_keywords = []
            missing_keywords = []
            score = 50.0  # Neutral score if no industry detected
        
        return {
            'score': score,
            'found_keywords': found_keywords,
            'missing_keywords': missing_keywords[:10],  # Top 10 missing
            'industry': best_industry[0] if best_industry[1] else 'general'
        }
    
    def _check_contact_info(self, text: str, recommendations: List[str]) -> float:
        """Check for essential contact information"""
        score = 0.0
        
        # Email
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
            score += 40
        else:
            recommendations.append("Add a professional email address")
        
        # Phone
        if re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text):
            score += 30
        else:
            recommendations.append("Add phone number")
        
        # LinkedIn or professional link
        if re.search(r'linkedin\.com|github\.com|portfolio', text.lower()):
            score += 30
        else:
            recommendations.append("Consider adding LinkedIn or GitHub profile")
        
        return score
    
    def _analyze_length(self, text: str, recommendations: List[str], 
                       strengths: List[str]) -> float:
        """Analyze resume length"""
        word_count = len(text.split())
        
        if 400 <= word_count <= 800:  # Optimal length (1-2 pages)
            strengths.append("Appropriate length")
            return 100.0
        elif word_count < 400:
            recommendations.append("Resume seems too short - add more details about your experience")
            return 60.0
        else:
            recommendations.append("Resume may be too long - try to condense to 1-2 pages")
            return 70.0


# Example usage
if __name__ == "__main__":
    # Sample resume text
    sample_resume = """
    John Doe
    john.doe@email.com | (555) 123-4567 | linkedin.com/in/johndoe
    
    PROFESSIONAL SUMMARY
    Experienced Software Engineer with 5+ years developing scalable applications.
    
    EXPERIENCE
    Senior Software Engineer | Tech Corp | 2020-Present
    • Led team of 5 developers in building microservices architecture
    • Improved application performance by 40% through code optimization
    • Implemented CI/CD pipeline using Docker and Kubernetes
    
    EDUCATION
    BS in Computer Science | University Name | 2018
    
    SKILLS
    Python, Java, JavaScript, React, AWS, Docker, SQL
    """
    
    analyzer = ATSResumeAnalyzer()
    results = analyzer.analyze_resume(sample_resume)
    
    print(f"Total Score: {results.total_score}/100")
    print(f"\nSection Scores: {results.section_scores}")
    print(f"\nRecommendations:")
    for rec in results.recommendations:
        print(f"  - {rec}")
    print(f"\nStrengths:")
    for strength in results.strengths:
        print(f"  ✓ {strength}")
