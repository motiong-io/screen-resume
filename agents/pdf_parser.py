import aiohttp
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class PDFParserAgent:
    """Agent responsible for parsing PDF documents using external API."""
    
    def __init__(self, api_url: str = "http://10.2.3.50:8000/parse_document/pdf"):
        self.api_url = api_url
        
    async def parse_pdf(self, pdf_content: bytes) -> Dict[str, Any]:
        """
        Parse PDF content using the external API.
        
        Args:
            pdf_content: The binary content of the PDF file
            
        Returns:
            Dict containing the parsed PDF data
        """
        try:
            async with aiohttp.ClientSession() as session:
                form = aiohttp.FormData()
                form.add_field('file',
                             pdf_content,
                             filename='document.pdf',
                             content_type='application/pdf')
                
                async with session.post(self.api_url, data=form) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        logger.error(f"PDF parsing failed with status {response.status}: {error_text}")
                        raise Exception(f"PDF parsing failed: {error_text}")
                        
        except Exception as e:
            logger.error(f"Error parsing PDF: {str(e)}")
            raise 