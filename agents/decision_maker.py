from typing import Dict, Any, List
import json
from .base_agent import BaseAgent
from .llm_client import LlamaClient

class DecisionMakerAgent(BaseAgent):
    """Agent responsible for evaluating candidates against job requirements."""
    
    def __init__(self):
        super().__init__("DecisionMaker")
        self.llm_client = LlamaClient()
        
    async def validate(self, data: Dict[str, Any]) -> bool:
        """Validate if the input contains required candidate and job data."""
        required_keys = ["candidate_info", "job_requirements"]
        return all(key in data for key in required_keys)
        
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate candidate fit against job requirements using LLM."""
        if not await self.validate(data):
            raise ValueError("Invalid input data format")
            
        candidate_info = data["candidate_info"]
        job_requirements = data["job_requirements"]
        
        # 构建评估提示
        evaluation_prompt = f"""
        请作为专业的HR评估专家，分析候选人与职位的匹配程度。

        职位要求：
        {json.dumps(job_requirements, ensure_ascii=False, indent=2)}

        候选人信息：
        {json.dumps(candidate_info, ensure_ascii=False, indent=2)}

        请提供详细的评估，并以以下JSON格式返回结果：
        {{
            "scores": {{
                "skills_match": "技能匹配得分(0-1)",
                "experience_match": "经验匹配得分(0-1)",
                "education_match": "教育背景匹配得分(0-1)"
            }},
            "analysis": {{
                "skills_analysis": "技能匹配分析",
                "experience_analysis": "经验匹配分析",
                "education_analysis": "教育背景匹配分析",
                "overall_analysis": "整体评估分析"
            }},
            "overall_score": "总体匹配得分(0-1)",
            "recommendation": "建议（'Strong Match - Highly Recommended' | 'Good Match - Recommended' | 'Moderate Match - Consider for Interview' | 'Weak Match - Not Recommended'）"
        }}

        请确保：
        1. 所有得分在0到1之间
        2. 分析要具体且有见地
        3. 只返回JSON格式数据，不要包含其他说明文字
        """

        try:
            response = await self.llm_client._call_llm(evaluation_prompt)
            # 提取JSON部分
            json_str = response[response.find("{"):response.rfind("}")+1]
            result = json.loads(json_str)
            
            # 确保得分在0-1之间
            result["scores"] = {k: min(max(float(v), 0), 1) for k, v in result["scores"].items()}
            result["overall_score"] = min(max(float(result["overall_score"]), 0), 1)
            
            return result
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error processing LLM response: {e}")
            # 返回默认结果
            return {
                "scores": {
                    "skills_match": 0.0,
                    "experience_match": 0.0,
                    "education_match": 0.0
                },
                "analysis": {
                    "skills_analysis": "无法进行技能分析",
                    "experience_analysis": "无法进行经验分析",
                    "education_analysis": "无法进行教育背景分析",
                    "overall_analysis": "评估过程出现错误"
                },
                "overall_score": 0.0,
                "recommendation": "Weak Match - Not Recommended"
            } 