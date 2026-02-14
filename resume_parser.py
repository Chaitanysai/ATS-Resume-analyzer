"""
Resume Parser Module
Extracts text from PDF and DOCX resume files
"""

import os
import re
from typing import Optional
import PyPDF2
from docx import Document


class ResumeParser:
    """Parse resumes from various file formats"""
    
    SUPPORTED_FORMATS = ['.pdf', '.docx', '.doc']
    
    def __init__(self):
        self.max_file_size = 10 * 1024 * 1024  # 10MB limit
    
    def parse_resume(self, file_path: str) -> Optional[str]:
        """
        Extract text from resume file
        
        Args:
            file_path: Path to resume file
            
        Returns:
            Extracted text or None if parsing failed
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Check file size
        if os.path.getsize(file_path) > self.max_file_size:
            raise ValueError("File size exceeds 10MB limit")
        
        # Get file extension
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {ext}. Supported: {self.SUPPORTED_FORMATS}")
        
        # Parse based on format
        try:
            if ext == '.pdf':
                return self._parse_pdf(file_path)
            elif ext in ['.docx', '.doc']:
                return self._parse_docx(file_path)
        except Exception as e:
            raise Exception(f"Error parsing resume: {str(e)}")
    
    def _parse_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract text from all pages
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
        
        return self._clean_text(text)
    
    def _parse_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        text = ""
        
        try:
            doc = Document(file_path)
            
            # Extract text from paragraphs
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            # Extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        text += cell.text + " "
                text += "\n"
        except Exception as e:
            raise Exception(f"Error reading DOCX: {str(e)}")
        
        return self._clean_text(text)
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        # Remove non-printable characters but keep common punctuation
        text = ''.join(char for char in text if char.isprintable() or char in '\n\t')
        
        return text.strip()
    
    def extract_metadata(self, file_path: str) -> dict:
        """Extract metadata from resume file"""
        metadata = {
            'filename': os.path.basename(file_path),
            'file_size': os.path.getsize(file_path),
            'format': os.path.splitext(file_path)[1].lower(),
        }
        
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext == '.pdf':
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    metadata['page_count'] = len(pdf_reader.pages)
                    
                    # Try to get PDF metadata
                    if pdf_reader.metadata:
                        metadata['author'] = pdf_reader.metadata.get('/Author', 'Unknown')
                        metadata['title'] = pdf_reader.metadata.get('/Title', 'Unknown')
            except:
                pass
        
        elif ext in ['.docx', '.doc']:
            try:
                doc = Document(file_path)
                metadata['page_count'] = 'N/A'  # Word doesn't have direct page count
                metadata['paragraph_count'] = len(doc.paragraphs)
                
                # Try to get document properties
                core_props = doc.core_properties
                if core_props:
                    metadata['author'] = core_props.author or 'Unknown'
                    metadata['title'] = core_props.title or 'Unknown'
            except:
                pass
        
        return metadata


# Example usage
if __name__ == "__main__":
    parser = ResumeParser()
    
    # Example: Parse a sample resume
    # text = parser.parse_resume("sample_resume.pdf")
    # print(text)
    
    print("Resume Parser initialized successfully!")
    print(f"Supported formats: {parser.SUPPORTED_FORMATS}")
