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
                    1. basic_info: Basic information including name, age, years of experience, current location
                    2. contact: Contact information including email and phone number
                    3. summary: A brief professional summary
                    4. skills: List of technical and professional skills
                    5. experience: List of work experiences with:
                       - company: Company name
                       - title: Job title
                       - duration: Employment period
                       - responsibilities: Key responsibilities and achievements
                    6. education: List of educational background with:
                       - degree: Degree name
                       - institution: School/University name
                       - year: Graduation year
                       - major: Field of study
                    7. projects: List of significant projects with:
                       - name: Project name
                       - description: Project description
                       - technologies: Technologies used
                       - role: Your role
                    8. certifications: List of professional certifications
                    9. languages: Language proficiencies
                    
                    Return the information in valid JSON format only.""",
            "zh": """请从简历中提取以下信息，并以JSON格式返回：
                    1. basic_info: 基本信息，包括姓名、年龄、工作年限、所在地
                    2. contact: 联系方式，包括邮箱和电话号码
                    3. summary: 个人简介
                    4. skills: 技术和专业技能列表
                    5. experience: 工作经历列表，包含：
                       - company: 公司名称
                       - title: 职位名称
                       - duration: 工作时间段
                       - responsibilities: 主要职责和成就
                    6. education: 教育背景列表，包含：
                       - degree: 学位
                       - institution: 学校名称
                       - year: 毕业年份
                       - major: 专业
                    7. projects: 项目经验列表，包含：
                       - name: 项目名称
                       - description: 项目描述
                       - technologies: 使用的技术
                       - role: 担任角色
                    8. certifications: 专业证书列表
                    9. languages: 语言能力
                    
                    仅返回有效的JSON格式数据。"""
        }
        
        prompt = f"{system_prompt[language]}\n\nResume text:\n{text}"
        
        try:
            response = await self._call_llm(prompt)
            # Extract JSON from response
            json_str = response[response.find("{"):response.rfind("}")+1]
            return json.loads(json_str)
        except Exception as e:
            print(f"Error processing with LLM: {e}")
            return {
                "basic_info": {},
                "contact": {},
                "summary": "",
                "skills": [],
                "experience": [],
                "education": [],
                "contact": {}
            }

    # async def extract_jd_requirements(self, text: str) -> Dict[str, Any]:
    #     """使用LLM提取JD要求"""
    #     prompt = f"""
    #     请从以下工作描述中提取关键要求：
    #     1. 必要技能
    #     2. 工作职责
    #     3. 工作经验要求
    #     4. 教育背景要求
    #     5. 其他要求

    #     工作描述：
    #     {text}
        
    #     请以结构化的JSON格式返回结果。
    #     """
        
    #     response = await self._call_llm(prompt)
    #     return response