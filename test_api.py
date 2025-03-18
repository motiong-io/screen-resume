import asyncio
import aiohttp
import json
from pathlib import Path
import base64

async def test_resume_screening_api(resume_text: str, job_description: str):
    """Test the resume screening API endpoint."""
    url = "http://localhost:8000/screen"
    
    # Create temporary files for testing
    resume_file = Path("test_resume.txt")
    jd_file = Path("test_jd.txt")
    
    try:
        # Write test files
        resume_file.write_text(resume_text, encoding='utf-8')
        jd_file.write_text(job_description, encoding='utf-8')
        
        # Prepare request data
        data = {
            "jd_file": str(jd_file),
            "resume_files": [str(resume_file)]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                result = await response.json()
                print("\nAPI Response:")
                print(json.dumps(result, ensure_ascii=False, indent=2))
                return result
                
    except Exception as e:
        print(f"Error testing API: {e}")
        return None
    finally:
        # Cleanup test files
        if resume_file.exists():
            resume_file.unlink()
        if jd_file.exists():
            jd_file.unlink()

async def run_api_tests():
    """Run API tests with different scenarios."""
    
    # Test job description
    job_description = """
    Senior Software Engineer - Backend
    
    We are looking for an experienced backend engineer with:
    - Strong Python and Java skills
    - Experience with microservices architecture
    - Knowledge of cloud platforms (AWS/Azure)
    - Understanding of distributed systems
    
    Responsibilities:
    - Design and implement scalable backend services
    - Lead technical projects and mentor junior developers
    - Optimize system performance
    - Collaborate with cross-functional teams
    
    Requirements:
    - 5+ years of software development experience
    - Master's degree in Computer Science or related field
    - Experience with cloud technologies
    """
    
    # Test with Chinese resume
    print("\nTesting Chinese Resume:")
    print("-" * 50)
    await test_resume_screening_api(test_resumes["chinese"], job_description)
    
    # Test with English resume
    print("\nTesting English Resume:")
    print("-" * 50)
    await test_resume_screening_api(test_resumes["english"], job_description)

if __name__ == "__main__":
    # Import test resumes from test_extraction.py
    from test_extraction import test_resumes
    asyncio.run(run_api_tests()) 