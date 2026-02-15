"""
Flask Web Application for ATS Resume Analyzer
Provides web interface for uploading and analyzing resumes
"""

from flask import Flask, request, render_template, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
import json
from datetime import datetime

from resume_parser import ResumeParser
from ats_analyzer import ATSResumeAnalyzer

app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx', 'doc'}

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize parsers
resume_parser = ResumeParser()
ats_analyzer = ATSResumeAnalyzer()


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def get_score_color(score):
    """Return color based on score"""
    if score >= 80:
        return 'success'
    elif score >= 60:
        return 'warning'
    else:
        return 'danger'


def get_score_grade(score):
    """Return letter grade based on score"""
    if score >= 90:
        return 'A'
    elif score >= 80:
        return 'B'
    elif score >= 70:
        return 'C'
    elif score >= 60:
        return 'D'
    else:
        return 'F'


@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_resume():
    """Handle resume upload and analysis"""
    
    # Check if file is present
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['resume']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': f'Invalid file type. Allowed: {", ".join(app.config["ALLOWED_EXTENSIONS"])}'}), 400
    
    try:
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        # Parse resume
        resume_text = resume_parser.parse_resume(filepath)
        
        if not resume_text or len(resume_text.strip()) < 50:
            os.remove(filepath)  # Clean up
            return jsonify({'error': 'Could not extract text from resume. Please ensure the file is not corrupted.'}), 400
        
        # Get optional job description
        target_job = request.form.get('job_description', None)
        
        # Analyze resume
        analysis_result = ats_analyzer.analyze_resume(resume_text, target_job)
        
        # Get metadata
        metadata = resume_parser.extract_metadata(filepath)
        
        # Clean up uploaded file
        os.remove(filepath)
        
        # Prepare response
        response = {
            'success': True,
            'filename': filename,
            'metadata': metadata,
            'total_score': analysis_result.total_score,
            'grade': get_score_grade(analysis_result.total_score),
            'score_color': get_score_color(analysis_result.total_score),
            'section_scores': analysis_result.section_scores,
            'recommendations': analysis_result.recommendations,
            'strengths': analysis_result.strengths,
            'keyword_analysis': {
                'industry': analysis_result.keyword_analysis.get('industry', 'general'),
                'found_keywords': analysis_result.keyword_analysis.get('found_keywords', []),
                'missing_keywords': analysis_result.keyword_analysis.get('missing_keywords', [])[:5]
            },
            'formatting_issues': analysis_result.formatting_issues,
            'word_count': len(resume_text.split()),
            'rewrite_suggestions': analysis_result.rewrite_suggestions  # New field
        }
        
        return jsonify(response)
    
    except Exception as e:
        # Clean up file if it exists
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return jsonify({'error': f'Error processing resume: {str(e)}'}), 500


@app.route('/api/analyze-text', methods=['POST'])
def analyze_text():
    """API endpoint for analyzing resume text directly"""
    
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    
    resume_text = data['text']
    target_job = data.get('job_description', None)
    
    if len(resume_text.strip()) < 50:
        return jsonify({'error': 'Text too short to analyze'}), 400
    
    try:
        # Analyze resume
        analysis_result = ats_analyzer.analyze_resume(resume_text, target_job)
        
        # Prepare response
        response = {
            'success': True,
            'total_score': analysis_result.total_score,
            'grade': get_score_grade(analysis_result.total_score),
            'section_scores': analysis_result.section_scores,
            'recommendations': analysis_result.recommendations,
            'strengths': analysis_result.strengths,
            'keyword_analysis': analysis_result.keyword_analysis
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': f'Error analyzing text: {str(e)}'}), 500


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({'error': 'File size exceeds 10MB limit'}), 413


if __name__ == '__main__':
    print("Starting ATS Resume Analyzer Server...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)
