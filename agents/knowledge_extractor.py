from typing import Dict, Any, List
import re
from .base_agent import BaseAgent
from .llm_client import LlamaClient

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
        
        # Validate and clean the results
        return {
            "skills": self._clean_skills(llm_result.get("skills", [])),
            "experience": self._clean_experience(llm_result.get("experience", [])),
            "education": self._clean_education(llm_result.get("education", [])),
            "contact_info": self._clean_contact_info(llm_result.get("contact", {}), language)
        }
    
    def _clean_skills(self, skills: List[str]) -> List[str]:
        """Clean and deduplicate skills."""
        # Remove empty strings and duplicates
        cleaned = {skill.strip() for skill in skills if skill.strip()}
        return list(cleaned)
    
    def _clean_experience(self, experience: List[Dict]) -> List[Dict]:
        """Clean experience entries."""
        cleaned = []
        for exp in experience:
            if isinstance(exp, dict):
                # Ensure all required fields are present
                cleaned_exp = {
                    "company": exp.get("company", ""),
                    "title": exp.get("title", ""),
                    "duration": exp.get("duration", ""),
                    "responsibilities": exp.get("responsibilities", [])
                }
                if cleaned_exp["company"] and cleaned_exp["title"]:  # Only include if has minimum required info
                    cleaned.append(cleaned_exp)
        return cleaned
    
    def _clean_education(self, education: List[Dict]) -> List[Dict]:
        """Clean education entries."""
        cleaned = []
        for edu in education:
            if isinstance(edu, dict):
                # Ensure all required fields are present
                cleaned_edu = {
                    "degree": edu.get("degree", ""),
                    "institution": edu.get("institution", ""),
                    "year": edu.get("year", "")
                }
                if cleaned_edu["institution"]:  # Only include if has minimum required info
                    cleaned.append(cleaned_edu)
        return cleaned
    
    def _clean_contact_info(self, contact: Dict[str, str], language: str) -> Dict[str, str]:
        """Clean and validate contact information."""
        cleaned = {}
        
        # Clean email
        if "email" in contact and isinstance(contact["email"], str):
            email = contact["email"].strip()
            if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                cleaned["email"] = email
        
        # Clean phone number based on language
        if "phone" in contact and isinstance(contact["phone"], str):
            phone = re.sub(r'\s+', '', contact["phone"])  # Remove whitespace
            phone_patterns = {
                "en": r'\+?\d{1,3}[-.]?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}',
                "zh": r'(?:\+?86)?1[3-9]\d{9}'
            }
            if re.match(phone_patterns[language], phone):
                cleaned["phone"] = phone
        
        return cleaned 