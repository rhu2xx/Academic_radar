"""
PDF parsing utilities.
Extracts text from academic papers using pymupdf.
"""
import logging
from pathlib import Path
from typing import Optional
import fitz  # PyMuPDF (pymupdf package imports as 'fitz')

logger = logging.getLogger(__name__)


class PDFParser:
    """Extracts text from PDF files."""
    
    @staticmethod
    def extract_text(pdf_path: str, max_pages: Optional[int] = None) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path: Path to PDF file
            max_pages: Maximum number of pages to extract (None = all)
            
        Returns:
            Extracted text as string
        """
        try:
            doc = fitz.open(pdf_path)
            text_parts = []
            
            pages_to_process = range(len(doc)) if max_pages is None else range(min(max_pages, len(doc)))
            
            for page_num in pages_to_process:
                page = doc[page_num]
                text_parts.append(page.get_text())
            
            doc.close()
            
            full_text = "\n\n".join(text_parts)
            logger.info(f"Extracted {len(full_text)} characters from {Path(pdf_path).name}")
            return full_text
            
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            raise
    
    @staticmethod
    def extract_sections(pdf_path: str, target_sections: list[str] = None) -> dict[str, str]:
        """
        Attempt to extract specific sections (e.g., 'Methodology', 'Results').
        Uses simple heuristics to identify section headers.
        
        Args:
            pdf_path: Path to PDF file
            target_sections: Section names to look for (case-insensitive)
            
        Returns:
            Dictionary mapping section names to their content
        """
        if target_sections is None:
            target_sections = ['abstract', 'introduction', 'methodology', 'method', 'approach', 'results']
        
        full_text = PDFParser.extract_text(pdf_path)
        sections = {}
        
        # Simple heuristic: look for section headers (lines with keywords followed by newlines)
        lines = full_text.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line_lower = line.strip().lower()
            
            # Check if line is a section header
            is_header = False
            for target in target_sections:
                if target in line_lower and len(line.strip()) < 50:  # Headers are usually short
                    # Save previous section
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content)
                    
                    current_section = target
                    current_content = []
                    is_header = True
                    break
            
            if not is_header and current_section:
                current_content.append(line)
        
        # Save last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    @staticmethod
    def smart_truncate(text: str, max_chars: int = 8000) -> str:
        """
        Truncate text intelligently to fit token limits.
        Tries to break at sentence boundaries.
        """
        if len(text) <= max_chars:
            return text
        
        truncated = text[:max_chars]
        
        # Try to break at last sentence
        last_period = truncated.rfind('. ')
        if last_period > max_chars * 0.8:  # Only if we don't lose too much
            truncated = truncated[:last_period + 1]
        
        return truncated + "\n\n[...truncated]"
