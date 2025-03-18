from typing import Dict, Any, List
import re
from .base_agent import BaseAgent
from .llm_client import LlamaClient
from .data.universities import is_211_university, is_985_university, is_qs_top20_university

class KnowledgeExtractorAgent(BaseAgent):
    """Agent responsible for extracting key information from resume text."""
    
    def __init__(self):
        super().__init__("KnowledgeExtractor")
        self.llm_client = LlamaClient()
    
    def detect_language(self, text: str) -> str:
        """Detect if the text is primarily Chinese or English."""
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_words = len(re.findall(r'[a-zA-Z]+', text))
        return "zh" if chinese_chars > english_words else "en"
    
    async def validate(self, data: Dict[str, str]) -> bool:
        """Validate if the input contains required text data."""
        return isinstance(data, dict) and "text" in data
        
    async def process(self, data: Dict[str, str]) -> Dict[str, Any]:
        """Extract key information from the resume text."""
        if not await self.validate(data):
            raise ValueError("Invalid input data format")
            
        text = data["text"]
        language = self.detect_language(text)
        
        # Use LLM to get structured information
        llm_result = await self.llm_client.extract_structured_info(text, language)
        
        # Process education information to check for university rankings
        education = llm_result.get("education", [])
        for edu in education:
            if isinstance(edu, dict) and "institution" in edu:
                edu["is_qs_top20"] = is_qs_top20_university(edu["institution"])
                edu["is_985"] = is_985_university(edu["institution"])
                edu["is_211"] = is_211_university(edu["institution"])
        
        # Return processed results
        return {
            "basic_info": llm_result.get("basic_info", {}),
            "contact": llm_result.get("contact", {}),
            "summary": llm_result.get("summary", ""),
            "skills": llm_result.get("skills", []),
            "experience": llm_result.get("experience", []),
            "education": education,
            "projects": llm_result.get("projects", []),
            "certifications": llm_result.get("certifications", []),
            "languages": llm_result.get("languages", [])
        } 