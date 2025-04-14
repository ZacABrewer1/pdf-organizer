import re
import os
import PyPDF2
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Class to handle PDF processing operations like content extraction"""
    
    def __init__(self, patterns: Optional[List[str]] = None):
        """
        Initialize with configurable patterns for job extraction
        
        Args:
            patterns: List of regex patterns to use for job extraction. 
                     Default is 'Job:\s*(.*)'
        """
        self.patterns = patterns or [r"Job:\s*(.*)"]
    
    def get_pdf_files(self, folder: str) -> List[str]:
        """
        Get all PDF files in a folder
        
        Args:
            folder: Path to folder containing PDF files
            
        Returns:
            List of PDF filenames
        """
        if not os.path.exists(folder):
            logger.error(f"Folder does not exist: {folder}")
            return []
            
        return [f for f in os.listdir(folder) if f.lower().endswith(".pdf")]
    
    def extract_job_text(self, pdf_path: str) -> str:
        """
        Extract job information from PDF using configured patterns
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted job text or "Unknown Job" if not found
        """
        try:
            with open(pdf_path, "rb") as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                num_pages = len(pdf_reader.pages)
                
                # Try each page until we find a match
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    # Try each pattern until we find a match
                    for pattern in self.patterns:
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            job_text = match.group(1).strip()
                            logger.debug(f"Extracted job text '{job_text}' from {pdf_path}")
                            return job_text
            
            logger.warning(f"No job information found in {pdf_path} using patterns {self.patterns}")
            return "Unknown Job"
            
        except Exception as e:
            logger.error(f"Error parsing PDF '{pdf_path}': {e}")
            return "Unknown Job"  # Handle errors gracefully
    
    def analyze_pdf_folder(self, folder_path: str, target_folders: Dict[str, str], 
                         existing_mapping: Dict[str, str]) -> Dict[str, Dict[str, str]]:
        """
        Analyze PDF folder and create a preview of file destinations
        
        Args:
            folder_path: Path to source folder
            target_folders: Dictionary mapping job names to target folders
            existing_mapping: Dictionary of previously mapped files
            
        Returns:
            Dictionary with file organization preview data
        """
        preview_data = {
            'to_process': {},
            'unknown': [],
            'already_mapped': {}
        }
        
        pdf_files = self.get_pdf_files(folder_path)
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(folder_path, pdf_file)
            
            # Check if already mapped
            if pdf_file in existing_mapping:
                target_folder = existing_mapping[pdf_file]
                preview_data['already_mapped'][pdf_file] = target_folder
            else:
                # Extract job info and determine target
                job_text = self.extract_job_text(pdf_path)
                
                if job_text in target_folders:
                    target_folder = target_folders[job_text]
                    preview_data['to_process'][pdf_file] = {
                        'job_text': job_text,
                        'target_folder': target_folder
                    }
                else:
                    preview_data['unknown'].append({
                        'file': pdf_file,
                        'job_text': job_text
                    })
        
        return preview_data
