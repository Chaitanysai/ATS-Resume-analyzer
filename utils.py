"""
Utility scripts for ATS Resume Analyzer
Includes setup helpers and testing functions
"""

import os
import sys


def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        'flask',
        'spacy',
        'PyPDF2',
        'docx',
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} installed")
        except ImportError:
            print(f"✗ {package} NOT installed")
            missing_packages.append(package)
    
    # Check spaCy model
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("✓ spaCy model 'en_core_web_sm' installed")
    except:
        print("✗ spaCy model 'en_core_web_sm' NOT installed")
        print("  Run: python -m spacy download en_core_web_sm")
        missing_packages.append('spacy-model')
    
    if missing_packages:
        print(f"\n❌ Missing {len(missing_packages)} dependencies")
        print("Run: pip install -r requirements.txt")
        print("Then: python -m spacy download en_core_web_sm")
        return False
    else:
        print("\n✅ All dependencies installed!")
        return True


def create_sample_resume():
    """Create a sample resume for testing"""
    sample_text = """
JANE DOE
jane.doe@email.com | (555) 987-6543 | linkedin.com/in/janedoe | New York, NY

PROFESSIONAL SUMMARY
Results-driven Marketing Manager with 8+ years of experience in digital marketing, 
content strategy, and team leadership. Proven track record of increasing brand 
awareness by 150% and driving ROI through data-driven campaigns.

PROFESSIONAL EXPERIENCE

Senior Marketing Manager | TechCorp Inc. | Jan 2020 - Present
• Led team of 10 marketing professionals in executing comprehensive digital campaigns
• Increased website traffic by 200% and conversion rates by 45% through SEO optimization
• Managed annual marketing budget of $2M, achieving 30% cost reduction while improving results
• Implemented marketing automation system, reducing manual tasks by 60%
• Developed content strategy that generated 500+ qualified leads per month

Marketing Specialist | Digital Solutions LLC | Jun 2016 - Dec 2019
• Created and executed social media campaigns reaching 2M+ users monthly
• Improved email marketing open rates from 15% to 35% through A/B testing
• Collaborated with sales team to generate $5M in new business revenue
• Managed Google Ads campaigns with average ROI of 400%

EDUCATION

Master of Business Administration (MBA) | New York University | 2016
Bachelor of Arts in Marketing | Boston University | 2014

SKILLS

Technical: Google Analytics, SEO/SEM, HubSpot, Salesforce, Adobe Creative Suite, 
HTML/CSS, WordPress, Email Marketing Platforms (Mailchimp, Constant Contact)

Marketing: Content Marketing, Social Media Marketing, Campaign Management, 
Marketing Automation, Brand Strategy, Market Research, Analytics & Reporting

Soft Skills: Team Leadership, Project Management, Strategic Planning, 
Communication, Problem Solving

CERTIFICATIONS

• Google Analytics Certified
• HubSpot Inbound Marketing Certification
• Facebook Blueprint Certification
• Project Management Professional (PMP)

ACHIEVEMENTS

• Awarded "Marketing Professional of the Year" 2022
• Speaker at Digital Marketing Summit 2021
• Published article in Marketing Today Magazine
"""
    
    # Create sample resume file
    filename = "sample_resume.txt"
    with open(filename, 'w') as f:
        f.write(sample_text)
    
    print(f"✓ Sample resume created: {filename}")
    return filename


def test_analyzer():
    """Test the ATS analyzer with sample resume"""
    try:
        from ats_analyzer import ATSResumeAnalyzer
        
        # Create sample resume
        filename = create_sample_resume()
        
        # Read sample
        with open(filename, 'r') as f:
            resume_text = f.read()
        
        # Analyze
        analyzer = ATSResumeAnalyzer()
        results = analyzer.analyze_resume(resume_text)
        
        # Display results
        print("\n" + "="*60)
        print("ANALYSIS RESULTS")
        print("="*60)
        print(f"\n📊 Total Score: {results.total_score}/100")
        
        print("\n📈 Section Scores:")
        for section, score in results.section_scores.items():
            print(f"  • {section.title()}: {score:.1f}/100")
        
        print(f"\n💡 Recommendations ({len(results.recommendations)}):")
        for i, rec in enumerate(results.recommendations, 1):
            print(f"  {i}. {rec}")
        
        print(f"\n✅ Strengths ({len(results.strengths)}):")
        for i, strength in enumerate(results.strengths, 1):
            print(f"  {i}. {strength}")
        
        print(f"\n🔑 Keywords Analysis:")
        print(f"  Industry: {results.keyword_analysis.get('industry', 'N/A')}")
        print(f"  Found: {len(results.keyword_analysis.get('found_keywords', []))} keywords")
        print(f"  Missing: {len(results.keyword_analysis.get('missing_keywords', []))} keywords")
        
        print("\n" + "="*60)
        
        # Cleanup
        os.remove(filename)
        print(f"\n✓ Test completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        return False


def setup_environment():
    """Complete setup check"""
    print("="*60)
    print("ATS RESUME ANALYZER - SETUP CHECK")
    print("="*60)
    print()
    
    # Check Python version
    print(f"Python version: {sys.version.split()[0]}")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher required!")
        return False
    print("✓ Python version OK")
    print()
    
    # Check dependencies
    print("Checking dependencies...")
    if not check_dependencies():
        return False
    print()
    
    # Create necessary directories
    print("Creating directories...")
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    print("✓ Directories created")
    print()
    
    return True


def main():
    """Main utility function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ATS Resume Analyzer Utilities')
    parser.add_argument('command', choices=['check', 'test', 'setup', 'sample'],
                       help='Command to run')
    
    args = parser.parse_args()
    
    if args.command == 'check':
        check_dependencies()
    elif args.command == 'test':
        if check_dependencies():
            test_analyzer()
    elif args.command == 'setup':
        if setup_environment():
            print("\n✅ Setup complete! You can now run: python app.py")
    elif args.command == 'sample':
        create_sample_resume()


if __name__ == '__main__':
    # If no arguments, run setup
    if len(sys.argv) == 1:
        if setup_environment():
            print("\nWould you like to run a test? (y/n)")
            response = input().lower()
            if response == 'y':
                test_analyzer()
    else:
        main()
