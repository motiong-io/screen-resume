import asyncio
from agents.knowledge_extractor import KnowledgeExtractorAgent
import json
from pprint import pprint

# Test resumes in different languages
test_resumes = {
    "chinese": """
张三
高级软件工程师

联系方式：
电话：13812345678
邮箱：zhangsan@example.com

专业技能：
• Python, Java, Golang
• 微服务架构, Docker, Kubernetes
• 分布式系统设计
• 机器学习和深度学习
• AWS, Azure云平台

工作经历：
腾讯科技（2020年3月 - 至今）
高级后端工程师
• 负责支付系统核心模块开发
• 优化系统性能，提升QPS 50%
• 带领5人团队完成微服务改造

阿里巴巴（2018年7月 - 2020年2月）
软件工程师
• 开发电商平台后端服务
• 实现订单处理系统
• 参与大规模分布式系统设计

教育背景：
清华大学 计算机科学与技术
硕士学位 2018年
北京大学 软件工程
学士学位 2015年
    """,
    
    "english": """
John Smith
Senior Software Engineer

Contact Information:
Phone: +1 (123) 456-7890
Email: john.smith@example.com

Technical Skills:
• Python, Java, Golang
• Microservices Architecture
• Docker, Kubernetes
• Machine Learning
• AWS, Azure Cloud

Professional Experience:
Google (March 2020 - Present)
Senior Software Engineer
• Led development of core payment processing system
• Improved system performance by 50%
• Managed team of 5 engineers

Facebook (July 2018 - February 2020)
Software Engineer
• Developed backend services for news feed
• Implemented real-time notification system
• Contributed to distributed systems design

Education:
Stanford University
Master of Science in Computer Science, 2018
MIT
Bachelor of Science in Computer Science, 2015
    """
}

async def test_single_resume(extractor: KnowledgeExtractorAgent, resume_text: str, language: str):
    """Test extraction for a single resume."""
    print(f"\nTesting {language} resume extraction:")
    print("-" * 50)
    
    try:
        result = await extractor.process({"text": resume_text})
        print(f"\nExtracted Information ({language}):")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return result
    except Exception as e:
        print(f"Error processing {language} resume: {e}")
        return None

async def run_tests():
    """Run all resume extraction tests."""
    extractor = KnowledgeExtractorAgent()
    
    results = {}
    for language, resume in test_resumes.items():
        results[language] = await test_single_resume(extractor, resume, language)
    
    # Validate results
    print("\nValidation Results:")
    print("-" * 50)
    for language, result in results.items():
        if result:
            print(f"\n{language.capitalize()} Resume Validation:")
            # Check for required fields
            has_skills = len(result["skills"]) > 0
            has_experience = len(result["experience"]) > 0
            has_education = len(result["education"]) > 0
            has_contact = len(result["contact_info"]) > 0
            
            print(f"✓ Skills extracted: {has_skills} ({len(result['skills'])} skills found)")
            print(f"✓ Experience extracted: {has_experience} ({len(result['experience'])} entries)")
            print(f"✓ Education extracted: {has_education} ({len(result['education'])} entries)")
            print(f"✓ Contact info extracted: {has_contact}")
            
            # Detailed validation
            if not has_skills:
                print("⚠️ Warning: No skills extracted")
            if not has_experience:
                print("⚠️ Warning: No experience extracted")
            if not has_education:
                print("⚠️ Warning: No education extracted")
            if not has_contact:
                print("⚠️ Warning: No contact information extracted")

if __name__ == "__main__":
    asyncio.run(run_tests()) 