# ATS Resume Analyzer

A comprehensive AI-powered tool that analyzes resumes for ATS (Applicant Tracking System) compatibility and provides actionable feedback to improve job application success rates.

## Features

- 📄 **Multi-Format Support**: Analyzes PDF and DOCX resumes
- 🎯 **Comprehensive Scoring**: Evaluates 6 key areas with detailed breakdown
- 🔍 **Keyword Analysis**: Detects industry-relevant keywords and suggests missing ones
- ✅ **Section Detection**: Ensures all essential resume sections are present
- 📊 **Visual Dashboard**: Beautiful, responsive web interface with real-time results
- 💡 **Actionable Recommendations**: Specific suggestions for improvement
- 🎨 **Formatting Check**: Identifies ATS-incompatible formatting issues

## Scoring Categories

1. **Resume Sections** (25%) - Presence of essential sections
2. **Formatting** (20%) - ATS-friendly formatting
3. **Content Quality** (20%) - Use of action verbs and quantifiable achievements
4. **Keywords** (20%) - Industry-relevant keyword density
5. **Contact Information** (10%) - Complete contact details
6. **Length** (5%) - Appropriate resume length

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone or Download

```bash
# If using git
git clone <repository-url>
cd ats-resume-analyzer

# Or download and extract the ZIP file
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Download spaCy Language Model

```bash
python -m spacy download en_core_web_sm
```

## Usage

### Starting the Web Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### Using the Web Interface

1. Open your browser and navigate to `http://localhost:5000`
2. Upload your resume (PDF or DOCX format)
3. Optionally paste a job description for targeted keyword analysis
4. Click "Analyze Resume"
5. Review your results and recommendations

### Using as a Python Module

```python
from resume_parser import ResumeParser
from ats_analyzer import ATSResumeAnalyzer

# Initialize
parser = ResumeParser()
analyzer = ATSResumeAnalyzer()

# Parse resume
resume_text = parser.parse_resume("path/to/resume.pdf")

# Analyze
results = analyzer.analyze_resume(resume_text)

# Access results
print(f"Total Score: {results.total_score}/100")
print(f"Recommendations: {results.recommendations}")
print(f"Strengths: {results.strengths}")
```

## Project Structure

```
ats-resume-analyzer/
├── app.py                  # Flask web application
├── resume_parser.py        # Resume text extraction
├── ats_analyzer.py         # Core analysis engine
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html         # Web interface
├── uploads/               # Temporary file storage (auto-created)
└── README.md             # This file
```

## API Endpoints

### POST /upload
Upload and analyze a resume file

**Request:**
- Form data with 'resume' file
- Optional 'job_description' field

**Response:**
```json
{
  "success": true,
  "total_score": 85.5,
  "grade": "B",
  "section_scores": {...},
  "recommendations": [...],
  "strengths": [...],
  "keyword_analysis": {...}
}
```

### POST /api/analyze-text
Analyze resume text directly (no file upload)

**Request:**
```json
{
  "text": "Resume text content...",
  "job_description": "Optional job description..."
}
```

## Customization

### Adding Industry Keywords

Edit `ats_analyzer.py` and add keywords to the `industry_keywords` dictionary:

```python
self.industry_keywords = {
    'software': ['python', 'java', 'javascript', ...],
    'your_industry': ['keyword1', 'keyword2', ...],
}
```

### Adjusting Scoring Weights

Modify the weights in the `analyze_resume` method:

```python
weights = {
    'sections': 0.25,
    'formatting': 0.20,
    'content': 0.20,
    'keywords': 0.20,
    'contact': 0.10,
    'length': 0.05
}
```

### Customizing Section Patterns

Update `section_patterns` in `ats_analyzer.py` to recognize different section headers:

```python
self.section_patterns = {
    'experience': [r'experience', r'work\s+history', r'your_pattern'],
}
```

## Troubleshooting

### Issue: "spaCy model not found"
**Solution:** Run `python -m spacy download en_core_web_sm`

### Issue: "Module not found"
**Solution:** Ensure you're in the virtual environment and run `pip install -r requirements.txt`

### Issue: "Cannot extract text from PDF"
**Solution:** 
- Ensure the PDF is not password-protected
- Try converting to DOCX format
- Check if the PDF contains actual text (not scanned images)

### Issue: "File too large"
**Solution:** The limit is 10MB. Compress your PDF or remove unnecessary images.

## Best Practices for Users

1. **Use Clean Formatting**: Avoid tables, text boxes, headers/footers
2. **Include Keywords**: Match job description terminology
3. **Use Standard Sections**: Work Experience, Education, Skills, etc.
4. **Add Contact Info**: Email, phone, LinkedIn
5. **Quantify Achievements**: Use numbers and percentages
6. **Use Action Verbs**: Start bullet points with strong verbs
7. **Keep It Concise**: 1-2 pages for most positions

## Technology Stack

- **Backend**: Flask (Python web framework)
- **NLP**: spaCy (natural language processing)
- **PDF Processing**: PyPDF2
- **DOCX Processing**: python-docx
- **Frontend**: HTML5, Bootstrap 5, JavaScript
- **Analysis**: Custom scoring algorithms

## Performance

- Average analysis time: 2-5 seconds
- Supported file size: Up to 10MB
- Concurrent users: Supports multiple simultaneous analyses

## Future Enhancements

- [ ] Support for more file formats (TXT, RTF)
- [ ] Machine learning-based scoring
- [ ] Comparison with successful resumes
- [ ] Export detailed reports as PDF
- [ ] Chrome extension for quick analysis
- [ ] Resume template suggestions
- [ ] Multi-language support
- [ ] Job description matching score

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is available for educational and personal use.

## Support

For issues, questions, or suggestions:
1. Check the Troubleshooting section
2. Review existing issues on GitHub
3. Create a new issue with detailed information

## Acknowledgments

- spaCy for NLP capabilities
- Bootstrap for UI components
- Flask framework for web application structure

---

**Note**: This tool provides suggestions for improvement but should be used as a guide. Always review and customize your resume for specific job applications.
