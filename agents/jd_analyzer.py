from typing import Dict, Any, List
import json
from .base_agent import BaseAgent
from .llm_client import LlamaClient

class JDAnalyzerAgent(BaseAgent):
    """Agent responsible for analyzing job descriptions and breaking them down into structured criteria."""
    
    def __init__(self):
        super().__init__("JDAnalyzer")
        self.llm_client = LlamaClient()
        
    async def validate(self, data: Dict[str, str]) -> bool:
        """Validate if the input contains required job description data."""
        return isinstance(data, dict) and "text" in data
        
    async def process(self, data: Dict[str, str]) -> Dict[str, Any]:
        """Break down job description into structured criteria using LLM."""
        if not await self.validate(data):
            raise ValueError("Invalid input data format")
            
        text = data["text"]
        
        # 直接使用LLM分析整个JD
        prompt = """
        请分析以下工作描述，提取关键信息并以JSON格式返回，包含以下字段：
        {
            "job_title": "职位名称",
            "industry": "所属行业",
            "required_skills": ["必需技能列表"],
            "preferred_skills": ["加分技能列表"],
            "responsibilities": ["工作职责列表"],
            "experience_requirements": {
                "years": "要求年限",
                "description": "经验要求描述"
            },
            "education_requirements": {
                "degree": "学历要求",
                "major": "专业要求"
            },
            "additional_requirements": ["其他要求列表"]
        }
        工作描述："""+text+"""
        请确保返回的是有效的JSON格式。只返回JSON数据，不要包含其他说明文字。
        """
        
        try:
            response = await self.llm_client._call_llm(prompt)
            # 提取JSON部分（以防LLM返回了额外的文本）
            json_str = response[response.find("{"):response.rfind("}")+1]
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Error parsing LLM response: {e}")
            return {
                "job_title": "",
                "industry": "",
                "required_skills": [],
                "preferred_skills": [],
                "responsibilities": [],
                "experience_requirements": {
                    "years": "",
                    "description": ""
                },
                "education_requirements": {
                    "degree": "",
                    "major": ""
                },
                "additional_requirements": []
            }
        
    async def _extract_job_title(self, text: str) -> str:
        """Extract the job title from the description."""
        # Implement job title extraction logic
        return ""
        
    async def _determine_job_variant(self, text: str) -> str:
        """Determine the specific variant of the job."""
        # Implement job variant determination logic
        return ""
        
    async def _determine_industry(self, text: str) -> str:
        """Determine the industry from the job description."""
        # Implement industry determination logic
        return ""
        
    async def _extract_description(self, text: str) -> str:
        """Extract the main job description."""
        # Implement description extraction logic
        return ""
        
    async def _extract_tasks(self, text: str) -> List[Dict[str, Any]]:
        """Extract tasks and their details from the job description."""
        tasks = []
        # Implement task extraction logic
        # Each task should follow the structure from the prompt
        return tasks
        
    async def _extract_skills(self, task_text: str) -> List[Dict[str, Any]]:
        """Extract skills and their variants for a specific task."""
        skills = []
        # Implement skill extraction logic
        return skills 

