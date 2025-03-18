from openai import AsyncOpenAI
import json
from typing import Dict, Any, List

class LlamaClient:
    """Client for interacting with Llama 3.3 70B model."""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            base_url="http://10.4.33.13:80/v1",
            api_key="123"
        )
        self.model = "ibnzterrell/Meta-Llama-3.3-70B-Instruct-AWQ-INT4"
        
    async def _call_llm(self, prompt: str) -> str:
        """Make an async call to the Llama API."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts structured information from resumes."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1  # Low temperature for more consistent outputs
        )
        return response.choices[0].message.content
    
    async def extract_structured_info(self, text: str, language: str) -> Dict[str, Any]:
        """Extract structured information from resume text using LLM."""
        system_prompt = {
            "en": """Extract the following information from the resume in JSON format:
                    1. Skills: List of technical and professional skills
                    2. Experience: List of work experiences with company, title, duration, and responsibilities
                    3. Education: List of educational background with degree, institution, and year
                    4. Contact: Email and phone number
                    Return the information in valid JSON format only.""",
            "zh": """请从简历中提取以下信息，并以JSON格式返回：
                    1. skills: 技术和专业技能列表
                    2. experience: 工作经历列表，包含公司名称、职位、时间段和职责
                    3. education: 教育背景列表，包含学位、院校和年份
                    4. contact: 邮箱和电话号码
                    仅返回有效的JSON格式数据。"""
        }
        
        prompt = f"{system_prompt[language]}\n\nResume text:\n{text}"
        
        try:
            response = await self._call_llm(prompt)
            # Extract JSON from response (in case LLM adds any extra text)
            json_str = response[response.find("{"):response.rfind("}")+1]
            return json.loads(json_str)
        except Exception as e:
            print(f"Error processing with LLM: {e}")
            return {
                "skills": [],
                "experience": [],
                "education": [],
                "contact": {}
            }