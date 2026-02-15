"""
ATS Resume Analyzer - Enhanced with Rewriting Suggestions
Analyzes resumes and provides specific before/after improvements
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
    rewrite_suggestions: List[Dict[str, str]]  # New: Before/After suggestions


class ATSResumeAnalyzer:
    """Main class for analyzing resume ATS compatibility"""
    
    def __init__(self):
        """Initialize the ATS analyzer with optional spaCy model"""
        # Try to load spaCy model - make it optional for deployment
        self.nlp = None
        try:
            self.nlp = spacy.load("en_core_web_sm")
            print("✓ spaCy model loaded successfully")
        except:
            print("⚠ WARNING: spaCy model not found. Running with limited NLP features.")
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
            'tables': r'[│┌┐└┘├┤┬┴┼─]',
            'images': r'\[image\]|\[photo\]',
            'headers_footers': r'page\s+\d+\s+of\s+\d+',
            'special_chars': r'[★☆●○■□▪▫◆◇]',
        }
        
        # Critical keywords for different fields
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
        
        # Action verbs for rewriting
        self.action_verbs_by_category = {
            'leadership': ['led', 'managed', 'directed', 'supervised', 'coordinated', 'oversaw'],
            'achievement': ['achieved', 'exceeded', 'surpassed', 'accomplished', 'attained'],
            'creation': ['created', 'developed', 'designed', 'built', 'established', 'launched'],
            'improvement': ['improved', 'enhanced', 'optimized', 'streamlined', 'increased', 'boosted'],
            'analysis': ['analyzed', 'evaluated', 'assessed', 'examined', 'researched', 'investigated'],
            'communication': ['presented', 'communicated', 'collaborated', 'negotiated', 'facilitated'],
        }
    
    def analyze_resume(self, resume_text: str, target_job: str = None) -> ResumeScore:
        """Main analysis function that orchestrates all checks"""
        section_scores = {}
        recommendations = []
        strengths = []
        formatting_issues = []
        rewrite_suggestions = []
        
        # 1. Analyze sections
        sections_found = self._detect_sections(resume_text)
        section_scores['sections'] = self._score_sections(sections_found, recommendations, strengths)
        
        # 2. Analyze formatting
        formatting_issues = self._check_formatting(resume_text)
        section_scores['formatting'] = self._score_formatting(formatting_issues, recommendations)
        
        # 3. Analyze content quality and generate rewrites
        section_scores['content'] = self._score_content(resume_text, recommendations, strengths, rewrite_suggestions)
        
        # 4. Analyze keywords and suggest additions
        keyword_analysis = self._analyze_keywords(resume_text, target_job)
        section_scores['keywords'] = keyword_analysis['score']
        
        # Generate keyword insertion suggestions
        if keyword_analysis['missing_keywords']:
            self._generate_keyword_suggestions(resume_text, keyword_analysis, rewrite_suggestions)
            recommendations.append(
                f"Add relevant keywords: {', '.join(keyword_analysis['missing_keywords'][:5])}"
            )
        
        # 5. Check contact information
        contact_score = self._check_contact_info(resume_text, recommendations, rewrite_suggestions)
        section_scores['contact'] = contact_score
        
        # 6. Analyze length
        length_score = self._analyze_length(resume_text, recommendations, strengths)
        section_scores['length'] = length_score
        
        # 7. Generate section-specific rewrites
        self._generate_section_rewrites(resume_text, sections_found, rewrite_suggestions)
        
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
            formatting_issues=formatting_issues,
            rewrite_suggestions=rewrite_suggestions
        )
    
    def _generate_keyword_suggestions(self, text: str, keyword_analysis: Dict, 
                                     rewrite_suggestions: List[Dict]) -> None:
        """Generate suggestions for adding missing keywords"""
        missing = keyword_analysis['missing_keywords'][:3]
        industry = keyword_analysis['industry']
        
        if not missing:
            return
        
        # Find the skills section to suggest keyword additions
        skills_match = re.search(r'(SKILLS|TECHNICAL SKILLS|COMPETENCIES)(.*?)(?=\n[A-Z]{2,}|\Z)', 
                                text, re.IGNORECASE | re.DOTALL)
        
        if skills_match:
            current_skills = skills_match.group(2).strip()
            # Suggest adding missing keywords
            suggested_skills = current_skills + ", " + ", ".join(missing)
            
            rewrite_suggestions.append({
                'type': 'keywords',
                'section': 'Skills',
                'before': current_skills[:200] + ('...' if len(current_skills) > 200 else ''),
                'after': f"Consider adding: {', '.join(missing)}",
                'reason': f'These keywords are commonly sought in {industry} roles'
            })
    
    def _generate_section_rewrites(self, text: str, sections_found: Dict[str, bool],
                                   rewrite_suggestions: List[Dict]) -> None:
        """Generate missing section templates"""
        
        # If missing summary section
        if not sections_found.get('summary'):
            rewrite_suggestions.append({
                'type': 'missing_section',
                'section': 'Professional Summary',
                'before': '[No summary section found]',
                'after': 'PROFESSIONAL SUMMARY\nResults-driven [Your Title] with [X] years of experience in [Industry/Field]. Proven track record of [Key Achievement]. Skilled in [Top 3 Skills]. Seeking to leverage expertise in [Target Role].',
                'reason': 'A professional summary immediately captures recruiter attention and highlights your value proposition'
            })
        
        # If missing certifications section but it's relevant
        if not sections_found.get('certifications'):
            rewrite_suggestions.append({
                'type': 'missing_section',
                'section': 'Certifications',
                'before': '[No certifications section found]',
                'after': 'CERTIFICATIONS\n• [Certification Name] - [Issuing Organization] ([Year])\n• [Certification Name] - [Issuing Organization] ([Year])',
                'reason': 'Certifications demonstrate ongoing professional development and expertise'
            })
    
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
                      strengths: List[str], rewrite_suggestions: List[Dict]) -> float:
        """Score content quality and generate rewriting suggestions"""
        score = 50.0
        
        # Extract bullet points from experience section
        bullet_points = re.findall(r'[•\-\*]\s*(.+)', text)
        
        # Analyze each bullet point and suggest improvements
        weak_bullets = []
        for bullet in bullet_points[:5]:  # Analyze first 5 bullets
            if not re.search(r'^(Led|Managed|Developed|Created|Improved|Increased|Achieved|Designed|Implemented|Built|Established)', bullet, re.IGNORECASE):
                if len(bullet) > 20:  # Only suggest for substantial bullets
                    weak_bullets.append(bullet)
        
        # Generate specific rewrites for weak bullets
        for i, bullet in enumerate(weak_bullets[:3]):  # Top 3 weak bullets
            improved = self._improve_bullet_point(bullet)
            if improved != bullet:
                rewrite_suggestions.append({
                    'type': 'bullet_improvement',
                    'section': 'Experience',
                    'before': bullet,
                    'after': improved,
                    'reason': 'Starts with strong action verb and includes impact'
                })
        
        # Check for action verbs
        if self.nlp:
            doc = self.nlp(text)
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
        
        # Check for quantifiable achievements
        numbers = re.findall(r'\d+%|\$\d+|\d+\+', text)
        if len(numbers) > 5:
            score += 20
            strengths.append("Includes quantifiable achievements")
        elif len(numbers) > 0:
            score += 10
        else:
            recommendations.append("Add quantifiable achievements (e.g., 'Increased sales by 25%')")
            # Suggest adding metrics to existing bullets
            if bullet_points:
                sample_bullet = bullet_points[0]
                improved_with_metrics = self._add_metrics_to_bullet(sample_bullet)
                rewrite_suggestions.append({
                    'type': 'add_metrics',
                    'section': 'Experience',
                    'before': sample_bullet,
                    'after': improved_with_metrics,
                    'reason': 'Quantifiable metrics demonstrate concrete impact and results'
                })
        
        return min(score, 100.0)
    
    def _improve_bullet_point(self, bullet: str) -> str:
        """Improve a weak bullet point with action verbs and better structure"""
        bullet = bullet.strip()
        
        # If it starts with a weak verb or no verb, suggest improvement
        weak_starters = ['responsible for', 'worked on', 'helped with', 'duties included', 'involved in']
        
        for weak in weak_starters:
            if bullet.lower().startswith(weak):
                # Extract the core activity
                core = bullet[len(weak):].strip()
                # Choose appropriate action verb
                if 'team' in core.lower() or 'project' in core.lower():
                    return f"Led {core}"
                elif 'develop' in core.lower() or 'create' in core.lower():
                    return f"Developed {core}"
                elif 'improve' in core.lower() or 'enhance' in core.lower():
                    return f"Improved {core}"
                else:
                    return f"Managed {core}"
        
        # If doesn't start with action verb, add one
        if not re.match(r'^[A-Z][a-z]+ed', bullet):
            return f"Managed {bullet.lower()}"
        
        return bullet
    
    def _add_metrics_to_bullet(self, bullet: str) -> str:
        """Add sample metrics to a bullet point"""
        bullet = bullet.strip()
        
        # Add metric examples based on content
        if 'team' in bullet.lower():
            return f"{bullet}, resulting in 25% increase in productivity"
        elif 'sales' in bullet.lower() or 'revenue' in bullet.lower():
            return f"{bullet}, generating $500K in additional revenue"
        elif 'customer' in bullet.lower() or 'client' in bullet.lower():
            return f"{bullet}, improving customer satisfaction by 30%"
        elif 'process' in bullet.lower() or 'system' in bullet.lower():
            return f"{bullet}, reducing processing time by 40%"
        else:
            return f"{bullet}, achieving 20% improvement in key metrics"
    
    def _analyze_keywords(self, text: str, target_job: str = None) -> Dict:
        """Analyze keyword density and relevance"""
        text_lower = text.lower()
        detected_keywords = {}
        
        for industry, keywords in self.industry_keywords.items():
            matches = [kw for kw in keywords if kw in text_lower]
            detected_keywords[industry] = matches
        
        best_industry = max(detected_keywords.items(), key=lambda x: len(x[1]))
        
        if best_industry[1]:
            found_keywords = best_industry[1]
            all_keywords = self.industry_keywords[best_industry[0]]
            missing_keywords = [kw for kw in all_keywords if kw not in found_keywords]
            score = (len(found_keywords) / len(all_keywords)) * 100
        else:
            found_keywords = []
            missing_keywords = []
            score = 50.0
        
        return {
            'score': score,
            'found_keywords': found_keywords,
            'missing_keywords': missing_keywords[:10],
            'industry': best_industry[0] if best_industry[1] else 'general'
        }
    
    def _check_contact_info(self, text: str, recommendations: List[str],
                           rewrite_suggestions: List[Dict]) -> float:
        """Check for essential contact information"""
        score = 0.0
        
        # Email
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
            score += 40
        else:
            recommendations.append("Add a professional email address")
            rewrite_suggestions.append({
                'type': 'missing_contact',
                'section': 'Contact Information',
                'before': '[No email found]',
                'after': 'john.doe@email.com | (555) 123-4567 | linkedin.com/in/johndoe',
                'reason': 'Complete contact information ensures recruiters can reach you easily'
            })
        
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
        
        if 400 <= word_count <= 800:
            strengths.append("Appropriate length")
            return 100.0
        elif word_count < 400:
            recommendations.append("Resume seems too short - add more details about your experience")
            return 60.0
        else:
            recommendations.append("Resume may be too long - try to condense to 1-2 pages")
            return 70.0
