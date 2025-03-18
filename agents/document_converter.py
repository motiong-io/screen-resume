from typing import Dict, Any
import PyPDF2
from docx import Document
from .base_agent import BaseAgent

class DocumentConverterAgent(BaseAgent):
    """Agent responsible for converting different document formats to text."""
    
    def __init__(self):
        super().__init__("DocumentConverter")
        
    async def validate(self, file_path: str) -> bool:
        """Validate if the file format is supported."""
        return file_path.lower().endswith(('.pdf', '.docx'))
    
    async def process(self, file_path: str) -> Dict[str, Any]:
        """Convert document to text based on file format."""
        if not await self.validate(file_path):
            raise ValueError(f"Unsupported file format: {file_path}")
            
        if file_path.lower().endswith('.pdf'):
            return await self._convert_pdf(file_path)
        elif file_path.lower().endswith('.docx'):
            return await self._convert_docx(file_path)
            
    async def _convert_pdf(self, file_path: str) -> Dict[str, Any]:
        """Convert PDF to text."""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return {"text": text, "format": "pdf"}
    
    async def _convert_docx(self, file_path: str) -> Dict[str, Any]:
        """Convert DOCX to text."""
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return {"text": text, "format": "docx"} 