from typing import Dict, Any, List
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .base_agent import BaseAgent

class DecisionMakerAgent(BaseAgent):
    """Agent responsible for evaluating candidates against job requirements."""
    
    def __init__(self):
        super().__init__("DecisionMaker")
        self.vectorizer = TfidfVectorizer()
        
    async def validate(self, data: Dict[str, Any]) -> bool:
        """Validate if the input contains required candidate and job data."""
        required_keys = ["candidate_info", "job_requirements"]
        return all(key in data for key in required_keys)
        
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate candidate fit against job requirements."""
        if not await self.validate(data):
            raise ValueError("Invalid input data format")
            
        candidate_info = data["candidate_info"]
        job_requirements = data["job_requirements"]
        
        scores = {
            "skills_match": await self._evaluate_skills(
                candidate_info["skills"],
                job_requirements["required_skills"]
            ),
            "experience_match": await self._evaluate_experience(
                candidate_info["experience"],
                job_requirements["required_experience"]
            ),
            "education_match": await self._evaluate_education(
                candidate_info["education"],
                job_requirements["required_education"]
            )
        }
        
        overall_score = await self._calculate_overall_score(scores)
        
        return {
            "scores": scores,
            "overall_score": overall_score,
            "recommendation": await self._generate_recommendation(overall_score),
            "analysis": await self._generate_analysis(scores, candidate_info, job_requirements)
        }
        
    async def _evaluate_skills(self, candidate_skills: List[str], required_skills: List[str]) -> float:
        """Evaluate the match between candidate skills and required skills."""
        if not candidate_skills or not required_skills:
            return 0.0
            
        # Convert skills to text for TF-IDF vectorization
        candidate_text = " ".join(candidate_skills)
        required_text = " ".join(required_skills)
        
        # Calculate similarity score
        vectors = self.vectorizer.fit_transform([candidate_text, required_text])
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        
        return float(similarity)
        
    async def _evaluate_experience(self, candidate_exp: List[Dict], required_exp: Dict) -> float:
        """Evaluate the match between candidate experience and required experience."""
        # Implement experience evaluation logic
        return 0.0
        
    async def _evaluate_education(self, candidate_edu: List[Dict], required_edu: Dict) -> float:
        """Evaluate the match between candidate education and required education."""
        # Implement education evaluation logic
        return 0.0
        
    async def _calculate_overall_score(self, scores: Dict[str, float]) -> float:
        """Calculate the overall candidate score."""
        weights = {
            "skills_match": 0.4,
            "experience_match": 0.4,
            "education_match": 0.2
        }
        
        overall_score = sum(score * weights[metric] for metric, score in scores.items())
        return round(overall_score, 2)
        
    async def _generate_recommendation(self, overall_score: float) -> str:
        """Generate a recommendation based on the overall score."""
        if overall_score >= 0.8:
            return "Strong Match - Highly Recommended"
        elif overall_score >= 0.6:
            return "Good Match - Recommended"
        elif overall_score >= 0.4:
            return "Moderate Match - Consider for Interview"
        else:
            return "Weak Match - Not Recommended"
            
    async def _generate_analysis(self, scores: Dict[str, float], 
                               candidate_info: Dict[str, Any],
                               job_requirements: Dict[str, Any]) -> str:
        """Generate a detailed analysis of the candidate's fit."""
        analysis = []
        
        # Add analysis implementation
        
        return "\n".join(analysis) 